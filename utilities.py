from data import data_access
import make_request
import model
import copy


def resolve_hero(hero_id):
    return data_access.retrieve_hero_ids()[str(hero_id)]


def resolve_item(item_id):
    return data_access.retrieve_item_ids()[str(item_id)]


def resolve_team(team_id):
    if team_id is None:
        return None
    if data_access.retrieve_team(team_id) == 'TEAM_NOT_FOUND':  # Get Team and Add to List
        name = make_request.get_team_name_from_id(team_id)
        data_access.add_team(model.Team(
            team_id=team_id,
            name=name,
            team_logo=f'[](/logo-dota \"{name}\")'
        ))
        resolve_team(team_id)
    else:
        team = data_access.retrieve_team(team_id)
        return model.Team(
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
    return model.League(
        name=data_access.get_league_name(league_id),
        league_id=league_id
    )


def is_potential_final_game(number, team_one_score, team_two_score):
    if number is 2 and team_one_score + team_two_score == 1:
        return True
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


def game_is_tracked(live_match):
    matches = data_access.get_tracked_series()
    for match in matches:
        if live_match.match_id == match.match_id:
            return True
    return False


def match_has_disappeared(live_matches, series):
    for live_match in live_matches:
        if series.match_id == live_match.match_id:
            return False
    return True


def get_teams_that_could_win(live_match):
    if live_match.radiant_series_wins + live_match.dire_series_wins == live_match.node_type - 1:
        return ['radiant', 'dire']
    if live_match.radiant_series_wins == (live_match.node_type / 2) - 0.5:
        return ['radiant']
    if live_match.dire_series_wins == (live_match.node_type / 2) - 0.5:
        return ['dire']
    raise Exception('Checking for teams that could win where there are no teams that can.')


def is_series_winner(live_match):
    latest_match = make_request.get_match_details(live_match.match_id)
    if latest_match is not False:
        teams_that_could_win = get_teams_that_could_win(live_match)
        for team in teams_that_could_win:
            if team == 'radiant':
                if latest_match['radiant_win']:
                    return resolve_team(latest_match['radiant_team_id'])
            if team == 'dire':
                if not latest_match['radiant_win']:
                    return resolve_team(latest_match['dire_team_id'])
        return False  # Series isn't over, wait for the next game.
    return False


def set_if_exists(kwargs, key):
    if key in kwargs.keys():
        return kwargs[key]
    return None


def resolve_region(region_number):
    if region_number is None:
        return None
    if region_number is 1:
        return 'North America'
    if region_number is 2:
        return 'South America'
    if region_number is 3:
        return 'Europe'
    if region_number is 4:
        return 'CIS'
    if region_number is 5:
        return 'China'
    if region_number is 6:
        return 'South-East Asia'


def resolve_broadcast_platform(platform_number):
    if platform_number is None:
        return None
    if platform_number is 1:
        return 'Steam TV'
    if platform_number is 2:
        return 'Twitch'
    if platform_number is 100:
        return 'Other'
    return 'Unknown Platform'


def resolve_language(language_number):
    if language_number is None:
        return None
    if language_number is 0:
        return 'English'
    if language_number is 6:
        return 'Chinese'
    if language_number is 8:
        return 'Russian'


def resolve_phase(phase_number):
    if phase_number is None:
        return None
    if phase_number is 1:
        return f'Qualifier'
    if phase_number is 2:
        return 'Group Stage'
    if phase_number is 3:
        return 'Playoffs'
    return f'Unknown ({phase_number})'


def resolve_node_type(node_type_number):
    if node_type_number is None:
        return None
    if node_type_number is 1:
        return 1
    if node_type_number is 2:
        return 3
    if node_type_number is 3:
        return 5
    if node_type_number is 4:
        return 2


def get_league_node(league, node_id):
    for node_group in league.node_groups:
        correct_node = search_node_group(node_group, node_id)
        if correct_node is not None:
            return correct_node


def search_node_group(node_group, node_id):
    for deep_node_group in node_group.node_groups:
        correct_node = search_node_group(deep_node_group, node_id)
        if correct_node:
            return correct_node
    correct_node = [x for x in list(map(lambda node: node if node.node_id == node_id else None,
                                        node_group.nodes)) if x]
    if not correct_node:
        return None
    return correct_node


def get_node_group(node_groups, node_group_id):
    for node_group in node_groups:
        if node_group.node_group_id == node_group_id:
            return node_group
        correct_node_group = get_node_group(node_group.node_groups, node_group_id)
        if correct_node_group is not None:
            return correct_node_group


