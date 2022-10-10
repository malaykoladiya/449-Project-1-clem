# 449-Project-1

## Documentation
Procfile and .env from https://github.com/ProfAvery/cpsc449/tree/master/quart/hello

## Issues
Everytime I run `foreman start`, the process is not actually ended when terminating the app, causing an `OSError: [Errno 98]` on the second run.
    TEMP FIX: run `kill -9 $(ps -A | grep python | awk '{print $1}')` to end all python processes