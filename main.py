import os
import discord
from random import randint
from discord import app_commands
from dotenv import load_dotenv

class BotClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

class User:
    def __init__(self, id: int) -> None:
        self.__id = id
        self.__xp = 0

    def get_id(self) -> int:
        return self.__id

    def add_xp(self, amount: int) -> None:
        self.__xp += amount

    def get_xp(self) -> int:
        return self.__xp

def db_has_user(user_id: int):
    for user in user_db:
        if user.get_id() == user_id:
            return True
    return False

def db_get_user(user_id: int):
    for user in user_db:
        if user.get_id() == user_id:
            return user
    return None

load_dotenv()

token: str = os.getenv('DISCORD_TOKEN')
guild: int = discord.Object(os.getenv('GUILD_ID'))

intents = discord.Intents.default()
intents.message_content = True

user_db: list = []

client = BotClient(intents=intents)

@client.event
async def on_ready():
    print(f'Bot is ready, logged in as {client.user}.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    author_id: int = message.author.id

    if not db_has_user(author_id):
        user_db.append(User(author_id))

    db_get_user(author_id).add_xp(1)

    await message.channel.send(f'{message.author.mention} now has {db_get_user(author_id).get_xp()} xp!')

# Implements /hello command. Syntax: /hello
@client.tree.command(description = "Say hello to liliumbot!")
async def greet(interaction: discord.Interaction):
    await interaction.response.send_message("Hello, I'm liliumbot!")

# Implements /roll command. Syntax: /roll <max-1: int>
@client.tree.command(description = "Roll a random number between 0 and max (default 6).")
async def roll(interaction: discord.Interaction, max: int = 6):
    await interaction.response.send_message(f'You rolled a {randint(1, max)}!')

# Implements /xp command. Syntax: /xp 

client.run(token)
