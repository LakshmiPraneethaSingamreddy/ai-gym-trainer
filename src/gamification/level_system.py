class LevelSystem:

    def xp_needed(self, level):
        # Exponential progression: each level costs roughly 1.5x previous
        # Level 1 → 500 XP
        # Level 2 → 1000 XP
        # Level 3 → 1500 XP
        # Level 4 → 2000 XP
        # etc.
        return int(500 * level)

    def check_level_up(self, player):

        required_xp = self.xp_needed(player.level)

        while player.xp >= required_xp:
            player.xp -= required_xp
            player.level_up()
            required_xp = self.xp_needed(player.level)
