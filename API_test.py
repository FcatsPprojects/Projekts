import requests
import sqlite3
import time
import random

# First API contact YIPPEE
req=requests.get("https://api.jikan.moe/v4/anime?status=complete&page=1")
data=req.json()

# Setting up values
anime=[]
info=[]
counter=int(1)
last_item=[]

max_page=data["pagination"]
total_items=max_page["items"]
total_items=total_items["total"]
max_page=max_page["last_visible_page"]

# Basicaly just set up to work with the database
con=sqlite3.connect("data.db")
cur=con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS anime(anime_id integer PRIMARY KEY, title_jp text, title_en text)''')
cur.execute('''CREATE TABLE IF NOT EXISTS info(anime_id integer, type text, source text, episodes integer, score real, aired_season text, aired_year text, FOREIGN KEY (anime_id) REFERENCES anime (anime_id))''')

# Checks if you have all the data, if not then gets it (Hooray to 20 min wait times)
for row in cur.execute('''SELECT anime_id FROM anime ORDER BY anime_id DESC LIMIT 1'''):
    last_item=list(row)
last_item.append(0)

if last_item[0]==total_items:
    ...
elif last_item[0]==0:
    for e in data["data"]:
        anime=[e["title"], e["title_english"]]
        info=[counter, e["type"], e["source"], e["episodes"], e["score"]]
        counter+=1
        aired=e["aired"]
        aired=aired["prop"]
        aired=aired["from"]
        if aired["month"] in range(0,4):
            info.append("Winter")
        elif aired["month"] in range(4,7):
            info.append("Spring")
        elif aired["month"] in range(7,10):
            info.append("Summer")
        else:
            info.append("Fall")
        info.append(aired["year"])
        cur.execute('INSERT OR IGNORE INTO anime(title_jp, title_en) VALUES(?,?)', anime)
        cur.execute('INSERT OR IGNORE INTO info VALUES(?,?,?,?,?,?,?)', info)
        con.commit()
    # IDK why i seperated the first one, felt like it i guess
    for i in range(2,max_page+1):
        req=requests.get(f"https://api.jikan.moe/v4/anime?status=complete&page={i}")
        data=req.json()
        # YES THE SLEEP IS NECESSARY
        # idk why if i try to do this for every 2nd or 3rd request it gets rate limited
        # tehnicaly api allows 3 requests per second
        # program 2 fast ig :P
        time.sleep(1)
        for e in data["data"]:
            anime=[e["title"], e["title_english"]]
            info=[counter, e["type"], e["source"], e["episodes"], e["score"]]
            counter+=1
            aired=e["aired"]
            aired=aired["prop"]
            aired=aired["from"]
            if aired["month"] in range(0,4):
                info.append("Winter")
            elif aired["month"] in range(4,7):
                info.append("Spring")
            elif aired["month"] in range(7,10):
                info.append("Summer")
            else:
                info.append("Fall")
            info.append(aired["year"])
            cur.execute('INSERT OR IGNORE INTO anime(title_jp, title_en) VALUES(?,?)', anime)
            cur.execute('INSERT OR IGNORE INTO info VALUES(?,?,?,?,?,?,?)', info)
            con.commit()
else:
    # I kinda like this. It takes the last full page of data and starts from there
    for i in range(int(last_item[0]/25),max_page+1):
        req=requests.get(f"https://api.jikan.moe/v4/anime?status=complete&page={i}")
        data=req.json()
        time.sleep(1)
        for e in data["data"]:
            anime=[e["title"], e["title_english"]]
            info=[counter, e["type"], e["source"], e["episodes"], e["score"]]
            counter+=1
            aired=e["aired"]
            aired=aired["prop"]
            aired=aired["from"]
            if aired["month"] in range(0,4):
                info.append("Winter")
            elif aired["month"] in range(4,7):
                info.append("Spring")
            elif aired["month"] in range(7,10):
                info.append("Summer")
            else:
                info.append("Fall")
            info.append(aired["year"])
            cur.execute('INSERT OR IGNORE INTO anime(title_jp, title_en) VALUES(?,?)', anime)
            cur.execute('INSERT OR IGNORE INTO info VALUES(?,?,?,?,?,?,?)', info)
            con.commit()


# Here starts the main part
answer_id=random.randint(1,total_items)
guess=input()
for row in cur.execute(f'SELECT anime_id FROM anime WHERE title_jp="{guess}" LIMIT 1'):
    guess_id=list(row)
guess_id.append(0)
guess_id=int(guess_id[0])
if guess_id==answer_id:
    print("You did it, Yippee")
else:
    print(f"what are you dumb {guess_id}")

# title(a switch for jp/en), type, source, episodes
# keys: "title" "title_english" "type" "source" "episodes"

# year of starting air, season of starting air(get these by calc)
# keys: "aired" > "from" or "string"

# score and rank ig
# keys: "score" "rank"

# studio maybe, but that doesnt do much for casuals
# keys: "studios" but that is a list, just go first ig

# genres could be interesting but probably hard to impliment
# keys: "genres" list again

# DIARY
# 
# ENTRY #1
# looks like lists are ordered by mal_id, studio is usually only one, could be trouble for genres
# if want go for genres, stacking all of them feels bad but might be kinda nececary mby
# pain to guess by, might cause misconceptions, but cant really give just one per anime
# also if yellow, kinda dumb to test which is correct if you have like 4-6 genres, if not more
# btw figure out how to get this shit into a db
# but then whats the point of calling api...
# but such a pain to get needed info from that...
# also search could be done with db, just in py that would be list of dicts
# and worse yet, prob need 2 for each anime if go en and jp title different
# just read requirements and go from there, if db needed then do that, if not then pain with api
# 
# ENTRY #2
# so db is needed
# means that i get data from api, throw that in to make db, use info from there on
# 
# ENTRY #3
# i dont wanna do this... but i gotta i guess
# finished the data getting part. could call it setup
# now its time to make the actual game... ughhh
# like it shouldnt be hard but i just dont wannaaaaaa
# scrapped rank and studio <probably should have wrote this in the last entry
# have an idea for genres, but might be a bit too complex to implement in 1.5 days
# gonna leave that to later if i decide to work on this
# also ive found writing logs like this kinda fun, just putting my thoughts somewhere
# or its because i can feel productive while not doing anything
# probably the latter
# 
# this is written later, hence the space
# so basically, gamemodes
# know it all (uses the whole db)
# normal, official, whatever you want to call it (only uses anime with a mal rating above 6.5)
# should probably make a mode where its only from anime with certain genres, but overlap makes that a bit hard
# yea thats it mostly
# know it all is easiest to make so start with that
# and its gonna be probably the only one for the exam thingymajig
# i mean its literaly make guessing infinite, show gray, yellow, green, up, down, that type stuff
# oh and i guess i can keep track of player stats in the database
# is there even anything else id need?
# well documentation obv but...
# ok well "normal" mode isnt that hard to make, you just limit the ids it can pick
# OOOH i have to add oop as well...
# ummmm getting stuff from the db can be made in
# HOLD THAT THOUGHT
# I CAN MAKE THE GUESSING INTO A CLASS
# need figure out the specifics but not bad idea eh?
# i also need sonething with parent-child class dynamic thingymajig
# ill figure that out tmr
# ill see if i make a log
# i mean i probably will right? since i will get lazy and need to look productive
# alright ill see if i can/want to do something more today and go sleep
# waking up at 0630 seems...
# yea why not