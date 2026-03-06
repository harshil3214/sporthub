from django.contrib import admin
from django.db import models
from django.contrib.admin.widgets import AdminSplitDateTime
from .models import VolleyballMatch

class VolleyballMatchAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.DateTimeField: {'widget': AdminSplitDateTime},
    }

    class Media:
        js = ('admin/js/vendor/jquery/jquery.js', 'admin/js/jquery.init.js')

    list_display = ('home_team', 'away_team', 'status', 'match_time')

admin.site.register(VolleyballMatch, VolleyballMatchAdmin)