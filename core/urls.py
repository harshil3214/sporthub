from django.urls import path
from . import views
from . import views_scorecard
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 0. Public Homepage
    path('', views.home, name='home'),
    
    # 1. Landing & Auth
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # 2. The Redirector (THIS FIXES YOUR ERROR)
    path('login-success/', views.login_redirect_view, name='login_success'),
    
    # 3. Main Pages
    path('dashboard/', views.home_dashboard, name='home_dashboard'),
    path('scores/', views.scores, name='scores'),
    path('my-students/', views.teacher_students_list, name='my_students'),
    
    # 4. Competitions & Rankings
    path('competitions/', views.competitions_view, name='competitions'),
    path('competitions/<int:competition_id>/', views.competition_detail, name='competition_detail'),
    path('rankings/', views.rankings_view, name='rankings'),
    
    # 5. Teams & Players
    path('team/<int:team_id>/', views.team_profile, name='team_profile'),
    path('player/<int:player_id>/', views.player_profile, name='player_profile'),
    path('head-to-head/<int:team1_id>/<int:team2_id>/', views.head_to_head_view, name='head_to_head'),
    
    # 6. News
    path('news/', views.news_view, name='news'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    
    # 7. User Features
    path('favorites/', views.favorites_view, name='favorites'),
    path('toggle-favorite/<str:content_type>/<int:object_id>/', views.toggle_favorite, name='toggle_favorite'),
    
    # 8. Calendar
    path('calendar/', views.calendar_view, name='calendar'),
    
    # 9. Background Checks
    path('check-status/', views.check_approval_status, name='check_status'),
    path('get-live-scores/', views.get_live_scores, name='get_live_scores'),

    # 10. Match Center
    path('matches/<str:sport>/<int:match_id>/', views.match_detail, name='match_detail'),
    
    # 11. New API endpoints
    path('api/live-scores/', views.live_scores_api, name='live_scores_api'),
    path('api/search/', views.search_api, name='search_api'),
    path('api/compare-players/', views.player_comparison, name='player_comparison'),
    
    # 12. User settings
    path('notifications/', views.notifications_settings, name='notifications_settings'),
    
    # 13. Scorecard APIs
    path('api/live-scorecard/<int:match_id>/', views_scorecard.live_scorecard_api, name='live_scorecard_api'),
    path('api/scorecard/<int:match_id>/', views_scorecard.static_scorecard_api, name='static_scorecard_api'),
    path('scorecard/<int:match_id>/', views.scorecard_view, name='scorecard'),
]