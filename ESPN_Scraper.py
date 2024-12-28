import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/108.0.0.0 Safari/537.36")
}

def NFL_Get_Scores(season=2024):
    titles = ['awayTeam', 'homeTeam', 'awayScore', 'homeScore']

    scores = []
    w = 1

    rows = []
    while True:
        url = (f"https://www.espn.com/nfl/scoreboard/_/week/{w}/year/{season}/seasontype/2")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(response.status_code)
            break

        soup = BeautifulSoup(response.text, "html.parser")
        html = soup.prettify()

        if html.count("No games on this date.") > 1:
            break

        scores = re.findall(r'<div class="ScoreCell__Score h4 clr-gray-01 fw-heavy tar ScoreCell_Score--scoreboard pl2">(.*?)<\/div>', html, flags=re.DOTALL)
        names = re.findall(r'<div class="ScoreCell__TeamName ScoreCell__TeamName--shortDisplayName db">(.*?)<\/div>', html, flags=re.DOTALL)

        for i in range(int(len(scores)/2)):
            row = []
            row.append(names[i * 2])
            row.append(names[i * 2 + 1])
            row.append(scores[i * 2])
            row.append(scores[i * 2 + 1])

            for i in range(len(row)):
                row[i] = row[i].strip()
            
            rows.append(row)

        
        w += 1

    return pd.DataFrame(rows, columns=titles)


def NFL_All_Player_Stats():
    url = (f"https://site.web.api.espn.com/apis/common/v3/sports/football/nfl/statistics/byathlete?region=us&lang=en&contentorigin=espn&isqualified=false&page=0&limit=10")
    total = requests.get(url, headers=headers)

    if total.status_code != 200:
        print(total.status_code)

    soupTotal = BeautifulSoup(total.text, "html.parser")
    statsTotal = json.loads(soupTotal.prettify())

    rowTitles = ['name', 'team', 'position']
    for i in statsTotal['categories']:
        rowTitles += i['names']

    check = set()
    rows = []
    p = 0
    while True:
        url = (f"https://site.web.api.espn.com/apis/common/v3/sports/football/nfl/statistics/byathlete?region=us&lang=en&contentorigin=espn&isqualified=false&page={p}&limit=1000")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(response.status_code)
            break

        soup = BeautifulSoup(response.text, "html.parser")
        stats = json.loads(soup.prettify())
        
        if "athletes" in stats:
            for i in stats["athletes"]:

                displayName = i["athlete"]["displayName"]
                if displayName in check:
                    continue

                row = []
                check.add(displayName)
                row.append(displayName)
                row.append(i["athlete"]["teamName"])
                row.append(i["athlete"]["position"]["abbreviation"])
                for j in i["categories"]:
                    row += j["values"]
                rows.append(row)
        else:
            break

        p += 1

    return pd.DataFrame(rows, columns=rowTitles)


def NFL_Offensive():
    url = "https://www.espn.com/nfl/stats/team"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(response.status_code)

    soup = BeautifulSoup(response.text, "html.parser")

    stats = re.search(r'("teamStats":\[.*?\]),"dictionary"', soup.prettify())
    stats = json.loads('{' + stats[1] + '}')

    rowTitles = ['displayName']
    for j in stats['teamStats'][0]['stats']:
        rowTitles.append(j['name'])

    rows = []
    for num, i in enumerate(stats['teamStats']):
        row = []
        row.append(i['team']['displayName'])
        for j in i['stats']:
            row.append(j['value'])
        rows.append(row)

    return pd.DataFrame(rows, columns=rowTitles)


def NFL_Defensive():
    url = "https://www.espn.com/nfl/stats/team/_/view/defense"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(response.status_code)

    soup = BeautifulSoup(response.text, "html.parser")

    stats = re.search(r'("teamStats":\[.*?\]),"dictionary"', soup.prettify())
    stats = json.loads('{' + stats[1] + '}')

    rowTitles = ['displayName']
    for j in stats['teamStats'][0]['stats']:
        rowTitles.append(j['name'])

    rows = []
    for num, i in enumerate(stats['teamStats']):
        row = []
        row.append(i['team']['displayName'])
        for j in i['stats']:
            row.append(j['value'])
        rows.append(row)

    return pd.DataFrame(rows, columns=rowTitles)


def NFL_SpecialTeams():
    url = "https://www.espn.com/nfl/stats/team/_/view/special"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(response.status_code)

    soup = BeautifulSoup(response.text, "html.parser")

    stats = re.search(r'("teamStats":\[.*?\]),"dictionary"', soup.prettify())
    stats = json.loads('{' + stats[1] + '}')

    rowTitles = ['displayName']
    for j in stats['teamStats'][0]['stats']:
        rowTitles.append(j['name'])

    rows = []
    for num, i in enumerate(stats['teamStats']):
        row = []
        row.append(i['team']['displayName'])
        for j in i['stats']:
            row.append(j['value'])
        rows.append(row)

    return pd.DataFrame(rows, columns=rowTitles)


def NFL_Turnovers():
    url = "https://www.espn.com/nfl/stats/team/_/view/turnovers"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(response.status_code)

    soup = BeautifulSoup(response.text, "html.parser")

    stats = re.search(r'("teamStats":\[.*?\]),"dictionary"', soup.prettify())
    stats = json.loads('{' + stats[1] + '}')

    rowTitles = ['displayName']
    for j in stats['teamStats'][0]['stats']:
        rowTitles.append(j['name'])

    rows = []
    for num, i in enumerate(stats['teamStats']):
        row = []
        row.append(i['team']['displayName'])
        for j in i['stats']:
            row.append(j['value'])
        rows.append(row)

    return pd.DataFrame(rows, columns=rowTitles)




with open("output.txt", 'w', encoding="utf-8") as f:
    for i in NFL_All_Player_Stats().columns:
        f.write(i + '\n')

