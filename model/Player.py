class Player:
    def __init__(self, **kwargs):
        self.name = kwargs['name']

        self.hero = kwargs['hero']
        self.items = kwargs['items']

        self.kills = kwargs['kills']
        self.deaths = kwargs['deaths']
        self.assists = kwargs['assists']
        self.level = kwargs['level']
        self.net_worth = kwargs['net_worth']
        self.gold_per_min = kwargs['gold_per_min']
        self.xp_per_min = kwargs['xp_per_min']
        self.last_hits = kwargs['last_hits']
        self.denies = kwargs['denies']
        self.scaled_hero_damage = kwargs['scaled_hero_damage']
        self.scaled_hero_healing = kwargs['scaled_hero_healing']
        self.scaled_tower_damage = kwargs['scaled_tower_damage']
