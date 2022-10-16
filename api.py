import databases
import dataclasses
import sqlite3
import json

from quart import Quart, g, request, abort, make_response
from quart_schema import validate_request, QuartSchema
from random import randint

app = Quart(__name__)
QuartSchema(app)

@dataclasses.dataclass
class User:
    username: str
    password: str

@dataclasses.dataclass
class Game:
    secretword: str
    username: str

@dataclasses.dataclass
class GameState:
    gameid: int
    guesses: int
    correct: int
    incorrect: int


async def _get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = databases.Database('sqlite+aiosqlite:///wordle_db')
        await db.connect()
    return db

async def _get_random_word():
    with open('correct.json') as file:
        data = json.load(file)
        rand_index = randint(0, len(data)-1)
        return data[rand_index]

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
    response.headers['WWW-Authenticate'] = 'Basic realm="User Login"'
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
    
    try:
        id = await db.execute( 
            """
            INSERT INTO user_data(username, password)
            VALUES(:username, :password)
            """,
            user,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)

    # TODO: possibly change location to /games/<username>
    return user, 201, {"Location": f"/users/{user['username']}"}

# ---------------------------------- sign in --------------------------------- #
@app.route("/signin")
async def signin():
    
    auth = request.authorization
    
    # return bad request if invalid auth header
    # check if authorization header is present
    if not auth:
        abort(400, "Authorization header is required.")
    
    # check if username and password are present
    if not auth.username or not auth.password:
        abort(400, "Username and password are required.")
        
    db = await _get_db()
    
    # 0 if username and password are incorrect, 1 if correct
    # TODO: if we hash passwords we would need to change this slightly
    exists = await db.fetch_val(
        """
        SELECT EXISTS(
            SELECT 1 FROM user_data 
            WHERE username = :username AND password = :password
        )
        """,
        auth
    )
    
    if exists == 1:
        return {"authenticated": True, "user": auth.username}, 200
    else:
        abort(401, "Username or password is incorrect.")

# -------------------------------- create game ------------------------------- #
# @app.route("/games/create", methods=["POST"])
# @validate_request(Game)
# async def create_game(data):
#     random_word = _get_random_word()
#     game = dataclasses.asdict(data)

#     db = await _get_db()

#     try:
#         id = await db.execute(
#             f"""
#             INSERT INTO games(secretword, username)
#             VALUES({random_word}, :username)
#             """,
#             game,
#         )
        
#     except sqlite3.IntegrityError as e:
#         abort(409, e)

#     game["gameid"] = id
#     return game, 201, dict(game)

@app.route("/games/create", methods=["POST"])
@validate_request(Game)
async def create_game(data):
    db = await _get_db()
    game = dataclasses.asdict(data)
    app.logger.debug(game)
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
    return game, 201, dict(game)