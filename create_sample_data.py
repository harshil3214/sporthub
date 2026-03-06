import os
import sys
import django
from datetime import datetime, timedelta
import pytz

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Team, FootballMatch, CricketMatch, UniversalMatch

# Clear existing data
print("Clearing existing data...")
Team.objects.all().delete()
FootballMatch.objects.all().delete()
CricketMatch.objects.all().delete()
UniversalMatch.objects.all().delete()

# Create Teams
print("Creating teams...")
teams_data = [
    # Football Teams
    {"name": "Manchester United", "sport": "FOOTBALL"},
    {"name": "Liverpool", "sport": "FOOTBALL"},
    {"name": "Chelsea", "sport": "FOOTBALL"},
    {"name": "Arsenal", "sport": "FOOTBALL"},
    {"name": "Manchester City", "sport": "FOOTBALL"},
    {"name": "Tottenham", "sport": "FOOTBALL"},
    
    # Cricket Teams
    {"name": "India", "sport": "CRICKET"},
    {"name": "Australia", "sport": "CRICKET"},
    {"name": "England", "sport": "CRICKET"},
    {"name": "Pakistan", "sport": "CRICKET"},
    {"name": "South Africa", "sport": "CRICKET"},
    {"name": "New Zealand", "sport": "CRICKET"},
    
    # Other Sports
    {"name": "Los Angeles Lakers", "sport": "BASKETBALL"},
    {"name": "Golden State Warriors", "sport": "BASKETBALL"},
    {"name": "Brooklyn Nets", "sport": "BASKETBALL"},
    {"name": "Boston Celtics", "sport": "BASKETBALL"},
    
    {"name": "Novak Djokovic", "sport": "TENNIS"},
    {"name": "Rafael Nadal", "sport": "TENNIS"},
    {"name": "Roger Federer", "sport": "TENNIS"},
    
    {"name": "India National", "sport": "KABADDI"},
    {"name": "Iran National", "sport": "KABADDI"},
    {"name": "South Korea National", "sport": "KABADDI"},
]

teams = {}
for team_data in teams_data:
    team = Team.objects.create(**team_data)
    teams[team.name] = team
    print(f"Created team: {team.name}")

# Set timezone
tz = pytz.timezone('Asia/Kolkata')
now = datetime.now(tz)

# Create Football Matches
print("\nCreating football matches...")
football_matches = [
    {
        "home_team": teams["Manchester United"],
        "away_team": teams["Liverpool"],
        "home_score": 2,
        "away_score": 1,
        "status": "LIVE",
        "competition_name": "Premier League",
        "country": "England",
        "venue": "Old Trafford",
        "match_datetime": now,
    },
    {
        "home_team": teams["Chelsea"],
        "away_team": teams["Arsenal"],
        "home_score": 0,
        "away_score": 0,
        "status": "UPCOMING",
        "competition_name": "Premier League",
        "country": "England",
        "venue": "Stamford Bridge",
        "match_datetime": now + timedelta(hours=3),
    },
    {
        "home_team": teams["Manchester City"],
        "away_team": teams["Tottenham"],
        "home_score": 3,
        "away_score": 1,
        "status": "FINISHED",
        "competition_name": "Premier League",
        "country": "England",
        "venue": "Etihad Stadium",
        "match_datetime": now - timedelta(hours=2),
    }
]

for match_data in football_matches:
    match = FootballMatch.objects.create(**match_data)
    print(f"Created football match: {match.home_team.name} vs {match.away_team.name}")

# Create Cricket Matches
print("\nCreating cricket matches...")
cricket_matches = [
    {
        "home_team": teams["India"],
        "away_team": teams["Australia"],
        "home_runs": 245,
        "home_wickets": 8,
        "home_overs": 45.2,
        "away_runs": 180,
        "away_wickets": 4,
        "away_overs": 32.0,
        "status": "LIVE",
        "competition_name": "ICC World Cup",
        "country": "International",
        "venue": "Wankhede Stadium, Mumbai",
        "match_datetime": now - timedelta(hours=1),
        "current_status_text": "India 245/8 (45.2 ov)",
        "is_live_now": True,
        "toss_winner": teams["Australia"],
        "toss_decision": "BAT"
    },
    {
        "home_team": teams["England"],
        "away_team": teams["Pakistan"],
        "home_runs": 0,
        "home_wickets": 0,
        "home_overs": 0.0,
        "away_runs": 0,
        "away_wickets": 0,
        "away_overs": 0.0,
        "status": "UPCOMING",
        "competition_name": "ICC World Cup",
        "country": "International",
        "venue": "Lord's, London",
        "match_datetime": now + timedelta(hours=5),
        "current_status_text": "Match starts at 15:00"
    }
]

for match_data in cricket_matches:
    match = CricketMatch.objects.create(**match_data)
    print(f"Created cricket match: {match.home_team.name} vs {match.away_team.name}")

# Create Universal Matches for other sports
print("\nCreating universal matches...")
universal_matches = [
    {
        "sport": "BASKETBALL",
        "home_team": teams["Los Angeles Lakers"],
        "away_team": teams["Golden State Warriors"],
        "home_score": "98",
        "away_score": "102",
        "status": "LIVE",
        "competition_name": "NBA",
        "country": "USA",
        "venue": "Staples Center",
        "match_datetime": now - timedelta(minutes=30),
        "match_info": "4th Quarter - 2:45"
    },
    {
        "sport": "TENNIS",
        "home_team": teams["Novak Djokovic"],
        "away_team": teams["Rafael Nadal"],
        "home_score": "6-4, 3-6",
        "away_score": "4-6, 6-3",
        "status": "LIVE",
        "competition_name": "Wimbledon",
        "country": "England",
        "venue": "Centre Court",
        "match_datetime": now,
        "match_info": "3rd Set - 4-4"
    },
    {
        "sport": "KABADDI",
        "home_team": teams["India National"],
        "away_team": teams["Iran National"],
        "home_score": "45",
        "away_score": "38",
        "status": "FINISHED",
        "competition_name": "Asian Games",
        "country": "International",
        "venue": "Hangzhou",
        "match_datetime": now - timedelta(hours=4),
        "match_info": "Full Time"
    }
]

for match_data in universal_matches:
    match = UniversalMatch.objects.create(**match_data)
    print(f"Created {match.sport} match: {match.home_team.name} vs {match.away_team.name}")

# Update team points
print("\nUpdating team points...")
for team in Team.objects.all():
    team.update_points()
    print(f"Updated points for {team.name}: {team.total_points}")

print("\nSample data creation completed!")
print(f"Created {Team.objects.count()} teams")
print(f"Created {FootballMatch.objects.count()} football matches")
print(f"Created {CricketMatch.objects.count()} cricket matches")
print(f"Created {UniversalMatch.objects.count()} universal matches")

# Create superuser if not exists
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("\nCreated superuser: admin/admin123")
else:
    print("\nSuperuser 'admin' already exists")
