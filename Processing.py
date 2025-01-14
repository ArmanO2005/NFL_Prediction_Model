from ESPN_Scraper import *
import pandas as pd
import numpy as np
import math
import json
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import seaborn as sns
import matplotlib.pyplot as plt


class NFL:
    def __init__(self, season):
        self.season = season
        self.off = NFL_Offensive(season)
        self.defen = NFL_Defensive(season)
        self.spec = NFL_SpecialTeams(season)
        self.turn = NFL_Turnovers(season)
        self.powerIndex = NFL_Power_Index(season).fillna(0)
        self.efficiency = NFL_Efficiencies(season)

        

    # positive value means team1 is better, negative means team2 is better
    def processing(self, team1, team2):
        if len(team1.split()) > 1 or len(team2.split()) > 1:
            with open('teamNames.json', 'r') as file:
                teamNames = json.load(file)

            shortLongNames = {}
            for i in teamNames:
                shortLongNames.update({i : i.split()[-1]})
        
        if len(team1.split()) > 1:
            team1 = shortLongNames[team1]
        if len(team2.split()) > 1:
            team2 = shortLongNames[team2]
        if team1 == 'Redskins':
            team1 = 'Commanders'
        if team2 == 'Redskins':
            team2 = 'Commanders'

        team1Off = self.off[self.off['displayName'] == team1]
        team2Off = self.off[self.off['displayName'] == team2]

        team1Def = self.defen[self.defen['displayName'] == team1]
        team2Def = self.defen[self.defen['displayName'] == team2]

        team1points = (float(team1Off['totalPointsPerGame'].iloc[0]) + float(team2Def['totalPointsPerGame'].iloc[0])) / 2
        team2points = (float(team2Off['totalPointsPerGame'].iloc[0]) + float(team1Def['totalPointsPerGame'].iloc[0])) / 2

        pointDiff = team1points - team2points

    # Turnover rating
        team1TO = self.turn[self.turn['displayName'] == team1]
        team2TO = self.turn[self.turn['displayName'] == team2]

        NFLAvgGivenTO = self.turn['totalGiveaways'].astype(float).mean()
        NFLAvgTakenTO = self.turn['totalTakeaways'].astype(float).mean()

        team1AvgGivenTO = float(team1TO['totalGiveaways'].iloc[0])
        team2AvgGivenTO = float(team2TO['totalGiveaways'].iloc[0])

        team1AvgForcedTO = float(team1TO['totalTakeaways'].iloc[0])
        team2AvgForcedTO = float(team2TO['totalTakeaways'].iloc[0])

        team1ExpTO = NFLAvgGivenTO * (team1AvgGivenTO / NFLAvgGivenTO) * (team2AvgForcedTO / NFLAvgTakenTO)
        team2ExpTO = NFLAvgGivenTO * (team2AvgGivenTO / NFLAvgGivenTO) * (team1AvgForcedTO / NFLAvgTakenTO)

        team1TORating = 1 / (team1ExpTO / NFLAvgGivenTO)
        team2TORating = 1 / (team2ExpTO / NFLAvgGivenTO)

        TORatingDiff = team1TORating - team2TORating
    # Turnover rating

    # Rush rating
        NFLAvgRushYards = self.off['rushingYardsPerGame'].astype(float).mean()
        NFLAvgRushDefense = self.defen['rushingYardsPerGame'].astype(float).mean()

        team1RushYardsOff = float(team1Off['rushingYardsPerGame'].iloc[0])
        team2RushYardsOff = float(team2Off['rushingYardsPerGame'].iloc[0])

        team1RushYardsDef = float(team1Def['rushingYardsPerGame'].iloc[0])
        team2RushYardsDef = float(team2Def['rushingYardsPerGame'].iloc[0])

        team1RushMultiplier = (team1RushYardsOff / NFLAvgRushYards) * (team2RushYardsDef / NFLAvgRushDefense)
        team1AdjRush = (team1RushYardsOff / float(team1Off['netYardsPerGame'].iloc[0])) - 0.5
        team1AdjRushRating = team1RushMultiplier ** (-math.log10(-team1AdjRush + 0.50001))

        team2RushMultiplier = (team2RushYardsOff / NFLAvgRushYards) * (team1RushYardsDef / NFLAvgRushDefense)
        team2AdjRush = (team2RushYardsOff / float(team2Off['netYardsPerGame'].iloc[0])) - 0.5
        team2AdjRushRating = team2RushMultiplier ** (-math.log10(-team2AdjRush + 0.50001))

        RushMultDiff = team1RushMultiplier - team2RushMultiplier
        AdjRushDiff = team1AdjRushRating - team2AdjRushRating
    # Rush rating

    # Pass rating
        NFLAvgPassYards = self.off['netPassingYardsPerGame'].astype(float).mean()
        NFLAvgPassDefense = self.defen['netPassingYardsPerGame'].astype(float).mean()

        team1PassYardsOff = float(team1Off['netPassingYardsPerGame'].iloc[0])
        team2PassYardsOff = float(team2Off['netPassingYardsPerGame'].iloc[0])

        team1PassYardsDef = float(team1Def['netPassingYardsPerGame'].iloc[0])
        team2PassYardsDef = float(team2Def['netPassingYardsPerGame'].iloc[0])

        team1PassMultiplier = (team1PassYardsOff / NFLAvgPassYards) * (team2PassYardsDef / NFLAvgPassDefense)
        team1AdjPass = (team1PassYardsOff / float(team1Off['netPassingYardsPerGame'].iloc[0])) - 0.5
        team1AdjPassRating  = team1PassMultiplier ** (-math.log10(-team1AdjPass + 0.50001))

        team2PassMultiplier = (team2PassYardsOff / NFLAvgPassYards) * (team1PassYardsDef / NFLAvgPassDefense)
        team2AdjPass = (team2PassYardsOff / float(team2Off['netPassingYardsPerGame'].iloc[0])) - 0.5
        team2AdjPassRating  = team2PassMultiplier ** (-math.log10(-team2AdjPass + 0.50001))

        PassMultDiff = team1PassMultiplier - team2PassMultiplier
        AdjPassDiff = team1AdjPassRating - team2AdjPassRating
    # Pass rating

    # ESPN FPI / SOS
        team1PowerIndex = self.powerIndex[self.powerIndex['displayName'] == team1]
        team2PowerIndex = self.powerIndex[self.powerIndex['displayName'] == team2]

        FPI_diff = float(team1PowerIndex['fpi'].iloc[0]) - float(team2PowerIndex['fpi'].iloc[0])

        SOS_diff = float(team1PowerIndex['avgsosrank'].iloc[0]) - float(team2PowerIndex['avgsosrank'].iloc[0])

        AVGWP = float(team1PowerIndex['avgingamewprank'].iloc[0]) - float(team2PowerIndex['avgingamewprank'].iloc[0])
    # ESPN FPI / SOS

    # ESPN Efficiency
        team1Efficiency = self.efficiency[self.efficiency['displayName'] == team1]
        team2Efficiency = self.efficiency[self.efficiency['displayName'] == team2]

        totEfficiencyDiff = float(team1Efficiency['totefficiency'].iloc[0]) - float(team2Efficiency['totefficiency'].iloc[0])

        offEfficiencyDiff = float(team1Efficiency['offefficiency'].iloc[0]) - float(team2Efficiency['offefficiency'].iloc[0])

        defEfficiencyDiff = float(team1Efficiency['defefficiency'].iloc[0]) - float(team2Efficiency['defefficiency'].iloc[0])
    # ESPN Efficiency

        features = [team1points, team2points, pointDiff, team1TORating, 
                    TORatingDiff, team2TORating,  team1RushMultiplier, 
                    team2RushMultiplier, RushMultDiff, AdjRushDiff,
                    team1AdjRushRating, team2AdjRushRating, team1PassMultiplier, 
                    team2PassMultiplier, team1AdjPassRating, team2AdjPassRating,
                    PassMultDiff, AdjPassDiff,
                    FPI_diff, SOS_diff, AVGWP,
                    totEfficiencyDiff, offEfficiencyDiff, defEfficiencyDiff]
        return np.array(features)

featureNames = ['team1points', 'team2points', 'pointDiff', 'team1TORating', 
                'TORatingDiff', 'team2TORating', 'team1RushMultiplier', 
                'team2RushMultiplier', 'RushMultDiff', 'AdjRushDiff',
                'team1AdjRushRating', 'team2AdjRushRating', 'team1PassMultiplier', 
                'team2PassMultiplier', 'team1AdjPassRating', 'team2AdjPassRating', 
                'PassMultDiff', 'AdjPassDiff',
                'FPI_diff', 'SOS_diff', 'AVGWP',
                'totEfficiencyDiff', 'offEfficiencyDiff', 'defEfficiencyDiff']

all_games_data = []
all_games_data_No_Outliers = [] 

for season in range(2014, 2025):
    NFL_Season = NFL(season)
    games = NFL_Get_Scores(season).fillna(0)

    for num, i in enumerate(featureNames):
        games[i] = games.apply(lambda x: NFL_Season.processing(x['awayTeam'], x['homeTeam'])[num], axis=1)
    games['spread'] = games['awayScore'].astype(int) - games['homeScore'].astype(int)

    all_games_data.append(games)

    games['spread_zscore'] = np.abs((games['spread'] - games['spread'].mean()) / games['spread'].std())
    games = games[games['spread_zscore'] <= 2.8]

    all_games_data_No_Outliers.append(games)

df_all_seasons = pd.concat(all_games_data, ignore_index=True)
df_all_seasons_No_Outliers = pd.concat(all_games_data_No_Outliers, ignore_index=True)



df_all_seasons.to_csv('DATA_all_seasons.csv', index=False)
df_all_seasons_No_Outliers.to_csv('DATA_all_seasons_No_Outliers.csv', index=False)



# corrFeatures = featureNames + ['spread']
# sns.heatmap(df_all_seasons[corrFeatures].corr(), annot=True)
# plt.show()


# X_train = df_all_seasons_No_Outliers[df_all_seasons_No_Outliers['season'] != 2024][featureNames]
# Y_train = df_all_seasons_No_Outliers.iloc[df_all_seasons_No_Outliers['season'] != 2024]['spread']
# X_test = df_all_seasons[df_all_seasons['season'] == 2024][featureNames]
# Y_test = df_all_seasons[df_all_seasons['season'] == 2024]['spread']


# modelR = linear_model.Ridge(alpha=0.3)
# modelR.fit(X_train, Y_train)
# print(mean_squared_error(Y_test, modelR.predict(X_test)))
# print(mean_absolute_error(Y_test, modelR.predict(X_test)))

# modelL = linear_model.Lasso(alpha=0.3)
# modelL.fit(X_train, Y_train)
# print(mean_squared_error(Y_test, modelL.predict(X_test)))
# print(mean_absolute_error(Y_test, modelL.predict(X_test)))

# model = linear_model.LinearRegression()
# model.fit(X_train, Y_train)
# print(mean_squared_error(Y_test, model.predict(X_test)))
# print(mean_absolute_error(Y_test, model.predict(X_test)))


# currSeason = NFL(2024)
# model = linear_model.Lasso(alpha=0.3)
# model.fit(df_all_seasons[featureNames], df_all_seasons['spread'])
# thisWeek = NFL_Get_Games(18)
# thisWeek['predictions'] = thisWeek.apply(lambda x : model.predict(currSeason.processing(x['awayTeam'], x['homeTeam']).reshape(1, -1)), axis=1)
# thisWeek.to_csv('thisWeek.csv', index=False)
