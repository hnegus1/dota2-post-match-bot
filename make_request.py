import requests
import json
from data import data_access
import time

api_key = data_access.get_config("valve_api_key")


def make_request_dota2(**kwargs):
    # Check we don't go over the request limit.
    if data_access.get_config('last_request') == time.time():
        time.sleep(1)

    # Init URL + headers
    headers = {'User-Agent': 'Dota2-Post-Match-Bot | /u/d2-match-bot-speaks'}

    # No API key is needed for doing it by the Dota 2 website API
    # This is probably Not Allowed.
    try:
        return requests.get(kwargs['url'], headers=headers).json()
    except:
        return False


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
    response = requests.get(request)
    data_access.update_config('last_request', time.time())
    try:
        return response.json()
    except:
        return False


def get_live_league_matches():
    request = make_request(url='http://api.steampowered.com/IDOTA2Match_570/GetLiveLeagueGames/v1/')['result']
    if 'error' in request.keys():
        return False
    return request['games']


def get_match_details(match_id):
    try:
        request = make_request(
            url='http://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v1/',
            parameters={'match_id': match_id}
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

# print(json.dumps(get_live_league_games(), indent=4, sort_keys=True))
