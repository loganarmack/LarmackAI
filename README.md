# LarmackAI
A multipurpose discord bot with a variety of features

## Prerequisites:
Python, pipenv

## To install packages:
`$ pipenv install`

You will need to define your own discord bot key in a .env file,
created in the root directory, with the tag DISCORD_TOKEN.

You'll also need to define a DATABASE_URL, which links to a postgres
database.

You can then run the bot with 
`pipenv run python bot.py`


## Features
- A word game — you can play it using the !start command
- Automated message reactions based off a complex sentiment analysis function
- Pre-programmed responses to a vast set of triggers
- A music bot that allows you to play songs in voice channels
