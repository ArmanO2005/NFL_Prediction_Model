from ESPN_Scraper import *
import pandas as pd
import numpy as np
import math
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error



off = NFL_Offensive()
defen = NFL_Defensive()
spec = NFL_SpecialTeams()
turn = NFL_Turnovers()

# positive value means team1 is better, negative means team2 is better
def processing(team1, team2):
    if len(team1.split()) == 1 or len(team2.split()) == 1:
        with open('teamNames.json', 'r') as file:
            teamNames = json.load(file)

        shortLongNames = {}
        for i in teamNames:
            shortLongNames.update({i.split()[-1] : i})
    
    if len(team1.split()) == 1:
        team1 = shortLongNames[team1]
    if len(team2.split()) == 1:
        team2 = shortLongNames[team2]

    team1Off = off[off['displayName'] == team1]
    team2Off = off[off['displayName'] == team2]

    team1Def = defen[defen['displayName'] == team1]
    team2Def = defen[defen['displayName'] == team2]

    team1points = (team1Off['totalPointsPerGame'].astype(float).iloc[0] + team2Def['totalPointsPerGame'].astype(float).iloc[0]) / 2
    team2points = (team2Off['totalPointsPerGame'].astype(float).iloc[0] + team1Def['totalPointsPerGame'].astype(float).iloc[0]) / 2


# Turnover rating
    team1TO = turn[turn['displayName'] == team1]
    team2TO = turn[turn['displayName'] == team2]

    NFLAvgGivenTO = turn['totalGiveaways'].astype(float).mean()
    NFLAvgTakenTO = turn['totalTakeaways'].astype(float).mean()

    team1AvgGivenTO = team1TO['totalGiveaways'].astype(float).iloc[0]
    team2AvgGivenTO = team2TO['totalGiveaways'].astype(float).iloc[0]

    team1AvgForcedTO = team1TO['totalTakeaways'].astype(float).iloc[0]
    team2AvgForcedTO = team2TO['totalTakeaways'].astype(float).iloc[0]

    team1ExpTO = NFLAvgGivenTO * (team1AvgGivenTO / NFLAvgGivenTO) * (team2AvgForcedTO / NFLAvgTakenTO)
    team2ExpTO = NFLAvgGivenTO * (team2AvgGivenTO / NFLAvgGivenTO) * (team1AvgForcedTO / NFLAvgTakenTO)

    team1TORating = 1 / (team1ExpTO / NFLAvgGivenTO)
    team2TORating = 1 / (team2ExpTO / NFLAvgGivenTO)

    # team1TORating = 1.1 ** (1 / (team1ExpTO / NFLAvgGivenTO) - 0.5)
    # team2TORating = 1.1 ** (1 / (team2ExpTO / NFLAvgGivenTO) - 0.5)
# Turnover rating

# Rush rating
    NFLAvgRushYards = off['rushingYardsPerGame'].astype(float).mean()
    NFLAvgRushDefense = defen['rushingYardsPerGame'].astype(float).mean()

    team1RushYardsOff = team1Off['rushingYardsPerGame'].astype(float).iloc[0]
    team2RushYardsOff = team2Off['rushingYardsPerGame'].astype(float).iloc[0]

    team1RushYardsDef = team1Def['rushingYardsPerGame'].astype(float).iloc[0]
    team2RushYardsDef = team2Def['rushingYardsPerGame'].astype(float).iloc[0]

    team1RushMultiplier = (team1RushYardsOff / NFLAvgRushYards) * (team2RushYardsDef / NFLAvgRushDefense)
    team1AdjRush = (team1RushYardsOff / team1Off['netYardsPerGame'].astype(float).iloc[0]) - 0.5
    team1AdjRushRating = team1RushMultiplier ** (-math.log10(-team1AdjRush + 0.50001))

    team2RushMultiplier = (team2RushYardsOff / NFLAvgRushYards) * (team1RushYardsDef / NFLAvgRushDefense)
    team2AdjRush = (team2RushYardsOff / team2Off['netYardsPerGame'].astype(float).iloc[0]) - 0.5
    team2AdjRushRating = team2RushMultiplier ** (-math.log10(-team2AdjRush + 0.50001))
# Rush rating

# Pass rating
    NFLAvgPassYards = off['netPassingYardsPerGame'].astype(float).mean()
    NFLAvgPassDefense = defen['netPassingYardsPerGame'].astype(float).mean()

    team1PassYardsOff = team1Off['netPassingYardsPerGame'].astype(float).iloc[0]
    team2PassYardsOff = team2Off['netPassingYardsPerGame'].astype(float).iloc[0]

    team1PassYardsDef = team1Def['netPassingYardsPerGame'].astype(float).iloc[0]
    team2PassYardsDef = team2Def['netPassingYardsPerGame'].astype(float).iloc[0]

    team1PassMultiplier = (team1PassYardsOff / NFLAvgPassYards) * (team2PassYardsDef / NFLAvgPassDefense)
    team1AdjPass = (team1PassYardsOff / team1Off['netPassingYardsPerGame'].astype(float).iloc[0]) - 0.5
    team1AdjPassRating  = team1PassMultiplier ** (-math.log10(-team1AdjPass + 0.50001))

    team2PassMultiplier = (team2PassYardsOff / NFLAvgPassYards) * (team1PassYardsDef / NFLAvgPassDefense)
    team2AdjPass = (team2PassYardsOff / team2Off['netPassingYardsPerGame'].astype(float).iloc[0]) - 0.5
    team2AdjPassRating  = team2PassMultiplier ** (-math.log10(-team2AdjPass + 0.50001))
# Pass rating

    features = [team1points, team2points, team1TORating, team2TORating, team1RushMultiplier, team2RushMultiplier, team1AdjRushRating, team2AdjRushRating, team1PassMultiplier, team2PassMultiplier, team1AdjPassRating, team2AdjPassRating]
    return np.array(features)

featureNames = ['team1points', 'team2points', 'team1TORating', 'team2TORating', 'team1RushMultiplier', 'team2RushMultiplier', 'team1AdjRushRating', 'team2AdjRushRating', 'team1PassMultiplier', 'team2PassMultiplier', 'team1AdjPassRating', 'team2AdjPassRating']

games = NFL_Get_Scores().fillna(0)
for num, i in enumerate(featureNames):
    games[i] = games.apply(lambda x: processing(x['awayTeam'], x['homeTeam'])[num], axis=1)
games['spread'] = games['awayScore'].astype(int) - games['homeScore'].astype(int)
games.to_csv('games.csv', index=False)


# X_train, X_test, Y_train, Y_test = train_test_split(games[featureNames], games['spread'], test_size=0.2)
# model = linear_model.Ridge(alpha=0.3)
# model.fit(X_train, Y_train)
# print(mean_squared_error(Y_test, model.predict(X_test)))

model = linear_model.Ridge(alpha=0.3)
model.fit(games[featureNames], games['spread'])
print(model.predict(processing('Lions', '49ers').reshape(1, -1)))
