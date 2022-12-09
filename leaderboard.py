import dataclasses
import toml
import redis

from quart import Quart, g, request, abort, make_response
from quart_schema import (
    tag,
    validate_request,
    QuartSchema,
    validate_response,
)

app = Quart(__name__)
QuartSchema(app)

app.config.from_file("./etc/wordle.toml", toml.load)

@dataclasses.dataclass
class Error:
    error: str

@dataclasses.dataclass
class Leaderboard:
    username: str
    gameresult: str
    guessno: str

r = redis.StrictRedis()
r.flushdb()
playerrank = "playerrank"

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
# ----------------------leaderboard----------------------------
@app.route("/leaderboard/updateScore", methods=["POST"])
@tag(["leaderboard"])
@validate_request(Leaderboard)
@validate_response(Error, 400)
@validate_response(Error, 409)
async def updateScore(data):
    """update the score of the user based on the result and guess number"""
    try: 
        gameinfo = dataclasses.asdict(data)
        currentScore = r.zscore("playerrank",gameinfo['username'])
        pointstoadd = 0
        if gameinfo['gameresult'] == 'won':
            pointstoadd = 7 - int(gameinfo['guessno'])
        if pointstoadd < 0:
            pointstoadd = 0
        if currentScore:
            pointstoadd+=currentScore
        
    
        r.hmset("players",{gameinfo['username']:pointstoadd})
        testdict = {}
        testdict[gameinfo['username']] = pointstoadd
        r.zadd(playerrank,testdict)
    except:
        abort(500,"Internal Server Error Cant update Leaderboard,please try again by refining the input parameters")

    return f"leaderboard Updated sucessfully for {gameinfo['username']} with score {pointstoadd}", 201


# ----------------------------Retrieve top 10------------------------------------
@app.route("/leaderboard/getleaders", methods=["GET"])
@tag(["leaderboard"])
@validate_response(Error, 400)
@validate_response(Error, 409)
async def getleaders():
    """retrieve the top 10 players from redis based on score"""
    try: 
        leaderlist = r.zrange(playerrank,0,9,desc=True,withscores=True)
    except:
        abort(500,"Internal Server Error Cant update Leaderboard,please try again by refining the input parameters")

    leaderlistStr = "*******LeaderBoard*********\nCurrent Top 10 for Wordle are: \nUsername / Score \n"
    for i in leaderlist:
            print("player",i)
            currentPlayer = ""
            for j in i:
                if  isinstance(j,bytes):
                    j = j.decode("utf-8")
                currentPlayer+= str(j) + " / "
            currentPlayer = currentPlayer.rstrip("/ ")
            currentPlayer+= "\n"
            leaderlistStr+=currentPlayer
    return leaderlistStr,200
