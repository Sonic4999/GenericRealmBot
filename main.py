import discord, os
import asyncio, logging
from discord.ext import commands
from datetime import datetime

from discord.ext.commands.core import command
import cogs.utils.universals as univ

from dotenv import load_dotenv
load_dotenv()

# we're going to use all intents for laziness purposes
# we could reasonably turn some of these off, but this bot is too small to really matter much
bot = commands.Bot(command_prefix='!?', fetch_offline_members=True, intents=discord.Intents.all())
bot.remove_command("help")

log = logging.getLogger('authentication')
log.setLevel(logging.ERROR)

@bot.event
async def on_ready():

    if bot.init_load == True:
        bot.config = {}
        bot.gamertags = {}
        bot.pastebins = {}

        application = await bot.application_info()
        bot.owner = application.owner

        bot.load_extension("cogs.config_fetch")
        while bot.config == {}:
            await asyncio.sleep(0.1)

        cogs_list = ["cogs.eval_cmd", "cogs.general_cmds", "cogs.mod_cmds", "cogs.playerlist"]

        for cog in cogs_list:
            bot.load_extension(cog)

        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------\n')

        activity = discord.Activity(name = 'over some Bedrock Edition Realms', type = discord.ActivityType.watching)
        await bot.change_presence(activity = activity)

    utcnow = datetime.utcnow()
    time_format = utcnow.strftime("%x %X UTC")

    connect_str = "Connected" if bot.init_load else "Reconnected"

    await univ.msg_to_owner(bot, f"{connect_str} at `{time_format}`!")

    bot.init_load = False
    
@bot.check
async def block_dms(ctx):
    return ctx.guild is not None

@bot.check
async def not_support_server(ctx: commands.Context):
    return not (ctx.guild.id == 775912554928144384 and not ctx.command.qualified_name in ("eval", "help", "ping"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        original = error.original
        if not isinstance(original, discord.HTTPException):
            await univ.error_handle(bot, error, ctx)
    elif isinstance(error, (commands.ConversionError, commands.UserInputError, commands.CommandOnCooldown)):
        await ctx.send(error)
    elif isinstance(error, commands.CheckFailure):
        if ctx.guild != None:
            await ctx.send("You do not have the proper permissions to use that command.")
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        await univ.error_handle(bot, error, ctx)

@bot.event
async def on_error(event, *args, **kwargs):
    try:
        raise
    except Exception as e:
        await univ.error_handle(bot, e)

bot.init_load = True
bot.run(os.environ.get("MAIN_TOKEN"))
