from django.db import models
from django.utils import timezone
from .models import Team, Player, Competition

class VideoHighlight(models.Model):
    """Video highlights for matches and general sports content"""
    
    VIDEO_TYPES = [
        ('match_highlight', 'Match Highlight'),
        ('goal', 'Goal'),
        ('interview', 'Interview'),
        ('analysis', 'Analysis'),
        ('news', 'News Clip'),
        ('trailer', 'Trailer/Promo'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_type = models.CharField(max_length=20, choices=VIDEO_TYPES, default='match_highlight')
    
    # Video URLs - support multiple platforms
    youtube_url = models.URLField(blank=True, help_text="YouTube video URL")
    vimeo_url = models.URLField(blank=True, help_text="Vimeo video URL")
    direct_url = models.URLField(blank=True, help_text="Direct video file URL")
    thumbnail_url = models.URLField(blank=True, help_text="Thumbnail image URL")
    
    # Related content
    match_type = models.CharField(max_length=20, blank=True, help_text="Match type (football, cricket, etc.)")
    match_id = models.PositiveIntegerField(null=True, blank=True, help_text="Match ID if related to a specific match")
    competition = models.ForeignKey(Competition, on_delete=models.SET_NULL, null=True, blank=True)
    teams = models.ManyToManyField(Team, blank=True, related_name='video_highlights')
    players = models.ManyToManyField(Player, blank=True, related_name='video_highlights')
    
    # Metadata
    duration = models.DurationField(null=True, blank=True, help_text="Video duration")
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False, help_text="Feature this video")
    is_premium = models.BooleanField(default=False, help_text="Premium content")
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    published_at = models.DateTimeField(null=True, blank=True, help_text="When to publish this video")
    
    # SEO and discovery
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['video_type', 'featured']),
            models.Index(fields=['published_at']),
            models.Index(fields=['featured', 'published_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug()
        if not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def generate_slug(self):
        """Generate unique slug from title"""
        import re
        base_slug = re.sub(r'[^a-z0-9]+', '-', self.title.lower()).strip('-')
        slug = base_slug
        counter = 1
        while VideoHighlight.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug
    
    def get_embed_url(self):
        """Get embeddable URL for the video"""
        if self.youtube_url:
            # Convert YouTube URL to embed format
            if 'youtube.com/watch?v=' in self.youtube_url:
                video_id = self.youtube_url.split('v=')[1].split('&')[0]
                return f"https://www.youtube.com/embed/{video_id}"
            elif 'youtu.be/' in self.youtube_url:
                video_id = self.youtube_url.split('youtu.be/')[1].split('?')[0]
                return f"https://www.youtube.com/embed/{video_id}"
        elif self.vimeo_url:
            # Convert Vimeo URL to embed format
            if 'vimeo.com/' in self.vimeo_url:
                video_id = self.vimeo_url.split('vimeo.com/')[1].split('?')[0]
                return f"https://player.vimeo.com/video/{video_id}"
        elif self.direct_url:
            return self.direct_url
        return None
    
    def get_thumbnail_url(self):
        """Get thumbnail URL with fallback"""
        if self.thumbnail_url:
            return self.thumbnail_url
        elif self.youtube_url:
            # Use YouTube thumbnail
            if 'youtube.com/watch?v=' in self.youtube_url:
                video_id = self.youtube_url.split('v=')[1].split('&')[0]
                return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            elif 'youtu.be/' in self.youtube_url:
                video_id = self.youtube_url.split('youtu.be/')[1].split('?')[0]
                return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        return "https://picsum.photos/seed/video/800/450.jpg"
    
    def increment_views(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def get_related_videos(self, limit=6):
        """Get related videos based on teams, competition, or video type"""
        related = VideoHighlight.objects.filter(id__ne=self.id)
        
        # First try videos with same teams
        if self.teams.exists():
            related = related.filter(teams__in=self.teams.all())
        
        # Then try same competition
        if self.competition and related.count() < limit:
            related = related | VideoHighlight.objects.filter(competition=self.competition).exclude(id=self.id)
        
        # Finally try same video type
        if related.count() < limit:
            related = related | VideoHighlight.objects.filter(video_type=self.video_type).exclude(id=self.id)
        
        return related.distinct()[:limit]


class VideoPlaylist(models.Model):
    """Video playlists for organizing content"""
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    videos = models.ManyToManyField(VideoHighlight, related_name='playlists')
    is_public = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    
    # Metadata
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    
    class Meta:
        ordering = ['-featured', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            import re
            base_slug = re.sub(r'[^a-z0-9]+', '-', self.name.lower()).strip('-')
            slug = base_slug
            counter = 1
            while VideoPlaylist.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_total_duration(self):
        """Get total duration of all videos in playlist"""
        total = timezone.timedelta()
        for video in self.videos.all():
            if video.duration:
                total += video.duration
        return total
    
    def get_video_count(self):
        """Get number of videos in playlist"""
        return self.videos.count()


class VideoComment(models.Model):
    """Comments on video highlights"""
    
    video = models.ForeignKey(VideoHighlight, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    content = models.TextField()
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['video', 'is_approved']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.video.title}"
