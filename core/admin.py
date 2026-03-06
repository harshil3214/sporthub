from django.contrib import admin
from django.contrib import messages
from .models import (
    Team, CricketMatch, FootballMatch, VolleyballMatch, 
    TeacherProfile, StudentProfile, UniversalMatch
)
# This imports the fetching logic we wrote in services.py
from .services import update_match_from_api 

# --- REUSABLE ACTION ---

@admin.action(description="Fetch latest scores from API")
def refresh_api_scores(modeladmin, request, queryset):
    """
    Triggers the API sync for selected matches.
    """
    updated_count = 0
    skipped_count = 0
    
    for match in queryset:
        # Check if match is set to API and has an ID
        if hasattr(match, 'data_source') and match.data_source == 'API' and match.external_api_id:
            success = update_match_from_api(match)
            if success:
                updated_count += 1
            else:
                skipped_count += 1
        else:
            skipped_count += 1
            
    if updated_count > 0:
        modeladmin.message_user(
            request, 
            f"Successfully updated {updated_count} matches from API.", 
            messages.SUCCESS
        )
    if skipped_count > 0:
        modeladmin.message_user(
            request, 
            f"Skipped {skipped_count} matches (either Manual source or missing API ID).", 
            messages.WARNING
        )

# --- ADMIN REGISTRATIONS ---

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'sport', 'total_points')
    search_fields = ('name',)
    list_filter = ('sport',)

@admin.register(CricketMatch)
class CricketMatchAdmin(admin.ModelAdmin):
    # Added runs, wickets, and overs to the display for better visibility
    list_display = (
        'home_team', 'home_runs', 'home_wickets', 'home_overs', 
        'away_team', 'away_runs', 'away_wickets', 'away_overs', 
        'status', 'data_source'
    )
    list_filter = ('status', 'data_source', 'match_datetime')
    search_fields = ('home_team__name', 'away_team__name', 'external_api_id')
    
    # Allows you to edit scores directly in the list view for manual matches
    list_editable = ('home_runs', 'home_wickets', 'away_runs', 'away_wickets', 'status')
    
    # Adds the "Fetch latest scores from API" button to the dropdown
    actions = [refresh_api_scores]

@admin.register(FootballMatch)
class FootballMatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'home_score', 'away_score', 'away_team', 'status', 'data_source')
    list_filter = ('status', 'data_source')
    list_editable = ('home_score', 'away_score', 'status')
    search_fields = ('home_team__name', 'away_team__name')
    actions = [refresh_api_scores]

@admin.register(VolleyballMatch)
class VolleyballMatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'home_sets_won', 'away_sets_won', 'away_team', 'status', 'data_source')
    list_filter = ('status', 'data_source')
    list_editable = ('home_sets_won', 'away_sets_won', 'status')
    actions = [refresh_api_scores]

@admin.register(UniversalMatch)
class UniversalMatchAdmin(admin.ModelAdmin):
    list_display = ('sport', 'home_team', 'home_score', 'away_score', 'away_team', 'status', 'data_source')
    list_filter = ('sport', 'status', 'data_source')
    list_editable = ('home_score', 'away_score', 'status')
    search_fields = ('home_team__name', 'away_team__name')
    actions = [refresh_api_scores]

admin.site.register(TeacherProfile)
admin.site.register(StudentProfile)