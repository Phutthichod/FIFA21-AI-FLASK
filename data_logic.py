from data_preprocess import formations
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import minkowski

PLAYER_AGE_PENALTY = 0.05
OLD_PLAYER_MARGIN = 35
YOUNG_PLAYER_MARGIN = 25

SIMILAR_CENTRAL_POSITIONS = ['CB', 'CDM', 'CM', 'CAM', 'CF', 'ST']
SIMILAR_SIDE_POSITIONS = ['LB', 'RB', 'LWB', 'RWB', 'LM', 'RM', 'LW', 'RW']

TEAM_ATTRIBUTES = ['Age', 'Aggression', 'BallControl', 'Composure', 'Positioning',
                   'Reactions', 'ShortPassing', 'SprintSpeed', 'Stamina', 'Strength']


def get_similar_positions(spot):
    similar_positions = []
    if spot in SIMILAR_CENTRAL_POSITIONS:
        spot_index = SIMILAR_CENTRAL_POSITIONS.index(spot)
        if spot_index-1 > 0:
            similar_positions.append(SIMILAR_CENTRAL_POSITIONS[spot_index-1])
        if spot_index+1 < len(SIMILAR_CENTRAL_POSITIONS):
            similar_positions.append(SIMILAR_CENTRAL_POSITIONS[spot_index+1])
    elif spot in SIMILAR_SIDE_POSITIONS:
        spot_index = SIMILAR_SIDE_POSITIONS.index(spot)
        if spot_index-2 > 0:
            similar_positions.append(SIMILAR_SIDE_POSITIONS[spot_index-2])
        if spot_index+2 < len(SIMILAR_SIDE_POSITIONS):
            similar_positions.append(SIMILAR_SIDE_POSITIONS[spot_index+2])
    return similar_positions


def first_team(formation, team_data):
    # print(team_data)
    form_list = formations()[formation]
    first_eleven = pd.DataFrame()
    for spot in form_list:
        limited_data = team_data.loc[team_data['player_positions'].apply(
            lambda x: spot in x)]
        print(limited_data[['Name', spot]], spot)
        print(team_data[['Name', 'player_positions']])
        # limited_data = pd.DataFrame()
        if len(limited_data) == 0:
            positions = get_similar_positions(spot)
            for pos in positions:
                limited_data = limited_data.append(
                    team_data.loc[team_data['player_positions'].apply(lambda x: pos in x)])
        if len(limited_data) == 0:
            limited_data = team_data
        limited_data['true_overall'] = np.where(limited_data['Age'] < YOUNG_PLAYER_MARGIN,
                                                (limited_data['Potential'] +
                                                 limited_data['Overall'])/2,
                                                limited_data['Overall'],)
        limited_data['top_position'] = (
            limited_data['true_overall']*3+limited_data[spot]*2)
        player = limited_data['top_position'].idxmax()
        player_pd = limited_data.loc[[player]]
        player_pd['NewPosition'] = spot
        first_eleven = first_eleven.append(player_pd)
        team_data.drop([player], axis=0, inplace=True)
    return first_eleven


def filtering_our_constraints(worst_player, position, dat):
    print(position)
    limited_data = dat.loc[dat['player_positions'].apply(
        lambda x: position in x)]
    limited_data = limited_data[limited_data.Club != worst_player['Club']]
    limited_data = limited_data[(limited_data[position] >= worst_player[position]+1)
                                | ((limited_data['Age'] <= 23)
                                   & (limited_data['Potential'] >= worst_player['Potential']+2))]
    limited_data = limited_data[limited_data['Wage'] < 2*worst_player['Wage']]
    # print(limited_data[['Name', 'Age', 'Overall', 'Potential', position]])
    filtered_constraints = limited_data
    # print('filtered_constraints')
    # print(filtered_constraints)
    # print('end filtered_constraints')
    return filtered_constraints


def filtering_user_constraints(dat, cons_json):
    limited_data = dat
    print(cons_json)
    if int(cons_json['min_price']) != -1:
        limited_data = limited_data[(
            limited_data['Value'] >= int(cons_json['min_price']))]
    if int(cons_json['max_price']) != -1:
        limited_data = limited_data[(
            limited_data['Value'] <= int(cons_json['max_price']))]

    if int(cons_json['min_age']) != -1:
        limited_data = limited_data[(
            limited_data['Age'] >= int(cons_json['min_age']))]
    if int(cons_json['max_age']) != -1:
        limited_data = limited_data[(
            limited_data['Age'] <= int(cons_json['max_age']))]

    if int(cons_json['min_wage']) != -1:
        limited_data = limited_data[(
            limited_data['Wage'] >= int(cons_json['min_wage']))]
    if int(cons_json['max_wage']) != -1:
        limited_data = limited_data[(
            limited_data['Wage'] <= int(cons_json['max_wage']))]

    if int(cons_json['min_overall']) != -1:
        limited_data = limited_data[(
            limited_data['Overall'] >= int(cons_json['min_overall']))]
    if int(cons_json['max_overall']) != -1:
        limited_data = limited_data[(
            limited_data['Overall'] <= int(cons_json['max_overall']))]

    return limited_data


def sort_first_eleven(players):
    players['true_overall'] = np.where(players['Age'] < YOUNG_PLAYER_MARGIN,
                                       (players['Potential'] +
                                        players['Overall'])/2,
                                       players['Overall'])
    players['diff'] = players['true_overall'] - players['true_overall'].mean()
    avg_wage = players['Wage'].mean()

    players['wage_diff'] = (players['Wage'] - avg_wage) / \
        (players['Wage'].max() - players['Wage'].min())
    players['diff'] = np.where((players['diff'] > 0) & (players['Age'] > YOUNG_PLAYER_MARGIN),
                               players['diff'] * (1 - (players['Age'] -
                                                       YOUNG_PLAYER_MARGIN) * PLAYER_AGE_PENALTY),
                               players['diff'])

    players['diff'] = np.where((players['diff'] < 0) & (players['Age'] > YOUNG_PLAYER_MARGIN),
                               players['diff'] * (0.5 + (players['Age'] -
                                                         YOUNG_PLAYER_MARGIN) * PLAYER_AGE_PENALTY),
                               players['diff'])

    players['diff'] = np.where((players['diff'] < 0) & (players['Age'] > YOUNG_PLAYER_MARGIN),
                               players['diff'] * (0.5 + (players['Age'] -
                                                         YOUNG_PLAYER_MARGIN) * PLAYER_AGE_PENALTY),
                               players['diff'])

    players['diff'] = (players['diff'] - players['diff'].mean()) / \
        (players['diff'].max() - players['diff'].min())
    # print(players.sort_values('diff')[['diff', 'Name', 'wage_diff']])
    players['diff'] = 0.7*players['diff'] + 0.3*(-1 * players['wage_diff'])
    # print(players.sort_values('diff')[['diff', 'Name', 'wage_diff']])
    # print(players.sort_values('diff'))
    print(players['diff'])
    print(players.sort_values('diff'))
    return players.sort_values('diff')


def first_eleven_stats(first_eleven):
    field_players = first_eleven[first_eleven['GK'] == 0]
    avg_stats = field_players[TEAM_ATTRIBUTES].mean()
    sd_stats = field_players[TEAM_ATTRIBUTES].std()
    # print(avg_stats)
    return (avg_stats, sd_stats)


def find_similar_to_team(team_stats, filtered_list, similarity='pearson'):
    avg_stats = team_stats[0]
    sd_stats = team_stats[1]
    avg_stats['Age'] = 21

    sd_stats = 1/sd_stats
    sd_stats = sd_stats / sd_stats.sum()

    avg_stats = avg_stats.values.reshape(-1, len(avg_stats))
    # print(filtered_list)
    fil_list = filtered_list[TEAM_ATTRIBUTES]
    # print(fil_list)
    # print(fil_list)
    fil_list = fil_list.mul(sd_stats, axis=1)
    # print(fil_list)

    avg_series = pd.Series(avg_stats.flatten(), index=fil_list.columns)

    if similarity == 'pearson':
        pearson_sim = fil_list.corrwith(avg_series, axis=1)
        filtered_list['pearson'] = pearson_sim
        return filtered_list.sort_values(['pearson'], ascending=False)

    if similarity == 'cosine':
        cos_sim = cosine_similarity(fil_list, avg_stats)
        filtered_list['cosine'] = pd.Series(
            [x for row in cos_sim for x in row], index=filtered_list.index)
        return filtered_list.sort_values(['cosine'], ascending=False)

    if similarity == 'minkowski':
        minkowski_sim = []
        for index, row in fil_list.iterrows():
            minkowski_sim.append(
                minkowski(row.values, avg_stats.flatten(), p=2))

        filtered_list['minkowski'] = pd.Series(
            minkowski_sim, index=filtered_list.index)
        return filtered_list.sort_values(['minkowski'], ascending=False)
