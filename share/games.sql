PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS valid_words;
DROP TABLE IF EXISTS game_history;
DROP TABLE IF EXISTS game_states;
DROP TABLE IF EXISTS games;




CREATE TABLE games (
    game_id TEXT NOT NULL,
    secret_word TEXT NOT NULL,
    username TEXT NOT NULL,
    PRIMARY KEY(game_id)
);

CREATE TABLE game_states (
    game_id TEXT NOT NULL,
    remaining_guesses TINYINT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);

CREATE TABLE game_history (
    game_id TEXT NOT NULL,
    guess TEXT NOT NULL,
    remaining_guesses TINYINT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);

CREATE TABLE valid_words (
    word TEXT NOT NULL,
    correct_word BOOLEAN NOT NULL,
    PRIMARY KEY(word)
);



INSERT INTO games VALUES ("cce036da-6572-48f1-8158-bc1fdc497327", "cigar", "john");
INSERT INTO game_states VALUES ("cce036da-6572-48f1-8158-bc1fdc497327", 2, "In Progress");
INSERT INTO game_history VALUES ("cce036da-6572-48f1-8158-bc1fdc497327", "cited", 5);
INSERT INTO game_history VALUES ("cce036da-6572-48f1-8158-bc1fdc497327", "amice", 4);
INSERT INTO game_history VALUES ("cce036da-6572-48f1-8158-bc1fdc497327", "baccy", 3);
INSERT INTO game_history VALUES ("cce036da-6572-48f1-8158-bc1fdc497327", "aglet", 2);
INSERT INTO games VALUES ("e42c57b8-fa31-4917-9df0-260cf18e2148", "rebut", "john");
INSERT INTO game_states VALUES ("e42c57b8-fa31-4917-9df0-260cf18e2148", 0, "lost");
INSERT INTO game_history VALUES ("e42c57b8-fa31-4917-9df0-260cf18e2148", "aahed", 5);
INSERT INTO game_history VALUES ("e42c57b8-fa31-4917-9df0-260cf18e2148", "aalii", 4);
INSERT INTO game_history VALUES ("e42c57b8-fa31-4917-9df0-260cf18e2148", "aapas", 3);
INSERT INTO game_history VALUES ("e42c57b8-fa31-4917-9df0-260cf18e2148", "aargh", 2);
INSERT INTO game_history VALUES ("e42c57b8-fa31-4917-9df0-260cf18e2148", "aarti", 1);
INSERT INTO game_history VALUES ("e42c57b8-fa31-4917-9df0-260cf18e2148", "abaca", 0);
INSERT INTO games VALUES ("d7dc4cde-6a56-43ce-bf93-c8924a4c5ee3", "sissy", "john");
INSERT INTO game_states VALUES ("d7dc4cde-6a56-43ce-bf93-c8924a4c5ee3", 5, "won");
INSERT INTO game_history VALUES ("d7dc4cde-6a56-43ce-bf93-c8924a4c5ee3", "sissy", 5);
INSERT INTO games VALUES ("4cc2ce24-fbec-4377-9d54-89a7869e4131", "humph", "john");
INSERT INTO game_states VALUES ("4cc2ce24-fbec-4377-9d54-89a7869e4131", 5, "In Progress");
INSERT INTO game_history VALUES ("4cc2ce24-fbec-4377-9d54-89a7869e4131", "bahus", 5);

COMMIT;
