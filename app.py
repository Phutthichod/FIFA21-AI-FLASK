from flask import *
from flask_cors import CORS
import pandas as pd
from data_preprocess import read_data2, group_by_team
from data_logic import first_team, sort_first_eleven, first_eleven_stats, find_similar_to_team, \
    filtering_our_constraints, filtering_user_constraints
import os

app = Flask(__name__)
CORS(app)
app.config.update(
    DEBUG=True,
    TEMPLATES_AUTO_RELOAD=True
)
app.secret_key = os.urandom(24)

dat = read_data2()
team_data = group_by_team(dat)


@app.route('/club')
def club():
    return jsonify(list(team_data.groups))


@app.route('/constraints', methods=['POST'])
def constraints():
    constraints_json = json.dumps(request.json)
    print(constraints_json)
    # session['constraints'] = constraints_json
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/player/<club>')
def player(club):
    players = team_data.get_group(club)
    return json.dumps(json.loads(
        players[['ID', 'Weight', 'Height', 'Wage', 'Value', 'Name', 'Age', 'Overall', 'Potential', 'Nationality', 'player_positions', 'Photo']].reset_index().to_json(orient='records')), indent=2)


@app.route('/firstTeam/<club>/<form>', methods=['POST'])
def firstTeam(club, form):
    start_eleven = first_team(
        form, team_data.get_group(club))
    sorted_start_eleven = sort_first_eleven(start_eleven)
    fr_el_stats = first_eleven_stats(start_eleven)
    worst_player = sorted_start_eleven.iloc[0]
    filtered_recommends = filtering_our_constraints(
        worst_player, worst_player['NewPosition'], dat)
    filtered_recommends = filtering_user_constraints(
        filtered_recommends, request.json)
    # print(filtered_recommends)

    sorted_similar_per = find_similar_to_team(
        fr_el_stats, filtered_recommends, similarity='pearson')
    # print(worst_player)
    return jsonify({'firstPlayer': json.dumps(json.loads(
        start_eleven[['ID', 'Weight', 'Height', 'Wage', 'Value', 'Potential', 'Name', 'NewPosition', 'Age', 'Nationality', 'Overall']].reset_index().to_json(orient='records')), indent=2), 'worst_player': json.dumps(json.loads(
            worst_player[['ID', 'Weight', 'Height', 'Wage', 'Value', 'Potential', 'Name', 'NewPosition', 'Age', 'Nationality', 'Overall']].reset_index().to_json(orient='records')), indent=2),
        'pearson': json.dumps(json.loads(
            sorted_similar_per.head(5)[['ID', 'Weight', 'Height', 'Wage', 'Value', 'Potential', 'Best Position', 'Name', 'Age', 'Nationality', 'Overall']].reset_index().to_json(orient='records')), indent=2)})


@ app.route('/findPlayer/<playerId>')
def findPlayer(playerId):
    player = dat[dat['ID'] == int(playerId)]
    print(player)
    return json.dumps(json.loads(
        player.reset_index().to_json(orient='records')), indent=2)


@ app.route('/pearson/<club>')
def recommender(club):
    start_eleven = first_team(
        '433', team_data.get_group(club))
    sorted_start_eleven = sort_first_eleven(start_eleven)
    fr_el_stats = first_eleven_stats(start_eleven)
    worst_player = sorted_start_eleven.iloc[0]
    print(worst_player)
    # print(dat['player_positions'])
    filtered_recommends = filtering_our_constraints(
        worst_player, worst_player['NewPosition'], dat)
    sorted_similar_per = find_similar_to_team(
        fr_el_stats, filtered_recommends, similarity='pearson')
    return json.dumps(json.loads(
        sorted_similar_per.head(5)[['Name', 'Position', 'Age', 'Overall']].reset_index().to_json(orient='records')), indent=2)


@ app.route('/')
def home():
    return "Hello My First Flask Project"

# @app.route('/api', methods=['GET'])
# def get_api():
#     return jsonify(data)  # Return web frameworks information


if __name__ == '__main__':
    app.run(debug=True)
