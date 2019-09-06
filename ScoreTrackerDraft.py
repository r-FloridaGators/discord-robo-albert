import requests
import json
from dateutil import rrule
import datetime

###------Constants-----###
BASE_URL = 'https://api.collegefootballdata.com/'
CURRENT_YEAR = '2019'
WEEK_0 = datetime.date(2019,8,24)

###-----Functions-----###
def weeks_between(start_date, end_date):
    weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date)
    return weeks.count() - 1

def get_current_week():
	cur_date = datetime.date.today()
	return weeks_between(WEEK_0, cur_date)

# Creates the initial dictionary for all games in the current week with
# the game_id as the key and game data as the value.
def create_games_dictionary():
  result = {}
  payload = {"year": CURRENT_YEAR, "week": get_current_week()}
  response = requests.get(BASE_URL + "games", params=payload)
  if(response.ok):
    games = json.loads(response.content)
    for i in range(len(games)):
      games[i].update({"last_drive": {},"drive_id": "0"})
      result[games[i]["id"]] = games[i]
    return result
  else:
    response.raise_for_status()
    return

# Queries for updates for the list of games. 
# Pass in games dictionary as a parameter.
def update_games(games):
  payload = {"year": CURRENT_YEAR, "week": get_current_week()}
  response = requests.get(BASE_URL + "games", params=payload)
  if(response.ok):
    new_data = json.loads(response.content)
    for i in range(len(new_data)):
      games[new_data[i]["id"]].update(new_data[i])
    return
  else:
    response.raise_for_status()
    return

# Queries for all of the drives for the week.
def get_drives():
  payload = {"year": CURRENT_YEAR, "week": get_current_week()}
  drives = requests.get(BASE_URL + "drives", payload)
  if(drives.ok):
    return json.loads(drives.content)
  else:
    drives.raise_for_status()
    return

# Queries the newest data for the games and updates tracking of most recent drive.
# If new drive happened, post to Discord.
def check_for_game_updates(games):
  update_games(games)
  drives = get_drives()
  for key in games.keys():
    newDrive = False
    for i in range(len(drives)):
      if(int(key) in drives[i].values()):
        if(int(games[key]["drive_id"]) < int(drives[i]["id"])):
          games[key]["drive_id"] = drives[i]["id"]
          games[key]["last_drive"] = drives[i]
          newDrive = True
    if(newDrive):
      # Function for Writing to Discord Goes here.
      # Flow should be: 
      # Check games[key]["last_drive"]["drive_result"] -> If Score (FG, TD) : 
      #   retrieve scores from games[key]["home_points"] & games[key]["away_points"]
      # Write out Drive Info.
      # If Score => Write Out New Score.
      return

# Bot should call create_games_dictionary() at the start of each week.
# Then call check_for_game_updates() on a polling interval.