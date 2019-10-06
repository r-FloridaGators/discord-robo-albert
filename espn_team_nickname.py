
import json

f= open('espn_teamnicknames.json', encoding='latin-1')
json_nicknames=json.load(f)

def confirm_teamname(nickname):
    lower_nickname = nickname.lower()

    for (k,v) in json_nicknames.items():
        if lower_nickname==k.lower() or lower_nickname in v:
            return k

    return('notfound')

