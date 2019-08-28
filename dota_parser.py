from data import data_access
import make_request
import model
import utilities as util


def track_live_series():
    # Series that are currently being tracked by the bot
    tracked_series = list(map(lambda live_match_tracked: model.LiveMatch(**live_match_tracked),
                              data_access.get_tracked_series()))
    try:
        for league_id in data_access.get_league_ids():
            league = model.League(**make_request.get_league_data(league_id))  # Get current league as py object
            live_matches = make_request.get_live_league_matches(league_id)  # Get all live matches for that league JSON
            # Serialise the JSON data into py object
            live_matches = list(map(lambda live_match_live: model.LiveMatch(**live_match_live), live_matches))

            for live_match in tracked_series:  # Foreach live match
                # If it's the potential final game...
                if util.is_potential_final_game(live_match.node_type,
                                                live_match.radiant_series_wins,
                                                live_match.dire_series_wins):
                    if util.match_has_disappeared(live_matches, live_match):  # check if the match has disappeared from live series
                        winner = util.is_series_winner(live_match)  # Get the winner of the series by parsing the match
                        if winner is not False:  # If there actually is a winner, then the series is over
                            # Get match in series
                            node = util.get_league_node(league, live_match.league_node_id)[0]
                            matches = []
                            for match in node.matches:
                                matches.append(match['match_id'])
                            # Add the last match to the un updated list of matches
                            matches.append(live_match.match_id)
                            matches = list(dict.fromkeys(matches))
                            # Get the match data by querying the API.
                            matches = list(map(lambda x: model.Match(**make_request.get_match_details(x)), matches))
                            series = model.Series(matches, node, league, winner)
                            data_access.stop_tracking_series(live_match.league_node_id)
                            return {'title': series.title, 'markdown': series.markdown}

            for match in live_matches:
                if match.match_id not in [x.match_id for x in tracked_series]:
                    if match.league_node_id != 0:
                        node = util.get_league_node(league, match.league_node_id)[0]
                        match.node_type = util.resolve_node_type(node.node_type)
                        match.series_id = node.series_id
                        data_access.track_match_node(**match.__dict__)
    except util.APIDownException:
        print('API IS DOWN')
        pass
    except TypeError:
        print('API IS DOWN OR YOU HAVE MADE A BIG MISTAKE')
