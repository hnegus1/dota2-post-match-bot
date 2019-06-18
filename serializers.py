import utilities as util
from model import Match, Player, PickBan, Series, LiveMatch, LiveTeam, LiveSeries
import make_request


def serialize_live_match_valve(match):
    return LiveMatch.LiveMatch(
        match_id=match['match_id'],
        league=util.resolve_league(match['league_id']),
        radiant_live_team=LiveTeam.LiveTeam(
            team=util.resolve_team(match['radiant_team']['team_id'], match['radiant_team']['team_name']),
            score=match['radiant_series_wins']
        ),
        dire_live_team=LiveTeam.LiveTeam(
            team=util.resolve_team(match['dire_team']['team_id'], match['dire_team']['team_name']),
            score=match['dire_series_wins']
        ),
        series_type=util.resolve_series_type(match['series_type'])
    )


def serialize_live_match_match_bot(match):
    return LiveMatch.LiveMatch(
        match_id=match['match_id'],
        league=util.resolve_league(match['league']['league_id']),
        radiant_live_team=LiveTeam.LiveTeam(
            team=util.resolve_team(
                match['radiant_live_team']['team']['team_id'],
                match['radiant_live_team']['team']['name']
            ),
            score=match['radiant_live_team']['score']
        ),
        dire_live_team=LiveTeam.LiveTeam(
            team=util.resolve_team(
                match['dire_live_team']['team']['team_id'],
                match['dire_live_team']['team']['name']
            ),
            score=match['dire_live_team']['score']
        ),
        series_type=util.resolve_series_type(match['series_type'])
    )


def serialize_live_series(series):
    return LiveSeries.LiveSeries(
        series_id=series['series_id'],
        league=util.resolve_league(series['league']['league_id']),
        live_team_one=LiveTeam.LiveTeam(
            team=util.resolve_team(
                series['live_team_one']['team']['team_id'],
                series['live_team_one']['team']['name']
            ),
            score=series['live_team_one']['score']
        ),
        live_team_two=LiveTeam.LiveTeam(
            team=util.resolve_team(
                series['live_team_two']['team']['team_id'],
                series['live_team_two']['team']['name']
            ),
            score=series['live_team_two']['score']
        ),
        series_type=series['series_type'],
        live_matches=list(map(serialize_live_match_match_bot, series['live_matches']))
    )


def serialize_series_from_live_series(live_series):
    matches = []
    for live_match in live_series.live_matches:
        matches.append(make_request.get_match_details(live_match.match_id))
    to_return = Series.Series(
        series_id=live_series.series_id,
        league=live_series.league,
        team_one=live_series.live_team_one,
        team_two=live_series.live_team_two,
        type=live_series.series_type,
        matches=list(map(serialize_match, matches))
    )
    if to_return.matches[-1].winner.team_id == to_return.team_one.team.team_id:
        to_return.team_one.score += 1
    else:
        to_return.team_two.score += 1

    return to_return


def serialize_match(match):
    def serialize_players(player):
        def serialize_items():
            items = []
            keys = ['item_0', 'item_1', 'item_2', 'item_3', 'item_4', 'item_5']
            for key in keys:
                if player[key] is not 0:
                    items.append(util.resolve_item(player[key]))
                else:
                    items.append('')
            return items

        return Player.Player(
            name=util.resolve_player_name(player['account_id']),
            hero=util.resolve_hero(player['hero_id']),
            items=serialize_items(),
            kills=player['kills'],
            deaths=player['deaths'],
            assists=player['assists'],
            level=player['level'],
            net_worth=player['gold'] + player['gold_spent'],
            gold_per_min=player['gold_per_min'],
            xp_per_min=player['xp_per_min'],
            last_hits=player['last_hits'],
            denies=player['denies'],
            scaled_hero_damage=player['scaled_hero_damage'],
            scaled_hero_healing=player['scaled_hero_healing'],
            scaled_tower_damage=player['scaled_tower_damage']
        )

    radiant = util.resolve_team(match['radiant_team_id'], match['radiant_name'])
    dire = util.resolve_team(match['dire_team_id'], match['dire_name'])

    def serialize_pick_bans(pick_ban):
        if pick_ban['team'] == 0:
            team = radiant
        else:
            team = dire
        return PickBan.PickBan(
            is_pick=pick_ban['is_pick'],
            hero_id=pick_ban['hero_id'],
            order=pick_ban['order'],
            team=team
        )

    return Match.Match(
        match_id=match['match_id'],
        radiant=radiant,
        dire=dire,
        radiant_win=match['radiant_win'],
        players=list(map(serialize_players, match['players'])),
        radiant_score=match['radiant_score'],
        dire_score=match['dire_score'],
        duration=match['duration'],
        pick_bans=list(map(serialize_pick_bans, match['picks_bans'])),
    )
