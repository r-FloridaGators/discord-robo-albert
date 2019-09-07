import configparser

import recruiting

from discord.ext import commands

config = configparser.ConfigParser()
config.read('config.ini')

TOKEN = config['default']['token']

bot = commands.Bot(command_prefix='?')
bot.add_cog(recruiting.Recruiting(bot))

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

bot.run(TOKEN)
