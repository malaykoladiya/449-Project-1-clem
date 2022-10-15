from click import get_binary_stream
import databases
import dataclasses
import sqlite3
from quart import Quart, g, request, redirect, url_for, abort
from quart_schema import validate_request, QuartSchema

app = Quart(__name__)
QuartSchema(app)

@dataclasses.dataclass
class User:
    username: str
    password: str


async def _get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = databases.Database('sqlite+aiosqlite:///wordle_db')
        await db.connect()
    return db

@app.route("/")
async def hello():
    return "Hello World"

@app.route("/register/", methods=["POST"])
@validate_request(User)
async def register_user(data):
    db = await _get_db()
    user = dataclasses.asdict(data)
    print(user)
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

    user["id"] = id
    return user, 201, {"Location": f"/register/{id}"}

