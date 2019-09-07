import requests
import json

###------Constants-----###
SUMMARY_URL = 'http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary'
SCOREBOARD_URL = 'http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard'
GROUP = {"FBS": 80, "ACC": 1, "American": 151, "B12": 4, "B1G": 5, "CUSA": 12, "IND": 18, "MAC": 15, "MWC": 17, "P12": 9, "SEC": 8, "SUN": 37}
QUERY_LIMIT = 100
SCOREBOARD_PAYLOAD = {'groups': GROUP['FBS'],'limit': QUERY_LIMIT}

###-----Functions-----###

# Creates the initial dictionary for all games in the current week with
# the game_id as the key and game data as the value.
def create_games_list():
  result = {}
  response = requests.get(SCOREBOARD_URL, SCOREBOARD_PAYLOAD)
  if(response.ok):
    games = json.loads(response.content)['events']
    for i in range(len(games)):
      home = games[i]['competitions'][0]['competitors'][0]
      away = games[i]['competitions'][0]['competitors'][1]
      games[i].update({'home_team': home['team']['displayName'], 'away_team': away['team']['displayName'], 'home_score': home['score'], 'away_score': away['score']})
      result.update({games[i]['id']: games[i]})
    return result
  else:
    response.raise_for_status()
    return

# Queries for updates for the list of games. 
# Pass in games dictionary as a parameter.
def update_games(games):
  response = requests.get(SCOREBOARD_URL, SCOREBOARD_PAYLOAD)
  if(response.ok):
    new_data = json.loads(response.content)['events']
    for i in range(len(new_data)):
      games[new_data[i]['id']].update(new_data[i])
    return
  else:
    response.raise_for_status()
    return

# Queries for last scoring drive for the given game id.
def get_last_scoring_drive(id):
  payload = {"event": id}
  response = requests.get(SUMMARY_URL, payload)
  if(response.ok):
    drives = json.loads(response.content)['drives']['previous']
    for drive in reversed(drives):
      if(drive['isScore']):
        return drive
  else:
    response.raise_for_status()
    return

# Checks to see if score has changed since previous poll.
def score_changed(game):
  home = game['competitions'][0]['competitors'][0]
  away = game['competitions'][0]['competitors'][1]
  if(game['home_score'] != home['score'] or game['away_score'] != away['score']):
    game['home_score'] = home['score']
    game['away_score'] = away['score']
    return True
  else:
    return False

# Checks to see if game has concluded.
def end_of_game(game):
  if(game['status']['type']['completed']):
    return True
  return False

# Creates the proper score update string to be posted in Discord.
def create_score_update_string(game, drive):
  result = drive['plays'][-1]['text'] + '\n'
  result += game['away_team'] + ': ' + game['away_score'] +'\n'
  result += game['home_team'] + ': ' + game['home_score']
  return result

#Creates the proper game final string to be posted in Discord.
def create_final_update_string(game):
  result = '*---FINAL---*\n'
  result += game['away_team'] + ': ' + game['away_score'] +'\n'
  result += game['home_team'] + ': ' + game['home_score']
  return result

# Polls the API for the most recent data and checks for updates to the games.
def poll_for_updates(games):
  update_games(games)
  count = 0
  completed_games = []
  for game in games.values():
    update = False
    if(score_changed(game)):
      drive = get_last_scoring_drive(game['id'])
      print(create_score_update_string(game, drive))
      update = True
    if(end_of_game(game)):
      print(create_final_update_string(game))
      completed_games.append(game['id'])
      update = True
    if(update):
      count += 1
  print(count)
  for id in completed_games:
    del games[id]

