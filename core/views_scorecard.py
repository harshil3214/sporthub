from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from core.models import FootballMatch, CricketMatch, VolleyballMatch, UniversalMatch
import json
import random
from datetime import datetime, timedelta

def live_scorecard_api(request, match_id):
    """API endpoint for live scorecard data"""
    try:
        # Try to get match from different sport types
        match = None
        sport = None
        
        for match_model, sport_name in [
            (FootballMatch, 'football'),
            (CricketMatch, 'cricket'),
            (VolleyballMatch, 'volleyball'),
            (UniversalMatch, 'universal')
        ]:
            try:
                match = match_model.objects.get(id=match_id)
                sport = sport_name
                break
            except match_model.DoesNotExist:
                continue
        
        if not match:
            return JsonResponse({'error': 'Match not found'}, status=404)
        
        # Generate live scorecard data based on sport
        if sport == 'cricket':
            data = generate_cricket_scorecard(match)
        elif sport == 'football':
            data = generate_football_scorecard(match)
        elif sport == 'volleyball':
            data = generate_volleyball_scorecard(match)
        else:
            data = generate_generic_scorecard(match, sport)
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def static_scorecard_api(request, match_id):
    """API endpoint for static scorecard data (completed matches)"""
    try:
        # Try to get match from different sport types
        match = None
        sport = None
        
        for match_model, sport_name in [
            (FootballMatch, 'football'),
            (CricketMatch, 'cricket'),
            (VolleyballMatch, 'volleyball'),
            (UniversalMatch, 'universal')
        ]:
            try:
                match = match_model.objects.get(id=match_id)
                sport = sport_name
                break
            except match_model.DoesNotExist:
                continue
        
        if not match:
            return JsonResponse({'error': 'Match not found'}, status=404)
        
        # Generate static scorecard data
        if sport == 'cricket':
            data = generate_cricket_scorecard(match, static=True)
        elif sport == 'football':
            data = generate_football_scorecard(match, static=True)
        elif sport == 'volleyball':
            data = generate_volleyball_scorecard(match, static=True)
        else:
            data = generate_generic_scorecard(match, sport, static=True)
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def generate_cricket_scorecard(match, static=False):
    """Generate cricket scorecard data"""
    # Mock data for demonstration
    batting_scorecard = [
        {
            'name': 'Virat Kohli',
            'runs': random.randint(50, 120) if not static else 85,
            'balls': random.randint(30, 100) if not static else 92,
            'fours': random.randint(4, 12) if not static else 8,
            'sixes': random.randint(0, 5) if not static else 2,
            'strikeRate': f"{random.uniform(80, 150):.2f}" if not static else "92.39",
            'status': 'Batting' if not static else 'c. Smith b. Johnson'
        },
        {
            'name': 'Rohit Sharma',
            'runs': random.randint(30, 80) if not static else 45,
            'balls': random.randint(20, 60) if not static else 38,
            'fours': random.randint(2, 8) if not static else 6,
            'sixes': random.randint(0, 3) if not static else 1,
            'strikeRate': f"{random.uniform(100, 180):.2f}" if not static else "118.42",
            'status': 'Batting' if not static else 'c. Warner b. Cummins'
        },
        {
            'name': 'KL Rahul',
            'runs': random.randint(20, 60) if not static else 32,
            'balls': random.randint(15, 45) if not static else 28,
            'fours': random.randint(1, 6) if not static else 4,
            'sixes': random.randint(0, 2) if not static else 0,
            'strikeRate': f"{random.uniform(80, 140):.2f}" if not static else "114.29",
            'status': 'c. Smith b. Johnson'
        },
        {
            'name': 'Rishabh Pant',
            'runs': random.randint(15, 50) if not static else 28,
            'balls': random.randint(10, 35) if not static else 22,
            'fours': random.randint(1, 5) if not static else 3,
            'sixes': random.randint(0, 2) if not static else 1,
            'strikeRate': f"{random.uniform(100, 160):.2f}" if not static else "127.27",
            'status': 'c. Warner b. Cummins'
        }
    ]
    
    bowling_scorecard = [
        {
            'name': 'Pat Cummins',
            'overs': f"{random.randint(6, 10)}.{random.randint(0, 5)}" if not static else "8.3",
            'runs': random.randint(30, 60) if not static else 45,
            'wickets': random.randint(1, 4) if not static else 2,
            'economy': f"{random.uniform(4.5, 7.5):.2f}" if not static else "5.29",
            'dots': random.randint(12, 25) if not static else 18,
            'fours': random.randint(2, 6) if not static else 4,
            'sixes': random.randint(0, 3) if not static else 1
        },
        {
            'name': 'Mitchell Starc',
            'overs': f"{random.randint(7, 10)}.{random.randint(0, 5)}" if not static else "9.0",
            'runs': random.randint(35, 70) if not static else 52,
            'wickets': random.randint(0, 3) if not static else 1,
            'economy': f"{random.uniform(5.0, 8.0):.2f}" if not static else "5.78",
            'dots': random.randint(10, 20) if not static else 15,
            'fours': random.randint(3, 7) if not static else 5,
            'sixes': random.randint(1, 4) if not static else 2
        },
        {
            'name': 'Josh Hazlewood',
            'overs': f"{random.randint(6, 9)}.{random.randint(0, 5)}" if not static else "8.0",
            'runs': random.randint(25, 50) if not static else 38,
            'wickets': random.randint(0, 3) if not static else 1,
            'economy': f"{random.uniform(4.0, 6.5):.2f}" if not static else "4.75",
            'dots': random.randint(15, 25) if not static else 20,
            'fours': random.randint(2, 5) if not static else 3,
            'sixes': random.randint(0, 2) if not static else 0
        }
    ]
    
    commentary = [
        {
            'time': f"{random.randint(40, 50)}.{random.randint(0, 5)}" if not static else "45.3",
            'text': random.choice([
                'FOUR! Beautiful cover drive by Kohli, finds the gap perfectly',
                'SIX! Massive hit over long-on by Rohit Sharma!',
                'DOT BALL! Good length delivery, defended back to the bowler',
                'SINGLE! Rohit pushes it to mid-wicket for a quick single',
                'WICKET! Clean bowled! Hazlewood strikes!'
            ]) if not static else 'FOUR! Beautiful cover drive by Kohli, finds the gap perfectly'
        },
        {
            'time': f"{random.randint(40, 50)}.{random.randint(0, 5)}" if not static else "45.2",
            'text': random.choice([
                'SINGLE! Rohit pushes it to mid-wicket for a quick single',
                'Excellent running between the wickets',
                'Good fielding effort in the deep',
                'Just a single from that delivery'
            ]) if not static else 'SINGLE! Rohit pushes it to mid-wicket for a quick single'
        },
        {
            'time': f"{random.randint(40, 50)}.{random.randint(0, 5)}" if not static else "45.1",
            'text': 'DOT BALL! Good length delivery, defended back to the bowler'
        },
        {
            'time': f"{random.randint(40, 50)}.{random.randint(0, 5)}" if not static else "45.0",
            'text': 'SIX! Massive hit over long-on by Rohit Sharma!'
        }
    ]
    
    # Calculate statistics
    total_runs = match.home_score + match.away_score
    total_wickets = random.randint(4, 10) if not static else 4
    total_overs = f"{random.randint(40, 50)}.{random.randint(0, 5)}" if not static else "45.3"
    run_rate = f"{random.uniform(5.5, 8.5):.1f}" if not static else "6.8"
    partnership = random.randint(50, 120) if not static else 87
    required_rate = f"{random.uniform(6.0, 8.5):.1f}" if not static else "7.2"
    
    return {
        'matchId': match.id,
        'sport': 'cricket',
        'status': 'LIVE' if not static else 'COMPLETED',
        'homeScore': match.home_score + (random.randint(0, 5) if not static else 0),
        'awayScore': match.away_score + (random.randint(0, 5) if not static else 0),
        'battingScorecard': batting_scorecard,
        'bowlingScorecard': bowling_scorecard,
        'commentary': commentary,
        'statistics': {
            'totalRuns': total_runs,
            'totalWickets': total_wickets,
            'totalOvers': total_overs,
            'runRate': run_rate,
            'partnership': partnership,
            'requiredRate': required_rate
        },
        'over': total_overs if not static else None
    }

def generate_football_scorecard(match, static=False):
    """Generate football scorecard data"""
    events = [
        {
            'minute': random.randint(1, 90) if not static else 23,
            'player': 'Erling Haaland',
            'team': 'Manchester City',
            'type': 'goal',
            'description': 'GOAL! Haaland scores with a powerful header!'
        },
        {
            'minute': random.randint(1, 90) if not static else 67,
            'player': 'Bukayo Saka',
            'team': 'Arsenal',
            'type': 'goal',
            'description': 'GOAL! Saka finishes beautifully after a great team move!'
        },
        {
            'minute': random.randint(1, 90) if not static else 45,
            'player': 'Rodri',
            'team': 'Manchester City',
            'type': 'yellow_card',
            'description': 'Yellow card for Rodri for a tactical foul'
        }
    ]
    
    statistics = {
        'possession': {
            'home': f"{random.randint(45, 65)}%" if not static else "58%",
            'away': f"{random.randint(35, 55)}%" if not static else "42%"
        },
        'shots': {
            'home': random.randint(8, 20) if not static else 15,
            'away': random.randint(5, 15) if not static else 9
        },
        'corners': {
            'home': random.randint(3, 10) if not static else 6,
            'away': random.randint(2, 8) if not static else 4
        },
        'fouls': {
            'home': random.randint(8, 18) if not static else 12,
            'away': random.randint(10, 20) if not static else 14
        }
    }
    
    return {
        'matchId': match.id,
        'sport': 'football',
        'status': 'LIVE' if not static else 'COMPLETED',
        'homeScore': match.home_score,
        'awayScore': match.away_score,
        'events': events,
        'statistics': statistics,
        'minute': random.randint(1, 90) if not static else None
    }

def generate_volleyball_scorecard(match, static=False):
    """Generate volleyball scorecard data"""
    sets = [
        {
            'set': 1,
            'homeScore': random.randint(15, 25) if not static else 25,
            'awayScore': random.randint(10, 23) if not static else 23
        },
        {
            'set': 2,
            'homeScore': random.randint(15, 25) if not static else 21,
            'awayScore': random.randint(15, 25) if not static else 25
        },
        {
            'set': 3,
            'homeScore': random.randint(15, 25) if not static else 25,
            'awayScore': random.randint(15, 23) if not static else 20
        }
    ]
    
    top_players = [
        {
            'player': 'Player One',
            'team': 'Team A',
            'points': random.randint(15, 30) if not static else 24,
            'attacks': random.randint(10, 25) if not static else 18,
            'blocks': random.randint(3, 10) if not static else 6
        },
        {
            'player': 'Player Two',
            'team': 'Team B',
            'points': random.randint(15, 30) if not static else 22,
            'attacks': random.randint(10, 25) if not static else 16,
            'blocks': random.randint(3, 10) if not static else 5
        }
    ]
    
    return {
        'matchId': match.id,
        'sport': 'volleyball',
        'status': 'LIVE' if not static else 'COMPLETED',
        'homeScore': match.home_sets_won,
        'awayScore': match.away_sets_won,
        'sets': sets,
        'topPlayers': top_players,
        'currentSet': random.randint(1, 3) if not static else None
    }

def generate_generic_scorecard(match, sport, static=False):
    """Generate generic scorecard data for other sports"""
    return {
        'matchId': match.id,
        'sport': sport,
        'status': 'LIVE' if not static else 'COMPLETED',
        'homeScore': match.home_score,
        'awayScore': match.away_score,
        'events': [
            {
                'time': f"{random.randint(1, 60)}'" if not static else "15'",
                'description': 'Match in progress'
            }
        ]
    }
