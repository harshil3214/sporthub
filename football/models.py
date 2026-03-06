from django.db import models
from core.models import Team

class FootballMatch(models.Model):
    STATUS_CHOICES = [('UPCOMING', 'Upcoming'), ('LIVE', 'Live'), ('FINISHED', 'Finished')]
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='football_home')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='football_away')
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    match_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UPCOMING')
    highlights_url = models.URLField(blank=True, help_text="YouTube URL")

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name}"