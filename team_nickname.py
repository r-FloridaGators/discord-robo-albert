
import json

f= open('teamnicknames.json', encoding='latin-1')
json_nicknames=json.load(f)

def confirm_teamname(nickname):
    name="notfound"
    for (k,v) in json_nicknames.items():
        currentteam=str(k)
        if nickname==currentteam:
            name=k
            break
        else:
            current_teamlist=str(v)
            found=current_teamlist.find("'"+ nickname + "'")
            if found != -1:
                name=k
                break
                #print("key: " + k)
    return(name)

