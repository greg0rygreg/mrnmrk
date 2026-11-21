import json
import os
import random

from discord import Message
from discord.ext import commands
from discord.flags import Intents
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix="m;", intents=Intents.all())

tendencies: dict[str, list[str]] = {}

@bot.event
async def on_ready():
  global tendencies
  print(f"{bot.user.name} is ready")
  with open("tendencies.json", "r") as f:
    tendencies = json.load(f)
  print(f"Tendencies loaded")

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
    f.write(json.dumps(tendencies, indent=2))
  await c.send("Saved.")

@bot.event
async def on_message(m: Message):
  await bot.process_commands(m)
  if m.author.bot or m.content.startswith("m;"): return
  if m.content.lower() != "merenus":
    _t = m.content.split("\n")
    t = []
    for j in _t:
      t.extend(j.split(" "))
    print(f"\"{m.content}\" {t}", end="\n\n")
    t = [x for x in t if x.strip()]
    t = [x for x in t if "https://" not in x]
    for i, st in enumerate(t):
      if i != len(t) - 1:
        if not tendencies.get(st): tendencies[st] = []
        tendencies[st].append(t[i+1])
  else:
    c = ""
    m2 = ""
    for i in range(random.randint(10, 100)):
      if not c:
        c = random.choice(list(tendencies.keys()))
      while not tendencies.get(c):
        c = random.choice(list(tendencies.keys()))
      v = random.choice(tendencies[c])
      c = v
      m2 += f"{v} "
    await m.channel.send(m2)


bot.run(os.getenv("TOKEN", ""))
