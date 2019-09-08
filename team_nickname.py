
import json

#f= open('teamnicknames.json')
#nicknamelist=json.load(f)
#f.close

def confirm_teamname(json_nicknames,nickname):
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

#theteam=find_teamname(nicknamelist,"floriddda")
#print(theteam)