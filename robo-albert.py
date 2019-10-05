import configparser

import betting
import recruiting
import stats
import ScoreInquiry
import ScoreTracker

from discord.ext import commands

config = configparser.ConfigParser()
config.read('config.ini')

TOKEN = config['default']['token']

bot = commands.Bot(command_prefix='?')
bot.add_cog(recruiting.Recruiting(bot))
bot.add_cog(stats.Stats(bot))
bot.add_cog(betting.Betting(bot))
bot.add_cog(ScoreInquiry.ScoreInquiry(bot))
bot.add_cog(ScoreTracker.ScoreTracker(bot))

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

bot.run(TOKEN)
