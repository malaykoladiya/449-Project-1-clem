# 449-Project-1

# Team members:
1. Michael Morikawa
2. Malay Narendrakumar Koladiya
## References
- Procfile and .env derrived from https://github.com/ProfAvery/cpsc449/tree/master/quart/hello
- Original project 1 base forked from https://github.com/ashleythorlin/449-Project-1

# How to initialize
1. To initialize the sqlite database, navigate to the project directory using a terminal
2. Do `mkdir var` to make a `var/` directory in the project root directory.
5. Initialize and populate the databases by running `./bin/init.sh`
4. Copy `./etc/nginx-conf` to the `/etc/ngnix/sites-enabled/` directory and restart the nginx service. 
5. Run `foreman start --formation users=1,games=3` to start the two services.
6. Go to browser and type `http://tufix-vm/games` and be prompted to login.
7. User the username of `john` and the password of `doe` to signin using a test user.
8. Broswer should recieve json back detailing the games in progress for the fake test user.

# How to use endpoints via httpie
  HTTP verbs | endpoints | Action 

- To register a new user: `http POST http://tuffix-vm/users/register username={user} password={pass}`
- To use any of the game endpoints need to pass an auth header by using -a {username}:{pass} before the http verb. 
- To create a game: `http POST localhost:5000/games`
- To make a guess: `http POST localhost:5000/games/{gameid} guess={guess}`  
- To list in-progress games : `http GET localhost:5000/games`
- To retrieve game state : `http GET localhost:5000/games/{gameid}`

Furthermore, you can view more documentation for these services when they are running by navigating to `http://localhost:5000/docs` or `http://localhost:5100/docs`in a web browser!










 

