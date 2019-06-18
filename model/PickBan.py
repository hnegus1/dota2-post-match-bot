import utilities as util


class PickBan:
    def __init__(self, **kwargs):
        self.isPick = kwargs['is_pick']
        self.hero = util.resolve_hero(kwargs['hero_id'])
        self.order = kwargs['order'] + 1
        self.team = kwargs['team']
