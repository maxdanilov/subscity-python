![Build Status](https://github.com/maxdanilov/subscity-python/actions/workflows/main.yml/badge.svg)
[![codecov](https://codecov.io/gh/maxdanilov/subscity-python/branch/master/graph/badge.svg)](https://codecov.io/gh/maxdanilov/subscity-python)

# SubsCity

## Setup

### pyenv & pyenv-alias

```
brew install pyenv
git clone https://github.com/s1341/pyenv-alias.git $(pyenv root)/plugins/pyenv-alias
```

### Dependencies

```
VERSION_ALIAS="$(cat .python-version)" AR="/usr/bin/ar" pyenv install $(cat .python-version | cut -d_ -f2)
./run pip3 install --upgrade pip
./run pip3 install -r requirements.txt
./run pip3 install -e .
```

## Initial DB migration

```
./run alembic upgrade head
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
./run flask run
```

## Tasks
```
./run update_base
./run update_movies
./run update_cinemas
./run update_screenings
```
