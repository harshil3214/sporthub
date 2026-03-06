import os
import django
from django.utils import timezone
from datetime import datetime, timedelta
import random

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import (
    Team, Player, Competition, Season, Standing, 
    FootballMatch, CricketMatch, VolleyballMatch, UniversalMatch,
    PlayerRanking, UserFavorites, HeadToHead, NewsArticle,
    TeacherProfile, StudentProfile
)
from django.contrib.auth.models import User

def create_comprehensive_sample_data():
    """Create comprehensive sample data for Flashscore-like features"""
    
    print("Creating comprehensive sample data...")
    
    # Create admin user if not exists
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@sports.com',
            'is_superuser': True,
            'is_staff': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("Created admin user")
    
    # Create teacher and student profiles
    teacher_user, created = User.objects.get_or_create(
        username='teacher1',
        defaults={'email': 'teacher@sports.com'}
    )
    if created:
        teacher_user.set_password('teacher123')
        teacher_user.save()
        TeacherProfile.objects.create(user=teacher_user, department="Physical Education")
    
    student_user, created = User.objects.get_or_create(
        username='student1',
        defaults={'email': 'student@sports.com'}
    )
    if created:
        student_user.set_password('student123')
        student_user.save()
        StudentProfile.objects.create(user=student_user, assigned_teacher=TeacherProfile.objects.first())
    
    # Create Competitions
    competitions_data = [
        # Football
        {'name': 'Premier League', 'sport': 'FOOTBALL', 'country': 'England', 'category': 'League', 'priority': 10},
        {'name': 'La Liga', 'sport': 'FOOTBALL', 'country': 'Spain', 'category': 'League', 'priority': 9},
        {'name': 'UEFA Champions League', 'sport': 'FOOTBALL', 'country': 'Europe', 'category': 'Cup', 'priority': 10},
        {'name': 'FIFA World Cup', 'sport': 'FOOTBALL', 'country': 'International', 'category': 'Tournament', 'priority': 10},
        {'name': 'Serie A', 'sport': 'FOOTBALL', 'country': 'Italy', 'category': 'League', 'priority': 8},
        {'name': 'Bundesliga', 'sport': 'FOOTBALL', 'country': 'Germany', 'category': 'League', 'priority': 8},
        
        # Cricket
        {'name': 'Indian Premier League', 'sport': 'CRICKET', 'country': 'India', 'category': 'League', 'priority': 10},
        {'name': 'ICC Cricket World Cup', 'sport': 'CRICKET', 'country': 'International', 'category': 'Tournament', 'priority': 10},
        {'name': 'The Ashes', 'sport': 'CRICKET', 'country': 'International', 'category': 'Series', 'priority': 9},
        
        # Tennis
        {'name': 'Wimbledon', 'sport': 'TENNIS', 'country': 'UK', 'category': 'Grand Slam', 'priority': 10},
        {'name': 'US Open', 'sport': 'TENNIS', 'country': 'USA', 'category': 'Grand Slam', 'priority': 9},
        {'name': 'ATP Finals', 'sport': 'TENNIS', 'country': 'International', 'category': 'Tournament', 'priority': 8},
        
        # Basketball
        {'name': 'NBA', 'sport': 'BASKETBALL', 'country': 'USA', 'category': 'League', 'priority': 10},
        {'name': 'EuroLeague', 'sport': 'BASKETBALL', 'country': 'Europe', 'category': 'League', 'priority': 8},
        
        # Volleyball
        {'name': 'CEV Champions League', 'sport': 'VOLLEYBALL', 'country': 'Europe', 'category': 'League', 'priority': 9},
        {'name': 'FIVB World Championship', 'sport': 'VOLLEYBALL', 'country': 'International', 'category': 'Tournament', 'priority': 10},
        
        # Other sports
        {'name': 'ATP Tour', 'sport': 'TENNIS', 'country': 'International', 'category': 'Tour', 'priority': 7},
        {'name': 'Kabaddi Pro League', 'sport': 'KABADDI', 'country': 'India', 'category': 'League', 'priority': 7},
        {'name': 'BWF World Tour', 'sport': 'BADMINTON', 'country': 'International', 'category': 'Tour', 'priority': 7},
    ]
    
    competitions = []
    for comp_data in competitions_data:
        comp, created = Competition.objects.get_or_create(
            name=comp_data['name'],
            sport=comp_data['sport'],
            country=comp_data['country'],
            defaults=comp_data
        )
        competitions.append(comp)
        if created:
            print(f"Created competition: {comp.name}")
    
    # Create Seasons for major competitions
    seasons = []
    for comp in competitions[:6]:  # Create seasons for top 6 competitions
        season, created = Season.objects.get_or_create(
            competition=comp,
            name=f"2023/24",
            defaults={
                'start_date': datetime(2023, 8, 1).date(),
                'end_date': datetime(2024, 5, 31).date(),
                'is_current': True
            }
        )
        seasons.append(season)
        if created:
            print(f"Created season: {season.name}")
    
    # Create Teams
    teams_data = [
        # Football Teams
        {'name': 'Manchester United', 'sport': 'FOOTBALL', 'country': 'England', 'stadium': 'Old Trafford'},
        {'name': 'Liverpool', 'sport': 'FOOTBALL', 'country': 'England', 'stadium': 'Anfield'},
        {'name': 'Manchester City', 'sport': 'FOOTBALL', 'country': 'England', 'stadium': 'Etihad Stadium'},
        {'name': 'Chelsea', 'sport': 'FOOTBALL', 'country': 'England', 'stadium': 'Stamford Bridge'},
        {'name': 'Arsenal', 'sport': 'FOOTBALL', 'country': 'England', 'stadium': 'Emirates Stadium'},
        {'name': 'Real Madrid', 'sport': 'FOOTBALL', 'country': 'Spain', 'stadium': 'Santiago Bernabéu'},
        {'name': 'Barcelona', 'sport': 'FOOTBALL', 'country': 'Spain', 'stadium': 'Camp Nou'},
        {'name': 'Bayern Munich', 'sport': 'FOOTBALL', 'country': 'Germany', 'stadium': 'Allianz Arena'},
        
        # Cricket Teams
        {'name': 'Mumbai Indians', 'sport': 'CRICKET', 'country': 'India', 'stadium': 'Wankhede Stadium'},
        {'name': 'Chennai Super Kings', 'sport': 'CRICKET', 'country': 'India', 'stadium': 'M.A. Chidambaram Stadium'},
        {'name': 'Royal Challengers Bangalore', 'sport': 'CRICKET', 'country': 'India', 'stadium': 'M. Chinnaswamy Stadium'},
        {'name': 'Australia', 'sport': 'CRICKET', 'country': 'Australia', 'stadium': 'Melbourne Cricket Ground'},
        {'name': 'India', 'sport': 'CRICKET', 'country': 'India', 'stadium': 'Eden Gardens'},
        
        # Tennis Players (as teams for individual sports)
        {'name': 'Novak Djokovic', 'sport': 'TENNIS', 'country': 'Serbia'},
        {'name': 'Rafael Nadal', 'sport': 'TENNIS', 'country': 'Spain'},
        {'name': 'Roger Federer', 'sport': 'TENNIS', 'country': 'Switzerland'},
        
        # Basketball Teams
        {'name': 'Los Angeles Lakers', 'sport': 'BASKETBALL', 'country': 'USA', 'stadium': 'Crypto.com Arena'},
        {'name': 'Golden State Warriors', 'sport': 'BASKETBALL', 'country': 'USA', 'stadium': 'Chase Center'},
        {'name': 'Boston Celtics', 'sport': 'BASKETBALL', 'country': 'USA', 'stadium': 'TD Garden'},
        
        # Volleyball Teams
        {'name': 'Italy Volley', 'sport': 'VOLLEYBALL', 'country': 'Italy'},
        {'name': 'Brazil Volley', 'sport': 'VOLLEYBALL', 'country': 'Brazil'},
        {'name': 'Russia Volley', 'sport': 'VOLLEYBALL', 'country': 'Russia'},
        
        # Other sports
        {'name': 'India Kabaddi', 'sport': 'KABADDI', 'country': 'India'},
        {'name': 'Iran Kabaddi', 'sport': 'KABADDI', 'country': 'Iran'},
    ]
    
    teams = []
    for team_data in teams_data:
        team, created = Team.objects.get_or_create(
            name=team_data['name'],
            sport=team_data['sport'],
            defaults=team_data
        )
        teams.append(team)
        if created:
            print(f"Created team: {team.name}")
    
    # Create Players
    players_data = [
        # Football Players
        {'name': 'Cristiano Ronaldo', 'team': 'Real Madrid', 'position': 'FWD', 'jersey_number': 7},
        {'name': 'Lionel Messi', 'team': 'Barcelona', 'position': 'FWD', 'jersey_number': 10},
        {'name': 'Erling Haaland', 'team': 'Manchester City', 'position': 'FWD', 'jersey_number': 9},
        {'name': 'Kevin De Bruyne', 'team': 'Manchester City', 'position': 'MID', 'jersey_number': 17},
        {'name': 'Mohamed Salah', 'team': 'Liverpool', 'position': 'FWD', 'jersey_number': 11},
        {'name': 'Virgil van Dijk', 'team': 'Liverpool', 'position': 'DEF', 'jersey_number': 4},
        {'name': 'Marcus Rashford', 'team': 'Manchester United', 'position': 'FWD', 'jersey_number': 10},
        {'name': 'Bruno Fernandes', 'team': 'Manchester United', 'position': 'MID', 'jersey_number': 8},
        
        # Cricket Players
        {'name': 'Virat Kohli', 'team': 'India', 'position': 'BATS', 'jersey_number': 18},
        {'name': 'Rohit Sharma', 'team': 'India', 'position': 'BATS', 'jersey_number': 45},
        {'name': 'Jasprit Bumrah', 'team': 'India', 'position': 'BOWL', 'jersey_number': 93},
        {'name': 'MS Dhoni', 'team': 'Chennai Super Kings', 'position': 'WK', 'jersey_number': 7},
        {'name': 'Rohit Sharma', 'team': 'Mumbai Indians', 'position': 'BATS', 'jersey_number': 45},
        
        # Basketball Players
        {'name': 'LeBron James', 'team': 'Los Angeles Lakers', 'position': 'FWD', 'jersey_number': 23},
        {'name': 'Stephen Curry', 'team': 'Golden State Warriors', 'position': 'MID', 'jersey_number': 30},
        {'name': 'Kevin Durant', 'team': 'Brooklyn Nets', 'position': 'FWD', 'jersey_number': 35},
    ]
    
    players = []
    for player_data in players_data:
        team = next((t for t in teams if t.name == player_data['team']), None)
        if team:
            player, created = Player.objects.get_or_create(
                name=player_data['name'],
                defaults={
                    'team': team,
                    'position': player_data['position'],
                    'jersey_number': player_data['jersey_number'],
                    'nationality': team.country,
                    'matches_played': random.randint(50, 500),
                    'goals_scored': random.randint(0, 200) if player_data['position'] in ['FWD', 'MID'] else random.randint(0, 20),
                    'assists': random.randint(0, 100),
                }
            )
            players.append(player)
            if created:
                print(f"Created player: {player.name}")
    
    # Create Standings
    for season in seasons:
        competition = season.competition
        if competition.sport == 'FOOTBALL':
            # Get football teams for this competition
            comp_teams = [t for t in teams if t.sport == 'FOOTBALL' and 
                         (competition.country == 'International' or t.country == competition.country)]
            
            for i, team in enumerate(comp_teams[:8]):  # Top 8 teams
                Standing.objects.get_or_create(
                    competition=competition,
                    season=season,
                    team=team,
                    defaults={
                        'position': i + 1,
                        'played': random.randint(25, 38),
                        'won': random.randint(5, 25),
                        'drawn': random.randint(3, 10),
                        'lost': random.randint(2, 15),
                        'goals_for': random.randint(30, 80),
                        'goals_against': random.randint(20, 60),
                        'points': (38 - i) * 3,
                        'form': ''.join(random.choices(['W', 'D', 'L'], k=5))
                    }
                )
    
    # Create Matches
    today = timezone.now()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    # Football Matches
    football_matches_data = [
        {'home': 'Manchester United', 'away': 'Liverpool', 'status': 'LIVE', 'home_score': 2, 'away_score': 1, 'competition': 'Premier League'},
        {'home': 'Manchester City', 'away': 'Chelsea', 'status': 'LIVE', 'home_score': 1, 'away_score': 1, 'competition': 'Premier League'},
        {'home': 'Real Madrid', 'away': 'Barcelona', 'status': 'UPCOMING', 'datetime': tomorrow, 'competition': 'La Liga'},
        {'home': 'Bayern Munich', 'away': 'Arsenal', 'status': 'FINISHED', 'home_score': 3, 'away_score': 1, 'datetime': yesterday, 'competition': 'UEFA Champions League'},
        {'home': 'Liverpool', 'away': 'Real Madrid', 'status': 'UPCOMING', 'datetime': tomorrow + timedelta(hours=3), 'competition': 'UEFA Champions League'},
    ]
    
    for match_data in football_matches_data:
        home_team = next((t for t in teams if t.name == match_data['home']), None)
        away_team = next((t for t in teams if t.name == match_data['away']), None)
        competition = next((c for c in competitions if c.name == match_data['competition']), None)
        
        if home_team and away_team and competition:
            match, created = FootballMatch.objects.get_or_create(
                home_team=home_team,
                away_team=away_team,
                competition=competition,
                defaults={
                    'status': match_data['status'],
                    'home_score': match_data.get('home_score', 0),
                    'away_score': match_data.get('away_score', 0),
                    'match_datetime': match_data.get('datetime', today),
                    'venue': f"{home_team.stadium or 'Stadium'}",
                    'home_possession': random.randint(40, 60),
                    'away_possession': random.randint(40, 60),
                    'home_shots': random.randint(10, 20),
                    'away_shots': random.randint(8, 18),
                }
            )
            if created:
                print(f"Created football match: {match}")
    
    # Cricket Matches
    cricket_matches_data = [
        {'home': 'India', 'away': 'Australia', 'status': 'LIVE', 'home_runs': 245, 'home_wickets': 4, 'home_overs': 35.2, 'away_runs': 180, 'away_wickets': 6, 'away_overs': 28.4, 'competition': 'ICC Cricket World Cup'},
        {'home': 'Mumbai Indians', 'away': 'Chennai Super Kings', 'status': 'UPCOMING', 'datetime': tomorrow, 'competition': 'Indian Premier League'},
        {'home': 'Royal Challengers Bangalore', 'away': 'Mumbai Indians', 'status': 'FINISHED', 'home_runs': 156, 'home_wickets': 8, 'away_runs': 160, 'away_wickets': 4, 'datetime': yesterday, 'competition': 'Indian Premier League'},
    ]
    
    for match_data in cricket_matches_data:
        home_team = next((t for t in teams if t.name == match_data['home']), None)
        away_team = next((t for t in teams if t.name == match_data['away']), None)
        competition = next((c for c in competitions if c.name == match_data['competition']), None)
        
        if home_team and away_team and competition:
            match, created = CricketMatch.objects.get_or_create(
                home_team=home_team,
                away_team=away_team,
                competition=competition,
                defaults={
                    'status': match_data['status'],
                    'home_runs': match_data.get('home_runs', 0),
                    'home_wickets': match_data.get('home_wickets', 0),
                    'home_overs': match_data.get('home_overs', 0),
                    'away_runs': match_data.get('away_runs', 0),
                    'away_wickets': match_data.get('away_wickets', 0),
                    'away_overs': match_data.get('away_overs', 0),
                    'match_datetime': match_data.get('datetime', today),
                    'venue': f"{home_team.stadium or 'Stadium'}",
                    'current_status_text': 'In Progress' if match_data['status'] == 'LIVE' else '',
                }
            )
            if created:
                print(f"Created cricket match: {match}")
    
    # Volleyball Matches
    volleyball_matches_data = [
        {'home': 'Italy Volley', 'away': 'Brazil Volley', 'status': 'LIVE', 'home_sets': 2, 'away_sets': 1, 'competition': 'FIVB World Championship'},
        {'home': 'Russia Volley', 'away': 'Italy Volley', 'status': 'UPCOMING', 'datetime': tomorrow, 'competition': 'CEV Champions League'},
    ]
    
    for match_data in volleyball_matches_data:
        home_team = next((t for t in teams if t.name == match_data['home']), None)
        away_team = next((t for t in teams if t.name == match_data['away']), None)
        competition = next((c for c in competitions if c.name == match_data['competition']), None)
        
        if home_team and away_team and competition:
            match, created = VolleyballMatch.objects.get_or_create(
                home_team=home_team,
                away_team=away_team,
                competition=competition,
                defaults={
                    'status': match_data['status'],
                    'home_sets_won': match_data.get('home_sets', 0),
                    'away_sets_won': match_data.get('away_sets', 0),
                    'match_datetime': match_data.get('datetime', today),
                    'venue': 'Sports Arena',
                    'home_set1': random.randint(15, 25),
                    'away_set1': random.randint(15, 25),
                    'home_set2': random.randint(15, 25),
                    'away_set2': random.randint(15, 25),
                }
            )
            if created:
                print(f"Created volleyball match: {match}")
    
    # Universal Matches for other sports
    universal_matches_data = [
        {'sport': 'TENNIS', 'home': 'Novak Djokovic', 'away': 'Rafael Nadal', 'status': 'FINISHED', 'home_score': '2-1', 'competition': 'Wimbledon'},
        {'sport': 'BASKETBALL', 'home': 'Los Angeles Lakers', 'away': 'Golden State Warriors', 'status': 'LIVE', 'home_score': '87', 'away_score': '82', 'competition': 'NBA'},
        {'sport': 'KABADDI', 'home': 'India Kabaddi', 'away': 'Iran Kabaddi', 'status': 'UPCOMING', 'datetime': tomorrow, 'competition': 'Kabaddi Pro League'},
    ]
    
    for match_data in universal_matches_data:
        home_team = next((t for t in teams if t.name == match_data['home']), None)
        away_team = next((t for t in teams if t.name == match_data['away']), None)
        competition = next((c for c in competitions if c.name == match_data['competition']), None)
        
        if home_team and away_team and competition:
            match, created = UniversalMatch.objects.get_or_create(
                home_team=home_team,
                away_team=away_team,
                sport=match_data['sport'],
                competition=competition,
                defaults={
                    'status': match_data['status'],
                    'home_score': match_data.get('home_score', '0'),
                    'away_score': match_data.get('away_score', '0'),
                    'match_datetime': match_data.get('datetime', today),
                    'venue': 'Tournament Venue',
                }
            )
            if created:
                print(f"Created universal match: {match}")
    
    # Create Player Rankings
    rankings_data = [
        # Tennis Rankings
        {'player': 'Novak Djokovic', 'type': 'ATP', 'position': 1, 'points': 11000},
        {'player': 'Rafael Nadal', 'type': 'ATP', 'position': 2, 'points': 9800},
        {'player': 'Roger Federer', 'type': 'ATP', 'position': 3, 'points': 8500},
        
        # FIFA Rankings
        {'player': 'Cristiano Ronaldo', 'type': 'FIFA', 'position': 1, 'points': 1800},
        {'player': 'Lionel Messi', 'type': 'FIFA', 'position': 2, 'points': 1750},
        {'player': 'Erling Haaland', 'type': 'FIFA', 'position': 3, 'points': 1600},
        
        # ICC Rankings
        {'player': 'Virat Kohli', 'type': 'ICCRANKING', 'position': 1, 'points': 900},
        {'player': 'Rohit Sharma', 'type': 'ICCRANKING', 'position': 2, 'points': 850},
        {'player': 'Jasprit Bumrah', 'type': 'ICCRANKING', 'position': 3, 'points': 800},
    ]
    
    for ranking_data in rankings_data:
        player = next((p for p in players if p.name == ranking_data['player']), None)
        if player:
            PlayerRanking.objects.get_or_create(
                player=player,
                ranking_type=ranking_data['type'],
                defaults={
                    'position': ranking_data['position'],
                    'points': ranking_data['points'],
                    'movement': random.randint(-2, 2),
                }
            )
            print(f"Created ranking for {player.name}")
    
    # Create News Articles
    news_data = [
        {
            'title': 'Manchester United defeats Liverpool in thrilling comeback',
            'summary': 'United came from behind to secure a 3-2 victory over their rivals',
            'content': 'Full match report...',
            'author': 'Sports Reporter',
            'sport': 'FOOTBALL',
            'is_featured': True,
            'is_trending': True,
        },
        {
            'title': 'India vs Australia: World Cup classic goes down to the wire',
            'summary': 'A thrilling match ended with India winning by 4 wickets',
            'content': 'Match details...',
            'author': 'Cricket Correspondent',
            'sport': 'CRICKET',
            'is_featured': False,
            'is_trending': True,
        },
        {
            'title': 'Novak Djokovic wins Wimbledon title',
            'summary': 'Djokovic defeats Nadal in an epic five-set final',
            'content': 'Final report...',
            'author': 'Tennis Editor',
            'sport': 'TENNIS',
            'is_featured': True,
            'is_trending': False,
        },
        {
            'title': 'NBA Finals: Lakers take series lead',
            'summary': 'LeBron James leads Lakers to crucial game 3 victory',
            'content': 'Game analysis...',
            'author': 'Basketball Analyst',
            'sport': 'BASKETBALL',
            'is_featured': False,
            'is_trending': True,
        },
    ]
    
    for news_item in news_data:
        news, created = NewsArticle.objects.get_or_create(
            title=news_item['title'],
            defaults={
                'summary': news_item['summary'],
                'content': news_item['content'],
                'author': news_item['author'],
                'sport': news_item['sport'],
                'is_featured': news_item['is_featured'],
                'is_trending': news_item['is_trending'],
                'published_at': today - timedelta(hours=random.randint(1, 48)),
                'view_count': random.randint(100, 10000),
            }
        )
        if created:
            print(f"Created news article: {news.title}")
    
    # Create Head-to-Head Records
    h2h_pairs = [
        ('Manchester United', 'Liverpool', 'FOOTBALL'),
        ('Real Madrid', 'Barcelona', 'FOOTBALL'),
        ('India', 'Australia', 'CRICKET'),
        ('Novak Djokovic', 'Rafael Nadal', 'TENNIS'),
    ]
    
    for team1_name, team2_name, sport in h2h_pairs:
        team1 = next((t for t in teams if t.name == team1_name), None)
        team2 = next((t for t in teams if t.name == team2_name), None)
        
        if team1 and team2:
            h2h, created = HeadToHead.objects.get_or_create(
                team1=team1,
                team2=team2,
                sport=sport,
                defaults={
                    'total_matches': random.randint(10, 50),
                    'team1_wins': random.randint(3, 25),
                    'team2_wins': random.randint(3, 25),
                    'draws': random.randint(0, 10),
                    'team1_goals_for': random.randint(20, 80),
                    'team2_goals_for': random.randint(20, 80),
                }
            )
            if created:
                print(f"Created H2H record: {team1.name} vs {team2.name}")
    
    # Create User Favorites
    if User.objects.filter(username='admin').exists():
        user_favorites, created = UserFavorites.objects.get_or_create(
            user=User.objects.get(username='admin'),
            defaults={
                'email_notifications': True,
                'push_notifications': True,
            }
        )
        
        # Add some favorites
        user_favorites.favorite_teams.add(*teams[:5])
        user_favorites.favorite_players.add(*players[:5])
        user_favorites.favorite_competitions.add(*competitions[:3])
        
        print("Created user favorites")
    
    print("\n✅ Comprehensive sample data created successfully!")
    print(f"Created {len(competitions)} competitions")
    print(f"Created {len(teams)} teams")
    print(f"Created {len(players)} players")
    print(f"Created {FootballMatch.objects.count()} football matches")
    print(f"Created {CricketMatch.objects.count()} cricket matches")
    print(f"Created {VolleyballMatch.objects.count()} volleyball matches")
    print(f"Created {UniversalMatch.objects.count()} universal matches")
    print(f"Created {NewsArticle.objects.count()} news articles")
    print(f"Created {PlayerRanking.objects.count()} player rankings")
    print(f"Created {HeadToHead.objects.count()} head-to-head records")

if __name__ == '__main__':
    create_comprehensive_sample_data()
