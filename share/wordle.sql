PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS valid_words;
DROP TABLE IF EXISTS game_states;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    PRIMARY KEY(username)
);

CREATE TABLE games (
    gameid INTEGER NOT NULL,
    secretword TEXT NOT NULL,
    username TEXT NOT NULL,
    PRIMARY KEY(gameid),
    FOREIGN KEY(username) REFERENCES users(username)
);

CREATE TABLE game_states (
    gameid INTEGER NOT NULL,
    guesses TINYINT NOT NULL,
    correct TEXT NOT NULL,
    incorrect TEXT NOT NULL,
    FOREIGN KEY (gameid) REFERENCES games(gameid)
);

CREATE TABLE valid_words (
    word TEXT NOT NULL,
    PRIMARY KEY(word)
);

COMMIT;