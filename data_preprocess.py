import pandas as pd


def transform_value(x):
    transformed = ''
    for ch in x:
        if ch == '.' or ch.isdigit():
            transformed = transformed + ch

    value = float(transformed)
    value = value*1000 if x[-1] == 'K' else value*1000000
    return value


def transform_attribute(x):
    if isinstance(x, int):
        return x
    transformed = ''
    for ch in x:
        if ch == '+' or ch == '-':
            return int(transformed)
        else:
            transformed = transformed + ch
    return int(transformed)


def checkZero(x):
    if type(x) == type(0):
        return []
    return x.split()


def checkType(x):
    if type(x) == type(0) or x == "nan":
        return "0"
    return x


def read_data2():
    dat21 = pd.read_csv("data/FIFA21_official_data.csv", delimiter=',')
    # dat21.fillna(value=0, axis=0, inplace=True)
    dat20 = pd.read_csv("data/fifa20Player.csv", delimiter=',')
    # dat20.fillna(value=0, axis=0, inplace=True)
    dat20 = dat20[['sofifa_id', 'player_positions', 'ls', 'st', 'rs', 'lw', 'lf', 'cf', 'rf', 'rw', 'lam', 'cam',
                   'ram', 'lm', 'lcm', 'cm', 'rcm', 'rm', 'lwb', 'ldm', 'cdm', 'rdm', 'rwb', 'lb', 'lcb', 'cb', 'rcb', 'rb']]
    # print(dat20)
    df_tran_prod = pd.merge(left=dat21, right=dat20,
                            left_on=['ID'],
                            right_on=['sofifa_id'],
                            how='left')
    # print(df_tran_prod)
    df_tran_prod.rename(columns={'ls': 'LS', 'st': 'ST', 'rs': 'RS', 'lw': 'LW', 'lf': 'LF', 'cf': 'CF', 'rf': 'RF', 'rw': 'RW', 'lam': 'LAM',
                                 'cam': 'CAM', 'ram': 'RAM', 'lm': 'LM', 'lcm': 'LCM', 'cm': 'CM', 'rcm': 'RCM', 'rm': 'RM', 'lwb': 'LWB', 'ldm': 'LDM', 'cdm': 'CDM', 'rdm': 'RDM',
                                 'rwb': 'RWB', 'lb': 'LB', 'lcb': 'LCB', 'cb': 'CB', 'rcb': 'RCB', 'rb': 'RB'}, inplace=True)
    df_tran_prod.fillna(value=0, axis=0, inplace=True)
    # print(type(0))
    print(type(df_tran_prod['Work Rate'][0]))
    print(df_tran_prod['Work Rate'][0])
    df_tran_prod['Contract Valid Until'] = df_tran_prod['Contract Valid Until'].apply(
        lambda x: checkType(x))
    checkName = df_tran_prod['Contract Valid Until'] > "2019"
    df_tran_prod = df_tran_prod[checkName]
    df_tran_prod[df_tran_prod.columns[67:]] = df_tran_prod[df_tran_prod.columns[67:]].apply(
        lambda x: x.apply(lambda y: transform_attribute(y)))
    # df_tran_prod = df_tran_prod[df_tran_prod['player_positions'] == 0]
    # print(df_tran_prod.columns.get_loc("ls"))
    # print(df_tran_prod.columns.get_loc("rb"))
    # print(df_tran_prod)
    df_tran_prod['player_positions'] = df_tran_prod['player_positions'].apply(
        lambda x: checkZero(x))

    df_tran_prod['GK'] = df_tran_prod['Overall'] * \
        df_tran_prod['Best Position'].apply(lambda x: 1 if 'GK' in x else 0)

    df_tran_prod['Value'] = df_tran_prod['Value'].apply(
        lambda x: transform_value(x))
    df_tran_prod['Wage'] = df_tran_prod['Wage'].apply(
        lambda x: transform_value(x))
    return df_tran_prod
    # print(df_tran_prod.columns.get_loc("ls"))
    # print(df_tran_prod.columns.get_loc("rb"))


def read_data():
    dat = pd.read_csv("data/CompleteDataset.csv", delimiter=',')
    dat = dat.drop_duplicates(['Name', 'Age', 'Club'])
    dat.fillna(value=0, axis=0, inplace=True)
    dat.drop(['Unnamed: 0', 'Photo', 'Flag', 'Club Logo',
              'Special', 'ID'], axis=1, inplace=True)
    dat['Preferred Positions'] = dat['Preferred Positions'].apply(
        lambda x: checkZero(x))
    # print(dat['Value'])
    dat['Value'] = dat['Value'].apply(lambda x: transform_value(x))
    # print(dat['Value'])
    dat['Wage'] = dat['Wage'].apply(lambda x: transform_value(x))
    dat['GK'] = dat['Overall'] * \
        dat['Preferred Positions'].apply(lambda x: 1 if 'GK' in x else 0)
    dat[dat.columns[8:42]] = dat[dat.columns[8:42]].apply(
        lambda x: x.apply(lambda y: transform_attribute(y)))
    # print(dat)
    return dat


def formations():
    formation_dict = {
        '433': ['GK', 'LB', 'CB', 'CB', 'RB', 'CDM', 'CDM', 'CM', 'LM', 'RM', 'ST'],
        '442': ['GK', 'LB', 'CB', 'CB', 'RB', 'CM', 'RM', 'LM', 'CM', 'ST', 'ST'],
        '352': ['GK', 'CB', 'CB', 'CB', 'CDM', 'CM', 'RWB', 'LWB', 'CM', 'CF', 'ST']
    }
    return formation_dict


def group_by_team(dat):
    # print(dat)
    grouped_data = dat.groupby('Club')
    # print(grouped_data)
    return grouped_data
