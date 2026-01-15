# backend

## setup pgsql database

best done with docker:

~~~
mkdir data
docker run -dt --name db -e POSTGRES_PASSWORD=lionheart -v "$PATH/data:/var/lib/postgresql:Z" -p 5432:5432 postgres
~~~

enter the psql shell:
~~~
docker exec -it db psql -U postgres
~~~

then execute:
~~~
create database backend;
~~~

to actually create the database

## install the project

best done with uv:

~~~
uv sync
~~~

this automatically creates a venv just for this project, so no manual fuss required

## run migrations

~~~
uv run manage.py migrate
~~~

this creates necessary database structures

## run server

~~~
uv run manage.py runserver 127.0.0.1:8787
~~~

open http://127.0.0.1:8787/ in your browser to view the site

