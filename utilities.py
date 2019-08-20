import make_request
import model
from data import data_access
import praw

r = praw.Reddit(client_id=data_access.get_config("bot_client_id"),
                client_secret=data_access.get_config("bot_client_secret"),
                password=data_access.get_config("bot_password"),
                user_agent=data_access.get_config("bot_user_agent"),
                username='dota2-post-match-bot')

subreddit = r.subreddit('dota2')
twitch_clip_bot = r.redditor('DotaClipMatchFinder')


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


def get_twitch_clips(match_id):
    clips = [x for x in list(map(lambda comment: f'[{comment.submission.title}]({comment.submission.url})'
             if str(match_id) in comment.body else None, twitch_clip_bot.comments.new())) if x]
    print(clips)
    return clips


class APIDownException(Exception):
    pass
