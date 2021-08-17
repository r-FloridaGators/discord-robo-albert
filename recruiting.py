import aiohttp
import configparser
import json

from discord.ext import commands
from team_nickname import confirm_teamname

class Recruiting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.API_KEY = config['default']['cfbdata_api_key']

    @commands.command()
    async def croot(self, ctx, *args):
        message = 'Invalid syntax -- ?croot <year> <name>'
        if len(args) <= 1:
            await ctx.send(message)
            return

        year = args[0]

        try:
            int(year)
        except ValueError:
            await ctx.send(message)
            return

        name = '%20'.join(args[1:])

        url = f'https://247sports.com/Season/{year}-Football/Recruits.json?&Items=15&Page=1&Player.FullName={name}'

        async with aiohttp.ClientSession(headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
) as session:
            raw_response = await session.get(url)
            response = await raw_response.text()
            response = json.loads(response)
            if not response or len(response) is 0:
                message = 'Sorry, no results found.'
                await ctx.send(message)
                return
            elif len(response) > 2:
                message = 'Too many results.  Please be more specific.'
                await ctx.send(message)
                return
            else:
                for value in response:
                    player = value['Player']
                    full_name = player['FullName']
                    position = player['PrimaryPlayerPosition']['Abbreviation']
                    evaluation = player['ScoutEvaluation']
                    url = player['Url']
                    composite_rating = player['CompositeRating']
                    stars = player['CompositeStarRating']
                    stars_str = f'⭐'*int(stars)

                    message = f'\n**{full_name} - {position}\n247 Composite:** {stars_str} ({composite_rating})\n{url}\n{evaluation or ""}\n'

                    await ctx.send(message)


    @commands.command()
    async def team_croot_rank(self, ctx, *args):
        message = 'Invalid syntax -- ?team_croot_rank <year> <team>'
        if len(args) <= 1:
            await ctx.send(message)
            return

        year = args[0]

        try:
            int(year)
        except ValueError:
            await ctx.send(message)
            return

        team = confirm_teamname((' '.join(args[1:])))

        url = f'https://api.collegefootballdata.com/recruiting/teams?year={year}&team={team}'
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f'Bearer {self.API_KEY}'}
            raw_response = await session.get(url, headers = headers)
            response = await raw_response.text()
            response = json.loads(response)
            if not response:
                message = 'No results.'
            else:
                rank = response[0]['rank']
                points = response[0]['points']
                message = f'247 Recruiting rank for **{team}** in {year}: **{rank}** ({points})'

            await ctx.send(message)
