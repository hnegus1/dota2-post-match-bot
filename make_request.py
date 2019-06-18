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
    headers = {'User-Agent': 'Dota2-Post-Match-Bot (Testing for now) | /u/d2-match-bot-speaks'}

    # No API key is needed for doing it by the Dota 2 website API
    # This is probably Not Allowed.
    return requests.get(kwargs['url'], headers=headers).json()


def make_request(**kwargs):
    # Check we don't go over the request limit.
    if data_access.get_config('last_request') == time.time():
        time.sleep(1)

    # Init URL + headers
    headers = {'User-Agent': 'Dota2-Post-Match-Bot (Testing for now) | /u/d2-match-bot-speaks'}
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
    return response.json()


def get_live_league_matches():
    return make_request(url='http://api.steampowered.com/IDOTA2Match_570/GetLiveLeagueGames/v1/')['result']['games']


def get_match_details(match_id):
    return make_request(
        url='http://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v1/',
        parameters={'match_id': match_id}
    )['result']


def get_player_info():
    return make_request_dota2(url='https://www.dota2.com/webapi/IDOTA2Fantasy/GetProPlayerInfo/v0001/')


# print(json.dumps(get_live_league_games(), indent=4, sort_keys=True))
