# D3Bot - **D**SA **D**iscord **D**ice Bot

A bot that makes it easy to roll skill checks for Das Schwarze Auge (The dark eye) especially 5th edition.

## Discord Token

If you don't have a token, [create a new app](https://discord.com/developers/applications) and activate the bot account for that app. Use the token from the "Bot" section (NOT the client secret).

Once you have a token, create a file `.env` and add your token.

```
DISCORD_TOKEN=<YOUR TOKEN HERE>
```

## How to add the bot to your discord server

Select your [application](https://discord.com/developers/applications) and go to the **OAuth2** in the list on the left. Here you need to generate a URL that will allow you to add the bot to any of your servers.

To generate this URL, select _bot_ in the **SCOPES** section. A new section **BOT PERMISSIONS** appears. Here you need to select:
- _Send Messages_
- _Add Reactions_
- _Read Message History_
- _Mention Everyone_

Afterwards copy the URL from the **SCOPES** section (e.g. `https://discord.com/api/oauth2/authorize?client_id=YOUR-CLIENT-ID&permissions=206912&scope=bot`) and open it in a new tab. Now you can add the bot to your server if you have the correct server permissions.

To interact with the bot, make sure it has permissions to read in the relevant channel, the script is running (see below) and you write `SUMMON`. If everything works, the bot will respond with `I am listening for rolls here`.

## How to install dependencies and run the script

The bot uses `pipenv` for dependency management. If you don't have `pipenv` installed, you can install via one of the following commands or by following the [official documentation](https://pipenv.pypa.io/en/latest/install/#installing-pipenv).

``` sh-session
# Using pip
$ pip install -U pipenv

# macOS with brew
$ brew install pipenv

# Fedora
$ sudo dnf install pipenv
```

Once `pipenv` is installed, you need to install the dependencies and dev dependencies.

``` sh-session
$ pipenv install --dev
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

Use the following command to run tests and generate coverage

``` sh-session
pipenv run tests
```

After that it is possible to generate a coverage report by running

``` sh-session
pipenv run cov
```
