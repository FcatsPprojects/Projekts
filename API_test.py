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
        anime=[str(e["title"]).upper(), str(e["title_english"]).upper()]
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
            anime=[str(e["title"]).upper(), str(e["title_english"]).upper()]
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
            anime=[str(e["title"]).upper(), str(e["title_english"]).upper()]
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
print("Normal mode: guess an anime with a MAL rating above 7.5. Type 'normal' to select")
print("Hard mode: guess an anime from all anime on MAL. Type 'hard' to select")
print("Select mode:")
mode=input()

if mode=="normal":
    answer_list=[]
    for row in cur.execute(f'SELECT anime_id FROM info WHERE score>7.5'):
        answer_list.append(list(row))
    answer_id=random.randint(1,len(answer_list))
    answer_id=answer_list[answer_id]
    answer_id=answer_id[0]
    for row in cur.execute(f'SELECT type, source, episodes, score, aired_season, aired_year FROM info WHERE anime_id={answer_id} LIMIT 1'):
        answer_info=list(row)
elif mode=="hard":
    answer_id=random.randint(1,total_items)
    for row in cur.execute(f'SELECT type, source, episodes, score, aired_season, aired_year FROM info WHERE anime_id={answer_id} LIMIT 1'):
        answer_info=list(row)
else:
    raise ValueError("Incorrect input")

guess_id=[]
while guess_id!=answer_id:
    guess_id=[]
    # Ok now we start
    guess=input()
    if guess=="end":
        print(answer_id)
        quit()

    for row in cur.execute(f'SELECT anime_id FROM anime WHERE title_jp="{guess.upper()}" LIMIT 1'):
        guess_id=list(row)
    guess_id.append(0)
    guess_id=int(guess_id[0])
    if guess_id!=0:
        for row in cur.execute(f'SELECT type, source, episodes, score, aired_season, aired_year FROM info WHERE anime_id={guess_id} LIMIT 1'):
            give_info=list(row)
        print(f"{give_info}")

        if give_info[0]==answer_info[0]:
            give_info[0]="yes"
        else:
            give_info[0]="no"

        if give_info[1]==answer_info[1]:
            give_info[1]="yes"
        else:
            give_info[1]="no"
        
        if give_info[2]==answer_info[2]:
            give_info[2]="yes"
        elif give_info[2]<answer_info[2]:
            give_info[2]="more"
        else:
            give_info[2]="less"

        if type(give_info[3])==type(answer_info[3]):
            if give_info[3]==answer_info[3]:
                give_info[3]="yes"
            elif give_info[3]<answer_info[3]:
                give_info[3]="more"
            else:
                give_info[3]="less"
        else:
            give_info[3]="no"
        
        if give_info[4]==answer_info[4]:
            give_info[4]="yes"
        else:
            give_info[4]="no"

        if give_info[5]==answer_info[5]:
            give_info[5]="yes"
        elif give_info[5]<answer_info[5]:
            give_info[5]="more"
        else:
            give_info[5]="less"
        
        print(give_info)
    else:
        print("Invalid guess")

print("You did it, Yippee")

# API INFO

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

# QVNEL
# 
# RAGEL #1
# ybbxf yvxr yvfgf ner beqrerq ol zny_vq, fghqvb vf hfhnyyl bayl bar, pbhyq or gebhoyr sbe traerf
# vs jnag tb sbe traerf, fgnpxvat nyy bs gurz srryf onq ohg zvtug or xvaqn arprpnel zol
# cnva gb thrff ol, zvtug pnhfr zvfpbaprcgvbaf, ohg pnag ernyyl tvir whfg bar cre navzr
# nyfb vs lryybj, xvaqn qhzo gb grfg juvpu vf pbeerpg vs lbh unir yvxr 4-6 traerf, vs abg zber
# ogj svther bhg ubj gb trg guvf fuvg vagb n qo
# ohg gura jungf gur cbvag bs pnyyvat ncv...
# ohg fhpu n cnva gb trg arrqrq vasb sebz gung...
# nyfb frnepu pbhyq or qbar jvgu qo, whfg va cl gung jbhyq or yvfg bs qvpgf
# naq jbefr lrg, cebo arrq 2 sbe rnpu navzr vs tb ra naq wc gvgyr qvssrerag
# whfg ernq erdhverzragf naq tb sebz gurer, vs qo arrqrq gura qb gung, vs abg gura cnva jvgu ncv
# 
# RAGEL #2
# fb qo vf arrqrq
# zrnaf gung v trg qngn sebz ncv, guebj gung va gb znxr qo, hfr vasb sebz gurer ba
# 
# RAGEL #3
# v qbag jnaan qb guvf... ohg v tbggn v thrff
# svavfurq gur qngn trggvat cneg. pbhyq pnyy vg frghc
# abj vgf gvzr gb znxr gur npghny tnzr... htuuu
# yvxr vg fubhyqag or uneq ohg v whfg qbag jnaannnnnn
# fpenccrq enax naq fghqvb <cebonoyl fubhyq unir jebgr guvf va gur ynfg ragel
# unir na vqrn sbe traerf, ohg zvtug or n ovg gbb pbzcyrk gb vzcyrzrag va 1.5 qnlf
# tbaan yrnir gung gb yngre vs v qrpvqr gb jbex ba guvf
# nyfb vir sbhaq jevgvat ybtf yvxr guvf xvaqn sha, whfg chggvat zl gubhtugf fbzrjurer
# be vgf orpnhfr v pna srry cebqhpgvir juvyr abg qbvat nalguvat
# cebonoyl gur ynggre
# 
# guvf vf jevggra yngre, urapr gur fcnpr
# fb onfvpnyyl, tnzrzbqrf
# xabj vg nyy (hfrf gur jubyr qo)
# abezny, bssvpvny, jungrire lbh jnag gb pnyy vg (bayl hfrf navzr jvgu n zny engvat nobir 6.5)
# fubhyq cebonoyl znxr n zbqr jurer vgf bayl sebz navzr jvgu pregnva traerf, ohg bireync znxrf gung n ovg uneq
# lrn gungf vg zbfgyl
# xabj vg nyy vf rnfvrfg gb znxr fb fgneg jvgu gung
# naq vgf tbaan or cebonoyl gur bayl bar sbe gur rknz guvatlznwvt
# v zrna vgf yvgrenyl znxr thrffvat vasvavgr, fubj tenl, lryybj, terra, hc, qbja, gung glcr fghss
# bu naq v thrff v pna xrrc genpx bs cynlre fgngf va gur qngnonfr
# vf gurer rira nalguvat ryfr vq arrq?
# jryy qbphzragngvba boi ohg...
# bx jryy "abezny" zbqr vfag gung uneq gb znxr, lbh whfg yvzvg gur vqf vg pna cvpx
# BBBU v unir gb nqq bbc nf jryy...
# hzzzz trggvat fghss sebz gur qo pna or znqr va
# UBYQ GUNG GUBHTUG
# V PNA ZNXR GUR THRFFVAT VAGB N PYNFF
# arrq svther bhg gur fcrpvsvpf ohg abg onq vqrn ru?
# v nyfb arrq fbarguvat jvgu cnerag-puvyq pynff qlanzvp guvatlznwvt
# vyy svther gung bhg gze
# vyy frr vs v znxr n ybt
# v zrna v cebonoyl jvyy evtug? fvapr v jvyy trg ynml naq arrq gb ybbx cebqhpgvir
# nyevtug vyy frr vs v pna/jnag gb qb fbzrguvat zber gbqnl naq tb fyrrc
# jnxvat hc ng 0630 frrzf...
# lrn jul abg