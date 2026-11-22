import os
import random
import re
import aiofiles

import simdjson
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class MerenusMarkov(commands.Bot):
  async def async_cleanup(self):  # example cleanup function
      print("\nClean up")
      async with aiofiles.open("transitions.json", "w") as f:
        await f.write(simdjson.dumps(transitions, indent=0))
      print(f"Saved {len(transitions)} states")

  async def close(self):
      await self.async_cleanup()
      await super().close()

bot = MerenusMarkov(command_prefix="m;", intents=discord.flags.Intents.all())

transitions: dict[str, list[str]] = {}
slurs = []

with open("Swear_20Words.txt", "r") as f:
  slurs = f.read().split("\n")
print(f"{len(slurs)} naughty words loaded")

with open("transitions.json", "r") as f:
  transitions = simdjson.load(f)
print(f"{len(transitions)} states loaded")

def add_transition(transition: str) -> None:
  _t = transition.split("\n")
  t = []
  for j in _t:
    t.extend(j.split(" "))
  t = [x for x in t if x.strip()]
  t = [x for x in t if x.lower() not in slurs]
  t = [x for x in t if not re.search(r"<.+>", x)]
  t = [x for x in t if not re.search(r"https?:/+", x.lower())]
  print(f"\"{transition}\" {t}", end="\n\n")
  for i, st in enumerate(t):
    if i != len(t) - 1:
      if st.lower() == t[i+1].lower(): continue
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
  await bot.tree.sync()
  await bot.change_presence(activity=discord.CustomActivity(name=generate(10)))
  print(f"{bot.user.name} is ready")


@bot.tree.command(name="ping", description="Shows how long I take to answer and some other things")
async def ping(c: discord.Interaction):
  await c.response.send_message(f"Pong!\n:wireless: {round(bot.latency*1000, 2)}ms\n:speech_balloon: {len(transitions)} states (top-level transitions)")

trans = discord.app_commands.Group(name="transitions", description="Transitions and states related commands")

@trans.command(name="save", description="Owner only; save my transitions for testing")
async def save_transitions(c: discord.Interaction):
  if c.user.id != bot.owner_id:
    await c.response.send_message("You're not the owner.", ephemeral=True)
    return
  async with aiofiles.open("transitions.json", "w") as f:
    await f.write(simdjson.dumps(transitions, indent=0))
  await c.response.send_message("Saved.")

@trans.command(name="load", description="Owner only; reload my transitions for manual profanity check")
async def load_tendencies(c: discord.Interaction):
  if c.user.id != bot.owner_id:
    await c.response.send_message("You're not the owner.", ephemeral=True)
    return
  global transitions
  async with aiofiles.open("transitions.json", "r") as f:
    transitions = simdjson.loads(await f.read())
  await bot.change_presence(activity=discord.CustomActivity(name=generate(10)))
  await c.response.send_message("Loaded.")

@trans.command(name="add", description="Owner only; train me on X amount of messages in this channel")
@discord.app_commands.describe(amount="Message count (default: 50)")
async def train(c: discord.Interaction, amount: int = 50):
  if c.user.id != bot.owner_id:
    await c.response.send_message("You're not the owner.", ephemeral=True)
    return
  await c.response.defer()
  try:
    before = len(transitions)
    async for m in c.channel.history(limit=amount):
      if m.author.bot or m.content.startswith("m;"): continue
      add_transition(m.content)
    after = len(transitions)
    await c.followup.send(f"Added {after-before} states.")
  except discord.Forbidden:
    if bot.user in c.guild.members:
      await c.followup.send("Can't read channel messages. Ask the owner if he gave me the Read Message History permission?")
    else:
      await c.followup.send("Can't read channel messages. This command was ran while I'm installed as a user app, not server bot.")

@trans.command(name="clear", description="Owner only; clear EVERY SINGLE TRANSITION. THIS IS (almost) IRREVERSABLE.")
async def clear(c: discord.Interaction):
  if c.user.id != bot.owner_id:
    await c.response.send_message("You're not the owner.", ephemeral=True)
    return
  global transitions
  transitions = {}
  await c.response.send_message("Cleared. It's all gone, unless you unexpectedly terminate the python process.")

@trans.command(name="text_train", description="Owner only; train me with a text file")
@discord.app_commands.describe(file="Text file")
async def file_train(c: discord.Interaction, file: discord.Attachment):
  if c.user.id != bot.owner_id:
    await c.response.send_message("You're not the owner.", ephemeral=True)
    return
  await c.response.defer()
  if (file.content_type or "None;None").split(";")[0] != "text/plain":
    await c.followup.send("A text file was not provided.")
    return
  d = await file.read()
  before = len(transitions)
  for m in d.decode().split("\n"):
    if m.strip().startswith("m;"): continue
    add_transition(m.strip())
  after = len(transitions)
  await c.followup.send(f"Added {after-before} states.")

bot.tree.add_command(trans)

@bot.tree.command(name="generate", description="Make me speak! You can also @mention me")
@discord.app_commands.describe(count="Word count (default: from 10 to 100)")
async def gen(c: discord.Interaction, count: int = random.randint(10, 100)):
  await c.response.defer()
  try:
    await c.followup.send(generate(count))
  except discord.HTTPException:
    await c.followup.send("Final message too long. Probably.")

@bot.event
async def on_message(m: discord.Message):
  await bot.process_commands(m)
  if m.author.bot or m.content.startswith("m;"): return
  if m.content.strip() != bot.user.mention: add_transition(m.content)
  else:
    async with m.channel.typing():
      m2 = generate(random.randint(10, 100))
    await m.channel.send(m2)

bot.run(os.getenv("TOKEN"))
