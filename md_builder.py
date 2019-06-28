import time

def h1(text):
    return '# ' + text + line_break()


def h2(text):
    return '## ' + text + line_break()


def h3(text):
    return '### ' + text + line_break()


def h4(text):
    return '#### ' + text + line_break()


def h5(text):
    return '##### ' + text + line_break()


def h6(text):
    return '###### ' + text + line_break()


def italics(text):
    return '*' + text + '*'


def bold(text):
    return '**' + text + '**'


def bold_and_italics(text):
    return '**_' + text + '_**'


def strikethrough(text):
    return '~~' + text + '~~'


def ordered_list(passed_list):
    to_return = ''
    for index, list_element in enumerate(passed_list):
        to_return = to_return + str(index) + '. ' + list_element + line_break()
    return to_return


def unordered_list(passed_list):
    to_return = ''
    for list_element in passed_list:
        to_return = to_return + '* ' + list_element + line_break()


def link(text, url):
    return '[' + text + ']' + '(' + url + ')'


def image(alt_text, url):
    return '![' + alt_text + ']' + '(' + url + ')'


"""
MD Table

Has to be an array of arrays

Something like this

table = []
table.append(['Hero', 'Player', 'Level'])
table.append(['Earthshaker', 'eyyou', '21'])
table.append(['Outworld Devourer', 'ARMEL', '23'])
etc
"""


def table(passed_table):
    table_builder = ''
    for index, row in enumerate(passed_table):
        for column in row:
            table_builder = table_builder + '| ' + str(column) + ' '
        if index == 0:
            table_builder = table_builder + line_break()
            for x in range(len(row)):
                table_builder = table_builder + '| --- '
        table_builder = table_builder + line_break()
    table_builder += line_break()
    return table_builder


def block_quotes(text):
    return '> ' + text


def divider():
    return '---' + line_break()


def line_break():
    return '  \n'


def convert_hero(name):
    if name == 'Underlord':
        name_to_reddit_string = 'abyssalunderlord'  # Mods, please fix this literally every other hero is consistent...
    else:
        name_to_reddit_string = name.lower().replace(" ", "").replace("'", "")
    return f'[](/hero-{name_to_reddit_string} "{name}")'


def raw(text):
    return text


def build_markdown(series):
    markdown = ''
    """MAIN HEADER"""
    markdown += h1(f'{series.team_one.team.team_logo}'
                      f'{series.team_one.team.name} '
                      f'{series.team_one.score}-{series.team_two.score} '
                      f'{series.team_two.team.name}'
                      f'{series.team_two.team.team_logo}')
    markdown += divider()
    """Go through each match"""
    for match_index, match in enumerate(series.matches):
        """Scores and kills"""
        markdown += h2(bold(f'Game {match_index + 1}'))
        markdown += h2(f'{match.radiant.name} '
                          f'{match.radiant_score}-{match.dire_score} '
                          f'{match.dire.name}')
        markdown += h2(f'{match.winner.name} Victory')
        markdown += h2(f'{time.strftime("%H:%M:%S", time.gmtime(match.duration))}')

        """Picks and bans"""
        picks_table = []
        picks_row_heroes = []
        picks_row_teams = []
        bans_table = []
        bans_row_heroes = []
        bans_row_teams = []

        bans_table.append(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])
        picks_table.append(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])

        for pick_ban_index, pick_ban in enumerate(match.pick_bans):
            if pick_ban.isPick:
                picks_row_heroes.append(convert_hero(pick_ban.hero))
                picks_row_teams.append(pick_ban.team.team_logo)
            else:
                bans_row_heroes.append(convert_hero(pick_ban.hero))
                bans_row_teams.append(pick_ban.team.team_logo)

        markdown += h3(bold('Bans'))
        bans_table.append(bans_row_teams)
        bans_table.append(bans_row_heroes)
        markdown += table(bans_table)

        markdown += h3(bold('Picks'))
        picks_table.append(picks_row_teams)
        picks_table.append(picks_row_heroes)
        markdown += table(picks_table)

        """Game Stats"""
        markdown += h3(bold('Stats'))
        stats_table = list()
        stats_table.append(['Hero', 'Player', 'Level', 'K/D/A', 'GPM/XPM', 'LH/D', 'Items', '', '', '', '', ''])
        for player_index, player in enumerate(match.players):  # PLAYER STATS
            if player_index == 5:
                stats_table.append(['', '', '', '', '', ''])
            stats_table.append([
                convert_hero(player.hero),
                player.name,
                player.level,
                f'{player.kills}/{player.deaths}/{player.assists}',
                f'{player.gold_per_min}/{player.xp_per_min}',
                f'{player.last_hits}/{player.denies}',
                player.items[0],
                player.items[1],
                player.items[2],
                player.items[3],
                player.items[4],
                player.items[5]
            ])
        markdown += table(stats_table)

        """"Post-Match Links"""
        markdown += f'Detailed stats: {link("Dotabuff", f"https://www.dotabuff.com/matches/{match.match_id}")} | '\
            f' {link("Opendota", f"https://www.opendota.com/matches/{match.match_id}")} | ' \
            f' {link("Datdota", f"http://datdota.com/matches/{match.match_id}")} | ' \
            f' {link("Stratz", f"https://stratz.com/en-us/match/{match.match_id}")}'
        markdown += line_break()
        markdown += divider()
    markdown += line_break()
    markdown += italics('This action was performed by a bot. For more information, [see here](https://www.reddit.com/user/d2-match-bot-speaks/comments/c26lfw/introducing_the_dota_2_post_match_bot/). Contact: /u/d2-match-bot-speaks')
    return {'markdown': markdown,
            'title': f'{series.team_one.team.name} vs {series.team_two.team.name} / '
            f'{series.league.name} / Post-Match Discussion',
            'series_id': series.series_id}
