#!/bin/sh
echo "Initializing database..."
echo "Initializing game database..."
sqlite3 ./var/primary/mount/games.db < ./share/games.sql
echo "Initializing user database..."
sqlite3 ./var/primary/mount/users.db < ./share/users.sql
echo "Successfully initialized both database."
echo "Populating database with words..."
python3 ./share/populate.py
