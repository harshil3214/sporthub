import os
import django
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
import requests

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Team

def add_team_logos():
    """Add placeholder logos to teams"""
    
    # Logo URLs for some major teams (using placeholder images)
    team_logos = {
        'Real Madrid': 'https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg',
        'Barcelona': 'https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona.svg',
        'Bayern Munich': 'https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_M%C3%BCnchen_logo_2017.svg',
        'Manchester United': 'https://upload.wikimedia.org/wikipedia/en/7/7a/Manchester_United_FC crest.svg',
        'Liverpool': 'https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg',
        'Manchester City': 'https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC crest.svg',
        'Chelsea': 'https://upload.wikimedia.org/wikipedia/en/c/cc/Chelsea_FC.svg',
        'Arsenal': 'https://upload.wikimedia.org/wikipedia/en/0/0c/Arsenal_FC.svg',
        'Mumbai Indians': 'https://upload.wikimedia.org/wikipedia/en/6/6d/Mumbai_Indians_Logo.svg',
        'Chennai Super Kings': 'https://upload.wikimedia.org/wikipedia/en/2/2c/Chennai_Super_Kings_Logo.svg',
        'Royal Challengers Bangalore': 'https://upload.wikimedia.org/wikipedia/en/2/20/Royal_Challengers_Bangalore_Logo.svg',
        'Italy Volley': 'https://via.placeholder.com/120x120/0066cc/ffffff?text=ITA',
        'Brazil Volley': 'https://via.placeholder.com/120x120/009739/ffffff?text=BRA',
        'Russia Volley': 'https://via.placeholder.com/120x120/cc0000/ffffff?text=RUS',
        'India Kabaddi': 'https://via.placeholder.com/120x120/FF9933/ffffff?text=IND',
        'Iran Kabaddi': 'https://via.placeholder.com/120x120/008000/ffffff?text=IRN',
    }
    
    # Create media directory if it doesn't exist
    media_dir = 'media/teams/logos/'
    os.makedirs(media_dir, exist_ok=True)
    
    print("Adding team logos...")
    
    for team in Team.objects.all():
        print(f"Processing team: {team.name}")
        
        # Check if team already has a logo
        if team.logo:
            print(f"  - Already has logo: {team.logo.name}")
            continue
        
        # Get logo URL
        logo_url = team_logos.get(team.name)
        if not logo_url:
            # Use a generic placeholder based on sport
            sport_colors = {
                'FOOTBALL': '#0066cc',
                'CRICKET': '#008000', 
                'BASKETBALL': '#FF6600',
                'TENNIS': '#FFD700',
                'VOLLEYBALL': '#9900CC',
            }
            color = sport_colors.get(team.sport, '#666666')
            logo_url = f'https://via.placeholder.com/120x120/{color.replace("#", "")}/ffffff?text={team.name[:3].upper()}'
        
        try:
            # Download the logo
            response = requests.get(logo_url, timeout=10)
            response.raise_for_status()
            
            # Create a SimpleUploadedFile
            filename = f"{team.name.lower().replace(' ', '_')}_logo.png"
            logo_file = SimpleUploadedFile(
                filename,
                response.content,
                content_type='image/png'
            )
            
            # Save to team
            team.logo.save(filename, logo_file, save=True)
            print(f"  - Added logo: {filename}")
            
        except Exception as e:
            print(f"  - Error adding logo: {e}")
            # Create a simple text-based logo
            try:
                from PIL import Image, ImageDraw, ImageFont
                import io
                
                # Create a simple image
                img = Image.new('RGB', (120, 120), color='#0066cc')
                draw = ImageDraw.Draw(img)
                
                # Add team name initials
                initials = ''.join([word[0] for word in team.name.split() if word])[:3].upper()
                draw.text((60, 60), initials, fill='white', anchor='mm')
                
                # Convert to bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                filename = f"{team.name.lower().replace(' ', '_')}_logo.png"
                logo_file = SimpleUploadedFile(
                    filename,
                    img_bytes.read(),
                    content_type='image/png'
                )
                
                team.logo.save(filename, logo_file, save=True)
                print(f"  - Created simple logo: {filename}")
                
            except Exception as e2:
                print(f"  - Could not create simple logo: {e2}")
    
    print("Team logos update complete!")

if __name__ == '__main__':
    add_team_logos()
