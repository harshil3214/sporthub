from celery import shared_task
from .models import CricketMatch, FootballMatch, VolleyballMatch
from .services import update_match_from_api

@shared_task
def update_all_live_matches():
    """
    This task finds all matches currently marked as 'LIVE' 
    and updates them using the API.
    """
    # 1. Update Cricket
    live_cricket = CricketMatch.objects.filter(status='LIVE', data_source='API')
    for match in live_cricket:
        update_match_from_api(match)

    # 2. Update Football
    live_football = FootballMatch.objects.filter(status='LIVE', data_source='API')
    for match in live_football:
        update_match_from_api(match)

    # 3. Update Volleyball
    live_volleyball = VolleyballMatch.objects.filter(status='LIVE', data_source='API')
    for match in live_volleyball:
        update_match_from_api(match)

    return f"Updated {live_cricket.count() + live_football.count() + live_volleyball.count()} matches."