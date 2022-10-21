#!/bin/sh

sqlite3 ./var/wordle.db < ./share/wordle.sql
python3 ./share/populate.py