from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from .models_video import VideoHighlight, VideoPlaylist, VideoComment
from .models import Team, Player, Competition

def video_highlights(request):
    """Main video highlights page"""
    
    # Get filters
    video_type = request.GET.get('type', '')
    competition_id = request.GET.get('competition', '')
    team_id = request.GET.get('team', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    videos = VideoHighlight.objects.filter(
        published_at__lte=timezone.now()
    ).select_related('competition').prefetch_related('teams', 'players')
    
    # Apply filters
    if video_type:
        videos = videos.filter(video_type=video_type)
    
    if competition_id:
        videos = videos.filter(competition_id=competition_id)
    
    if team_id:
        videos = videos.filter(teams__id=team_id)
    
    if search:
        videos = videos.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(tags__icontains=search)
        )
    
    # Order by featured first, then by published date
    videos = videos.order_by('-featured', '-published_at')
    
    # Pagination
    paginator = Paginator(videos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    competitions = Competition.objects.filter(
        videohighlights__isnull=False
    ).distinct().order_by('name')
    
    teams = Team.objects.filter(
        videohighlights__isnull=False
    ).distinct().order_by('name')
    
    context = {
        'page_obj': page_obj,
        'video_types': VideoHighlight.VIDEO_TYPES,
        'competitions': competitions,
        'teams': teams,
        'selected_type': video_type,
        'selected_competition': competition_id,
        'selected_team': team_id,
        'search_query': search,
    }
    
    return render(request, 'core/video_highlights.html', context)

def video_detail(request, slug):
    """Individual video page"""
    video = get_object_or_404(
        VideoHighlight.objects.select_related('competition').prefetch_related('teams', 'players'),
        slug=slug
    )
    
    # Increment view count
    video.increment_views()
    
    # Get related videos
    related_videos = video.get_related_videos()
    
    # Get comments
    comments = video.comments.filter(is_approved=True).select_related('user').order_by('-created_at')
    
    # Get playlists containing this video
    playlists = video.playlists.filter(is_public=True)
    
    context = {
        'video': video,
        'related_videos': related_videos,
        'comments': comments,
        'playlists': playlists,
    }
    
    return render(request, 'core/video_detail.html', context)

@login_required
def video_comment(request, video_id):
    """Add comment to video"""
    video = get_object_or_404(VideoHighlight, id=video_id)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        
        if content:
            comment = VideoComment.objects.create(
                video=video,
                user=request.user,
                content=content
            )
            
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'user': comment.user.username,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                }
            })
        else:
            return JsonResponse({'success': False, 'error': 'Comment cannot be empty'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def video_like(request, video_id):
    """Like/unlike a video"""
    video = get_object_or_404(VideoHighlight, id=video_id)
    
    if request.method == 'POST':
        # This is a simplified like system
        # In a real app, you'd have a separate Like model
        video.like_count += 1
        video.save(update_fields=['like_count'])
        
        return JsonResponse({
            'success': True,
            'like_count': video.like_count
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def video_playlists(request):
    """Browse video playlists"""
    playlists = VideoPlaylist.objects.filter(
        is_public=True,
        videos__published_at__lte=timezone.now()
    ).distinct().annotate(
        video_count=Count('videos')
    ).order_by('-featured', 'name')
    
    # Pagination
    paginator = Paginator(playlists, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'core/video_playlists.html', context)

def video_playlist_detail(request, slug):
    """Individual playlist page"""
    playlist = get_object_or_404(
        VideoPlaylist.objects.prefetch_related('videos'),
        slug=slug
    )
    
    videos = playlist.videos.filter(
        published_at__lte=timezone.now()
    ).order_by('published_at')
    
    context = {
        'playlist': playlist,
        'videos': videos,
    }
    
    return render(request, 'core/video_playlist_detail.html', context)

def video_search_api(request):
    """API for video search"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'results': []})
    
    videos = VideoHighlight.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(tags__icontains=query)
    ).filter(published_at__lte=timezone.now())[:10]
    
    results = []
    for video in videos:
        results.append({
            'id': video.id,
            'title': video.title,
            'description': video.description[:100] + '...' if video.description else '',
            'thumbnail': video.get_thumbnail_url(),
            'duration': str(video.duration) if video.duration else None,
            'view_count': video.view_count,
            'url': f'/videos/{video.slug}/',
            'type': video.get_video_type_display(),
        })
    
    return JsonResponse({'results': results})

def video_trending(request):
    """Trending videos page"""
    # Get videos with most views in the last 7 days
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)
    
    trending_videos = VideoHighlight.objects.filter(
        published_at__gte=seven_days_ago,
        published_at__lte=timezone.now()
    ).order_by('-view_count', '-like_count')[:20]
    
    # Also get most recent videos
    recent_videos = VideoHighlight.objects.filter(
        published_at__lte=timezone.now()
    ).order_by('-published_at')[:20]
    
    context = {
        'trending_videos': trending_videos,
        'recent_videos': recent_videos,
    }
    
    return render(request, 'core/video_trending.html', context)
