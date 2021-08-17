import aiohttp
import configparser
import json
from datetime import datetime
from discord.ext import commands

from team_nickname import confirm_teamname

class Betting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.API_KEY = config['default']['cfbdata_api_key']

    @commands.command()
    async def odds(self, ctx, *args):
        message = 'Invalid syntax. ?odds <school>'
        if len(args) == 0:
            await ctx.send(message)
            return

        year = datetime.now().year
        team = confirm_teamname((' '.join(args[0:])))

        url = f'https://api.collegefootballdata.com/lines?year={year}&seasonType=regular&team={team}'

        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f'Bearer {self.API_KEY}'}
            raw_response = await session.get(url, headers = headers)
            response = await raw_response.text()
            response = json.loads(response)
            if not response or len(response) is 0:
                message = 'No results.'
                await ctx.send(message)
                return
            else:
                response.reverse()
                for value in response:
                    lines = value['lines']
                    if len(lines) > 0:
                        line = lines[0]
                        message = f'{value["awayTeam"]} @ {value["homeTeam"]}: **{line["formattedSpread"]}** (O/U: {line["overUnder"]})'
                        await ctx.send(message)
                        return
