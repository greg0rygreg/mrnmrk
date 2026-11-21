import json
import os
import random
import re

from discord.ext import commands
from discord.flags import Intents
from dotenv import load_dotenv
from discord import Message, CustomActivity

load_dotenv()

bot = commands.Bot(command_prefix="m;", intents=Intents.all())

tendencies: dict[str, list[str]] = {}

with open("tendencies.json", "r") as f:
  tendencies = json.load(f)
print("Tendencies loaded")

def add_tendency(tendency: str) -> None:
  _t = tendency.split("\n")
  t = []
  for j in _t:
    t.extend(j.split(" "))
  t = [
    x for x in t \
    if x.strip() \
    or "https://" not in x \
    or not re.search("<@\d*>", x)
  ]
  print(f"\"{tendency}\" {t}", end="\n\n")
  for i, st in enumerate(t):
    if i != len(t) - 1:
      if st != t[i+1]: continue
      if not tendencies.get(st): tendencies[st] = []
      tendencies[st].append(t[i+1])

def generate(word_count: int) -> str:
  c = ""
  m2 = ""
  for i in range(word_count):
    while not tendencies.get(c):
      c = random.choice(list(tendencies.keys()))
    v = random.choice(tendencies[c])
    c = v
    m2 += f"{v} "

  return m2

@bot.event
async def on_ready():
  print(f"{bot.user.name} is ready")
  await bot.change_presence(activity=CustomActivity(name=generate(5), emoji=":speech_balloon:"))

@bot.command()
async def ping(c: commands.Context):
  """
  Shows how long I take to answer
  """
  await c.reply(f"Pong!\n:wireless: {round(bot.latency*1000, 2)}ms\n:speech_balloon: {len(tendencies)} tendencies")

@bot.command(aliases=["st", "save"])
@commands.is_owner()
async def save_tendencies(c: commands.Context):
  """
  Owner only; save my tendencies for later use
  """
  await c.reply("Saving...")
  with open("tendencies.json", "w") as f:
    f.write(json.dumps(tendencies))
  await c.send("Saved.")

@bot.command(aliases=["rt", "reload", "rl"])
@commands.is_owner()
async def reload_tendencies(c: commands.Context):
  """
  Owner only; reload my tendencies for manual profanity check
  """
  global tendencies
  await c.reply("Loading...")
  with open("tendencies.json", "r") as f:
    tendencies = json.load(f)
  await c.send("Loaded.")

@bot.command(aliases=["generate", "speak", "talk", "gibberish"])
async def gen(c: commands.Context, count: int = random.randint(10, 100)):
  """
  Make me speak! You can also say "merenus"
  """
  async with c.typing():
    m2 = generate(count)
  await c.reply(m2)

@bot.event
async def on_message(m: Message):
  await bot.process_commands(m)
  if m.author.bot or m.content.startswith("m;"): return
  if m.content.lower() != bot.user.mention: add_tendency(m.content)
  else:
    async with m.channel.typing():
      m2 = generate(random.randint(10, 100))
    await m.channel.send(m2)


bot.run(os.getenv("TOKEN", ""))
