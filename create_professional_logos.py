import os
import django
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image, ImageDraw, ImageFont
import io

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Team

def create_professional_logos():
    """Create professional-looking team logos with proper colors and styling"""
    
    # Define professional team colors and styles
    team_styles = {
        # Football Teams
        'Real Madrid': {
            'bg': '#FFFFFF',
            'text': '#00529F',
            'accent': '#FEBE10',
            'style': 'circular'
        },
        'Barcelona': {
            'bg': '#004D98',
            'text': '#A50044',
            'accent': '#FF6600',
            'style': 'striped'
        },
        'Bayern Munich': {
            'bg': '#DC052D',
            'text': '#FFFFFF',
            'accent': '#FFFFFF',
            'style': 'circular'
        },
        'Manchester United': {
            'bg': '#DA020E',
            'text': '#FFF0F5',
            'accent': '#FFD700',
            'style': 'shield'
        },
        'Manchester City': {
            'bg': '#6CABDD',
            'text': '#1C2C5B',
            'accent': '#FFC72C',
            'style': 'circular'
        },
        'Liverpool': {
            'bg': '#C8102E',
            'text': '#FFFFFF',
            'accent': '#00B2A9',
            'style': 'circular'
        },
        'Arsenal': {
            'bg': '#EF0107',
            'text': '#FFFFFF',
            'accent': '#FFFFFF',
            'style': 'circular'
        },
        'Chelsea': {
            'bg': '#034694',
            'text': '#FFFFFF',
            'accent': '#FFFFFF',
            'style': 'circular'
        },
        'Tottenham': {
            'bg': '#FFFFFF',
            'text': '#132257',
            'accent': '#FFFFFF',
            'style': 'circular'
        },
        
        # Cricket Teams
        'India': {
            'bg': '#FF6600',
            'text': '#FFFFFF',
            'accent': '#138808',
            'style': 'circular'
        },
        'Australia': {
            'bg': '#FFD700',
            'text': '#00843D',
            'accent': '#FFFFFF',
            'style': 'circular'
        },
        'England': {
            'bg': '#FFFFFF',
            'text': '#00224D',
            'accent': '#CC0000',
            'style': 'circular'
        },
        'Pakistan': {
            'bg': '#006400',
            'text': '#FFFFFF',
            'accent': '#FFFFFF',
            'style': 'circular'
        },
        'South Africa': {
            'bg': '#007A4D',
            'text': '#FFB20F',
            'accent': '#FFFFFF',
            'style': 'circular'
        },
        'New Zealand': {
            'bg': '#000000',
            'text': '#FFFFFF',
            'accent': '#000000',
            'style': 'circular'
        },
        'Mumbai Indians': {
            'bg': '#004BA0',
            'text': '#FFFFFF',
            'accent': '#FFFFFF',
            'style': 'circular'
        },
        'Chennai Super Kings': {
            'bg': '#FFFF00',
            'text': '#0081E8',
            'accent': '#0081E8',
            'style': 'circular'
        },
        'Royal Challengers Bangalore': {
            'bg': '#000000',
            'text': '#FF322E',
            'accent': '#FFFFFF',
            'style': 'circular'
        },
        
        # Basketball Teams
        'Los Angeles Lakers': {
            'bg': '#552583',
            'text': '#FDB927',
            'accent': '#FDB927',
            'style': 'circular'
        },
        'Boston Celtics': {
            'bg': '#007A33',
            'text': '#FFFFFF',
            'accent': '#FFFFFF',
            'style': 'circular'
        },
        'Golden State Warriors': {
            'bg': '#1D428A',
            'text': '#FFC72C',
            'accent': '#FFFFFF',
            'style': 'circular'
        },
        'Brooklyn Nets': {
            'bg': '#000000',
            'text': '#FFFFFF',
            'accent': '#FFFFFF',
            'style': 'circular'
        },
        'Boston Celtics': {
            'bg': '#007A33',
            'text': '#FFFFFF',
            'accent': '#FFFFFF',
            'style': 'circular'
        },
        
        # Default style for other teams
        'default': {
            'bg': '#0066CC',
            'text': '#FFFFFF',
            'accent': '#FFFFFF',
            'style': 'circular'
        }
    }
    
    # Create media directory if it doesn't exist
    media_dir = 'media/teams/logos/'
    os.makedirs(media_dir, exist_ok=True)
    
    print("Creating professional team logos...")
    
    for team in Team.objects.all():
        print(f"Processing team: {team.name}")
        
        # Get team style or use default
        style = team_styles.get(team.name, team_styles['default'])
        
        try:
            # Create professional logo
            img = create_professional_logo(team.name, style)
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG', quality=95)
            img_bytes.seek(0)
            
            # Create a SimpleUploadedFile
            filename = f"{team.name.lower().replace(' ', '_').replace('/', '_')}_logo.png"
            logo_file = SimpleUploadedFile(
                filename,
                img_bytes.read(),
                content_type='image/png'
            )
            
            # Save to team
            team.logo.save(filename, logo_file, save=True)
            print(f"  - Created professional logo: {filename}")
            
        except Exception as e:
            print(f"  - Error creating logo: {e}")
    
    print("Professional logos creation complete!")

def create_professional_logo(team_name, style):
    """Create a professional-looking logo"""
    bg_color = style['bg']
    text_color = style['text']
    accent_color = style['accent']
    logo_style = style['style']
    
    # Create image
    img = Image.new('RGB', (120, 120), bg_color)
    draw = ImageDraw.Draw(img)
    
    if logo_style == 'circular':
        # Create circular logo with border
        draw.ellipse([5, 5, 115, 115], fill=bg_color, outline=accent_color, width=3)
        
        # Add team initials in center
        initials = get_team_initials(team_name)
        draw_text_centered(draw, initials, 60, 60, text_color, 32)
        
    elif logo_style == 'shield':
        # Create shield shape
        points = [
            (60, 10),   # top
            (100, 30),  # right top
            (100, 80),  # right bottom
            (60, 110),  # bottom
            (20, 80),   # left bottom
            (20, 30),   # left top
        ]
        draw.polygon(points, fill=bg_color, outline=accent_color, width=3)
        
        initials = get_team_initials(team_name)
        draw_text_centered(draw, initials, 60, 60, text_color, 28)
        
    elif logo_style == 'striped':
        # Create striped background
        for i in range(0, 120, 20):
            draw.rectangle([i, 0, i+10, 120], fill=accent_color if (i//20) % 2 == 0 else bg_color)
        
        # Add circular border
        draw.ellipse([5, 5, 115, 115], outline=text_color, width=3)
        
        initials = get_team_initials(team_name)
        draw_text_centered(draw, initials, 60, 60, text_color, 30)
        
    else:
        # Default circular style
        draw.ellipse([5, 5, 115, 115], fill=bg_color, outline=accent_color, width=3)
        initials = get_team_initials(team_name)
        draw_text_centered(draw, initials, 60, 60, text_color, 32)
    
    return img

def get_team_initials(team_name):
    """Get team initials for logo"""
    words = team_name.split()
    if len(words) >= 2:
        return words[0][0] + words[1][0]
    else:
        if len(words[0]) >= 2:
            return words[0][:2].upper()
        else:
            return words[0][:1].upper()

def draw_text_centered(draw, text, x, y, color, size):
    """Draw text centered at position"""
    try:
        # Try to use Arial font
        font = ImageFont.truetype("arial.ttf", size)
    except:
        try:
            # Try default font
            font = ImageFont.load_default()
        except:
            font = None
    
    if font:
        # Calculate text position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text
        text_x = x - text_width // 2
        text_y = y - text_height // 2
        
        draw.text((text_x, text_y), text, fill=color, font=font, anchor='lt')
    else:
        # Fallback without font
        text_x = x - len(text) * 3
        text_y = y - 5
        draw.text((text_x, text_y), text, fill=color)

if __name__ == '__main__':
    create_professional_logos()
