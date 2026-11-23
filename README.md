# Merenus Markov
*Welcome back! I hope you've had a good a rest. It's time to continue.*

A Discord bot that uses Markov chains to speak and listen  
https://discord.com/oauth2/authorize?client_id=1573727390507598015

# Commands

**`ping`**: Shows latency in ms and amount of transitions saved

**`transitions save`**: Saves the transitions it's recorded

**`transitions load`**: Loads transitions from disk

**`transitions clear`**: Clears transitions from RAM. You are f❤️ked once you use this (unless the python process dies unexpectedly)

**`transitions add [amount]`**: Adds [amount] messages from the current channel as transitions

**`transitions text_train <file>`**: Adds \<file> as transitions

**`generate [count]`**: Makes the bot talk using [count] words

**Mentioning the bot**: Makes the bot talk using 10-100 words

# Running
## Requirements
- Python
  - `discord`
  - `aiofiles`
  - `pysimdjson`
  - `dotenv`
- A Discord bot
- A `.env` file containing your bot's token (`TOKEN`) and your Discord user id (`OWNER`)
- Some patience
- Optional: `git` if you're tech-savvy

## Actually running it
1. Clone the repo (using `git clone` or the website)
2. Open a terminal, `cd` into the repo and type `python main.py`
3. done

# Honourable mentions
timgaunt: [Swear word list](https://gist.github.com/timgaunt/a7e9fff6f04c20925b3282a5063e08e9#file-swear-words-txt)
FinNLP: [Human names list](https://github.com/FinNLP/humannames)

# AI Disclosure
No AI was used here. F❤️k off AI bros.
