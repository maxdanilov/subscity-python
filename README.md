# SubsCity

## Setup

```
virtualenv -p python3 .
./run pip install -r requirements.txt
./run pip install -e .
```

## Tests

```
./test
```

## Linting

```
./lint
```

## Running

```
FLASK_APP=subscity/main.py ./run python -m flask run
```
