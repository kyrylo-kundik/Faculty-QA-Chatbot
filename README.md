# FI QA Chat-bot

This source code of [Fi Chat-bot](https://t.me/FIChatbot) that created as a course work and of course for the freshmen students and for the entrants on my faculty.

Also search feature is available as RESTful API web service.

### Stack:

* [aiogram]() python telegram bot async framework with [uvloop](), [ujson](), [aiohttp[speedups]]() boosters;
* [Flask]() python web micro-framework;
* [Flask-Migrate]() - Flask extensions for database migrations managing and [Flask-SQLAlchemy]() - Flask ORM;
* [pdfminer.six]() - python .pdf document parser for parsing parts of knowledge base;
* [gunicorn]() - production WSGI HTTP server;
* [torch]() - python ML framework. I'm using it for building [BERT]()-based ML model for question-answering system;
* [elasticsearch]() - NoSQL database for indexing knowledge for question-answering system;
* [ingest]() - Elasticsearch plugin for indexing file attachments. Was used for indexing knowledge base .pdf docs paragraphs;
* [PostgreSQL]() - RDBMS for managing all bot data. 

#### Environment variables (put them in a file in the root of project called `.env`):
```.env
# postgres env
POSTGRES_DB
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_EXTERNAL_PORT
POSTGRES_USER
POSTGRES_PASS

# web app env
WEB_APP_PORT
WEB_APP_HOST
PDF_URL
QA_TXT_URL

# elastic env
ELASTIC_PORT
ELASTIC_EXTERNAL_PORT
ELASTIC_HOST

# bot env
BOT_API_TOKEN
API_HOST
SUPPORT_CHAT_ID

# common
PG_HOST
ES_HOST
ES_USER
ES_PASS
```

#### Requirements (docker-based start):
* Engine ^18.0
* Compose ^1.18

#### Requirements (local start):
* Python ^3.7.0
* gunicorn ^20.0
* PostgreSQL ^9.6
* Elasticsearch ^7.0.0 (with installed ingest plugin via `bin/elasticsearch-plugin install --batch ingest-attachment` command)

#### Start (docker-based start):

* To build and start all services:

`docker-compose up --build` *(Web service will be available at `$YOUR_HOST:$YOUR_PORT` from `.env` file)*

* To stop all services:

`docker-compose stop`

* To stop specific service:

`docker-compose stop <SERVICE_NAME>`

* To kill specific service:

`docker-compose kill <SERVICE_NAME>`

* To start specific service:

`docker-compose start <SERVICE_NAME>`

* To build specific service: 

`docker-compose build <SERVICE_NAME>`

* To attach to a specific service:

`docker-compose attach <SERVICE_NAME>`

#### Start (local start):

1. Make sure PostgreSQL and Elasticsearch services are up. 
1. Make sure you create a PostgreSQL Database (`CREATE DATABASE <db_name>;`).
1. Create a venv for python `python -m venv venv` and activate it `source venv/bin/activate`.
1. Install requirements from `web_service` and `bot` folders with `pip install -r requirements.txt`.
1. Migrate a database with `flask db upgrade --directory web_service/migrations` command.
1. *(Recommended)* Reseed database from knowledge base: `flask force_reseed_db`.
1. **Will be available soon. TODO:** *(Recommended)* Check app for all needed data: `flask check_app`.
1. To start server: `gunicorn -w <WORKERS_COUNT (Python processes)> -b <YOUR_HOST>:<YOUR_PORT> "main:app"`. *You will see a message in console that your server is running on `$YOUR_HOST:$YOUR_PORT`*. 
