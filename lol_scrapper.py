import requests
from bs4 import BeautifulSoup
import webbrowser
import json


def main(configs):
    allMatchUps = {}
    opponent = input("Enemy Champion: ").capitalize()
    webDomain = configs["webDomain"]
    champPool = configs["champPool"]
    matchupClass = configs["matchupClass"] # Parent Class


    for champ in champPool:
        link = f"{webDomain}/lol/champions/{champ}/counters"
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')  # Get HTML content
        match_ups = soup.find_all(class_=matchupClass)
        champStats = getStats(match_ups, configs)
        allMatchUps[champ] = champStats

    bestPick = getMatchUp(allMatchUps, opponent)
    return print(f'-------- {bestPick} is the best pick --------')


# Returns a dictionary of matchups for a champion
def getStats(match_ups, configs):
    champNameClass = configs["champNameClass"] # Child Class
    gdClass = configs["gdClass"] # Child Class
    champMatchUps = {}
    for match_up in match_ups:
        for child in match_up.contents:
            champNameHtml = child.find_all(class_=champNameClass)
            champStatsHtml = child.find_all(class_=gdClass)
            champName = champNameHtml[0].get_text()
            champMatchUps[champName] = {
                "GD@15": champStatsHtml[0].get_text(),
                "winRate": champStatsHtml[1].get_text(),
                "link": child.get('href')
            }
    return champMatchUps


# Returns best pick from the matchup stats for each champ in the pool for @opponent
# Opens mobalytics matchup page if there is an optimal pick
def getMatchUp(allMatchUps, opponent):
    bestGD = {"key": "filler", "value": 0}
    bestWR = {"key": "filler", "value": 0}
    for champ, stats in allMatchUps.items():
        try:
            opStats = stats[opponent]
        except KeyError:
            opStats = {"GD@15": "N/A", "winRate": "N/A"}

        if opStats["GD@15"] == "N/A":
            pass
        else:
            matchUpGD = parseStr(opStats["GD@15"])
            matchUpWR = parseStr(opStats["winRate"])
            if (matchUpGD > bestGD["value"]):
                bestGD = {"key": champ, "value": matchUpGD}
            if (matchUpWR > bestWR["value"]):
                bestWR = {"key": champ, "value": matchUpWR}
        print(
            champ.ljust(15, " ").capitalize(),
            "|",
            "GD@15:",
            opStats.get("GD@15").ljust(10, " "),
            "|",
            "WinRate:",
            opStats.get("winRate").ljust(10, " "))

    if (bestGD.get("key") == bestWR.get("key")):
        matchUpPage = PAGE+allMatchUps[bestGD["key"]][opponent].get("link")
        webbrowser.open(matchUpPage)
        return bestGD.get("key").capitalize()


def parseStr(string):
    if (string[0] == "+" or string[0] == "-"):
        return float(string[1:])
    elif (string[-1] == "%"):
        return float(string[:-1])


if __name__ == "__main__":
    config_file = input("Config File:")
    with open(config_file, "r") as cfg:
        configs = json.load(cfg)
        main(configs)
