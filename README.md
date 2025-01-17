# Hebrew Semantle
A Hebrew version of [Semantle](https://semantle.com/).

## Installation

Extract word2vec model in repository.
you can download one by following the instructions [here](https://github.com/Iddoyadlin/hebrew-w2v).

### Console 

```commandline
python -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

unless you want to do dev stuff and then you can replace the last line with:

```commandline
pip install -r requirements-dev.txt
```

Install [mongodb](https://www.mongodb.com/docs/manual/installation/) and [redis](https://redis.io/docs/getting-started/installation/).

### Docker Compose
install Docker Compose from [here](https://docs.docker.com/compose/install/)

build the game with: 
```commandline
docker build compose
```

## Configuring databases
populate mongodb with vectors from word2vec model by running `populate.py` (make sure mongo db is running).
select secret word by running `set_secret.py` (make sure redis and mongo are running).

## Running the game

configurations should be set by creating a config.yaml file with the relevant settings (see config.format.yaml).
when running with docker compose, every change to configuration requires rebuilding.

### Console

You can run the game with:
```commandline
python app.py
```

you should run and configure mongo and redis server (see "Configuring Databases" section).
Word2Vec model was trained as described [here](https://github.com/Iddoyadlin/hebrew-w2v)

### Docker Compose

run the game with:
```commandline
docker build up
```

## Scripts

There are some useful scripts in the `scripts/` folder:

- `populate.py`: Given a Word2Vec model, will populate mongo collection used by the game.
- `set_secret.py`: Well...
- `semantle.py`: A CLI version of the game.

## Tests

Only for some of the logic right now. Sorry.

