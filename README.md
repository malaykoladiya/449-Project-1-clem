# 449-Project-1

# Team members:
1. Ashley Thorlin
2. Clemente Solorio
3. Eddie Poulson Valdez 
4. Shreya Bhattacharya

## Documentation
Procfile and .env from https://github.com/ProfAvery/cpsc449/tree/master/quart/hello

# Introduction
The goal is to Design endpoints for an application similar to Wordle.It will allow user to play more than one game in a day unlike the orignal wordle.The user will get overall six chances to guess the correct word.The guesses will be matched against the secret word to determine if it is correct or incorrect. If its correct the game will stop and if it is incorrect the user will get his/her remaining chances to guess.
The implementation of API is done in Python using the Quart framework and some ancillary tools like Foreman and sqlite3.The project also requires to create relational database schemas for the API implementation.

# How to initialize
To initialize the sqlite database, navigate to the project directory using a terminal and then type in `./bin/init.sh` or `sh ./bin/init.sh` and then create a locally hosted server by using `foreman start`

# How to use endpoints
- To register a new user: `http POST localhost:5000/auth/register username={user} password={pass}`
- To sign in: `http -a {username}:{password} localhost:5000/auth/signin`
- To create a game: `http POST localhost:5000/games/create username={username}`
- To make a guess: `http POST localhost:5000/games/{gameid} guess={guess}`  

Furthermore, you can view these endpoint in Quart Schema Documentation form when the server is running by navigating to `localhost:5000/docs`

 # Features:
 Creating a RESTful API that perform the following functionalities:

 - User registration
 - User Signin(Authentication with password hashing)
 - Starting a new game
 - Make a guess
 - Retrieve state of in progress games
 - Listing in-progress games

# Database:
The var folder holds wordle.db which contains the following tables:
- users
- games
- game_states
- valid_words
 

