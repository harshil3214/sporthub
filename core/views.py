from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg, F, Case, When, IntegerField
from django.views.decorators.http import require_POST
from datetime import datetime, time as dt_time, timedelta
from .models import (
    Team, Player, FootballMatch, CricketMatch,
    VolleyballMatch, TeacherProfile, StudentProfile, UniversalMatch,
    Competition, Season, Standing, PlayerRanking, NewsArticle,
    UserFavorites, HeadToHead, MatchEvent
)

@login_required(login_url='login')
def login_redirect_view(request):
    """
    Role-Based Redirector.
    """
    user = request.user
    if hasattr(user, 'teacher_profile'):
        return redirect('my_students')
    return redirect('home_dashboard')

@login_required(login_url='login')
def teacher_students_list(request):
    """
    Page for Teachers only.
    """
    user = request.user
    if not hasattr(user, 'teacher_profile') and not user.is_superuser:
        messages.error(request, "Access Denied: This area is for Teachers only.")
        return redirect('home_dashboard')

    if user.is_superuser:
        students = StudentProfile.objects.all()
    else:
        students = StudentProfile.objects.filter(assigned_teacher=user.teacher_profile)

    return render(request, 'core/my_students.html', {'students': students})

@login_required(login_url='login')
def home_dashboard(request):
    """
    Main sports dashboard.
    Ensures all match types are fetched and ordered by time.
    Teams are sorted by points (highest first).
    """
    context = {
        'football_matches': FootballMatch.objects.all().order_by('-match_datetime'),
        'cricket_matches': CricketMatch.objects.all().order_by('-match_datetime'),
        'volleyball_matches': VolleyballMatch.objects.all().order_by('-match_datetime'),
        'universal_matches': UniversalMatch.objects.all().order_by('-match_datetime'),
        
        # RESTORED: Sorting by total_points now that it is a DB field.
        # '-total_points' means descending order (highest points at the top).
        'teams': Team.objects.all().order_by('-total_points', 'name'), 
    }
    return render(request, 'core/dashboard.html', context)


@login_required(login_url='login')
def scores(request):
    """
    Flashscore-inspired list page:
    - filter by date + sport
    - search teams/competitions
    - group Sport -> Country -> Competition
    """
    sport = (request.GET.get("sport") or "all").strip().lower()
    q = (request.GET.get("q") or "").strip()
    date_str = (request.GET.get("date") or "").strip()

    tz = timezone.get_current_timezone()
    if date_str:
        try:
            day = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            day = timezone.localdate()
    else:
        day = timezone.localdate()

    day_start = timezone.make_aware(datetime.combine(day, dt_time.min), tz)
    day_end = timezone.make_aware(datetime.combine(day, dt_time.max), tz)

    def _team_competition_filter(prefix: str = "") -> Q:
        if not q:
            return Q()
        # prefix is "" for direct model fields; we keep for future expansions
        filter_q = (
            Q(**{f"{prefix}home_team__name__icontains": q})
            | Q(**{f"{prefix}away_team__name__icontains": q})
        )
        # Add competition filter for models that have competition relationship
        if prefix == "":
            filter_q |= Q(competition__name__icontains=q)
        else:
            filter_q |= Q(**{f"{prefix}competition__name__icontains": q})
        return filter_q

    rows = []

    def add_matches(sport_key: str, qs, score_kind: str):
        for m in qs:
            competition_name = "Other"
            if hasattr(m, 'competition') and m.competition:
                competition_name = m.competition.name
            elif hasattr(m, 'competition_name') and m.competition_name:
                competition_name = m.competition_name.strip() or "Other"
            
            rows.append(
                {
                    "sport": sport_key,
                    "id": m.id,
                    "status": m.status,
                    "status_display": getattr(m, "get_status_display", lambda: m.status)(),
                    "competition_name": competition_name,
                    "country": (m.country or "").strip() or "International",
                    "round_name": (m.round_name or "").strip(),
                    "match_datetime": m.match_datetime,
                    "venue": (m.venue or "").strip(),
                    "referee": (m.referee or "").strip(),
                    "home_team": m.home_team,
                    "away_team": m.away_team,
                    "score_kind": score_kind,
                    "m": m,
                }
            )

    if sport in ("all", "football"):
        fb = (
            FootballMatch.objects.filter(match_datetime__range=(day_start, day_end))
            .filter(_team_competition_filter())
            .select_related("home_team", "away_team", "competition")
            .order_by("competition__name", "match_datetime")
        )
        add_matches("football", fb, "score")

    if sport in ("all", "cricket"):
        cr = (
            CricketMatch.objects.filter(match_datetime__range=(day_start, day_end))
            .filter(_team_competition_filter())
            .select_related("home_team", "away_team", "toss_winner", "competition")
            .order_by("competition__name", "match_datetime")
        )
        add_matches("cricket", cr, "cricket")

    if sport in ("all", "volleyball"):
        vb = (
            VolleyballMatch.objects.filter(match_datetime__range=(day_start, day_end))
            .filter(_team_competition_filter())
            .select_related("home_team", "away_team", "competition")
            .order_by("competition__name", "match_datetime")
        )
        add_matches("volleyball", vb, "sets")

    if sport in ("all", "universal"):
        uni = (
            UniversalMatch.objects.filter(match_datetime__range=(day_start, day_end))
            .filter(
                Q(home_team__name__icontains=q)
                | Q(away_team__name__icontains=q)
                | Q(competition__name__icontains=q)
                | Q(match_info__icontains=q)
                if q
                else Q()
            )
            .select_related("home_team", "away_team", "competition")
            .order_by("competition__name", "match_datetime")
        )
        add_matches("universal", uni, "score")

    # Group Sport -> Country -> Competition
    rows.sort(
        key=lambda r: (
            r["sport"],
            r["country"],
            r["competition_name"],
            r["match_datetime"] or timezone.now(),
        )
    )

    grouped = {}
    for r in rows:
        grouped.setdefault(r["sport"], {}).setdefault(r["country"], {}).setdefault(r["competition_name"], []).append(r)

    context = {
        "selected_sport": sport,
        "q": q,
        "day": day,
        "grouped": grouped,
        "sport_order": ["football", "cricket", "volleyball", "universal"],
    }
    return render(request, "core/scores.html", context)

def home(request):
    """
    Public homepage - Flashscore style landing page
    """
    # Get today's matches for public view
    tz = timezone.get_current_timezone()
    today = timezone.localdate()
    day_start = timezone.make_aware(datetime.combine(today, dt_time.min), tz)
    day_end = timezone.make_aware(datetime.combine(today, dt_time.max), tz)
    
    # Get live matches
    live_matches = []
    
    # Football live matches
    fb_live = FootballMatch.objects.filter(status='LIVE').select_related("home_team", "away_team", "competition")
    for match in fb_live:
        live_matches.append({
            'id': match.id,
            'sport': 'football',
            'home_team': match.home_team,
            'away_team': match.away_team,
            'home_score': match.home_score,
            'away_score': match.away_score,
            'competition_name': match.competition.name if match.competition else 'Football',
            'venue': match.venue,
            'match_info': 'Live'
        })
    
    # Cricket live matches
    cr_live = CricketMatch.objects.filter(status='LIVE').select_related("home_team", "away_team", "competition")
    for match in cr_live:
        live_matches.append({
            'id': match.id,
            'sport': 'cricket',
            'home_team': match.home_team,
            'away_team': match.away_team,
            'home_score': f"{match.home_runs}/{match.home_wickets}",
            'away_score': f"{match.away_runs}/{match.away_wickets}",
            'competition_name': match.competition.name if match.competition else 'Cricket',
            'venue': match.venue,
            'match_info': match.current_status_text or 'Live'
        })
    
    # Universal live matches
    uni_live = UniversalMatch.objects.filter(status='LIVE').select_related("home_team", "away_team", "competition")
    for match in uni_live:
        live_matches.append({
            'id': match.id,
            'sport': match.sport.lower(),
            'home_team': match.home_team,
            'away_team': match.away_team,
            'home_score': match.home_score,
            'away_score': match.away_score,
            'competition_name': match.competition.name if match.competition else match.get_sport_display(),
            'venue': match.venue,
            'match_info': match.match_info or 'Live'
        })
    
    # Get trending news
    trending_news = NewsArticle.objects.filter(is_trending=True)[:5]
    
    # Get upcoming matches
    upcoming_matches = []
    for match in FootballMatch.objects.filter(status='UPCOMING').select_related("home_team", "away_team", "competition")[:5]:
        upcoming_matches.append({
            'id': match.id,
            'sport': 'football',
            'home_team': match.home_team,
            'away_team': match.away_team,
            'competition_name': match.competition.name if match.competition else 'Football',
            'match_datetime': match.match_datetime,
            'venue': match.venue
        })
    
    context = {
        'live_matches': live_matches,
        'trending_news': trending_news,
        'upcoming_matches': upcoming_matches,
        'total_teams': Team.objects.count(),
        'total_matches': (
            FootballMatch.objects.count() + 
            CricketMatch.objects.count() + 
            VolleyballMatch.objects.count() + 
            UniversalMatch.objects.count()
        ),
        'today_matches_count': (
            FootballMatch.objects.filter(match_datetime__range=(day_start, day_end)).count() +
            CricketMatch.objects.filter(match_datetime__range=(day_start, day_end)).count() +
            VolleyballMatch.objects.filter(match_datetime__range=(day_start, day_end)).count() +
            UniversalMatch.objects.filter(match_datetime__range=(day_start, day_end)).count()
        ),
        'competitions': Competition.objects.filter(is_active=True).count(),
        'featured_competitions': Competition.objects.filter(is_active=True).order_by('-priority')[:6]
    }
    
    return render(request, 'core/home.html', context)

def competitions_view(request):
    """
    List all competitions by sport
    """
    sport_filter = request.GET.get('sport', '')
    
    competitions = Competition.objects.filter(is_active=True)
    if sport_filter:
        competitions = competitions.filter(sport=sport_filter.upper())
    
    # Group by sport
    sports = {}
    for competition in competitions:
        sport = competition.get_sport_display()
        if sport not in sports:
            sports[sport] = []
        sports[sport].append(competition)
    
    context = {
        'sports': sports,
        'selected_sport': sport_filter,
        'sport_choices': Team.SPORT_CHOICES
    }
    return render(request, 'core/competitions.html', context)

def competition_detail(request, competition_id):
    """
    Competition details with standings and matches
    """
    competition = get_object_or_404(Competition, id=competition_id)
    
    # Get current season
    current_season = competition.seasons.filter(is_current=True).first()
    if not current_season:
        current_season = competition.seasons.order_by('-start_date').first()
    
    # Get standings if available
    standings = None
    if current_season:
        standings = Standing.objects.filter(
            competition=competition, 
            season=current_season
        ).order_by('position')
    
    # Get recent matches
    recent_matches = []
    for match in competition.matches.filter(
        status='FINISHED'
    ).order_by('-match_datetime')[:10]:
        recent_matches.append(match)
    
    # Get upcoming matches
    upcoming_matches = []
    for match in competition.matches.filter(
        status='UPCOMING'
    ).order_by('match_datetime')[:10]:
        upcoming_matches.append(match)
    
    context = {
        'competition': competition,
        'current_season': current_season,
        'standings': standings,
        'recent_matches': recent_matches,
        'upcoming_matches': upcoming_matches,
    }
    return render(request, 'core/competition_detail.html', context)

def team_profile(request, team_id):
    """
    Detailed team profile with statistics
    """
    team = get_object_or_404(Team, id=team_id)
    
    # Get recent matches
    recent_matches = []
    for match in FootballMatch.objects.filter(
        Q(home_team=team) | Q(away_team=team)
    ).order_by('-match_datetime')[:10]:
        recent_matches.append(match)
    
    # Get team form
    form = team.get_form()
    
    # Get head-to-head with common opponents
    h2h_records = HeadToHead.objects.filter(
        Q(team1=team) | Q(team2=team)
    ).select_related('team1', 'team2')
    
    # Get squad
    squad = team.players.filter(is_active=True)
    
    context = {
        'team': team,
        'recent_matches': recent_matches,
        'form': form,
        'h2h_records': h2h_records,
        'squad': squad,
    }
    return render(request, 'core/team_profile.html', context)

def player_profile(request, player_id):
    """
    Detailed player profile with statistics
    """
    player = get_object_or_404(Player, id=player_id)
    
    # Get player rankings
    rankings = PlayerRanking.objects.filter(player=player)
    
    # Get recent matches
    recent_matches = []
    # This would need to be implemented based on match events
    
    # Get news related to player
    news = NewsArticle.objects.filter(players=player)[:5]
    
    context = {
        'player': player,
        'rankings': rankings,
        'recent_matches': recent_matches,
        'news': news,
    }
    return render(request, 'core/player_profile.html', context)

def rankings_view(request):
    """
    Player rankings for different sports
    """
    ranking_type = request.GET.get('type', 'ATP')
    
    rankings = PlayerRanking.objects.filter(
        ranking_type=ranking_type
    ).select_related('player').order_by('position')
    
    # Get available ranking types
    ranking_types = PlayerRanking.RANKING_TYPES
    
    context = {
        'rankings': rankings,
        'selected_type': ranking_type,
        'ranking_types': ranking_types,
    }
    return render(request, 'core/rankings.html', context)

def news_view(request):
    """
    News articles listing
    """
    sport_filter = request.GET.get('sport', '')
    
    news = NewsArticle.objects.all()
    if sport_filter:
        news = news.filter(sport=sport_filter.upper())
    
    # Featured news
    featured_news = news.filter(is_featured=True)[:3]
    
    # Regular news (exclude featured from main list)
    regular_news = news.exclude(is_featured=True).order_by('-published_at')
    
    # Trending news
    trending_news = news.filter(is_trending=True).order_by('-view_count')[:5]
    
    context = {
        'featured_news': featured_news,
        'regular_news': regular_news,
        'trending_news': trending_news,
        'selected_sport': sport_filter,
        'sport_choices': Team.SPORT_CHOICES,
    }
    return render(request, 'core/news.html', context)

def news_detail(request, news_id):
    """
    Individual news article
    """
    news = get_object_or_404(NewsArticle, id=news_id)
    
    # Increment view count
    news.view_count += 1
    news.save()
    
    # Get related news
    related_news = NewsArticle.objects.filter(
        sport=news.sport
    ).exclude(id=news.id).order_by('-published_at')[:5]
    
    context = {
        'news': news,
        'related_news': related_news,
    }
    return render(request, 'core/news_detail.html', context)

@login_required(login_url='login')
def favorites_view(request):
    """
    User's favorite teams, players, and competitions
    """
    user_favorites, created = UserFavorites.objects.get_or_create(user=request.user)
    
    context = {
        'favorites': user_favorites,
    }
    return render(request, 'core/favorites.html', context)

@login_required(login_url='login')
def toggle_favorite(request, content_type, object_id):
    """
    Toggle favorite status for teams, players, or competitions
    """
    if request.method == 'POST':
        user_favorites, created = UserFavorites.objects.get_or_create(user=request.user)
        
        if content_type == 'team':
            team = get_object_or_404(Team, id=object_id)
            if team in user_favorites.favorite_teams.all():
                user_favorites.favorite_teams.remove(team)
                is_favorited = False
            else:
                user_favorites.favorite_teams.add(team)
                is_favorited = True
                
        elif content_type == 'player':
            player = get_object_or_404(Player, id=object_id)
            if player in user_favorites.favorite_players.all():
                user_favorites.favorite_players.remove(player)
                is_favorited = False
            else:
                user_favorites.favorite_players.add(player)
                is_favorited = True
                
        elif content_type == 'competition':
            competition = get_object_or_404(Competition, id=object_id)
            if competition in user_favorites.favorite_competitions.all():
                user_favorites.favorite_competitions.remove(competition)
                is_favorited = False
            else:
                user_favorites.favorite_competitions.add(competition)
                is_favorited = True
        
        return JsonResponse({'is_favorited': is_favorited})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def head_to_head_view(request, team1_id, team2_id):
    """
    Head-to-head statistics between two teams
    """
    team1 = get_object_or_404(Team, id=team1_id)
    team2 = get_object_or_404(Team, id=team2_id)
    
    # Get H2H record
    h2h = HeadToHead.objects.filter(
        Q(team1=team1, team2=team2) | Q(team1=team2, team2=team1)
    ).first()
    
    # Get previous matches
    previous_matches = []
    for match in FootballMatch.objects.filter(
        Q(home_team=team1, away_team=team2) | 
        Q(home_team=team2, away_team=team1)
    ).order_by('-match_datetime')[:10]:
        previous_matches.append(match)
    
    context = {
        'team1': team1,
        'team2': team2,
        'h2h': h2h,
        'previous_matches': previous_matches,
    }
    return render(request, 'core/head_to_head.html', context)

def calendar_view(request):
    """
    Calendar/schedule view
    """
    # Get date from request or use today
    date_str = request.GET.get('date', '')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = timezone.localdate()
    else:
        selected_date = timezone.localdate()
    
    # Get matches for selected date
    day_start = timezone.make_aware(datetime.combine(selected_date, dt_time.min), timezone.get_current_timezone())
    day_end = timezone.make_aware(datetime.combine(selected_date, dt_time.max), timezone.get_current_timezone())
    
    matches = []
    
    # Football matches
    for match in FootballMatch.objects.filter(
        match_datetime__range=(day_start, day_end)
    ).select_related("home_team", "away_team", "competition"):
        matches.append(match)
    
    # Cricket matches
    for match in CricketMatch.objects.filter(
        match_datetime__range=(day_start, day_end)
    ).select_related("home_team", "away_team", "competition"):
        matches.append(match)
    
    # Universal matches
    for match in UniversalMatch.objects.filter(
        match_datetime__range=(day_start, day_end)
    ).select_related("home_team", "away_team", "competition"):
        matches.append(match)
    
    # Sort by time
    matches.sort(key=lambda x: x.match_datetime or timezone.now())
    
    context = {
        'selected_date': selected_date,
        'matches': matches,
        'prev_date': selected_date - timedelta(days=1),
        'next_date': selected_date + timedelta(days=1),
    }
    return render(request, 'core/calendar.html', context)

def register(request):
    """
    Handles registration with Admin Approval.
    """
    if request.user.is_authenticated:
        return redirect('home_dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False 
            user.save()
            request.session['pending_username'] = user.username
            return render(request, 'registration/pending_approval.html')
        else:
            messages.error(request, "Please correct errors below.")
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def check_approval_status(request):
    """
    AJAX check for user approval.
    """
    username = request.session.get('pending_username')
    if not username:
        return JsonResponse({'is_approved': False})
    
    try:
        user = User.objects.get(username=username)
        return JsonResponse({'is_approved': user.is_active})
    except User.DoesNotExist:
        return JsonResponse({'is_approved': False})

def get_live_scores(request):
    """
    Enhanced API endpoint for real-time score updates.
    Returns comprehensive data for homepage and live updates.
    """
    tz = timezone.get_current_timezone()
    today = timezone.localdate()
    day_start = timezone.make_aware(datetime.combine(today, dt_time.min), tz)
    day_end = timezone.make_aware(datetime.combine(today, dt_time.max), tz)
    
    # Get live matches with full details
    live_matches = []
    
    # Football live matches
    fb_live = FootballMatch.objects.filter(status='LIVE').select_related("home_team", "away_team")
    for match in fb_live:
        live_matches.append({
            'id': match.id,
            'sport': 'football',
            'home_team': {'name': match.home_team.name, 'id': match.home_team.id},
            'away_team': {'name': match.away_team.name, 'id': match.away_team.id},
            'home_score': match.home_score,
            'away_score': match.away_score,
            'competition_name': match.competition_name or 'Football',
            'venue': match.venue,
            'match_info': match.match_info or 'Live',
            'match_datetime': match.match_datetime.isoformat() if match.match_datetime else None
        })
    
    # Cricket live matches
    cr_live = CricketMatch.objects.filter(status='LIVE').select_related("home_team", "away_team")
    for match in cr_live:
        live_matches.append({
            'id': match.id,
            'sport': 'cricket',
            'home_team': {'name': match.home_team.name, 'id': match.home_team.id},
            'away_team': {'name': match.away_team.name, 'id': match.away_team.id},
            'home_score': f"{match.home_runs}/{match.home_wickets} ({match.home_overs} ov)",
            'away_score': f"{match.away_runs}/{match.away_wickets} ({match.away_overs} ov)",
            'competition_name': match.competition_name or 'Cricket',
            'venue': match.venue,
            'match_info': match.current_status_text or 'Live',
            'match_datetime': match.match_datetime.isoformat() if match.match_datetime else None
        })
    
    # Universal live matches
    uni_live = UniversalMatch.objects.filter(status='LIVE').select_related("home_team", "away_team")
    for match in uni_live:
        live_matches.append({
            'id': match.id,
            'sport': match.sport.lower(),
            'home_team': {'name': match.home_team.name, 'id': match.home_team.id},
            'away_team': {'name': match.away_team.name, 'id': match.away_team.id},
            'home_score': match.home_score,
            'away_score': match.away_score,
            'competition_name': match.competition_name or match.get_sport_display(),
            'venue': match.venue,
            'match_info': match.match_info or 'Live',
            'match_datetime': match.match_datetime.isoformat() if match.match_datetime else None
        })
    
    # Calculate statistics
    total_matches = (
        FootballMatch.objects.count() + 
        CricketMatch.objects.count() + 
        VolleyballMatch.objects.count() + 
        UniversalMatch.objects.count()
    )
    
    today_matches = (
        FootballMatch.objects.filter(match_datetime__range=(day_start, day_end)).count() +
        CricketMatch.objects.filter(match_datetime__range=(day_start, day_end)).count() +
        VolleyballMatch.objects.filter(match_datetime__range=(day_start, day_end)).count() +
        UniversalMatch.objects.filter(match_datetime__range=(day_start, day_end)).count()
    )
    
    return JsonResponse({
        'live_matches': live_matches,
        'live_count': len(live_matches),
        'total_matches': total_matches,
        'today_matches': today_matches,
        'total_teams': Team.objects.count(),
        'competitions': Team.objects.values('sport').distinct().count(),
        'last_updated': timezone.now().isoformat()
    })

@login_required(login_url='login')
def match_detail(request, sport, match_id):
    """
    Match Center page for a single match.
    This intentionally stays generic (works for cricket/football/volleyball/universal).
    """
    sport_key = (sport or "").strip().lower()
    model_by_sport = {
        "cricket": CricketMatch,
        "football": FootballMatch,
        "volleyball": VolleyballMatch,
        "universal": UniversalMatch,
    }

    model = model_by_sport.get(sport_key)
    if not model:
        return render(request, "core/match_not_found.html", status=404)

    match = get_object_or_404(model, id=match_id)

    context = {
        "sport": sport_key,
        "match": match,
    }
    return render(request, "core/match_detail.html", context)

# --- NEW ADVANCED FEATURES ---

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user favorites
            UserFavorites.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    """Custom login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'core/login.html')

@login_required
def match_detail(request, sport, match_id):
    """Detailed match page with live commentary and statistics"""
    model_by_sport = {
        "football": FootballMatch,
        "cricket": CricketMatch,
        "volleyball": VolleyballMatch,
        "universal": UniversalMatch,
    }
    
    model = model_by_sport.get(sport)
    if not model:
        return render(request, "core/match_not_found.html", status=404)
    
    match = get_object_or_404(model, id=match_id)
    
    # Get match events
    events = MatchEvent.objects.filter(
        match_type=sport,
        match_id=match_id
    ).order_by('minute')
    
    # Get head-to-head statistics
    h2h_data = None
    if hasattr(match, 'home_team') and hasattr(match, 'away_team'):
        h2h = HeadToHead.objects.filter(
            Q(team1=match.home_team, team2=match.away_team) |
            Q(team1=match.away_team, team2=match.home_team)
        ).first()
        if h2h:
            h2h_data = {
                'total_matches': h2h.total_matches,
                'team1_wins': h2h.team1_wins if h2h.team1 == match.home_team else h2h.team2_wins,
                'team2_wins': h2h.team2_wins if h2h.team1 == match.home_team else h2h.team1_wins,
                'draws': h2h.draws,
            }
    
    # Get recent form for both teams
    home_form = match.home_team.get_form() if hasattr(match.home_team, 'get_form') else []
    away_form = match.away_team.get_form() if hasattr(match.away_team, 'get_form') else []
    
    context = {
        'sport': sport,
        'match': match,
        'events': events,
        'h2h': h2h_data,
        'home_form': home_form,
        'away_form': away_form,
        'is_favorited': False,
    }
    
    # Check if match is in user favorites
    if request.user.is_authenticated:
        user_favorites = UserFavorites.objects.get_or_create(user=request.user)[0]
        if sport == 'football':
            context['is_favorited'] = user_favorites.favorite_teams.filter(
                Q(id=match.home_team.id) | Q(id=match.away_team.id)
            ).exists()
    
    return render(request, 'core/match_detail.html', context)

@login_required
@require_POST
def toggle_favorite(request):
    """Toggle favorite team/player/competition"""
    item_type = request.POST.get('type')  # 'team', 'player', 'competition'
    item_id = request.POST.get('id')
    
    user_favorites = UserFavorites.objects.get_or_create(user=request.user)[0]
    
    if item_type == 'team':
        team = get_object_or_404(Team, id=item_id)
        if user_favorites.favorite_teams.filter(id=team.id).exists():
            user_favorites.favorite_teams.remove(team)
            return JsonResponse({'status': 'removed'})
        else:
            user_favorites.favorite_teams.add(team)
            return JsonResponse({'status': 'added'})
    
    elif item_type == 'player':
        player = get_object_or_404(Player, id=item_id)
        if user_favorites.favorite_players.filter(id=player.id).exists():
            user_favorites.favorite_players.remove(player)
            return JsonResponse({'status': 'removed'})
        else:
            user_favorites.favorite_players.add(player)
            return JsonResponse({'status': 'added'})
    
    elif item_type == 'competition':
        competition = get_object_or_404(Competition, id=item_id)
        if user_favorites.favorite_competitions.filter(id=competition.id).exists():
            user_favorites.favorite_competitions.remove(competition)
            return JsonResponse({'status': 'removed'})
        else:
            user_favorites.favorite_competitions.add(competition)
            return JsonResponse({'status': 'added'})
    
    return JsonResponse({'status': 'error'}, status=400)

def search_api(request):
    """Advanced search API"""
    query = request.GET.get('q', '').strip()
    sport = request.GET.get('sport', 'all')
    
    if not query:
        return JsonResponse({'results': []})
    
    results = []
    
    # Search teams
    team_qs = Team.objects.filter(name__icontains=query)
    if sport != 'all':
        team_qs = team_qs.filter(sport=sport.upper())
    
    for team in team_qs[:10]:
        results.append({
            'type': 'team',
            'id': team.id,
            'name': team.name,
            'sport': team.sport,
            'url': f'/team/{team.id}/'
        })
    
    # Search players
    player_qs = Player.objects.filter(name__icontains=query)
    for player in player_qs[:10]:
        results.append({
            'type': 'player',
            'id': player.id,
            'name': player.name,
            'sport': player.team.sport if player.team else 'Unknown',
            'url': f'/player/{player.id}/'
        })
    
    # Search competitions
    comp_qs = Competition.objects.filter(name__icontains=query)
    if sport != 'all':
        comp_qs = comp_qs.filter(sport=sport.upper())
    
    for comp in comp_qs[:10]:
        results.append({
            'type': 'competition',
            'id': comp.id,
            'name': comp.name,
            'sport': comp.sport,
            'url': f'/competition/{comp.id}/'
        })
    
    return JsonResponse({'results': results})

def live_scores_api(request):
    """API for live scores"""
    live_matches = []
    
    # Football matches
    fb_matches = FootballMatch.objects.filter(status='LIVE').select_related('home_team', 'away_team', 'competition')
    for match in fb_matches:
        live_matches.append({
            'id': match.id,
            'sport': 'football',
            'home_team': match.home_team.name,
            'away_team': match.away_team.name,
            'home_score': match.home_score,
            'away_score': match.away_score,
            'competition': match.competition.name if match.competition else 'Football',
            'status': match.status,
            'venue': match.venue,
            'minute': getattr(match, 'current_minute', None)
        })
    
    # Cricket matches
    cr_matches = CricketMatch.objects.filter(status='LIVE').select_related('home_team', 'away_team', 'competition')
    for match in cr_matches:
        live_matches.append({
            'id': match.id,
            'sport': 'cricket',
            'home_team': match.home_team.name,
            'away_team': match.away_team.name,
            'home_score': f"{match.home_runs}/{match.home_wickets}",
            'away_score': f"{match.away_runs}/{match.away_wickets}",
            'competition': match.competition.name if match.competition else 'Cricket',
            'status': match.status,
            'venue': match.venue,
            'overs': f"{match.home_overs}",
            'status_text': match.current_status_text
        })
    
    return JsonResponse({'matches': live_matches})

@login_required
def player_comparison(request):
    """Compare two players"""
    player1_id = request.GET.get('player1')
    player2_id = request.GET.get('player2')
    
    if not player1_id or not player2_id:
        return JsonResponse({'error': 'Please select two players to compare'}, status=400)
    
    player1 = get_object_or_404(Player, id=player1_id)
    player2 = get_object_or_404(Player, id=player2_id)
    
    comparison_data = {
        'player1': {
            'name': player1.name,
            'team': player1.team.name if player1.team else 'N/A',
            'position': player1.position,
            'matches_played': player1.matches_played,
            'goals_scored': player1.goals_scored,
            'assists': player1.assists,
        },
        'player2': {
            'name': player2.name,
            'team': player2.team.name if player2.team else 'N/A',
            'position': player2.position,
            'matches_played': player2.matches_played,
            'goals_scored': player2.goals_scored,
            'assists': player2.assists,
        }
    }
    
    return JsonResponse(comparison_data)

@login_required
def scorecard_view(request, match_id):
    """View for detailed match scorecard"""
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
        return render(request, 'core/match_not_found.html')
    
    context = {
        'match': match,
        'sport': sport,
        'total_score': match.home_score + match.away_score,
    }
    
    return render(request, 'core/scorecard.html', context)

def notifications_settings(request):
    """User notification preferences"""
    if request.method == 'POST':
        user_favorites = UserFavorites.objects.get_or_create(user=request.user)[0]
        
        user_favorites.email_notifications = request.POST.get('email_notifications') == 'on'
        user_favorites.push_notifications = request.POST.get('push_notifications') == 'on'
        user_favorites.favorite_match_notifications = request.POST.get('match_notifications') == 'on'
        
        user_favorites.save()
        messages.success(request, 'Notification settings updated!')
        return redirect('favorites')
    
    user_favorites = UserFavorites.objects.get_or_create(user=request.user)[0]
    return render(request, 'core/notifications_settings.html', {
        'favorites': user_favorites
    })