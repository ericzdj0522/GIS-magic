import pandas as pd
from scipy.spatial import distance_matrix

def dm_station():
    df_csv = pd.read_csv('/Users/dj/Documents/QGIS/CSV/Prod/JPN_stations_DM.csv')

    dm_result = pd.DataFrame(distance_matrix(df_csv[['x', 'y']].values, df_csv[['x', 'y']].values), index=df_csv['station'], columns=df_csv['station'])
    print(dm_result)
    dm_result.to_csv('/Users/dj/Documents/QGIS/CSV/Prod/JPN_stations_DM_result.csv', index=True)


    #s = dm_result['JPAK00JPN']
    #s_sorted = s.sort_values(ascending=True)
    #s_index = s_sorted[1:4].index.to_series(index=[0, 1, 2])

    #Empty list to store all series
    slist = []
    for index in dm_result.index:
        s = dm_result[index]
        s_sorted = s.sort_values(ascending=True)
        s_index = s_sorted[1:4].index.to_series(index=[0, 1, 2])
        #Assign series name with index
        s_index.name = index
        print(s_index)
        slist.append(s_index)

    final_df = pd.DataFrame(slist)
    final_df.to_csv('/Users/dj/Documents/QGIS/CSV/Prod/JPN_stations_final_result.csv', index=True)

def k_neareast_stations(index):
    print('test')


if __name__ == '__main__':
    dm_station()