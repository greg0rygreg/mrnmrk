import os
import random
import string

import json
import aiofiles
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix="m;", intents=discord.flags.Intents.all())

transitions: dict[str, list[str]] = {}

with open("transitions.json", "r") as f:
  transitions = json.load(f)

def add_transition(transition: str) -> None:
  _t = transition.split("\n")
  t = []
  for j in _t:
    t.extend(j.split(" "))
  t = [x for x in t if x.strip()]
  t = [x.lower().strip(string.punctuation + string.whitespace) for x in t]
  print(f"\"{transition}\" {t}")
  for i, st in enumerate(t):
    if i != len(t) - 1:
      if st == t[i+1]: continue
      if not transitions.get(st): transitions[st] = []
      transitions[st].append(t[i+1])

def generate(word_count: int) -> str:
  c = ""
  m2 = ""
  try:
    for i in range(word_count):
      while not transitions.get(c):
        c = random.choice(list(transitions.keys()))
      v = random.choice(transitions[c])
      c = v
      m2 += f"{v} "
  except:
    m2 = "(empty)"

  return m2

@bot.event
async def on_ready():
  bot.owner_id = int(os.getenv("OWNER"))
  print(f"{bot.user.name} is ready")

@bot.command(name="save", description="Owner only; save my transitions for a shutdown")
@commands.is_owner()
async def save_transitions(c: commands.Context):
  async with aiofiles.open("transitions.json", "w") as f:
    await f.write(json.dumps(transitions))
  await c.reply("Saved.")

@bot.event
async def on_message(m: discord.Message):
  await bot.process_commands(m)
  if m.author.bot or m.content.startswith("m;"): return
  if m.content.strip() != bot.user.mention: add_transition(m.content)
  else:
    m2 = generate(random.randint(10, 25))
    await m.reply(m2)

bot.run(os.getenv("TOKEN"))
