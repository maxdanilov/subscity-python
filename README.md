[![Build Status](https://travis-ci.org/maxdanilov/subscity-python.svg?branch=master)](https://travis-ci.org/maxdanilov/subscity-python)
[![Test Coverage](https://codeclimate.com/github/maxdanilov/subscity-python/badges/coverage.svg)](https://codeclimate.com/github/maxdanilov/subscity-python/coverage)

# SubsCity

## Setup

### pyenv & pyenv-alias

```
brew install pyenv
git clone https://github.com/s1341/pyenv-alias.git $(pyenv root)/plugins/pyenv-alias
```

### Dependencies

```
VERSION_ALIAS="subscity_3.5.2" pyenv install 3.5.2
pyenv local subscity_3.5.2
pyenv exec pip3 install --upgrade pip
pyenv exec pip3 install -r requirements.txt
pyenv exec pip3 install -e .
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
./run update_movies
./run update_cinemas
./run update_screenings
```
