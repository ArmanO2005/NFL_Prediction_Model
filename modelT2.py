from ESPN_Scraper import *
import pandas as pd
from sklearn import linear_model

# This doesnt work yet, use T1

team1ScoreModel = linear_model.LinearRegression()
team2ScoreModel = linear_model.LinearRegression()

playerData = NFL_All_Player_Stats().fillna(0)
scores = NFL_Get_Scores()

teamSums = playerData.groupby('team').sum()

with open('defensiveStats.json', 'r') as file:
    defensiveStats = json.load(file)

with open('offensiveStats.json', 'r') as file:
    offensiveStats = json.load(file)

teamSumsDef = teamSums[defensiveStats]
teamSumsOff = teamSums[offensiveStats]
teamSumsOff.to_csv('teamSumsOff.csv')

teamSumsOff_reset = teamSumsOff.reset_index().rename(columns=lambda x: f"team1_{x}" if x != 'team' else 'team1_team')
teamSumsDef_reset = teamSumsDef.reset_index().rename(columns=lambda x: f"team1_{x}" if x != 'team' else 'team1_team')

train = scores.merge(teamSumsOff_reset, left_on='awayTeam', right_on='team1_team', how='left')
train = train.merge(teamSumsDef_reset, left_on='awayTeam', right_on='team1_team', how='left', suffixes=('_off', '_def'))

team2_off = teamSumsOff.reset_index().rename(columns=lambda x: f"team2_{x}" if x != 'team' else 'team2_team')
train = train.merge(team2_off, left_on='homeTeam', right_on='team2_team', how='left')

team2_def = teamSumsDef.reset_index().rename(columns=lambda x: f"team2_{x}" if x != 'team' else 'team2_team')
train = train.merge(team2_def, left_on='homeTeam', right_on='team2_team', how='left', suffixes=('_off', '_def'))

# for i in train.columns:
#     print(i)

train.fillna(0, inplace=True)

team1_off_features = [col for col in train.columns if col.startswith('team1_') and not col.endswith('_score')]
team2_def_features = [col for col in train.columns if col.startswith('team2_') and 'def' in col]
feature_team1 = team1_off_features + team2_def_features

team2_off_features = [col for col in train.columns if col.startswith('team2_') and not col.endswith('_score')]
team1_def_features = [col for col in train.columns if col.startswith('team1_') and 'def' in col]
feature_team2 = team2_off_features + team1_def_features

X1 = train[feature_team1].drop(['team1_team_off', 'team2_team_def', 'team1_team_def'], axis=1)
y1 = train['awayScore']

X2 = train[feature_team2].drop(['team2_team_off', 'team1_team_def', 'team2_team_def'], axis=1)
y2 = train['homeScore']

X1.to_csv('X1.csv', index=False)

team1ScoreModel.fit(X1, y1)
team2ScoreModel.fit(X2, y2)

def predictV2(team1, team2):
    teamSumsOff.to_csv('teamSumsOff.csv')
    teamSumsDef.to_csv('teamSumsDef.csv')
    team1Off = teamSumsOff.loc[team1].values
    team2Def = teamSumsDef.loc[team2].values

    team2Off = teamSumsOff.loc[team2].values
    team1Def = teamSumsDef.loc[team1].values

    team1_features = list(team1Off)[1:] + list(team2Def)[1:]
    team2_features = list(team2Off)[1:] + list(team1Def)[1:]

    team1_features = [team1_features]
    team2_features = [team2_features]

    predicted_team1_score = team1ScoreModel.predict(team1_features)[0]
    predicted_team2_score = team2ScoreModel.predict(team2_features)[0]

    return predicted_team1_score - predicted_team2_score

print(predictV2('Broncos', 'Bengals'))