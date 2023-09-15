import os
import discord
import datetime
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
        self.__last_message = datetime.datetime(1900, 1, 1)
        self.__level = 0

    def get_id(self) -> int:
        return self.__id

    def add_xp(self, amount: int) -> None:
        self.__xp += amount

    def get_xp(self) -> int:
        return self.__xp

    def get_last_message_timestamp(self) -> datetime.datetime:
        return self.__last_message

    def update_last_message_timestamp(self) -> None:
        self.__last_message = datetime.datetime.now()

    def get_level(self) -> str:
        return self.__level

    def set_level(self, level: int) -> None:
        self.__level = level

class Level:
    def __init__(self, name: str, threshold: int, id: int = -1) -> None:
        self.__name = name
        self.__threshold = threshold
        self.__id = id

    def get_name(self) -> str:
        return self.__name

    def get_threshold(self) -> int:
        return self.__threshold

    def get_id(self) -> int:
        return self.__id

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

client = BotClient(intents=intents)

# initialize all actual variables related to bot functions

user_db = []

levels = [Level("Beginner", 0), Level("Apprentice", 5, 1057176952559124560), Level("Journeyman", 15, 1057176994883833966), Level("Adept", 40, 1057177012135022695), Level("Master", 75, 1057177029000306738), Level("Grandmaster", 125, 1085465765316141147)]

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

    if (datetime.datetime.now() - db_get_user(author_id).get_last_message_timestamp()).total_seconds() >= 72000:
        user_db_entry = db_get_user(author_id)
        user_db_entry.update_last_message_timestamp()
        user_db_entry.add_xp(1)
        for i, level in enumerate(levels):
            if level.get_threshold() == db_get_user(author_id).get_xp():
                previous_level = levels[i-1].get_name()
                current_level = levels[i].get_name()
                # await message.author.remove_roles(level_roles)
                # await message.author.add_role(level_roles[i])
                user_db_entry.set_level(i)
                await message.channel.send(f'{message.author.mention} ranks up! {previous_level} ⇒ {current_level}')
                break

# Implements /hello command. Syntax: /hello
@client.tree.command(description = "Say hello to liliumbot!")
async def greet(interaction: discord.Interaction):
    await interaction.response.send_message("Hello, I'm liliumbot!")

# Implements /roll command. Syntax: /roll <max: int>
@client.tree.command(description = "Roll a random number between 0 and max (default 6).")
async def roll(interaction: discord.Interaction, max: int = 6):
    await interaction.response.send_message(f'You rolled a {randint(1, max)}!')

# Implements /addxp command. Syntax: /setxp <user: discord.User> <amount: int>
@client.tree.command(description = "Adds XP to user. Levels user up if they reach any thresholds.")
async def addxp(interaction: discord.Interaction, user: discord.User, xp: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have the required permissions to use this command.", ephemeral=True)
        return
    if not db_has_user(user.id):
        user_db.append(User(user.id))

    user_db_entry = db_get_user(user.id)
    response = f'Gave {xp} XP to {user.mention}.'
    for n in range(xp):
        user_db_entry.add_xp(1)
        for i, level in enumerate(levels):
            if level.get_threshold() == user_db_entry.get_xp():
                previous_level = levels[i-1].get_name()
                current_level = levels[i].get_name()
                response += f'\n{user.mention} ranks up! {previous_level} ⇒ {current_level}'
                user_db_entry.set_level(i)
                break
    await interaction.response.send_message(response)

# Implements /xp command. Syntax: /setxp <user: discord.User>
@client.tree.command(description = "Lists statistics about a given user's xp status.")
async def xp(interaction: discord.Interaction, user: discord.User = None):
    u = None
    if user is None:
        u = interaction.user
    else:
        u = user
    if not db_has_user(u.id):
        user_db.append(User(u.id))
    user_db_entry = db_get_user(u.id)
    response = f'{u.mention}\'s XP status: ```Rank: {levels[user_db_entry.get_level()].get_name()}\nXP: {user_db_entry.get_xp()}```'
    await interaction.response.send_message(response)

client.run(token)
