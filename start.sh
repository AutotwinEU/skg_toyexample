#!/bin/bash
echo Starting web server
# Run the web server in the background 
# mini_httpd &
# Run our flask application
echo Starting flask application
python3 -m flask run --host=0.0.0.0
echo Done
