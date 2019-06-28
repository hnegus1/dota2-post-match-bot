import praw
import praw.exceptions
import prawcore
import time
import dota_parser
import re
from data import data_access

r = praw.Reddit(client_id=data_access.get_config("bot_client_id"),
                client_secret=data_access.get_config("bot_client_secret"),
                password=data_access.get_config("bot_password"),
                user_agent=data_access.get_config("bot_user_agent"),
                username='dota2-post-match-bot')

subreddit = r.subreddit('dota2')


def run_bot():
    while True:
        operate_bot()
        print('Boop')
        time.sleep(60)


def operate_bot():
    # Go through all active leagues and check for any change in number of series.
    series = dota_parser.track_live_series()
    if series is not False:
        try:
            print(series['markdown'])
            print()
            subreddit.submit(
                series['title'],
                series['markdown'],
                spoiler=True,
            )
        except prawcore.exceptions.ServerError:
            print('praw threw servererror, skipping')
        except prawcore.exceptions.ResponseException:
            print('praw threw responseexception, skipping')
        except praw.exceptions.APIException as e:
            time_to_sleep = (int(re.sub("\D", "", e.message)) * 60) - 60
            print(f'praw threw rate exception. Trying again in {time_to_sleep} seconds')
            time.sleep(time_to_sleep)
        else:
            data_access.stop_tracking_series(series['series_id'])


run_bot()
