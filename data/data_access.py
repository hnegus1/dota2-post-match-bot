import json
import os


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
        "team_logo": team.team_logo
    })
    json.dumps(teams)
    open_json_file_w('/data/teams.json', teams)


def get_league_ids():
    leagues = open_json_file_r('/data/leagues.json')
    to_return = []
    for league in leagues:
        to_return.append(league['league_id'])
    return to_return


def get_league_name(league_id):
    leagues = open_json_file_r('/data/leagues.json')
    for league in leagues:
        if league['league_id'] == league_id:
            return league['name']
    raise Exception('League not found in get_league_name')


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


def track_new_series(live_match):
    live_games = open_json_file_r('/data/tracked_series.json')
    live_games.append({
        'series_id': get_config('series_tracked'),
        'league': {
            'league_id': live_match.league.league_id,
            'name': live_match.league.name
        },
        'live_team_one': {
            'team': {
                'name': live_match.radiant_live_team.team.name,
                'team_id': live_match.radiant_live_team.team.team_id,
                'team_logo': live_match.radiant_live_team.team.team_logo
            },
            'score': live_match.radiant_live_team.score
        },
        'live_team_two': {
            'team': {
                'name': live_match.dire_live_team.team.name,
                'team_id': live_match.dire_live_team.team.team_id,
                'team_logo': live_match.dire_live_team.team.team_logo
            },
            'score': live_match.dire_live_team.score
        },
        'series_type': live_match.series_type,
        'live_matches': [
            {
                'match_id': live_match.match_id,
                'league': {
                    'league_id': live_match.league.league_id,
                    'name': live_match.league.name
                },
                'radiant_live_team': {
                    'team': {
                        'name': live_match.radiant_live_team.team.name,
                        'team_id': live_match.radiant_live_team.team.team_id,
                        'team_logo': live_match.radiant_live_team.team.team_logo
                    },
                    'score': live_match.radiant_live_team.score
                },
                'dire_live_team': {
                    'team': {
                        'name': live_match.dire_live_team.team.name,
                        'team_id': live_match.dire_live_team.team.team_id,
                        'team_logo': live_match.dire_live_team.team.team_logo
                    },
                    'score': live_match.dire_live_team.score
                },
                'series_type': live_match.series_type
            }
        ]
    })
    json.dumps(live_games)
    open_json_file_w('/data/tracked_series.json', live_games)


def track_new_match(live_match, series_id):
    live_games = open_json_file_r('/data/tracked_series.json')
    for index, series in enumerate(live_games):
        if series['series_id'] == series_id:
            live_games[index]['live_matches'].append({
                'radiant_live_team': {
                    'team': {
                        'name': live_match.radiant_live_team.team.name,
                        'team_id': live_match.radiant_live_team.team.team_id,
                        'team_logo': live_match.radiant_live_team.team.team_logo
                    },
                    'score': live_match.radiant_live_team.score
                },
                'dire_live_team': {
                    'team': {
                        'name': live_match.dire_live_team.team.name,
                        'team_id': live_match.dire_live_team.team.team_id,
                        'team_logo': live_match.dire_live_team.team.team_logo
                    },
                    'score': live_match.dire_live_team.score
                },
                'match_id': live_match.match_id,
                'series_type': live_match.series_type,
                'league': {
                    'league_id': live_match.league.league_id,
                    'name': live_match.league.name
                },
            })
    json.dumps(live_games)
    open_json_file_w('/data/tracked_series.json', live_games)


def stop_tracking_series(series_id):
    live_games = open_json_file_r('/data/tracked_series.json')
    for index, series in enumerate(live_games):
        if series['series_id'] == series_id:
            del live_games[index]
    json.dumps(live_games)
    open_json_file_w('/data/tracked_series.json', live_games)


def increment_series_tracked():
    config = open_json_file_r('/data/config.json')
    config['series_tracked'] += 1
    json.dumps(config)
    open_json_file_w('/data/config.json', config)


def update_series_wins(team_one_win_count, team_two_win_count, series_id):
    live_games = open_json_file_r('/data/tracked_series.json')
    for index, series in enumerate(live_games):
        if series['series_id'] == series_id:
            series['live_team_one']['score'] = team_one_win_count
            series['live_team_two']['score'] = team_two_win_count
    json.dumps(live_games)
    open_json_file_w('/data/tracked_series.json', live_games)
