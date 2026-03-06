import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import FootballMatch, CricketMatch, VolleyballMatch, UniversalMatch, MatchEvent

class MatchUpdatesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'match_updates'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'subscribe')
        
        if message_type == 'subscribe_matches':
            # Send current live matches
            live_matches = await self.get_live_matches()
            await self.send(text_data=json.dumps({
                'type': 'live_matches',
                'matches': live_matches
            }))
    
    # Receive message from room group
    async def match_update(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))
    
    @database_sync_to_async
    def get_live_matches(self):
        matches = []
        
        # Football matches
        fb_matches = FootballMatch.objects.filter(status='LIVE').select_related('home_team', 'away_team', 'competition')
        for match in fb_matches:
            matches.append({
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
            matches.append({
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
        
        # Volleyball matches
        vb_matches = VolleyballMatch.objects.filter(status='LIVE').select_related('home_team', 'away_team', 'competition')
        for match in vb_matches:
            matches.append({
                'id': match.id,
                'sport': 'volleyball',
                'home_team': match.home_team.name,
                'away_team': match.away_team.name,
                'home_score': match.home_sets_won,
                'away_score': match.away_sets_won,
                'competition': match.competition.name if match.competition else 'Volleyball',
                'status': match.status,
                'venue': match.venue,
                'current_set': getattr(match, 'current_set', 1)
            })
        
        # Universal matches
        uni_matches = UniversalMatch.objects.filter(status='LIVE').select_related('home_team', 'away_team', 'competition')
        for match in uni_matches:
            matches.append({
                'id': match.id,
                'sport': match.sport.lower(),
                'home_team': match.home_team.name,
                'away_team': match.away_team.name,
                'home_score': match.home_score,
                'away_score': match.away_score,
                'competition': match.competition.name if match.competition else match.get_sport_display(),
                'status': match.status,
                'venue': match.venue
            })
        
        return matches

class MatchDetailConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.room_group_name = f'match_{self.match_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'ping')
        
        if message_type == 'ping':
            await self.send(text_data=json.dumps({'type': 'pong'}))
    
    # Receive message from room group
    async def match_event(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))
