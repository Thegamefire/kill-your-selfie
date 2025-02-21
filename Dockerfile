# syntax=docker/dockerfile:1

# build stage
FROM python:3.12.8-alpine AS build

WORKDIR /

RUN pip install poetry

RUN pip install poetry-plugin-export

COPY pyproject.toml poetry.lock ./

RUN poetry export --without-hashes --format=requirements.txt > requirements.txt

RUN pip install -r requirements.txt


# production
FROM python:3.12.8-alpine AS production

COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

COPY --from=build /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 8000

CMD [ "gunicorn", "-w", "2", "-b", "0.0.0.0", "kill_your_selfie.app:app" ]
