from data import data_access
import make_request
from model import Team, League
import time


def resolve_hero(hero_id):
    return data_access.retrieve_hero_ids()[str(hero_id)]


def resolve_item(item_id):
    return data_access.retrieve_item_ids()[str(item_id)]


def resolve_team(team_id, team_name):
    if data_access.retrieve_team(team_id) == 'TEAM_NOT_FOUND':  # Get Team and Add to List
        data_access.add_team(Team.Team(
            team_id=team_id,
            name=team_name,
            team_logo='[](/logo-dota \"\")'
        ))
        resolve_team(team_id, team_name)
    else:
        team = data_access.retrieve_team(team_id)
        return Team.Team(
            team_id=team['team_id'],
            name=team['name'],
            team_logo=team['team_logo']
        )


def resolve_player_name(account_id):
    players = make_request.get_player_info()
    if players is None:
        return False
    for player in players['player_infos']:
        if player['account_id'] == account_id:
            return player['name']
    return 'Unknown Standin'


def resolve_league(league_id):
    return League.League(
        name=data_access.get_league_name(league_id),
        league_id=league_id
    )


def is_potential_final_game(number, team_one_score, team_two_score):
    if team_one_score + team_two_score == number - 1:
        return True
    if team_one_score == (number / 2) - 0.5:
        return True
    if team_two_score == (number / 2) - 0.5:
        return True
    return False


def resolve_series_type(series_type):
    if series_type == 0:
        return 1
    if series_type == 1:
        return 3
    if series_type == 2:
        return 5
    else:
        raise Exception('This is a series type I haven\'t seen. Please panic.')


def team_one_is_radiant(live_match):
    tracked_series = data_access.get_tracked_series()
    for series in tracked_series:
        if (series['live_team_one']['team']['team_id'] == live_match.radiant_live_team.team.team_id and
            series['live_team_two']['team']['team_id'] == live_match.dire_live_team.team.team_id) or \
                (series['live_team_one']['team']['team_id'] == live_match.dire_live_team.team.team_id and
                 series['live_team_two']['team']['team_id'] == live_match.radiant_live_team.team.team_id):
            if series['live_team_one']['team']['team_id'] == live_match.radiant_live_team.team.team_id:
                return True
            else:
                return False


def series_is_tracked(live_match):
    tracked_series = data_access.get_tracked_series()
    for series in tracked_series:
        if (series['live_team_one']['team']['team_id'] == live_match.radiant_live_team.team.team_id and
            series['live_team_two']['team']['team_id'] == live_match.dire_live_team.team.team_id) or \
                (series['live_team_one']['team']['team_id'] == live_match.dire_live_team.team.team_id and
                 series['live_team_two']['team']['team_id'] == live_match.radiant_live_team.team.team_id):
            return series
    return False


def game_is_tracked(live_match):
    series = series_is_tracked(live_match)
    for tracked_match in series['live_matches']:
        if tracked_match['match_id'] == live_match.match_id:
            return True
    return False


def match_has_disappeared(live_matches, series):
    for live_match in live_matches:
        if series.live_matches[-1].match_id == live_match.match_id:
            return False
    return True


def get_teams_that_could_win(series):
    if series.live_team_one.score + series.live_team_two.score == series.series_type - 1:
        return [series.live_team_one.team, series.live_team_two.team]
    if series.live_team_one.score == (series.series_type / 2) - 0.5:
        return [series.live_team_one.team]
    if series.live_team_two.score == (series.series_type / 2) - 0.5:
        return [series.live_team_two.team]
    raise Exception('Checking for teams that could win where there are no teams that can.')


def get_series_winner(series):
    latest_match = make_request.get_match_details(series.live_matches[-1].match_id)
    if latest_match is not False:
        teams_that_could_win = get_teams_that_could_win(series)
        for team in teams_that_could_win:
            if latest_match['radiant_win'] and latest_match['radiant_team_id'] == team.team_id or \
                    not latest_match['radiant_win'] and latest_match['dire_team_id'] == team.team_id:
                return team
        return False  # Series isn't over, wait for the next game.
    return False
