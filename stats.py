import aiohttp
import json

from discord.ext import commands

class Stats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def games(self, ctx, *args):
        message = 'Invalid syntax. ?games <year> <school>'
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

        url = f'https://api.collegefootballdata.com/games?year={year}&seasonType=regular&team={team}'

        async with aiohttp.ClientSession() as session:
            raw_response = await session.get(url)
            response = await raw_response.text()
            response = json.loads(response)
            if not response or len(response) is 0:
                message = 'No results.'
                return
            else:
                message = f'**{team} in {year} (Regular season)**:\n'
                for value in response:
                    message += f'Week {value["week"]}: {value["away_team"]} @ {value["home_team"]} - {value["away_points"]} - {value["home_points"]}\n'

            await ctx.send(message)

        url = f'https://api.collegefootballdata.com/games?year={year}&seasonType=postseason&team={team}'

        async with aiohttp.ClientSession() as session:
            raw_response = await session.get(url)
            response = await raw_response.text()
            response = json.loads(response)
            if not response or len(response) is 0:
                message = ''
                return
            else:
                message = f'**{team} in {year} (Post season)**:\n'
                for value in response:
                    message += f'Week {value["week"]}: {value["away_team"]} @ {value["home_team"]} - {value["away_points"]} - {value["home_points"]}\n'

            await ctx.send(message)
