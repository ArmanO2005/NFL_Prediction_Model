from ESPN_Scraper import *
import pandas as pd
from sklearn import linear_model



#positive value means team1 is better, negative means team2 is better
# def predictV1(team1, team2):
#     off = NFL_Offensive()
#     defen = NFL_Defensive()
#     spec = NFL_SpecialTeams()
#     turn = NFL_Turnovers()

#     team1Off = off[off['displayName'] == team1]
#     team2Off = off[off['displayName'] == team2]

#     team1Def = defen[defen['displayName'] == team1]
#     team2Def = defen[defen['displayName'] == team2]

#     team1TO = turn[turn['displayName'] == team1]
#     team2TO = turn[turn['displayName'] == team2]

#     team1points = (team1Off['totalPointsPerGame'].astype(float).iloc[0] + team2Def['totalPointsPerGame'].astype(float).iloc[0]) / 2
#     team2points = (team2Off['totalPointsPerGame'].astype(float).iloc[0] + team1Def['totalPointsPerGame'].astype(float).iloc[0]) / 2

#     NFLAvgGivenTO = turn['totalGiveaways'].astype(float).mean()
#     NFLAvgTakenTO = turn['totalTakeaways'].astype(float).mean()
#     team1AvgGivenTO = team1TO['totalGiveaways'].astype(float).iloc[0]
#     team2AvgGivenTO = team2TO['totalGiveaways'].astype(float).iloc[0]

#     team1AvgForcedTO = team1TO['totalTakeaways'].astype(float).iloc[0]
#     team2AvgForcedTO = team2TO['totalTakeaways'].astype(float).iloc[0]

#     team1ExpTO = NFLAvgGivenTO * (team1AvgGivenTO / NFLAvgGivenTO) * (team2AvgForcedTO / NFLAvgTakenTO)
#     team2ExpTO = NFLAvgGivenTO * (team2AvgGivenTO / NFLAvgGivenTO) * (team1AvgForcedTO / NFLAvgTakenTO)

#     team1TORating = 1 / (team1ExpTO / NFLAvgGivenTO)
#     team2TORating = 1 / (team2ExpTO / NFLAvgGivenTO)

#     return (team1points * team1TORating) - (team2points * team2TORating)


offensivePos = ['QB', 'RB', 'WR', 'TE', 'C', 'FB', 'G', 'OT']
defensivePos = ['CB', 'S', 'LB', 'DE', 'DT']

team1Score = linear_model.Lasso(alpha=0.1)
team2Score = linear_model.Lasso(alpha=0.1)

playerData = NFL_All_Player_Stats().fillna(0)
scores = NFL_Get_Scores()

teamSums = playerData.groupby('team').sum()

with open('defensiveStats.json', 'r') as file:
    defensiveStats = json.load(file)

with open('offensiveStats.json', 'r') as file:
    offensiveStats = json.load(file)

teamSumsDef = teamSums[defensiveStats]
teamSumsOff = teamSums[offensiveStats]

teamSumsOff_reset = teamSumsOff.reset_index().rename(columns=lambda x: f"team1_{x}" if x != 'team' else 'team1_team')
teamSumsDef_reset = teamSumsDef.reset_index().rename(columns=lambda x: f"team1_{x}" if x != 'team' else 'team1_team')

train = scores.merge(teamSumsOff_reset, left_on='awayTeam', right_on='team1_team', how='left')
train = train.merge(teamSumsDef_reset, left_on='awayTeam', right_on='team1_team', how='left', suffixes=('_off', '_def'))

team2_off = teamSumsOff.reset_index().rename(columns=lambda x: f"team2_{x}" if x != 'team' else 'team2_team')
train = train.merge(team2_off, left_on='homeTeam', right_on='team2_team', how='left')

team2_def = teamSumsDef.reset_index().rename(columns=lambda x: f"team2_{x}" if x != 'team' else 'team2_team')
train = train.merge(team2_def, left_on='homeTeam', right_on='team2_team', how='left', suffixes=('_off', '_def'))

train.drop(['team1_team', 'team2_team'], axis=1, inplace=True)

train.fillna(0, inplace=True)

team1_off_features = [col for col in train.columns if col.startswith('team1_') and col != 'team1_score']
team2_def_features = [col for col in train.columns if col.startswith('team2_') and 'def' in col]
feature_team1 = team1_off_features + team2_def_features

X1 = train[feature_team1]
y1 = train['team1_score']

team2_off_features = [col for col in train.columns if col.startswith('team2_') and col != 'team2_score']
team1_def_features = [col for col in train.columns if col.startswith('team1_') and 'def' in col]
feature_team2 = team2_off_features + team1_def_features

X2 = train[feature_team2]
y2 = train['team2_score']

team1Score.fit(X1, y1)
team2Score.fit(X2, y2)

def predictV2(team1, team2):
    team1Off = teamSumsOff.loc[team1].values
    team1Def = teamSumsDef.loc[team1].values

    team2Off = teamSumsOff.loc[team2].values
    team2Def = teamSumsDef.loc[team2].values

    team1Score = team1Score.predict([team1Off + team2Def])
    team2Score = team2Score.predict([team2Off + team1Def])

    return team1Score - team2Score


print(predictV2('Denver Broncos', 'Cincinnati Bengals'))





