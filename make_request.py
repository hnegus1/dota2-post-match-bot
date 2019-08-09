import requests
import json
from data import data_access
import time

api_key = data_access.get_config("valve_api_key")


# dota2 undocumented API
def make_request_dota2(**kwargs):
    # Check we don't go over the request limit.
    if data_access.get_config('last_request') == time.time():
        time.sleep(1)

    # Init URL + headers
    headers = {'User-Agent': 'Dota2-Post-Match-Bot | /u/d2-match-bot-speaks'}
    request = f'{kwargs["url"]}'

    # Handle parameters
    if 'parameters' in kwargs:
        if isinstance(kwargs['parameters'], dict):
            for dict_key, value in kwargs['parameters'].items():
                request += f'?{dict_key}={value}'
        elif kwargs['parameters'] is not None:
            raise Exception(f'Invalid Parameters: {kwargs["parameters"]}')

    # No API key is needed for doing it by the Dota 2 website API
    try:
        return requests.get(request, headers=headers).json()
    except:
        return False


# steampowered api
def make_request(**kwargs):
    # Check we don't go over the request limit.
    if data_access.get_config('last_request') == time.time():
        time.sleep(1)

    # Init URL + headers
    headers = {'User-Agent': 'Dota2-Post-Match-Bot | /u/d2-match-bot-speaks'}
    request = f'{kwargs["url"]}?key={api_key}'

    # Handle parameters
    if 'parameters' in kwargs:
        if isinstance(kwargs['parameters'], dict):
            for dict_key, value in kwargs['parameters'].items():
                request += f'&{dict_key}={value}'
        elif kwargs['parameters'] is not None:
            raise Exception(f'Invalid Parameters: {kwargs["parameters"]}')

    # Fire the request - update the time of the last request
    response = requests.get(request, headers=headers)
    data_access.update_config('last_request', time.time())
    try:
        return response.json()
    except:
        return False


# datdota
def make_request_dat_dota(**kwargs):
    # Check we don't go over the request limit.
    if data_access.get_config('last_request') == time.time():
        time.sleep(1)

    # Init URL + headers
    headers = {'User-Agent': 'Dota2-Post-Match-Bot | /u/d2-match-bot-speaks | Used to get team names from ids'}
    request = f'{kwargs["url"]}/{kwargs["parameter"]}'

    # Fire the request - update the time of the last request
    response = requests.get(request, headers=headers)
    data_access.update_config('last_request', time.time())
    try:
        return response.json()
    except:
        return False


def get_live_league_matches(league_id):
    request = make_request(url='http://api.steampowered.com/IDOTA2Match_570/GetLiveLeagueGames/v1/',
                           parameters={'league_id': str(league_id)})['result']
    if 'error' in request.keys():
        return False
    return request['games']


def get_match_details(match_id):
    try:
        request = make_request(
            url='http://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v1/',
            parameters={'match_id': match_id, 'include_persona_names': 1}
        )['result']
        if 'error' in request.keys():
            return False
        return request
    except KeyError:
        return False


def get_player_info():
    request = make_request_dota2(url='https://www.dota2.com/webapi/IDOTA2Fantasy/GetProPlayerInfo/v0001/')
    if request is None:
        return False
    return request


def get_league_data(league_id):
    request = make_request_dota2(
        url='https://www.dota2.com/webapi/IDOTA2League/GetLeagueData/v0001/',
        parameters={'league_id': league_id})
    return request


def get_team_name_from_id(team_id):
    try:
        request = make_request_dat_dota(
            url='https://www.datdota.com/api/teams',
            parameter=str(team_id)
        )
        return request['data']['team']['name']
    except TypeError:
        return 'Unknown Team'

# print(json.dumps(get_live_league_games(), indent=4, sort_keys=True))
