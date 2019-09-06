import aiohttp
import configparser
import json

from discord.ext import commands

config = configparser.ConfigParser()
config.read('config.ini')

TOKEN = config['default']['token']

bot = commands.Bot(command_prefix='?')

@bot.command()
async def team_croot_rank(ctx, *args):
    message = 'Invalid syntax.  ?team_croot_rank <year> <team>'
    if len(args) <= 1:
        await ctx.send(message)
        return

    year = args[0]

    try:
        int(year)
    except ValueError:
        await ctx.send(message)
        return

    team = ' '.join(args[1:])

    url = f'https://api.collegefootballdata.com/recruiting/teams?year={year}&team={team}'
    async with aiohttp.ClientSession() as session:
        raw_response = await session.get(url)
        response = await raw_response.text()
        response = json.loads(response)
        if not response:
            message = 'No results.'
        else:
            rank = response[0]['rank']
            points = response[0]['points']
            message = f'Recruiting rank for {team} in {year}: {rank} ({points})'

        await ctx.send(message)

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

bot.run(TOKEN)
