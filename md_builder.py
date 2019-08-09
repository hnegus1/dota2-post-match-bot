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


def md_list(py_list):
    list_builder = ''
    for x in py_list:
        list_builder += f'* x' + line_break()
    return list_builder