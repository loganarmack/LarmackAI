# LarmackAI
A discord bot originally created as an interface for my substring game.

## Prerequisites:
Python, pipenv

## To install packages:
`$ pipenv install`

You'll also need to download the list of words from nltk. To do this:
```
$ python
>>> import nltk
>>> nltk.download('words')
```

You will need to define your own discord bot key in a .env file,
created in the root directory.

You can then run the bot with 
`pipenv run python bot.py`


