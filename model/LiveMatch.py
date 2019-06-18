class LiveMatch:
    def __init__(self, **kwargs):
        self.match_id = kwargs['match_id']
        self.league = kwargs['league']
        self.radiant_live_team = kwargs['radiant_live_team']
        self.dire_live_team = kwargs['dire_live_team']
        self.series_type = kwargs['series_type']
