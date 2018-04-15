[![Build Status](https://travis-ci.org/maxdanilov/subscity-python.svg?branch=master)](https://travis-ci.org/maxdanilov/subscity-python)
[![codecov](https://codecov.io/gh/maxdanilov/subscity-python/branch/master/graph/badge.svg)](https://codecov.io/gh/maxdanilov/subscity-python)
[![Updates](https://pyup.io/repos/github/maxdanilov/subscity-python/shield.svg)](https://pyup.io/repos/github/maxdanilov/subscity-python/)

# SubsCity

## Setup

### pyenv & pyenv-alias

```
brew install pyenv
git clone https://github.com/s1341/pyenv-alias.git $(pyenv root)/plugins/pyenv-alias
```

### Dependencies

```
VERSION_ALIAS="subscity_3.6.4" pyenv install 3.6.4
pyenv local subscity_3.6.4
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
./run update_base
./run update_movies
./run update_cinemas
./run update_screenings
```
