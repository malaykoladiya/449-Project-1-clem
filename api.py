import databases
import dataclasses
import sqlite3
import json
import toml
import hashlib
import secrets

from quart import Quart, g, request, abort, make_response
from quart_schema import validate_request, QuartSchema
from random import randint

app = Quart(__name__)
QuartSchema(app)

app.config.from_file("./etc/wordle.toml", toml.load)


@dataclasses.dataclass
class User:
    username: str
    password: str


@dataclasses.dataclass
class Game:
    username: str
    secretword: str = 'blank'


@dataclasses.dataclass
class GameState:
    gameid: int
    guesses: int
    correct: int
    incorrect: int


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


async def _verify_password(password: str, hashed_password: str) -> bool:
    if not hashed_password or hashed_password.count("$") != 1:
        return False

    salt = hashed_password.split("$")[0]
    computed_hash = await _hash_password(password, salt)
    return secrets.compare_digest(hashed_password, computed_hash)


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

async def check_string(string: str, word: str):
    correct = 0
    for i in string:
        if(i.find(word)):
            correct += 1
    return correct



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


@app.errorhandler(409)
async def username_exists(e):
    return {"error": "Username already exists"}, 409


# ---------------------------------------------------------------------------- #
#                                  api routes                                  #
# ---------------------------------------------------------------------------- #
@app.route("/")
async def hello():
    return "Hello World"


# --------------------------------- register --------------------------------- #
@app.route("/register", methods=["POST"])
@validate_request(User)
async def register_user(data):
    db = await _get_db()
    user = dataclasses.asdict(data)

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
    except sqlite3.IntegrityError:
        abort(409, "Username already exists!")

    # TODO: possibly change location to /games/<username>
    return user, 201, {"Location": f"/users/{user['username']}"}


# ---------------------------------- sign in --------------------------------- #
@app.route("/signin")
async def signin():

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
    return {"authenticated": True, "user": auth.username}, 200


# -------------------------------- create game ------------------------------- #
@app.route("/games/create", methods=["POST"])
@validate_request(Game)
async def create_game(data):
    game = dataclasses.asdict(data)
    game["secretword"] = await _get_random_word()

    db = await _get_db()

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

    game_state = {"gameid" : game["gameid"], "guesses" : 6, "correct" : 0, "incorrect" : 0}
    # create new row in game_states
    try:
        id = await db.execute(
            """
            INSERT INTO game_states(gameid, guesses, correct, incorrect)
            VALUES(:gameid, :guesses, :correct, :incorrect)
            """,
            game_state,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)

    return game_state, 201, dict(game_state)

# ---------------------------- retrieve game state --------------------------- #
@app.route("/games/game/<int:gameid>", methods=["GET"])
async def get_game_state(gameid):
    db = await _get_db()
    game_state = await db.fetch_one(
        "SELECT * FROM game_states WHERE gameid = :gameid", 
        values={"gameid": gameid}
        )
    if game_state:
        return dict(game_state)
    else:
        abort(404)

#--- make a guess / update game state ---#
@app.route("/games/game/<int:gameid>", methods=["POST"])
async def check_guess(gameid):
    gamestate = await get_game_state(gameid)
    guess = await request.get_json()
    db = await _get_db()
    secretword = await db.fetch_one("SELECT secretword FROM games WHERE gameid = :gameid", values={"gameid": gameid})

    gamestate['guesses'] -= 1
    if guess['guess'] == secretword[0]:
        try:
            # Temp code just to make sure this works, but gamestate would call get game state function and decrement/increment as necessary
            # then would update table with new values rather than inserting anything
            gamestate['correct'] += len(secretword[0])
            id = await db.execute (
                """
                UPDATE game_states SET guesses = :guesses, correct = :correct, incorrect = :incorrect WHERE gameid = :gameid
                """,
                gamestate,
            )
        except sqlite3.IntegrityError as e:
            abort(400, e)
        return gamestate, 201, dict(gamestate)
    else:
        gamestate['correct'] += await check_string(guess['guess'], secretword[0])
        gamestate['incorrect'] += abs(len(secretword[0]) - gamestate['correct'])
        try:
            id = await db.execute (
                """
                UPDATE game_states SET guesses = :guesses, correct = :correct, incorrect = :incorrect WHERE gameid = :gameid
                """,
                gamestate,
            )
        except sqlite3.IntegrityError as e:
            abort(400, e)
        return gamestate, 201, dict(gamestate)
    