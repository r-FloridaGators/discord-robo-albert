import requests
import json

from discord.ext import commands
from espn_team_nickname import confirm_teamname

TEAMS_URL = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/"
SUMMARY_URL = 'http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary'
class ScoreInquiry(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def score(self, ctx, *args):
        message = 'Invalid syntax -- ?score <teamname>'
        if len(args) < 1:
            await ctx.send(message)
            return
        else:
            team = " ".join(args).strip()
            message = self.get_score(self.get_game_id(team))
            await ctx.send(message)

    def get_game_id(self, team):
        team_name = confirm_teamname(team)
        if team_name == 'notfound':
            return None
        team_name = team_name.replace(' ', '')
        response = requests.get(TEAMS_URL+team_name)
        game_id = ''
        if response.ok:
            team_info = json.loads(response.content)
            game_id = team_info['team']['nextEvent'][0]['id']
            return game_id
        else:
            response.raise_for_status()
            return None

    def get_score(self, game_id):
        if game_id != None:
            payload = {'event': game_id}
            response = requests.get(SUMMARY_URL, payload)
            if response.ok:
                game = json.loads(response.content)
                print(game)
                return self.create_score_string(game)
            else:
                response.raise_for_status()
                return "There was an error in retrieving the info."
        else:
            return "Team not recognized. Please try a different team name."

    def create_score_string(self, game):
        competition = game['header']['competitions'][0]

        status = competition['status']['type']['shortDetail']
        home = competition['competitors'][0]
        away = competition['competitors'][1]

        try:
          home_win_probability = round(float(game['winprobability'][-1]['homeWinPercentage']), 3) * 100
        except:
          print('Game not started, no probability info yet.')

        if 'score' in home:
          result = '-----------------\n'
          result += away['team']['displayName'] + ': ' + away['score'] + ('\t🏈' if away['possession'] else '') + '\n'
          result += home['team']['displayName'] + ': ' + home['score'] + ('\t🏈' if home['possession'] else '') + '\n'
          result += status + '\n'
          result += 'Win Probability: ' + ((str(home_win_probability) + '% ' + home['team']['displayName']) if home_win_probability >= 50.0 else (str(100 - home_win_probability) + '% ' + away['team']['displayName']))
          result += '\n-----------------'
        else:
            result = '-----------------\n'
            result += away['team']['displayName'] + " @ " + home['team']['displayName'] + "\n"
            result += "Game will start on:\n"
            result += game['header']['competitions'][0]['status']['type']['detail'] + "\n"
            result += "Broadcast on: " + game['header']['competitions'][0]['broadcasts'][0]['media']['shortName'] + "\n"
            result += '-----------------'
        return result.strip()
