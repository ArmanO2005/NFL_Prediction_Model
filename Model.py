import pandas as pd
import numpy as np
import math
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error

featureNames = ['team1points', 'team2points', 'pointDiff', 'team1TORating', 
                'TORatingDiff', 'team2TORating', 'team1RushMultiplier', 
                'team2RushMultiplier', 'RushMultDiff', 'AdjRushDiff',
                'team1AdjRushRating', 'team2AdjRushRating', 'team1PassMultiplier', 
                'team2PassMultiplier', 'team1AdjPassRating', 'team2AdjPassRating', 
                'PassMultDiff', 'AdjPassDiff',
                'FPI_diff', 'SOS_diff', 'AVGWP',
                'totEfficiencyDiff', 'offEfficiencyDiff', 'defEfficiencyDiff']

df_all_seasons = pd.read_csv('DATA_all_seasons.csv')
df_all_seasons_No_Outliers = pd.read_csv('DATA_all_seasons_no_outliers.csv')


print(df_all_seasons_No_Outliers[df_all_seasons['season'] == 2024].head())

# print((df_all_seasons['team2points'] - df_all_seasons['team1points']).corr(df_all_seasons['spread']))
# plt.scatter(df_all_seasons['team2points'] - df_all_seasons['team1points'], df_all_seasons['spread'], alpha=0.5)
# plt.show()

# corrFeatures = featureNames + ['spread']
# sns.heatmap(df_all_seasons[corrFeatures].corr(), annot=True)
# plt.show()


# X_train = df_all_seasons_No_Outliers[df_all_seasons_No_Outliers['season'] != 2024][featureNames]
# Y_train = df_all_seasons_No_Outliers[df_all_seasons_No_Outliers['season'] != 2024]['spread']
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