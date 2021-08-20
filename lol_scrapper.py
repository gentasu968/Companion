import requests
from bs4 import BeautifulSoup
import webbrowser


# css class for mobalytics matchups page
MATCHUP_CLASS = 'm-jnzqnj'  # Parent Class
GD_CLASS = 'm-1wyf6ef'  # Child Class
CHAMP_NAME_CLASS = 'm-1fvxu1d'  # Child Class
PAGE = 'https://app.mobalytics.gg'


def main(champPool):
    allMatchUps = {}
    opponent = input("Enemy Champion: ").capitalize()

    for champ in champPool:
        link = f"{PAGE}/lol/champions/{champ}/counters"
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')  # Get HTML content
        match_ups = soup.find_all(class_=MATCHUP_CLASS)
        champStats = getStats(match_ups)
        allMatchUps[champ] = champStats

    bestPick = getMatchUp(allMatchUps, opponent)
    return print(f'-------- {bestPick} is the best pick --------')


# Returns a dictionary of matchups for a champion
def getStats(match_ups):
    champMatchUps = {}
    for match_up in match_ups:
        for child in match_up.contents:
            champNameHtml = child.find_all(class_=CHAMP_NAME_CLASS)
            champStatsHtml = child.find_all(class_=GD_CLASS)
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


alexPool = ["akali", "kassadin", "anivia", "ahri"]
trucPool = ["nunu", "drmundo", "nocturne"]

if __name__ == "__main__":
    main(alexPool)
