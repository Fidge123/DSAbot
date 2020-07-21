# D3Bot - **D**SA **D**iscord **D**ice Bot

A bot that makes it easy to roll skill throws for Das Schwarze Auge (The dark eye) especially 5th edition.

## Discord Token

If you don't have a token, [create a new app](https://discord.com/developers/applications) and activate the bot account for that app. Use the token from the "Bot" section (NOT the client secret).

Once you have a token, create a file `.env` and add your token.

```
DISCORD_TOKEN=<YOUR TOKEN HERE>
```

## How to install

The bot uses `pipenv` for dependency management. If you don't have `pipenv` installed, you can install via one of the following commands or by following the [official documentation](https://pipenv.pypa.io/en/latest/install/#installing-pipenv).

``` sh-session
# Using pip
$ pip install -U pipenv

# macOS with brew
$ brew install pipenv

# Fedora
$ sudo dnf install pipenv
```

Once `pipenv` is installed, you need to install the dependencies.

``` sh-session
$ pipenv install
```

Afterwards execute the script via `pipenv` 

``` sh-session
$ pipenv run python DSAbot.py
```

or active the `virtualenv` to run it as you would normally.

``` sh-session
$ pipenv shell 
Loading .env environment variables…
Launching subshell in virtual environment…

$ python DSAbot.py
...

$ exit
```

## Run tests

Use the following command to run tests

``` sh-session
pipenv run python -m unittest UnitTests/bot_tests.py
```

