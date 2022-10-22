import databases
import dataclasses
import sqlite3
import json
import toml
import hashlib
import secrets

from quart import Quart, g, request, abort, make_response
from quart_schema import (
    tag,
    validate_request,
    QuartSchema,
    validate_response,
)
from random import randint
from typing import List, Tuple

app = Quart(__name__)
QuartSchema(app)

app.config.from_file("./etc/wordle.toml", toml.load)


@dataclasses.dataclass
class Error:
    error: str


@dataclasses.dataclass
class AuthorizedUser:
    authenticated: bool


@dataclasses.dataclass
class Guess:
    guess: str


@dataclasses.dataclass
class User:
    username: str
    password: str


@dataclasses.dataclass
class Game:
    username: str


@dataclasses.dataclass
class GameState:
    """The state of the game including information about last guess."""

    gameid: int
    guesses: int = 6
    correct: str = "h??lo"
    incorrect: str = "??e??"
    completed: bool = False


@dataclasses.dataclass
class Main:
    title: str = "Wordle"


# ---------------------------------------------------------------------------- #
#                                 helper funcs                                 #
# ---------------------------------------------------------------------------- #

# functions to hash and verify from https://til.simonwillison.net/python/password-hashing-with-pbkdf2
async def _hash_password(password: str, salt: str = None):
    if not salt:
        salt = secrets.token_hex(16)

    pw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()

    return f"{salt}${pw_hash}"


async def _get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = databases.Database(app.config["DATABASES"]["URL"])
        await db.connect()
    return db


async def _get_random_word():
    with open("./share/correct.json") as file:
        data = json.load(file)
        rand_index = randint(0, len(data) - 1)
        return data[rand_index]


async def _check_string(guess: str, goal: str) -> Tuple[str, str]:

    guess = guess.lower()

    if guess == goal:
        return (goal, "?????")

    # helper function to replace a character in an index of a string
    def replace_idx(s: str, idx: int, letter: str) -> str:
        return s[:idx] + letter + s[idx + 1 :]

    # create a hashmap of goal string and letter count
    goal_cnt = {}
    for letter in goal:
        goal_cnt[letter] = goal_cnt.get(letter, 0) + 1

    correct_spot = "?????"
    incorrect_spot = "?????"

    # first pass to check for correct spot which deals with duplicates,
    # ex: guess = "hello", goal = "world", we dont want to count the first 'l'.
    for i in range(len(guess)):
        if guess[i] == goal[i]:
            correct_spot = replace_idx(correct_spot, i, guess[i])
            goal_cnt[guess[i]] -= 1

    # second pass to check for incorrect spot
    for i in range(len(guess)):
        if guess[i] != goal[i] and goal_cnt.get(guess[i], 0) > 0:
            incorrect_spot = replace_idx(incorrect_spot, i, guess[i])
            goal_cnt[guess[i]] -= 1

    return (correct_spot, incorrect_spot)


# ---------------------------------------------------------------------------- #
#                                error handlers                                #
# ---------------------------------------------------------------------------- #
@app.errorhandler(400)
async def bad_request(e):
    return {"error": f"Bad Request: {e.description}"}, 400


@app.errorhandler(401)
async def unauthorized(e):
    response = await make_response({"error": f"Unauthorized: {e.description}"}, 401)
    response.status_code = 401
    response.headers["WWW-Authenticate"] = 'Basic realm="User Login"'
    return response


@app.errorhandler(404)
async def not_found(e):
    return {"error": f"Not Found: {e.description}"}, 404


@app.errorhandler(409)
async def username_exists(e):
    return {"error": "Username already exists"}, 409


# ---------------------------------------------------------------------------- #
#                                  api routes                                  #
# ---------------------------------------------------------------------------- #

# --------------------------------- register --------------------------------- #
@app.route("/auth/register", methods=["POST"])
@tag(["auth"])
@validate_request(User)
@validate_response(User, 201)
@validate_response(Error, 400)
@validate_response(Error, 409)
async def register_user(data):
    """Register a new user with a username and password."""
    db = await _get_db()
    user = dataclasses.asdict(data)

    if not user["username"] or not user["password"]:
        abort(400, "Username and password cannot be empty.")

    hashed_pw = await _hash_password(user["password"])
    user["password"] = hashed_pw
    try:
        id = await db.execute(
            """
            INSERT INTO users(username, password)
            VALUES(:username, :password)
            """,
            user,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)

    # TODO: possibly change location to /games/<username>
    return user, 201, {"Location": f"/users/{user['username']}"}


# ---------------------------------- sign in --------------------------------- #
@app.route("/auth/signin")
@tag(["auth"])
@validate_response(AuthorizedUser, 200)
@validate_response(Error, 400)
@validate_response(Error, 401)
async def signin():
    """
    Check if a username/password combination is valid.
    Uses Basic Auth passed through Authorization header.
    """

    auth = request.authorization

    # return bad request if invalid auth header
    if not auth:
        abort(400, "Authorization header is required.")

    # check both username and password are present
    if not auth.username or not auth.password:
        abort(400, "Username and password are required.")

    db = await _get_db()

    # fetch the row for the entered username
    user_row = await db.fetch_one(
        """
        SELECT *
        FROM users
        WHERE username = :username
        """,
        {"username": auth.username},
    )

    # if the username doesn't exist, return unauthorized
    if not user_row:
        abort(401, "Username does not exist.")

    # compute the hash of the entered password
    stored_pw = user_row[1]
    salt = stored_pw.split("$")[0]
    computed_hash = await _hash_password(auth.password, salt)

    # if the computed hash doesn't match the stored hash, return unauthorized
    if not secrets.compare_digest(computed_hash, stored_pw):
        abort(401, "Incorrect password.")

    # finally, return authenticated = true
    return {"authenticated": True}, 200


# -------------------------------- create game ------------------------------- #
@app.route("/games/create", methods=["POST"])
@tag(["games"])
@validate_request(Game)
@validate_response(GameState, 201)
@validate_response(Error, 400)
async def create_game(data):
    """Create a new game for a user with a random word."""
    game = dataclasses.asdict(data)
    game["secretword"] = await _get_random_word()

    db = await _get_db()

    username = await db.fetch_one(
        "SELECT * from users WHERE username = :username",
        values={"username": game["username"]},
    )

    if username:
        # create new row in game
        try:
            id = await db.execute(
                """
                INSERT INTO games(secretword, username)
                VALUES(:secretword, :username)
                """,
                game,
            )
        except sqlite3.IntegrityError as e:
            abort(409, e)

        game["gameid"] = id

        game_state = {
            "gameid": game["gameid"],
            "guesses": 6,
            "correct": "?????",
            "incorrect": "?????",
            "completed": False,
        }
        # create new row in game_states
        try:
            id = await db.execute(
                """
                INSERT INTO game_states(gameid, guesses, correct, incorrect, completed)
                VALUES(:gameid, :guesses, :correct, :incorrect, :completed)
                """,
                game_state,
            )
        except sqlite3.IntegrityError as e:
            abort(409, e)

        return game_state, 201, {"Location": f"/games/{game['gameid']}"}

    return "User does not exist.", 400


# ---------------------------- retrieve game state --------------------------- #
@app.route("/games/<int:gameid>", methods=["GET"])
@tag(["games"])
@validate_response(GameState, 200)
@validate_response(Error, 404)
async def get_game_state(gameid):
    """Retrieve the state of a game with a given gameid."""
    db = await _get_db()
    game_state = await db.fetch_one(
        "SELECT * FROM game_states WHERE gameid = :gameid", values={"gameid": gameid}
    )
    if game_state:
        return dict(game_state)
    else:
        abort(404, "Game with that id does not exist.")


# --------------------- make a guess / update game state --------------------- #
@app.route("/games/<int:gameid>", methods=["POST"])
@tag(["games"])
@validate_request(Guess)
@validate_response(GameState, 200)
@validate_response(Error, 400)
async def check_guess(data, gameid):
    """Make a guess for a game with a given gameid. Returns updated game state."""

    guess = await request.get_json()
    guess = guess["guess"]

    if len(guess) != 5:
        abort(400, "Guess must be 5 letters long.")

    db = await _get_db()

    # perform lookup in db table "valid_words" to check if guess is valid
    valid_word = await db.fetch_val(
        "SELECT EXISTS(SELECT 1 FROM valid_words WHERE word = :word)",
        values={"word": guess},
    )

    # 0 if not in table, 1 if in table
    if valid_word == 0:
        abort(400, "Guess is not a valid word.")

    # fetch a tuple of (secretword, guesses) from db
    info = await db.fetch_one(
        """
        SELECT secretword, guesses
        FROM games INNER JOIN game_states ON games.gameid = game_states.gameid
        WHERE games.gameid = :gameid
        """,
        {"gameid": gameid},
    )

    if not info:
        abort(404, "Game with that id does not exist.")

    # returns a tuple of formatted strings (correct, incorrect)
    # ex: ("?a???", "???b?") -> a is correct spot, b is incorrect spot
    state_fields = await _check_string(guess, info[0])

    # check if there are any guesses left
    if info[1] > 0:
        # check if guess is correct and update game state
        game_info = {
            "gameid": gameid,
            "guesses": info[1] - 1,
            "correct": state_fields[0],
            "incorrect": state_fields[1],
            "completed": False,
        }
        if guess == info[0]:
            game_info["completed"] = True
            await db.execute(
                """
                UPDATE game_states
                SET completed = :completed, guesses = :guesses, correct = :correct, incorrect = :incorrect
                WHERE gameid = :gameid
                """,
                values=game_info,
            )
        # if guess is incorrect, update game state
        else:
            await db.execute(
                """
                UPDATE game_states
                SET completed = :completed, guesses = guesses - 1, guesses = :guesses, correct = :correct, incorrect = :incorrect
                WHERE gameid = :gameid
                """,
                values=game_info,
            )
    else:
        abort(400, "No guesses left.")

    return game_info, 200


# -----------------------------------Listing in progress games------------------------#
@app.route("/users/<string:username>", methods=["GET"])
async def get_progress_game(username):
    """Retrieve the list of games in progress for a user with a given username."""
    db = await _get_db()
    progress_game = await db.fetch_all(
        """
        SELECT games.gameid,username
        FROM games LEFT JOIN game_states ON games.gameid = game_states.gameid 
        WHERE username = :username AND game_states.guesses != 0
        """,
        values={"username": username},
    )
    print("Progress of game1:", progress_game)
    if progress_game:
        print("Progress of game:", progress_game)
        return list(map(dict, progress_game))
    else:
        abort(404, "No games in progress for that user.")
