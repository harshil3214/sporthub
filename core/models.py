from django.db import models
from django.db.models import Q, Count, Avg
from django.contrib.auth.models import User
from django.utils import timezone

# --- MULTI-TENANT USER PROFILES ---

class TeacherProfile(models.Model):
    """Teachers act as group leaders/managers for specific users."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Teacher: {self.user.username}"

class StudentProfile(models.Model):
    """Students are assigned to a specific Teacher."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    assigned_teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, related_name='students')

    def __str__(self):
        return f"Student: {self.user.username} (Assigned to: {self.assigned_teacher.user.username if self.assigned_teacher else 'None'})"


# --- COMPETITIONS AND LEAGUES ---

class Competition(models.Model):
    """Competitions, leagues, and tournaments"""
    name = models.CharField(max_length=200)
    sport = models.CharField(max_length=50, choices=[
        ('FOOTBALL', 'Football'),
        ('CRICKET', 'Cricket'),
        ('VOLLEYBALL', 'Volleyball'),
        ('TENNIS', 'Tennis'),
        ('BASKETBALL', 'Basketball'),
        ('BADMINTON', 'Badminton'),
        ('BOXING', 'Boxing'),
        ('MOTORSPORT', 'Motorsport'),
        ('GOLF', 'Golf'),
        ('HANDBALL', 'Handball'),
        ('ICE_HOCKEY', 'Ice Hockey'),
        ('RUGBY', 'Rugby'),
        ('SNOOKER', 'Snooker'),
        ('TABLE_TENNIS', 'Table Tennis'),
        ('WATER_POLO', 'Water Polo'),
        ('DARTS', 'Darts'),
        ('ESPORTS', 'Esports'),
        ('HORSE_RACING', 'Horse Racing'),
        ('BASEBALL', 'Baseball'),
        ('KABADDI', 'Kabaddi'),
        ('ATHLETICS', 'Athletics'),
    ])
    country = models.CharField(max_length=100, default="International")
    category = models.CharField(max_length=100, help_text="e.g., League, Cup, Tournament")
    season = models.CharField(max_length=50, blank=True)
    logo = models.ImageField(upload_to='competitions/logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Higher priority shows first")
    flashscore_id = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-priority', 'sport', 'country', 'name']
        unique_together = ['name', 'sport', 'country']
    
    def __str__(self):
        return f"{self.name} ({self.get_sport_display()})"

    def get_sport_display(self):
        sport_choices = {
            'FOOTBALL': 'Football',
            'CRICKET': 'Cricket',
            'VOLLEYBALL': 'Volleyball',
            'TENNIS': 'Tennis',
            'BASKETBALL': 'Basketball',
            'BADMINTON': 'Badminton',
            'BOXING': 'Boxing',
            'MOTORSPORT': 'Motorsport',
            'GOLF': 'Golf',
            'HANDBALL': 'Handball',
            'ICE_HOCKEY': 'Ice Hockey',
            'RUGBY': 'Rugby',
            'SNOOKER': 'Snooker',
            'TABLE_TENNIS': 'Table Tennis',
            'WATER_POLO': 'Water Polo',
            'DARTS': 'Darts',
            'ESPORTS': 'Esports',
            'HORSE_RACING': 'Horse Racing',
            'BASEBALL': 'Baseball',
            'KABADDI': 'Kabaddi',
            'ATHLETICS': 'Athletics',
        }
        return sport_choices.get(self.sport, self.sport)

class Season(models.Model):
    """Season information for competitions"""
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='seasons')
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.competition.name} - {self.name}"


# --- ENHANCED TEAM MODELS ---

class Team(models.Model):
    SPORT_CHOICES = [
        ('FOOTBALL', 'Football'),
        ('CRICKET', 'Cricket'),
        ('VOLLEYBALL', 'Volleyball'),
        ('TENNIS', 'Tennis'),
        ('BASKETBALL', 'Basketball'),
        ('BADMINTON', 'Badminton'),
        ('BOXING', 'Boxing'),
        ('MOTORSPORT', 'Motorsport'),
        ('GOLF', 'Golf'),
        ('HANDBALL', 'Handball'),
        ('ICE_HOCKEY', 'Ice Hockey'),
        ('RUGBY', 'Rugby'),
        ('SNOOKER', 'Snooker'),
        ('TABLE_TENNIS', 'Table Tennis'),
        ('WATER_POLO', 'Water Polo'),
        ('DARTS', 'Darts'),
        ('ESPORTS', 'Esports'),
        ('HORSE_RACING', 'Horse Racing'),
        ('BASEBALL', 'Baseball'),
        ('KABADDI', 'Kabaddi'),
        ('ATHLETICS', 'Athletics'),
    ]
    
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50, blank=True)
    logo = models.ImageField(upload_to='teams/logos/', blank=True, null=True)
    sport = models.CharField(max_length=50, choices=SPORT_CHOICES)
    country = models.CharField(max_length=100, default="International")
    founded_year = models.IntegerField(null=True, blank=True)
    stadium = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    total_points = models.IntegerField(default=0, help_text="Total points calculated from match results")
    rank = models.IntegerField(null=True, blank=True, help_text="Current ranking position")
    flashscore_id = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-total_points', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.sport})"

    def update_points(self):
        points = 0
        if self.sport == 'FOOTBALL':
            matches = FootballMatch.objects.filter(Q(home_team=self) | Q(away_team=self), status='FINISHED')
            for m in matches:
                if m.home_score == m.away_score:
                    points += 1
                elif (m.home_team == self and m.home_score > m.away_score) or \
                     (m.away_team == self and m.away_score > m.home_score):
                    points += 3
        
        elif self.sport == 'VOLLEYBALL':
            matches = VolleyballMatch.objects.filter(Q(home_team=self) | Q(away_team=self), status='FINISHED')
            for m in matches:
                if (m.home_team == self and m.home_sets_won > m.away_sets_won) or \
                   (m.away_team == self and m.away_sets_won > m.home_sets_won):
                    points += 2
        
        self.total_points = points
        self.save()

    def get_form(self, last_matches=5):
        """Get team form for last N matches"""
        if self.sport == 'FOOTBALL':
            matches = FootballMatch.objects.filter(
                Q(home_team=self) | Q(away_team=self), 
                status='FINISHED'
            ).order_by('-match_datetime')[:last_matches]
            
            form = []
            for match in matches:
                if match.home_team == self:
                    if match.home_score > match.away_score:
                        form.append('W')
                    elif match.home_score == match.away_score:
                        form.append('D')
                    else:
                        form.append('L')
                else:
                    if match.away_score > match.home_score:
                        form.append('W')
                    elif match.away_score == match.home_score:
                        form.append('D')
                    else:
                        form.append('L')
            return form
        return []


# --- ENHANCED PLAYER MODELS ---

class Player(models.Model):
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('DEF', 'Defender'),
        ('MID', 'Midfielder'),
        ('FWD', 'Forward'),
        ('ALL', 'All-Rounder'),
        ('BATS', 'Batsman'),
        ('BOWL', 'Bowler'),
        ('WK', 'Wicket Keeper'),
        ('SINGLE', 'Singles'),
        ('DOUBLE', 'Doubles'),
        ('MIXED', 'Mixed Doubles'),
    ]
    
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players', null=True, blank=True)
    jersey_number = models.IntegerField(null=True, blank=True)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    photo = models.ImageField(upload_to='players/photos/', blank=True, null=True)
    biography = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    flashscore_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Statistics
    matches_played = models.IntegerField(default=0)
    goals_scored = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.team.name if self.team else 'Free Agent'})"

    def get_age(self):
        if self.date_of_birth:
            return int((timezone.now().date() - self.date_of_birth).days / 365.25)
        return None


# --- ENHANCED MATCH MODELS ---

class MatchBase(models.Model):
    STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming'), 
        ('LIVE', 'Live'), 
        ('FINISHED', 'Finished'),
        ('POSTPONED', 'Postponed'),
        ('CANCELLED', 'Cancelled')
    ]
    SOURCE_CHOICES = [('MANUAL', 'Manual (Internal)'), ('API', 'External API (Auto)')]
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UPCOMING')
    data_source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='MANUAL')
    external_api_id = models.CharField(max_length=100, null=True, blank=True, help_text="ID from sports API provider")
    
    highlights_url = models.URLField(blank=True, null=True)
    match_datetime = models.DateTimeField(null=True, blank=True)
    
    # Enhanced competition information
    competition = models.ForeignKey(Competition, on_delete=models.SET_NULL, null=True, blank=True, related_name='fb_matches')
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True)
    round_name = models.CharField(max_length=120, blank=True, default="")
    
    # Venue and match details
    venue = models.CharField(max_length=120, blank=True, default="")
    city = models.CharField(max_length=80, blank=True, default="")
    country = models.CharField(max_length=80, blank=True, default="")
    referee = models.CharField(max_length=120, blank=True, default="")
    attendance = models.IntegerField(null=True, blank=True)
    
    # Additional metadata
    weather = models.CharField(max_length=100, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'FINISHED':
            if hasattr(self, 'home_team'): self.home_team.update_points()
            if hasattr(self, 'away_team'): self.away_team.update_points()


class MatchEvent(models.Model):
    """Events during a match (goals, cards, substitutions, etc.)"""
    EVENT_TYPES = [
        ('GOAL', 'Goal'),
        ('ASSIST', 'Assist'),
        ('YELLOW_CARD', 'Yellow Card'),
        ('RED_CARD', 'Red Card'),
        ('SUBSTITUTION', 'Substitution'),
        ('PENALTY', 'Penalty'),
        ('OWN_GOAL', 'Own Goal'),
        ('VAR', 'VAR Review'),
        ('INJURY', 'Injury'),
        ('HALF_TIME', 'Half Time'),
        ('FULL_TIME', 'Full Time'),
    ]
    
    match_type = models.CharField(max_length=20)  # 'football', 'cricket', etc.
    match_id = models.IntegerField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    minute = models.IntegerField()
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    extra_info = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['minute']
    
    def __str__(self):
        return f"{self.minute}' - {self.get_event_type_display()}: {self.description}"


class FootballMatch(MatchBase):
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='fb_home')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='fb_away')
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    
    # Football specific fields
    home_halftime_score = models.IntegerField(null=True, blank=True)
    away_halftime_score = models.IntegerField(null=True, blank=True)
    home_pens = models.IntegerField(null=True, blank=True)
    away_pens = models.IntegerField(null=True, blank=True)
    
    # Match statistics
    home_possession = models.IntegerField(null=True, blank=True)
    away_possession = models.IntegerField(null=True, blank=True)
    home_shots = models.IntegerField(null=True, blank=True)
    away_shots = models.IntegerField(null=True, blank=True)
    home_shots_on_target = models.IntegerField(null=True, blank=True)
    away_shots_on_target = models.IntegerField(null=True, blank=True)
    home_corners = models.IntegerField(null=True, blank=True)
    away_corners = models.IntegerField(null=True, blank=True)
    home_fouls = models.IntegerField(null=True, blank=True)
    away_fouls = models.IntegerField(null=True, blank=True)
    home_yellow_cards = models.IntegerField(null=True, blank=True)
    away_yellow_cards = models.IntegerField(null=True, blank=True)
    home_red_cards = models.IntegerField(null=True, blank=True)
    away_red_cards = models.IntegerField(null=True, blank=True)
    
    # Odds (if implementing betting features)
    home_win_odds = models.FloatField(null=True, blank=True)
    draw_odds = models.FloatField(null=True, blank=True)
    away_win_odds = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.home_team.name} {self.home_score} - {self.away_score} {self.away_team.name}"
    
    def get_result(self):
        if self.status == 'FINISHED':
            if self.home_score > self.away_score:
                return 'H'
            elif self.home_score < self.away_score:
                return 'A'
            else:
                return 'D'
        return None


class CricketMatch(MatchBase):
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='cr_home')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='cr_away')
    home_runs = models.IntegerField(default=0)
    home_wickets = models.IntegerField(default=0)
    away_runs = models.IntegerField(default=0)
    away_wickets = models.IntegerField(default=0)
    home_overs = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    away_overs = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    
    # Cricket specific fields
    toss_winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='cr_toss_wins')
    toss_decision = models.CharField(max_length=10, choices=[('BAT', 'Batting'), ('BOWL', 'Bowling')], null=True, blank=True)
    current_status_text = models.CharField(max_length=255, blank=True)
    is_live_now = models.BooleanField(default=False)
    
    # Match format
    match_format = models.CharField(max_length=20, choices=[
        ('T20', 'T20'),
        ('ODI', 'ODI'),
        ('TEST', 'Test'),
        ('T10', 'T10'),
        ('T100', 'The Hundred'),
    ], default='T20')
    
    # Innings details
    home_innings1_runs = models.IntegerField(null=True, blank=True)
    home_innings1_wickets = models.IntegerField(null=True, blank=True)
    home_innings1_overs = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    away_innings1_runs = models.IntegerField(null=True, blank=True)
    away_innings1_wickets = models.IntegerField(null=True, blank=True)
    away_innings1_overs = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    
    # Competition relation
    competition = models.ForeignKey(Competition, on_delete=models.SET_NULL, null=True, blank=True, related_name='cr_matches')
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.home_team.name} {self.home_runs}/{self.home_wickets} vs {self.away_team.name} {self.away_runs}/{self.away_wickets}"


class VolleyballMatch(MatchBase):
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='vol_home')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='vol_away')
    home_sets_won = models.IntegerField(default=0)
    away_sets_won = models.IntegerField(default=0)
    
    # Set scores
    home_set1 = models.IntegerField(null=True, blank=True)
    away_set1 = models.IntegerField(null=True, blank=True)
    home_set2 = models.IntegerField(null=True, blank=True)
    away_set2 = models.IntegerField(null=True, blank=True)
    home_set3 = models.IntegerField(null=True, blank=True)
    away_set3 = models.IntegerField(null=True, blank=True)
    home_set4 = models.IntegerField(null=True, blank=True)
    away_set4 = models.IntegerField(null=True, blank=True)
    home_set5 = models.IntegerField(null=True, blank=True)
    away_set5 = models.IntegerField(null=True, blank=True)
    
    # Competition relation
    competition = models.ForeignKey(Competition, on_delete=models.SET_NULL, null=True, blank=True, related_name='vol_matches')
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True)
    
    def get_set_scores(self):
        sets = []
        for i in range(1, 6):
            home_score = getattr(self, f'home_set{i}', None)
            away_score = getattr(self, f'away_set{i}', None)
            if home_score is not None and away_score is not None:
                sets.append(f"{home_score}-{away_score}")
        return ', '.join(sets)
    
    def __str__(self):
        return f"{self.home_team.name} {self.home_sets_won} - {self.away_sets_won} {self.away_team.name}"


class UniversalMatch(MatchBase):
    sport = models.CharField(max_length=50, choices=Team.SPORT_CHOICES)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='uni_home')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='uni_away')
    home_score = models.CharField(max_length=20, default="0")
    away_score = models.CharField(max_length=20, default="0")
    match_info = models.CharField(max_length=100, blank=True, null=True)
    
    # Sport-specific details stored as JSON
    sport_details = models.JSONField(default=dict, blank=True)
    
    # Competition relation
    competition = models.ForeignKey(Competition, on_delete=models.SET_NULL, null=True, blank=True, related_name='uni_matches')
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.get_sport_display()}: {self.home_team.name} vs {self.away_team.name}"


# --- RANKINGS AND STANDINGS ---

class Standing(models.Model):
    """League standings and rankings"""
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='standings')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='standings')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='standings')
    
    position = models.IntegerField()
    played = models.IntegerField(default=0)
    won = models.IntegerField(default=0)
    drawn = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)
    
    # Goals/Points
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    
    # Form (last 5 matches)
    form = models.CharField(max_length=10, blank=True)  # e.g., "WWLDW"
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['competition', 'season', 'team']
        ordering = ['competition', 'season', 'position']
    
    def __str__(self):
        return f"{self.position}. {self.team.name} - {self.points}pts"


class PlayerRanking(models.Model):
    """Player rankings for various sports"""
    RANKING_TYPES = [
        ('ATP', 'ATP Singles'),
        ('WTA', 'WTA Singles'),
        ('ATP_DOUBLES', 'ATP Doubles'),
        ('WTA_DOUBLES', 'WTA Doubles'),
        ('FIFA', 'FIFA World Ranking'),
        ('ICCRANKING', 'ICC Cricket Ranking'),
        ('BWF', 'BWF World Ranking'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='rankings')
    ranking_type = models.CharField(max_length=20, choices=RANKING_TYPES)
    position = models.IntegerField()
    points = models.IntegerField(default=0)
    movement = models.IntegerField(default=0, help_text="Position change from previous ranking")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['player', 'ranking_type']
        ordering = ['ranking_type', 'position']
    
    def __str__(self):
        return f"#{self.position} {self.player.name} ({self.get_ranking_type_display()})"


# --- USER PREFERENCES ---

class UserFavorites(models.Model):
    """User's favorite teams, players, and competitions"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='favorites')
    favorite_teams = models.ManyToManyField(Team, blank=True, related_name='favorited_by')
    favorite_players = models.ManyToManyField(Player, blank=True, related_name='favorited_by')
    favorite_competitions = models.ManyToManyField(Competition, blank=True, related_name='favorited_by')
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    favorite_match_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Favorites"


# --- HEAD-TO-HEAD RECORDS ---

class HeadToHead(models.Model):
    """Head-to-head records between teams"""
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='h2h_team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='h2h_team2')
    sport = models.CharField(max_length=50, choices=Team.SPORT_CHOICES)
    
    total_matches = models.IntegerField(default=0)
    team1_wins = models.IntegerField(default=0)
    team2_wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    
    team1_goals_for = models.IntegerField(default=0)
    team2_goals_for = models.IntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['team1', 'team2', 'sport']
    
    def __str__(self):
        return f"{self.team1.name} vs {self.team2.name} H2H"
    
    def update_h2h(self, match):
        """Update head-to-head statistics after a match"""
        if match.status != 'FINISHED':
            return
            
        self.total_matches += 1
        
        if hasattr(match, 'home_score') and hasattr(match, 'away_score'):
            self.team1_goals_for += match.home_score
            self.team2_goals_for += match.away_score
            
            if match.home_score > match.away_score:
                self.team1_wins += 1
            elif match.home_score < match.away_score:
                self.team2_wins += 1
            else:
                self.draws += 1
        
        self.save()


# --- NEWS AND TRENDS ---

class NewsArticle(models.Model):
    """News articles and updates"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.CharField(max_length=500)
    author = models.CharField(max_length=100)
    image = models.ImageField(upload_to='news/images/', blank=True, null=True)
    
    sport = models.CharField(max_length=50, choices=Team.SPORT_CHOICES, blank=True)
    competition = models.ForeignKey(Competition, on_delete=models.SET_NULL, null=True, blank=True, related_name='news')
    teams = models.ManyToManyField(Team, blank=True, related_name='news')
    players = models.ManyToManyField(Player, blank=True, related_name='news')
    
    is_trending = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-published_at']
    
    def __str__(self):
        return self.title
