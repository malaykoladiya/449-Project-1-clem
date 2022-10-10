from quart import Quart, request, redirect, url_for

app = Quart(__name__)


@app.route("/")
async def hello():
    return "Hello World"
