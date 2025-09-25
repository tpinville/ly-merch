SHELL := /bin/bash

up:
\tdocker compose --env-file .env up -d --build

down:
\tdocker compose down

logs:
\tdocker compose logs -f

ps:
\tdocker compose ps

reset-db:
\tdocker compose down -v
\tdocker compose up -d db
\tdocker compose logs -f db

curl-api:
\tcurl -s http://localhost:8000/health | jq .

open-adminer:
\t@echo "Open http://localhost:8081 (Server: db, User: $$MYSQL_USER, Pass: $$MYSQL_PASSWORD, DB: $$MYSQL_DATABASE)"
