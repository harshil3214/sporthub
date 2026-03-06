import requests
from .models import CricketMatch, FootballMatch, VolleyballMatch
from django.utils.dateparse import parse_datetime

# Keys from your provided dashboards
CRIC_API_KEY = "f240b8c4-82bc-4bbf-8f31-36fd9c9d035b"
API_SPORTS_KEY = "09fa11b099cf7916e99f3ebb40562dba"

def update_match_from_api(match):
    """
    Main entry point called by Admin actions. 
    Determines the sport and calls the appropriate fetcher.
    """
    if not match.external_api_id:
        return False

    # Check match type and route to the correct helper
    if isinstance(match, CricketMatch):
        return sync_cricket(match)
    elif isinstance(match, FootballMatch):
        return sync_football(match)
    elif isinstance(match, VolleyballMatch):
        return sync_volleyball(match)
    
    return False

# --- CRICKET LOGIC (CricketData.org) ---

def sync_cricket(match):
    url = f"https://api.cricapi.com/v1/match_info?apikey={CRIC_API_KEY}&id={match.external_api_id}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("status") == "success":
            match_data = data.get("data", {})
            scores = match_data.get("score", [])

            # Common metadata (best-effort; API fields vary)
            series_name = match_data.get("series") or match_data.get("seriesName") or ""
            if series_name:
                match.competition_name = series_name
            match_type = match_data.get("matchType") or match_data.get("match_type") or ""
            if match_type:
                match.round_name = match_type
            venue = match_data.get("venue")
            if isinstance(venue, str) and venue:
                match.venue = venue
            elif isinstance(venue, dict):
                match.venue = venue.get("name") or match.venue
                match.city = venue.get("city") or match.city
                match.country = venue.get("country") or match.country

            dt_str = match_data.get("dateTimeGMT") or match_data.get("dateTime") or match_data.get("date") or ""
            if dt_str:
                dt = parse_datetime(dt_str)
                if dt:
                    match.match_datetime = dt
            
            if len(scores) >= 1:
                match.home_runs = scores[0].get("r", 0)
                match.home_wickets = scores[0].get("w", 0)
                match.home_overs = scores[0].get("o", 0.0)
            if len(scores) >= 2:
                match.away_runs = scores[1].get("r", 0)
                match.away_wickets = scores[1].get("w", 0)
                match.away_overs = scores[1].get("o", 0.0)

            match.current_status_text = match_data.get("status", "")
            if match_data.get("matchEnded"):
                match.status = 'FINISHED'
            elif match_data.get("matchStarted"):
                match.status = 'LIVE'
            
            match.save()
            return True
    except Exception as e:
        print(f"Cricket Sync Error: {e}")
    return False

# --- FOOTBALL & VOLLEYBALL LOGIC (API-Sports) ---

def sync_football(match):
    url = f"https://v3.football.api-sports.io/fixtures?id={match.external_api_id}"
    headers = {
        'x-apisports-key': API_SPORTS_KEY,
        'x-apisports-host': "v3.football.api-sports.io"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        if data.get("response"):
            fixture = data["response"][0]

            # Common metadata (league/round/venue/referee/datetime)
            league = fixture.get("league") or {}
            match.competition_name = league.get("name") or match.competition_name
            if league.get("season") is not None:
                match.season_name = str(league.get("season"))
            match.round_name = league.get("round") or match.round_name

            fixture_info = fixture.get("fixture") or {}
            venue = fixture_info.get("venue") or {}
            if isinstance(venue, dict):
                match.venue = venue.get("name") or match.venue
                match.city = venue.get("city") or match.city
            match.referee = fixture_info.get("referee") or match.referee

            dt_str = fixture_info.get("date") or ""
            if dt_str:
                dt = parse_datetime(dt_str)
                if dt:
                    match.match_datetime = dt

            match.home_score = fixture["goals"]["home"]
            match.away_score = fixture["goals"]["away"]
            
            # Map API status to your model status
            api_status = fixture["fixture"]["status"]["short"]
            if api_status == "FT":
                match.status = 'FINISHED'
            elif api_status in ["1H", "2H", "HT"]:
                match.status = 'LIVE'
                
            match.save()
            return True
    except Exception as e:
        print(f"Football Sync Error: {e}")
    return False

def sync_volleyball(match):
    url = f"https://v1.volleyball.api-sports.io/fixtures?id={match.external_api_id}"
    headers = {
        'x-apisports-key': API_SPORTS_KEY,
        'x-apisports-host': "v1.volleyball.api-sports.io"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        if data.get("response"):
            fixture = data["response"][0]

            # Common metadata (best-effort; depends on API payload)
            league = fixture.get("league") or {}
            match.competition_name = league.get("name") or match.competition_name
            if league.get("season") is not None:
                match.season_name = str(league.get("season"))
            match.round_name = league.get("round") or match.round_name

            fixture_info = fixture.get("fixture") or {}
            venue = fixture_info.get("venue") or {}
            if isinstance(venue, dict):
                match.venue = venue.get("name") or match.venue
                match.city = venue.get("city") or match.city
            match.referee = fixture_info.get("referee") or match.referee

            dt_str = fixture_info.get("date") or ""
            if dt_str:
                dt = parse_datetime(dt_str)
                if dt:
                    match.match_datetime = dt

            match.home_sets_won = fixture["scores"]["home"]
            match.away_sets_won = fixture["scores"]["away"]
            
            api_status = fixture["fixture"]["status"]["short"]
            if api_status == "FT":
                match.status = 'FINISHED'
            else:
                match.status = 'LIVE'
                
            match.save()
            return True
    except Exception as e:
        print(f"Volleyball Sync Error: {e}")
    return False

# --- HELPER TO FIND IDs ---

def get_live_ids(sport_type='football'):
    """
    Run in shell to find IDs for Football, Volleyball, or Basketball.
    Example: get_live_ids('volleyball')
    """
    host = f"v1.{sport_type}.api-sports.io"
    if sport_type == 'football': host = "v3.football.api-sports.io"
    
    url = f"https://{host}/fixtures?live=all"
    headers = {'x-apisports-key': API_SPORTS_KEY, 'x-apisports-host': host}
    
    resp = requests.get(url, headers=headers).json()
    for item in resp.get("response", []):
        fixture_id = item['fixture']['id']
        teams = f"{item['teams']['home']['name']} vs {item['teams']['away']['name']}"
        print(f"ID: {fixture_id} | Match: {teams}")