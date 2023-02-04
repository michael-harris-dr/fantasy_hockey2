import sys
import os
import requests
import json

def update_team_list():
    print("Updating team list...")
    apiStr2 = "https://statsapi.web.nhl.com/api/v1/teams"
    response = requests.get(apiStr2)
    print(f"Updating team list, respone: {response.status_code}")

    if(response.status_code != 200):
        print("Response not OK, terminating...")
    else:
        print("Response 200")
        nhlJson = json.loads(response.text)
    #print(nhlJson)

    fp = open("NHL_TEAMS.json", "w")
    json.dump(nhlJson, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=3, separators=None)
    fp.close()
    print("Teams list finished update.")

def update_player_list(teamID):
    apiStr = f"https://statsapi.web.nhl.com/api/v1/teams/{teamID}/roster" #?expand=team.roster"
    response = requests.get(apiStr)
    print(f"Updating player list for team id={teamID}, response: {response.status_code}")
    if(response.status_code != 200):
        print(f"Response for {apiStr} not OK, terminating...")
    else:
        teamJson = json.loads(response.text)

        teamJson["copyright"] = teamID #changes copyright text to team ID
        #print(nhlJson)
    
        fp = open(f"db/TEAM_ROSTER_{teamID}.json", "w")
        json.dump(teamJson, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=3, separators=None)

        fp.close()

def update_entire_player_list(idList):
    for id in idList:
        update_player_list(id)
    print("All rosters updated...")

def input_names():
    #print("Enter player names in the form \"lastname,lastname,lastname\":")
    inp = input("Enter player surnames:")
    nameList = inp.replace(" ",",").split(',')
    print(nameList)
    return nameList

def menu_loop(idTeam):
    inp = "0"
    while(inp != "1" and inp != "2"):
        inp = input("(1) Refresh team list and rosters\n(2) Skip\nEnter command: ")
    if(inp == "1"):
        update_team_list()
        update_entire_player_list(idTeam)
        print("\n\n\n")
        return
    elif(inp == "2"):
        return
    else:
        print("critical error 1")
    
def fanPts(player):
    return (3*player["goals"] + 2*player["assists"])

def find_players(nameList, idTeam):
    #find players in the league and store their IDs
    playerIDs = {}

    for player in nameList: #for every player the user requested
        for id in idTeam:   #for every id in the team id list (for each NHL team)
            tmp = player
            #open and load the corresponding JSON for the current team
            fp2 = open(f"./db/TEAM_ROSTER_{id}.json")
            teamJson = json.load(fp2)

            for name in teamJson["roster"]: #for every player on the team
                surname = name["person"]["fullName"].split(" ")[1]  #isolate their last name
                
                if(player == surname):  #if the last name of the current player matches the last name of the current desired player
                    print(f"Found {player} matches {surname} on team: " + idTeam[teamJson["copyright"]])
                    
                    #accounting for repeated names (e.g. "Tkachuk")
                    while player in playerIDs:
                        player = f"{player}*"
                        #print(playerIDs)
                    playerIDs[player] = name["person"]["id"]    #add the current player as a key in the dict with their value as their ID
                player = tmp
            fp2.close()
    return playerIDs


def populate_stats(playerIDs, yearStrings):
    playerStats = {}

    goals = 0
    assists = 0
    shotPct = 0
    games = 0

    for years in yearStrings:
        for player in playerIDs:
            apiStr = f"https://statsapi.web.nhl.com/api/v1/people/{playerIDs[player]}/stats?stats=statsSingleSeason&season={years}"
            response = requests.get(apiStr)
            playerJson = json.loads(response.text)
            print(response.status_code)
            #print(playerJson)
            #print(playerJson["stats"][0]["splits"][0]["stat"])
            if "shutouts" in playerJson["stats"][0]["splits"][0]["stat"]:
                print(f"{player} is goalie")
            else:
                stats = playerJson["stats"][0]["splits"][0]["stat"]
            
                goals += stats["goals"]
                assists += stats["assists"]
                shotPct += stats["shotPct"]
                games += stats["games"]
            playerStats[player] = {"goals":goals, "assists":assists, "shotPct":shotPct, "games":games}
    return playerStats

#TODO: add players previous years stats and adjust xFP (expected fantasy points) accordingly
#TODO: add GP as stat and factor into xFP
def populate_player_stats(playerIDs):
    #adding a player's stats to the playerStats dict
    playerStats = {}

    for player in playerIDs:
        apiStr = f"https://statsapi.web.nhl.com/api/v1/people/{playerIDs[player]}/stats?stats=statsSingleSeason&season=20222023"
        response = requests.get(apiStr)
        playerJson = json.loads(response.text)
        print(response.status_code)
        #print(playerJson)
        #print(playerJson["stats"][0]["splits"][0]["stat"])
        if "shutouts" in playerJson["stats"][0]["splits"][0]["stat"]:
            print(f"{player} is goalie")
        else:
            stats = playerJson["stats"][0]["splits"][0]["stat"]
        
            goals = stats["goals"]
            assists = stats["assists"]
            shotPct = stats["shotPct"]
            games = stats["games"]

            playerStats[player] = {"goals":goals, "assists":assists, "shotPct":shotPct, "games":games}
    return playerStats

def populate_past_stats(playerIDs):
    #adding a player's stats to the playerStats dict
    pastStats = {}

    for player in playerIDs:
        apiStr = f"https://statsapi.web.nhl.com/api/v1/people/{playerIDs[player]}/stats?stats=statsSingleSeason&season=20212022"        
        response = requests.get(apiStr)
        playerJson = json.loads(response.text)
        
        print(response.status_code)
        #print(playerJson)
        #print(playerJson["stats"][0]["splits"][0]["stat"])
        if "shutouts" in playerJson["stats"][0]["splits"][0]["stat"]:
            print(f"{player} is goalie")
        else:
            stats = playerJson["stats"][0]["splits"][0]["stat"]
        
            goals = stats["goals"]
            assists = stats["assists"]
            shotPct = stats["shotPct"]
            games = stats["games"]

            pastStats[player] = {"goals":goals, "assists":assists, "shotPct":shotPct, "games":games}

            apiStr = f"https://statsapi.web.nhl.com/api/v1/people/{playerIDs[player]}/stats?stats=statsSingleSeason&season=20202021"        
            response = requests.get(apiStr)
            playerJson = json.loads(response.text)

            stats = playerJson["stats"][0]["splits"][0]["stat"]

            pastStats[player]["goals"] += stats["goals"]
            pastStats[player]["assists"] += stats["assists"]
            pastStats[player]["games"] += stats["games"]

            print(((pastStats[player]["shotPct"] * pastStats[player]["games"]) + (stats["shotPct"] * stats["games"])) / (pastStats[player]["games"] + stats["games"]))

    return pastStats

#MAIN()###########################################################################################################

def main():
    idTeam = {}#dict()

    fp = open("NHL_TEAMS.json", "r")
    nhlJson = json.load(fp)
    for team in nhlJson["teams"]: #for each team
        idTeam[team["id"]] = team["name"] #add the team name to the dict w/ the team ID as the key

    menu_loop(idTeam)

    nameList = input_names()

    playerIDs = find_players(nameList, idTeam)
    #print(playerIDs)

    yearIDs = ["20222023"]
    playerStats = populate__stats(playerIDs, yearIDs)
    print(playerStats)

    pastStats = populate_past_stats(playerIDs)
    print(pastStats)

    #isolating useful stats
    for player in playerStats:
        print(f"fanPts for {player} = {fanPts(playerStats[player])}")

    fp.close()

main()
#FIN