import aiohttp
import configparser
import json

from discord.ext import commands

config = configparser.ConfigParser()
config.read('config.ini')

TOKEN = config['default']['token']

bot = commands.Bot(command_prefix='?')

@bot.command()
async def team_croot_rank(ctx, year, team):
    url = f'https://api.collegefootballdata.com/recruiting/teams?year={year}&team={team}'
    async with aiohttp.ClientSession() as session:
        raw_response = await session.get(url)
        response = await raw_response.text()
        response = json.loads(response)
        if not response:
            message = 'No results.  If the school is more than one word, use quotes around the entire school name.'
        else:
            rank = response[0]['rank']
            message = f'Recruiting rank for {team} in {year}: {rank}'

        await ctx.send(message)

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

bot.run(TOKEN)
