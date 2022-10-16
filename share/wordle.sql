-- TODO: create tables
BEGIN TRANSACTION;
DROP TABLE IF EXISTS game_states, games, users;

CREATE TABLE game_states (
    gameid INTEGER,
    guesses INTEGER(1) NOT NULL,
    correct INTEGER(1) NOT NULL,
    incorrect INTEGER(1) NOT NULL,
    PRIMARY KEY(gameid)
);

CREATE TABLE games (
    gameid INTEGER,
    secretword VARCHAR(5) NOT NULL,
    username VARCHAR(20),
    PRIMARY KEY(gameid)
);

CREATE TABLE users (
    username VARCHAR(20) NOT NULL,
    password VARCHAR(20) NOT NULL,
    PRIMARY KEY(username)
);

COMMIT;