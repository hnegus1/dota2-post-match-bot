import utilities as util
import md_builder as md
import time
import bot
import datetime


class League:
    def __init__(self, **kwargs):
        self.name = util.set_if_exists(kwargs['info'], 'name')
        self.league_id = util.set_if_exists(kwargs['info'], 'league_id')
        self.region = util.set_if_exists(kwargs['info'], 'region')
        self.url = util.set_if_exists(kwargs['info'], 'url')
        self.description = util.set_if_exists(kwargs['info'], 'description')
        self.pro_circuit_points = util.set_if_exists(kwargs['info'], 'pro_circuit_points')
        self.status = util.set_if_exists(kwargs['info'], 'status')
        self.prize_pool = PrizePool(**kwargs['prize_pool'])
        self.streams = list(map(lambda stream: Stream(**stream), kwargs['streams']))
        self.node_groups = list(map(lambda node_group: NodeGroup(None, **node_group), kwargs['node_groups']))


class PrizePool:
    def __init__(self, **kwargs):
        self.base_prize_pool = util.set_if_exists(kwargs, 'base_prize_pool')
        self.total_price_pool = util.set_if_exists(kwargs, 'total_prize_pool')
        self.prize_pool_split = util.set_if_exists(kwargs, 'prize_split_pct_x100')


class Stream:
    def __init__(self, **kwargs):
        self.stream_id = util.set_if_exists(kwargs, 'stream_id')
        self.language = util.set_if_exists(kwargs, 'language')
        self.name = util.set_if_exists(kwargs, 'name')
        self.broadcast_provider = util.set_if_exists(kwargs, 'broadcast_provider')
        self.stream_url = util.set_if_exists(kwargs, 'stream_url')


# Most of the operations within NodeGroup are simply fixing a lot of the mistakes that TOs have made or things that just
# haven't been done
class NodeGroup:
    def __init__(self, parent, **kwargs):
        self.name = util.set_if_exists(kwargs, 'name')
        self.node_group_id = util.set_if_exists(kwargs, 'node_group_id')
        self.parent_node_group_id = util.set_if_exists(kwargs, 'parent_node_group_id')
        self.incoming_node_group_ids = util.set_if_exists(kwargs, 'incoming_node_group_ids')
        self.advancing_node_group_id = util.set_if_exists(kwargs, 'advancing_node_group_id')
        self.advancing_team_count = util.set_if_exists(kwargs, 'advancing_team_count')
        self.team_count = util.set_if_exists(kwargs, 'team_count')
        self.is_tiebreaker = util.set_if_exists(kwargs, 'is_tiebreaker')
        self.is_final_group = util.set_if_exists(kwargs, 'is_final_group')
        self.is_completed = util.set_if_exists(kwargs, 'is_completed')
        self.region = util.set_if_exists(kwargs, 'region')
        self.phase = util.set_if_exists(kwargs, 'phase')
        self.nodes = list(map(lambda node: Node(self, **node), kwargs['nodes']))
        self.node_groups = list(map(lambda node_group: NodeGroup(self, **node_group), kwargs['node_groups']))
        self.team_standings = list(map(lambda team_standing: TeamStanding(**team_standing), kwargs['team_standings']))
        # Fix an issue where child node_groups are not given the correct phase
        if parent is not None:
            if hasattr(parent, 'phase'):
                self.phase = parent.phase
        # Assign a proper name to the node groups
        if self.name == '':
            if self.phase == 1:
                self.name = f'{util.resolve_region(self.region)} {util.resolve_phase(self.phase)}'
            else:
                self.name = util.resolve_phase(self.phase)
        self.fix_nodes()
        # Attempt to normalise some of the data by moving any node groups that have 1 node group as a child forward
        # to its node group
        if parent is None and len(self.node_groups) == 1:
            ng = self.node_groups[0]
            self.name = ng.name
            self.node_group_id = ng.node_group_id
            self.parent_node_group_id = ng.parent_node_group_id
            self.incoming_node_group_ids = ng.incoming_node_group_ids
            self.advancing_node_group_id = ng.advancing_node_group_id
            self.advancing_team_count = ng.advancing_team_count
            self.team_count = ng.team_count
            self.is_tiebreaker = ng.is_tiebreaker
            self.is_final_group = ng.is_final_group
            self.is_completed = ng.is_completed
            self.phase = ng.phase
            self.nodes = ng.nodes
            self.node_groups = ng.node_groups
            self.team_standings = ng.team_standings

        # If all nodes groups within a node group are completed, the complete the nodegroup.
        if all(node_group.is_completed for node_group in self.node_groups):
            self.is_completed = True

    def fix_nodes(self):
        # Add direct object links to the winning nodes. Add bracket types.
        for node in self.nodes:
            if self.phase == 'Playoffs':
                if hasattr(node, 'losing_node'):
                    node.bracket_type = 'Upper Bracket'
                else:
                    node.bracket_type = 'Lower Bracket'
            else:
                node.bracket_type = ''

        def set_round(number, node):
            node.round = number
            if hasattr(node, 'winning_node'):
                set_round(number + 1, node.winning_node)
            if hasattr(node, 'losing_node'):
                set_round(number + 1, node.losing_node)

        def set_name(node):
            node.name = f'{node.bracket_type} Round {node.round} {node.team_1} vs {node.team_2}'
            if hasattr(node, 'winning_node'):
                set_name(node.winning_node)
            if hasattr(node, 'losing_node'):
                set_name(node.losing_node)

        # Assign each node a round number and a name
        for node in self.nodes:
            set_round(1, node)
            set_name(node)

    def __str__(self):
        return self.name


class TeamStanding:
    def __init__(self, **kwargs):
        self.team = util.resolve_team(util.set_if_exists(kwargs, 'team_id'))
        self.standing = util.set_if_exists(kwargs, 'standing')
        self.wins = util.set_if_exists(kwargs, 'wins')
        self.losses = util.set_if_exists(kwargs, 'losses')
        self.score = util.set_if_exists(kwargs, 'score')

    def __str__(self):
        return self.team


class Node:
    def __init__(self, parent, **kwargs):
        self.name = util.set_if_exists(kwargs, 'name')
        self.node_id = util.set_if_exists(kwargs, 'node_id')
        self.node_group_id = util.set_if_exists(kwargs, 'node_group_id')
        self.winning_node_id = util.set_if_exists(kwargs, 'winning_node_id')
        self.losing_node_id = util.set_if_exists(kwargs, 'losing_node_id')
        self.incoming_node_id_1 = util.set_if_exists(kwargs, 'incoming_node_id_1')
        self.incoming_node_id_2 = util.set_if_exists(kwargs, 'incoming_node_id_2')
        self.node_type = util.set_if_exists(kwargs, 'node_type')
        self.series_id = util.set_if_exists(kwargs, 'series_id')
        self.team_id_1 = util.set_if_exists(kwargs, 'team_id_1')
        self.team_id_2 = util.set_if_exists(kwargs, 'team_id_2')
        self.team_1_wins = util.set_if_exists(kwargs, 'team_1_wins')
        self.team_2_wins = util.set_if_exists(kwargs, 'team_2_wins')
        self.has_started = util.set_if_exists(kwargs, 'has_started')
        self.is_completed = util.set_if_exists(kwargs, 'is_completed')
        self.actual_time = util.set_if_exists(kwargs, 'actual_time')
        # We're not serialising matches because it would take TEN YEARS.
        self.matches = util.set_if_exists(kwargs, 'matches')

        self.team_1 = util.resolve_team(self.team_id_1)
        self.team_2 = util.resolve_team(self.team_id_2)

    def __str__(self):
        return f'{self.name}'


class Match:
    def __init__(self, **kwargs):
        self.duration = util.set_if_exists(kwargs, 'duration')
        self.match_id = util.set_if_exists(kwargs, 'match_id')
        self.radiant = Radiant(**kwargs)
        self.dire = Dire(**kwargs)
        self.pick_bans = list(map(lambda pick_ban: PickBan(**pick_ban), kwargs['picks_bans']))
        self.players = list(map(lambda player: Player(**player), kwargs['players']))
        self.clips = bot.get_twitch_clips(self.match_id)


class LiveMatch:
    def __init__(self, **kwargs):
        self.league_id = util.set_if_exists(kwargs, 'league_id')
        self.league_node_id = util.set_if_exists(kwargs, 'league_node_id')
        self.match_id = util.set_if_exists(kwargs, 'match_id')
        self.radiant_series_wins = util.set_if_exists(kwargs, 'radiant_series_wins')
        self.dire_series_wins = util.set_if_exists(kwargs, 'dire_series_wins')
        self.dire_team = util.set_if_exists(kwargs, 'dire_team')
        self.radiant_team = util.set_if_exists(kwargs, 'radiant_team')
        self.node_type = util.set_if_exists(kwargs, 'node_type')
        self.series_id = util.set_if_exists(kwargs, 'series_id')


class Radiant:
    def __init__(self, **kwargs):
        self.victory = util.set_if_exists(kwargs, 'radiant_win')
        self.score = util.set_if_exists(kwargs, 'radiant_score')
        self.team_id = util.set_if_exists(kwargs, 'radiant_team_id')
        self.name = util.set_if_exists(kwargs, 'radiant_name')
        self.series_wins = util.set_if_exists(kwargs, 'radiant_series_wins')
        if self.team_id is not None:
            self.team = util.resolve_team(self.team_id)

    def __str__(self):
        return self.name


class Dire:
    def __init__(self, **kwargs):
        if util.set_if_exists(kwargs, 'radiant_win') is None:
            self.victory = None
        else:
            self.victory = not util.set_if_exists(kwargs, 'radiant_win')
        self.score = util.set_if_exists(kwargs, 'dire_score')
        self.team_id = util.set_if_exists(kwargs, 'dire_team_id')
        self.name = util.set_if_exists(kwargs, 'dire_name')
        self.series_wins = util.set_if_exists(kwargs, 'dire_series_wins')
        if self.team_id is not None:
            self.team = util.resolve_team(self.team_id)

    def __str__(self):
        return self.name


class PickBan:
    def __init__(self, **kwargs):
        self.isPick = util.set_if_exists(kwargs, 'is_pick')
        self.hero = util.set_if_exists(kwargs, 'hero_id')
        self.order = util.set_if_exists(kwargs, 'order') + 1
        self.team = util.set_if_exists(kwargs, 'team')


class Player:
    def __init__(self, **kwargs):
        self.name = util.set_if_exists(kwargs, 'persona')
        self.hero_id = util.set_if_exists(kwargs, 'hero_id')
        self.item_0 = util.set_if_exists(kwargs, 'item_0')
        self.item_1 = util.set_if_exists(kwargs, 'item_1')
        self.item_2 = util.set_if_exists(kwargs, 'item_2')
        self.item_3 = util.set_if_exists(kwargs, 'item_3')
        self.item_4 = util.set_if_exists(kwargs, 'item_4')
        self.item_5 = util.set_if_exists(kwargs, 'item_5')
        self.kills = util.set_if_exists(kwargs, 'kills')
        self.deaths = util.set_if_exists(kwargs, 'deaths')
        self.assists = util.set_if_exists(kwargs, 'assists')
        self.level = util.set_if_exists(kwargs, 'level')
        self.net_worth = util.set_if_exists(kwargs, 'gold') + util.set_if_exists(kwargs, 'gold_spent')
        self.gold_per_min = util.set_if_exists(kwargs, 'gold_per_min')
        self.xp_per_min = util.set_if_exists(kwargs, 'xp_per_min')
        self.last_hits = util.set_if_exists(kwargs, 'last_hits')
        self.denies = util.set_if_exists(kwargs, 'denies')
        self.scaled_hero_damage = util.set_if_exists(kwargs, 'scaled_hero_damage')
        self.scaled_hero_healing = util.set_if_exists(kwargs, 'scaled_hero_healing')
        self.scaled_tower_damage = util.set_if_exists(kwargs, 'scaled_tower_damage')


class Team:
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.team_id = kwargs['team_id']
        self.team_logo = kwargs['team_logo']

    def __str__(self):
        return self.name


class Series:
    def __init__(self, matches, node, league, winner):
        node_group = util.get_node_group(league.node_groups, node.node_group_id)
        self.node = node
        self.matches = matches
        self.team_1 = node.team_1
        self.team_2 = node.team_2
        self.title = f'{league.name} {node_group.name}s / {node.name} / Post-Match Discussion'
        self.team_1_standing = [x for x in list(map(lambda x: x if self.team_1.team_id == x.team.team_id else None, node_group.team_standings)) if x][0]
        self.team_2_standing = [x for x in list(map(lambda x: x if self.team_2.team_id == x.team.team_id else None, node_group.team_standings)) if x][0]
        self.winner = winner
        self.consequences_text = ''

        # Make up a different title if the team has already played in the same day
        if node_group.name == 'Playoff':
            incoming_node_1 = None
            incoming_node_2 = None
            if self.node.incoming_node_id_1 is not None:
                incoming_node_1 = util.get_league_node(league, self.node.incoming_node_id_1)
                if datetime.datetime.fromtimestamp(self.node.actual_time).day == datetime.datetime.fromtimestamp(incoming_node_1.actual_time).day:
                    # It's the same day so set another title
                    self.title = f'{league.name} {node_group.name}s / Post-Match Discussion'
            if self.node.incoming_node_id_2 is not None:
                incoming_node_2 = util.get_league_node(league, self.node.incoming_node_id_2)
                if datetime.datetime.fromtimestamp(self.node.actual_time).day == datetime.datetime.fromtimestamp(incoming_node_2.actual_time).day:
                    # It's the same day so set another title
                    self.title = f'{league.name} {node_group.name}s / Post-Match Discussion'

        if self.winner.team_id == self.team_1.team_id:
            self.node.team_1_wins += 1
            self.loser = self.team_2
        else:
            self.node.team_2_wins += 1
            self.loser = self.team_1

        # For Round Robin Groups
        if node.winning_node_id == 0 and node.losing_node_id == 0 and node_group.name == 'Group':
            self.consequences_text = f'{self.team_1.name} are {self.team_1_standing.wins}-{self.team_1_standing.losses}' \
                f'\n' \
                f'{self.team_2.name} are {self.team_2_standing.wins}-{self.team_2_standing.losses}'
        # For Tournaments - Upper Bracket
        if node.winning_node_id != 0 and node.losing_node_id == 0 and node_group.name == 'Playoff':
            self.consequences_text = f'{self.team_1.name} have advanced to the next winners round' \
                f'\n' \
                f'{self.team_2.name} have been eliminated from {league.name}'
        # For Tournaments - Upper Bracket
        if node.winning_node_id != 0 and node.losing_node_id != 0 and node_group.name == 'Playoff':
            self.consequences_text = f'{self.team_1.name} have advanced to the next upper bracket round' \
                f'\n' \
                f'{self.team_2.name} have dropped to the lower bracket'
        if node.winning_node_id == 0 and node.losing_node_id == 0 and node_group.name == 'Playoff':
            self.consequences_text = f'Congratulations to {self.winner} for winning {league.name}!'
        print()
        self.markdown = self.build_md()

    def build_md(self):
        markdown = ''
        # MAIN HEADER
        markdown += md.h2(f'{self.team_1.team_logo}'
                          f'{self.team_1.name} '
                          f'{self.node.team_1_wins}-{self.node.team_2_wins} '
                          f'{self.team_2.name}'
                          f'{self.team_2.team_logo}')
        markdown += md.h2(self.consequences_text)
        markdown += md.divider()
        for match_index, match in enumerate(self.matches):
            markdown += md.h2(md.bold(f'Game {match_index + 1}'))
            markdown += md.h2(f'{match.radiant.team.team_logo}'
                              f'{match.radiant.team.name} '
                              f'{match.radiant.score}'
                              f'-'
                              f'{match.dire.score} '
                              f'{match.dire.team.name}'
                              f'{match.dire.team.team_logo}')
            if match.radiant.victory:
                markdown += md.h2(f'{match.radiant.team.team_logo}'
                                  f'{match.radiant.team.name}'
                                  f'{match.radiant.team.team_logo} Victory')
            else:
                markdown += md.h2(f'{match.dire.team.team_logo}'
                                  f'{match.dire.team.name}'
                                  f'{match.dire.team.team_logo} Victory')
            markdown += md.h2(f'{time.strftime("%H:%M:%S", time.gmtime(match.duration))}')

            """Picks and bans"""
            picks_table = list()
            bans_table = list()

            bans_table.append([match.radiant.team.team_logo, 'Bans', 'Dire', match.dire.team.team_logo])
            picks_table.append([match.radiant.team.team_logo, 'Picks', 'Dire', match.dire.team.team_logo])
            bans_radiant = list()
            bans_dire = list()
            picks_radiant = list()
            picks_dire = list()

            # Phase 1 Bans
            bans_radiant.append([])
            bans_dire.append([])
            for i in range(6):
                if match.pick_bans[i].team == 0:
                    bans_radiant[0].append(md.convert_hero(util.resolve_hero(match.pick_bans[i].hero)))
                else:
                    bans_dire[0].append(md.convert_hero(util.resolve_hero(match.pick_bans[i].hero)))
            # Phase 1 Picks
            picks_radiant.append([])
            picks_dire.append([])
            for i in range(6, 10):
                if match.pick_bans[i].team == 0:
                    picks_radiant[0].append(md.convert_hero(util.resolve_hero(match.pick_bans[i].hero)))
                else:
                    picks_dire[0].append(md.convert_hero(util.resolve_hero(match.pick_bans[i].hero)))
            # Phase 2 Bans
            bans_radiant.append([])
            bans_dire.append([])
            for i in range(10, 14):
                if match.pick_bans[i].team == 0:
                    bans_radiant[1].append(md.convert_hero(util.resolve_hero(match.pick_bans[i].hero)))
                else:
                    bans_dire[1].append(md.convert_hero(util.resolve_hero(match.pick_bans[i].hero)))
            # Phase 2 Picks
            picks_radiant.append([])
            picks_dire.append([])
            for i in range(14, 18):
                if match.pick_bans[i].team == 0:
                    picks_radiant[1].append(md.convert_hero(util.resolve_hero(match.pick_bans[i].hero)))
                else:
                    picks_dire[1].append(md.convert_hero(util.resolve_hero(match.pick_bans[i].hero)))
            # Phase 3 Bans
            bans_radiant.append([])
            bans_dire.append([])
            for i in range(18, 20):
                if match.pick_bans[i].team == 0:
                    bans_radiant[2].append(md.convert_hero(util.resolve_hero(match.pick_bans[i].hero)))
                else:
                    bans_dire[2].append(md.convert_hero(util.resolve_hero(match.pick_bans[i].hero)))
            # Phase 3 Picks
            picks_radiant.append([])
            picks_dire.append([])
            for i in range(20, 22):
                if match.pick_bans[i].team == 0:
                    picks_radiant[2].append(md.convert_hero(util.resolve_hero(match.pick_bans[i].hero)))
                else:
                    picks_dire[2].append(md.convert_hero(util.resolve_hero(match.pick_bans[i].hero)))

            bans_table.append(['1', str(''.join(bans_radiant[0])), str(''.join(bans_dire[0])), '1'])
            bans_table.append(['2', str(''.join(bans_radiant[1])), str(''.join(bans_dire[1])), '2'])
            bans_table.append(['3', str(''.join(bans_radiant[2])), str(''.join(bans_dire[2])), '3'])

            picks_table.append(['1', str(''.join(picks_radiant[0])), str(''.join(picks_dire[0])), '1'])
            picks_table.append(['2', str(''.join(picks_radiant[1])), str(''.join(picks_dire[1])), '2'])
            picks_table.append(['3', str(''.join(picks_radiant[2])), str(''.join(picks_dire[2])), '3'])
            markdown += md.table(bans_table)
            markdown += md.table(picks_table)
            stats_table = list()
            stats_table.append(['Hero', 'Player', 'Level', 'K/D/A', 'GPM/XPM', 'LH/D', 'Net Worth', 'Hero Damage', 'Hero Healing', 'Tower Damage'])
            for player_index, player in enumerate(match.players):  # PLAYER STATS
                if player_index == 5:
                    stats_table.append(['', '', '', '', '', ''])
                stats_table.append([
                    md.convert_hero(util.resolve_hero(player.hero_id)),
                    player.name,
                    player.level,
                    f'{player.kills}/{player.deaths}/{player.assists}',
                    f'{player.gold_per_min}/{player.xp_per_min}',
                    f'{player.last_hits}/{player.denies}',
                    player.net_worth,
                    player.scaled_hero_damage,
                    player.scaled_hero_healing,
                    player.scaled_tower_damage
                ])
            markdown += md.table(stats_table)
            """"Post-Match Links"""
            markdown += f'Detailed stats: {md.link("Dotabuff", f"https://www.dotabuff.com/matches/{match.match_id}")} | ' \
                f' {md.link("Opendota", f"https://www.opendota.com/matches/{match.match_id}")} | ' \
                f' {md.link("Datdota", f"http://datdota.com/matches/{match.match_id}")} | ' \
                f' {md.link("Stratz", f"https://stratz.com/en-us/match/{match.match_id}")}'
            markdown += md.line_break()
            markdown += md.divider()
            if match.clips:
                markdown += md.h2('Clips')
                markdown += md.md_list(match.clips)
        markdown += md.line_break()
        markdown += md.italics('This action was performed by a bot. For more information, [see here](https://www.reddit.com/user/d2-match-bot-speaks/comments/c26lfw/introducing_the_dota_2_post_match_bot/). Contact: /u/d2-match-bot-speaks')
        markdown += md.italics('This new version of the bot has not been properly tested. Please forgive any errors that may occur in the first few series.')
        return markdown
