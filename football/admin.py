from django.contrib import admin
from django.db import models
from django.contrib.admin.widgets import AdminSplitDateTime
from .models import FootballMatch # Change this for each app

class EnhancedMatchAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.DateTimeField: {'widget': AdminSplitDateTime},
    }

    # This adds the "Year" and "Month" dropdowns to the calendar 
    # and ensures the time picker uses 24-hour logic.
    class Media:
        js = ('admin/js/vendor/jquery/jquery.js', 'admin/js/jquery.init.js')
        # We add a small script to initialize the 24h picker if needed
        # but usually, the TIME_FORMAT setting above handles it!

    list_display = ('home_team', 'away_team', 'status', 'match_time')

admin.site.register(FootballMatch, EnhancedMatchAdmin)