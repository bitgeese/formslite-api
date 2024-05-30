.PHONY: venv-create install install-dev lint celery redis docker-up docker-up-build docker-down docker-down-v createsuperuser makemigrations migrate black isort flake8 test

## ENV SETUP
venv-create:
	python -m venv venv

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

## DEVELOPMENT helpers
lint:
	black . --exclude=migrations
	isort . --skip=migrations --profile black

celery:
	celery -A railway_django_stack worker --beat -l INFO

redis:
	docker run -p 6379:6379 redis

## DOCKER COMMANDS
up:
	docker-compose -f docker-compose.local.yml up -d

up-build:
	docker-compose -f docker-compose.local.yml up -d --build

down:
	docker-compose -f docker-compose.local.yml down

down-v:
	docker-compose -f docker-compose.local.yml down -v

createsuperuser:
	docker-compose -f docker-compose.local.yml run django python manage.py createsuperuser

makemigrations:
	docker-compose -f docker-compose.local.yml run django python manage.py makemigrations

migrate:
	docker-compose -f docker-compose.local.yml run django python manage.py migrate

black:
	docker-compose -f docker-compose.local.yml run django black --exclude=migrations .

isort:
	docker-compose -f docker-compose.local.yml run django isort --skip=migrations .

flake8:
	docker-compose -f docker-compose.local.yml run django flake8 .

test:
	docker-compose -f docker-compose.local.yml run django pytest --cov=web_forms --cov-fail-under=60 --cov-report=term-missing

## ADDITIONAL COMMANDS
shell:
	docker-compose -f docker-compose.local.yml run django python manage.py shell

makemessages:
	docker-compose -f docker-compose.local.yml run django python manage.py makemessages -l en

compilemessages:
	docker-compose -f docker-compose.local.yml run django python manage.py compilemessages

collectstatic:
	docker-compose -f docker-compose.local.yml run django python manage.py collectstatic --noinput
