# 449-Project-1

# Team members:
1.Ashley Thorlin
2.Clemente Solorio
3.Eddie Poulson Valdez 
4.Shreya Bhattacharya

## Documentation
Procfile and .env from https://github.com/ProfAvery/cpsc449/tree/master/quart/hello

# Introduction
The goal is to Design endpoints for an application similar to Wordle.It will allow user to play more than one game in a day unlike the orignal wordle.The user will get overall six chances to guess the correct word.The guesses will be matched against the secret word to determine if it is correct or incorrect. If its correct the game will stop and if it is incorrect the user will get his/her remaining chances to guess.
The implementation of API is done in Python using the Quart framework and some ancillary tools like Foreman and sqlite3.The project also requires to create relational database schemas for the API implementation.

 # Features:
 Creating RESTful Api that perform the following functionalities:

 -User registration
 -User Signin(Authentication with password hashing)
 -Starting a new game
 -Make a guess
 -Retrieve state of in progress games
 -Listing in-progress games

# Database:
The var folder holds wordle.db which contains the following tables:
-users
-games
-game_states
-valid_words
 


