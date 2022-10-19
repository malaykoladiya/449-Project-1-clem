import json
import sqlite3


def insert_valid_words(cursor: sqlite3.Cursor) -> int:

    with open("./share/valid.json") as f:
        words = json.load(f)

    for word in words:
        cursor.execute("INSERT INTO valid_words (word) VALUES (?)", (word,))

    return len(words)


if __name__ == "__main__":
    connection = sqlite3.connect("./var/wordle.db")
    cursor = connection.cursor()

    print("Inserting words...")
    count = insert_valid_words(cursor)
    connection.commit()
    print(f"Successfully inserted {count} words.")
