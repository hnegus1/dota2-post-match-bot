import make_request
from model import PickBan


class Match:
    def __init__(self, **kwargs):
        self.match_id = kwargs['match_id']
        self.radiant = kwargs['radiant']
        self.dire = kwargs['dire']

        if kwargs['radiant_win']:
            self.winner = self.radiant
        else:
            self.winner = self.dire

        self.players = kwargs['players']
        self.radiant_score = kwargs['radiant_score']
        self.dire_score = kwargs['dire_score']
        self.duration = kwargs['duration']
        self.pick_bans = kwargs['pick_bans']

