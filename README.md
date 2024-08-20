# Shipping Rates API

This project provides a Flask-based API to retrieve average shipping rates between ports or regions. It uses PostgreSQL as the database and Docker for containerization. 

## Features

- Retrieve average shipping rates between ports or regions.
- Handle requests with date ranges and origin/destination ports or regions.
- Dockerized setup with PostgreSQL .
- Secure credential management using environment variables.

## Setup and Installation
- Just run psql on docker as you have mentioned in the task requirements as i have done the same .
- I have added Dockerfile and rates.sql file .

### Clone the Repository
- git clone https://github.com/osamaliaqat/ratetask.git
- cd your-repo

### Test API
- run command python app.py
- Test api e.g: curl "http://127.0.0.1:5000/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=finland_main"
