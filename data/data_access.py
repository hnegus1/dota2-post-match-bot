import json
import os
import datetime


def open_json_file_r(path):
    with open(os.getcwd() + path, 'r') as f:
        return json.load(f)


def open_json_file_w(path, data):
    with open(os.getcwd() + path, 'w') as f:
        json.dump(data, f, indent=2)


def retrieve_hero_ids():
    return open_json_file_r('/data/hero_ids.json')


def retrieve_item_ids():
    return open_json_file_r('/data/item_ids.json')


def retrieve_team(team_id):
    teams = open_json_file_r('/data/teams.json')
    for team in teams:
        if team['team_id'] == team_id:
            return team
    return 'TEAM_NOT_FOUND'


def add_team(team):
    teams = open_json_file_r('/data/teams.json')
    teams.append({
        "name": team.name,
        "team_id": team.team_id,
        "team_logo": team.team_logo,
        "last_played": team.last_played
    })
    json.dumps(teams)
    open_json_file_w('/data/teams.json', teams)


def get_league_ids():
    leagues = open_json_file_r('/data/leagues.json')
    to_return = []
    for league in leagues:
        to_return.append(league['league_id'])
    return to_return


def get_config(field):
    config = open_json_file_r('/data/config.json')
    return config[field]


def update_config(field, value):
    config = open_json_file_r('/data/config.json')
    config[field] = value
    json.dumps(config)
    open_json_file_w('/data/config.json', config)


def get_tracked_series():
    return open_json_file_r('/data/tracked_series.json')


def stop_tracking_series(league_node_id):
    live_games = open_json_file_r('/data/tracked_series.json')
    for index, match in enumerate(live_games):
        if match['league_node_id'] == league_node_id:
            del live_games[index]
    json.dumps(live_games)
    open_json_file_w('/data/tracked_series.json', live_games)


def track_match_node(**kwargs):
    live_games = open_json_file_r('/data/tracked_series.json')
    for node in live_games:
        if node['league_node_id'] == kwargs['league_node_id']:
            live_games.remove(node)
    live_games.append(kwargs)
    json.dumps(live_games)
    open_json_file_w('/data/tracked_series.json', live_games)


def set_team_last_played(team):
    teams = open_json_file_r('/data/teams.json')
    for tm in teams:
        if tm['team_id'] == team.team_id:
            tm['last_played'] = str(datetime.datetime.now().timestamp())
    json.dumps(teams)
    open_json_file_w('/data/teams.json', teams)



