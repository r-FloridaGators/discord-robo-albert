import requests
import json
import time
from discord.ext import tasks, commands

URL = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard"
SUMMARY_URL = 'http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary'
GROUP = {"FBS": 80, "ACC": 1, "American": 151, "B12": 4, "B1G": 5, "CUSA": 12, "IND": 18, "MAC": 15, "MWC": 17, "P12": 9, "SEC": 8, "SUN": 37}

class ScoreTracker(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.games = self.create_games_list()
    self.get_scores.start()


  def create_games_list(self):
    result = {}
    payload = {'groups': GROUP['FBS'],'limit': 100}
    response = requests.get(URL, payload)
    if(response.ok):
      games = json.loads(response.content)['events']
      for i in range(len(games)):
        home = games[i]['competitions'][0]['competitors'][0]
        away = games[i]['competitions'][0]['competitors'][1]
        games[i].update({'home_team': home['team']['displayName'], 'away_team': away['team']['displayName'], 'home_score': home['score'], 'away_score': away['score'], 'last_scoring_play': ''})
        result.update({games[i]['id']: games[i]})
      return result
    else:
      response.raise_for_status()
      return

  def update_games(self, games):
    payload = {'groups': GROUP['FBS'],'limit': 100}
    response = requests.get(URL, payload)
    if(response.ok):
      new_data = json.loads(response.content)['events']
      for i in range(len(new_data)):
        key = new_data[i]['id']
        if key in games:
          games[key].update(new_data[i])
      return
    else:
      response.raise_for_status()
      return

  def get_last_scoring_drive(self, id):
    payload = {"event": id}
    response = requests.get(SUMMARY_URL, payload)
    if(response.ok):
      try:
        drives = json.loads(response.content)['drives']['previous']
      except:
        return None
      for drive in reversed(drives):
        if(drive['isScore']):
          return drive
    else:
      response.raise_for_status()
      return

  def score_changed(self, game):
    home = game['competitions'][0]['competitors'][0]
    away = game['competitions'][0]['competitors'][1]
    if(game['home_score'] != home['score'] or game['away_score'] != away['score']):
      game['home_score'] = home['score']
      game['away_score'] = away['score']
      return True
    else:
      return False

  def end_of_game(self, game):
    return game['status']['type']['completed']

  def create_score_update_string(self, game, drive):
    result = '-----------------\n'
    if(drive != None and self.new_scoring_play(game, drive)):
      result += game['last_scoring_play'] + '\n'
    result += game['away_team'] + ': ' + game['away_score'] + '\n'
    result += game['home_team'] + ': ' + game['home_score'] + '\n'
    result += '-----------------'
    return result
    
  def create_final_update_string(self, game):
    result = '***------FINAL------***\n'
    result += game['away_team'] + ': ' + game['away_score'] + '\n'
    result += game['home_team'] + ': ' + game['home_score'] + '\n'
    result += '***-------------------***'
    return result

  def poll_for_updates(self, games):
    self.update_games(games)
    completed_games = []
    results = []
    for game in games.values():
      if(self.score_changed(game)):
        drive = self.get_last_scoring_drive(game['id'])
        results.append(self.create_score_update_string(game, drive))
      elif(self.end_of_game(game)):
        results.append(self.create_final_update_string(game))
        completed_games.append(game['id'])
    
    for id in completed_games:
      del games[id]

    return results

  def new_scoring_play(self, game, drive):
    play = drive['plays'][-1]['text']
    if(game['last_scoring_play'] != play):
      game['last_scoring_play'] = play
      return True
    else:
      return False

  @tasks.loop(seconds=60.0)
  async def get_scores(self):
    channel = self.bot.get_channel(628800815389343746)
    scores = self.poll_for_updates(self.games)
    for score in scores:
      await channel.send(score)

  @get_scores.before_loop
  async def before_get_scores(self):
    await self.bot.wait_until_ready()
