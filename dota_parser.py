import make_request
import utilities as util
from data import data_access
import md_builder as md
import serializers as s


def track_live_series():
    def get_live_league_match(match):
        if match['league_id'] in data_access.get_league_ids():
            return match
    # Serialize all live games.
    if make_request.get_live_league_matches() is False:
        return False
    live_matches_json_full = list(map(get_live_league_match, make_request.get_live_league_matches()))
    live_matches_json = [x for x in live_matches_json_full if x]
    live_matches_full = list(map(s.serialize_live_match_valve, live_matches_json))
    live_matches = [x for x in live_matches_full if x]
    for x in live_matches_full:
        if x.match_id == 0:
            live_matches_full.remove(x)
    tracked_series = list(map(s.serialize_live_series, data_access.get_tracked_series()))

    for live_series in tracked_series:
        if util.is_potential_final_game(
                live_series.series_type,
                live_series.live_team_one.score,
                live_series.live_team_two.score):
            if util.match_has_disappeared(live_matches, live_series):
                winner = util.get_series_winner(live_series)
                if winner is not False:
                    serialised_series = s.serialize_series_from_live_series(live_series)
                    if serialised_series is False:
                        return False
                    return md.build_markdown(serialised_series)

    for live_match in live_matches:
        if live_match.league.league_id in data_access.get_league_ids():
            series = util.series_is_tracked(live_match)
            if series is not False:  # If series is already being tracked
                if util.game_is_tracked(live_match) is False:  # If game is already being tracked
                    if util.team_one_is_radiant(live_match):
                        data_access.update_series_wins(
                            live_match.radiant_live_team.score,
                            live_match.dire_live_team.score,
                            series['series_id']
                        )
                    else:
                        data_access.update_series_wins(
                            live_match.dire_live_team.score,
                            live_match.radiant_live_team.score,
                            series['series_id']
                        )
                    data_access.track_new_match(live_match, series['series_id'])
            else:
                data_access.track_new_series(live_match)
                data_access.increment_series_tracked()
    return False  # No series have concluded


