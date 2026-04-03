class LevelSystem:
    """Manages level progression with exponential XP requirements."""

    def xp_needed(self, level):
        """Get XP required to reach next level.
        
        Args:
            level: Current level.
        
        Returns:
            int: XP needed for next level (500 * level).
        """
        # Exponential progression: each level costs roughly 1.5x previous
        # Level 1 → 500 XP
        # Level 2 → 1000 XP
        # Level 3 → 1500 XP
        # Level 4 → 2000 XP
        # etc.
        return int(500 * level)

    def check_level_up(self, player):
        """Check and apply level ups if XP threshold reached.
        
        Args:
            player: Player profile to update.
        """

        required_xp = self.xp_needed(player.level)

        while player.xp >= required_xp:
            player.xp -= required_xp
            player.level_up()
            required_xp = self.xp_needed(player.level)
