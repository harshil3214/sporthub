from django.db import models
from core.models import Team

class CricketMatch(models.Model):
    STATUS_CHOICES = [('UPCOMING', 'Upcoming'), ('LIVE', 'Live'), ('FINISHED', 'Finished')]
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='cricket_home')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='cricket_away')
    # Cricket needs Runs and Wickets
    home_runs = models.IntegerField(default=0)
    home_wickets = models.IntegerField(default=0)
    away_runs = models.IntegerField(default=0)
    away_wickets = models.IntegerField(default=0)
    match_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UPCOMING')
    highlights_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name}"