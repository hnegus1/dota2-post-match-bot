class LiveSeries:
    def __init__(self, **kwargs):
        self.series_id = kwargs['series_id']
        self.league = kwargs['league']
        self.live_team_one = kwargs['live_team_one']
        self.live_team_two = kwargs['live_team_two']
        self.series_type = kwargs['series_type']
        self.live_matches = kwargs['live_matches']
