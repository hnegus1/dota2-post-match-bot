class Series:
    def __init__(self, **kwargs):
        self.series_id = kwargs['series_id']
        self.league = kwargs['league']
        self.matches = kwargs['matches']
        self.team_one = kwargs['team_one']
        self.team_two = kwargs['team_two']
        self.type = kwargs['type']
