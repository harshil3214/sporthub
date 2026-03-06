import os
import django
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
import requests
from PIL import Image, ImageDraw, ImageFont
import io

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Team

def add_official_team_logos():
    """Add official team logos using better sources and styling"""
    
    # Official team logo URLs from reliable sources
    official_logos = {
        # Football Teams
        'Real Madrid': 'https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg',
        'Barcelona': 'https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona.svg',
        'Bayern Munich': 'https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_M%C3%BCnchen_logo_2017.svg',
        'Manchester United': 'https://upload.wikimedia.org/wikipedia/en/7/7a/Manchester_United_FC_crest.svg',
        'Manchester City': 'https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_crest.svg',
        'Liverpool': 'https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg',
        'Chelsea': 'https://upload.wikimedia.org/wikipedia/en/c/cc/Chelsea_FC.svg',
        'Arsenal': 'https://upload.wikimedia.org/wikipedia/en/0/0c/Arsenal_FC.svg',
        'Tottenham': 'https://upload.wikimedia.org/wikipedia/en/b/bb/Tottenham_Hotspur.svg',
        'Juventus': 'https://upload.wikimedia.org/wikipedia/en/1/16/Juventus_FC_2017_logo.svg',
        'AC Milan': 'https://upload.wikimedia.org/wikipedia/en/0/0a/AC_Milan_logo_2017.svg',
        'Inter Milan': 'https://upload.wikimedia.org/wikipedia/en/5/51/Inter_Milan_2021.svg',
        'PSG': 'https://upload.wikimedia.org/wikipedia/commons/8/86/Paris_Saint-Germain_FC.svg',
        
        # Cricket Teams
        'India': 'https://upload.wikimedia.org/wikipedia/en/8/85/BCCI_logo.svg',
        'Australia': 'https://upload.wikimedia.org/wikipedia/en/4/41/Cricket_Australia.svg',
        'England': 'https://upload.wikimedia.org/wikipedia/en/f/f2/ECCB_logo.svg',
        'Pakistan': 'https://upload.wikimedia.org/wikipedia/en/6/65/PCB_logo.svg',
        'South Africa': 'https://upload.wikimedia.org/wikipedia/en/8/87/CSA_logo.svg',
        'New Zealand': 'https://upload.wikimedia.org/wikipedia/en/c/c2/New_Zealand_Cricket.svg',
        'West Indies': 'https://upload.wikimedia.org/wikipedia/en/6/6a/West_Indies_Cricket_Board.svg',
        'Sri Lanka': 'https://upload.wikimedia.org/wikipedia/en/2/2c/Sri_Lanka_Cricket_Logo.svg',
        'Bangladesh': 'https://upload.wikimedia.org/wikipedia/en/9/9e/Bangladesh_Cricket_Board_logo.svg',
        'Afghanistan': 'https://upload.wikimedia.org/wikipedia/en/2/21/Afghanistan_Cricket_Board_logo.svg',
        
        # IPL Teams
        'Mumbai Indians': 'https://upload.wikimedia.org/wikipedia/en/6/6d/Mumbai_Indians_Logo.svg',
        'Chennai Super Kings': 'https://upload.wikimedia.org/wikipedia/en/2/2c/Chennai_Super_Kings_Logo.svg',
        'Royal Challengers Bangalore': 'https://upload.wikimedia.org/wikipedia/en/2/20/Royal_Challengers_Bangalore_Logo.svg',
        'Kolkata Knight Riders': 'https://upload.wikimedia.org/wikipedia/en/8/86/Kolkata_Knight_Riders_Logo.svg',
        'Delhi Capitals': 'https://upload.wikimedia.org/wikipedia/en/6/6e/Delhi_Capitals_IPL.svg',
        'Rajasthan Royals': 'https://upload.wikimedia.org/wikipedia/en/2/29/Rajasthan_Royals_Logo.svg',
        'Sunrisers Hyderabad': 'https://upload.wikimedia.org/wikipedia/en/8/8a/Sunrisers_Hyderabad_Logo.svg',
        'Punjab Kings': 'https://upload.wikimedia.org/wikipedia/en/6/66/Punjab_Kings_IPL.svg',
        'Lucknow Super Giants': 'https://upload.wikimedia.org/wikipedia/en/3/3a/Lucknow_Super_Giants_IPL.svg',
        'Gujarat Titans': 'https://upload.wikimedia.org/wikipedia/en/8/89/Gujarat_Titans_IPL.svg',
        
        # Basketball Teams
        'Los Angeles Lakers': 'https://upload.wikimedia.org/wikipedia/commons/3/3c/Los_Angeles_Lakers_logo.svg',
        'Boston Celtics': 'https://upload.wikimedia.org/wikipedia/commons/8/8b/Boston_Celtics_logo.svg',
        'Golden State Warriors': 'https://upload.wikimedia.org/wikipedia/commons/3/31/Golden_State_Warriors_logo.svg',
        'Miami Heat': 'https://upload.wikimedia.org/wikipedia/commons/3/34/Miami_Heat_logo.svg',
        'Brooklyn Nets': 'https://upload.wikimedia.org/wikipedia/commons/9/96/Brooklyn_Nets_new_logo.svg',
        'Chicago Bulls': 'https://upload.wikimedia.org/wikipedia/commons/d/d1/Chicago_Bulls_logo.svg',
        'Cleveland Cavaliers': 'https://upload.wikimedia.org/wikipedia/commons/9/99/Cleveland_Cavaliers_logo.svg',
        'Phoenix Suns': 'https://upload.wikimedia.org/wikipedia/commons/2/27/Phoenix_Suns_logo.svg',
        
        # Tennis Players (as teams for individual sports)
        'Novak Djokovic': 'https://upload.wikimedia.org/wikipedia/commons/6/66/Novak_Djokovic_2023.svg',
        'Rafael Nadal': 'https://upload.wikimedia.org/wikipedia/commons/4/4d/Rafael_Nadal_2023.svg',
        'Roger Federer': 'https://upload.wikimedia.org/wikipedia/commons/4/41/Roger_Federer_2018.svg',
        'Serena Williams': 'https://upload.wikimedia.org/wikipedia/commons/9/99/Serena_Williams_2019.svg',
    }
    
    # Create media directory if it doesn't exist
    media_dir = 'media/teams/logos/'
    os.makedirs(media_dir, exist_ok=True)
    
    print("Adding official team logos...")
    
    for team in Team.objects.all():
        print(f"Processing team: {team.name}")
        
        # Check if team already has a logo
        if team.logo:
            print(f"  - Already has logo: {team.logo.name}")
            continue
        
        # Get official logo URL
        logo_url = official_logos.get(team.name)
        
        if logo_url:
            try:
                # Download the logo
                response = requests.get(logo_url, timeout=10)
                response.raise_for_status()
                
                # For SVG files, we need to convert to PNG
                if logo_url.endswith('.svg'):
                    # Create a colored background with team initials
                    img = create_logo_from_svg(response.content, team.name)
                else:
                    img = Image.open(io.BytesIO(response.content))
                
                # Resize to standard size
                img = img.resize((120, 120), Image.Resampling.LANCZOS)
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Convert to bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG', quality=95)
                img_bytes.seek(0)
                
                # Create a SimpleUploadedFile
                filename = f"{team.name.lower().replace(' ', '_')}_logo.png"
                logo_file = SimpleUploadedFile(
                    filename,
                    img_bytes.read(),
                    content_type='image/png'
                )
                
                # Save to team
                team.logo.save(filename, logo_file, save=True)
                print(f"  - Added official logo: {filename}")
                
            except Exception as e:
                print(f"  - Error downloading official logo: {e}")
                # Create a better styled logo
                create_styled_logo(team)
        else:
            # Create a styled logo for teams without official logos
            create_styled_logo(team)
    
    print("Official team logos update complete!")

def create_logo_from_svg(svg_content, team_name):
    """Create a logo from SVG content"""
    try:
        # For now, create a styled logo with team colors
        return create_styled_logo_image(team_name)
    except:
        return create_styled_logo_image(team_name)

def create_styled_logo(team):
    """Create a styled logo for teams without official logos"""
    try:
        img = create_styled_logo_image(team.name)
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG', quality=95)
        img_bytes.seek(0)
        
        # Create a SimpleUploadedFile
        filename = f"{team.name.lower().replace(' ', '_')}_logo.png"
        logo_file = SimpleUploadedFile(
            filename,
            img_bytes.read(),
            content_type='image/png'
        )
        
        # Save to team
        team.logo.save(filename, logo_file, save=True)
        print(f"  - Created styled logo: {filename}")
        
    except Exception as e:
        print(f"  - Could not create styled logo: {e}")

def create_styled_logo_image(team_name):
    """Create a professional styled logo with team colors"""
    # Define team colors
    team_colors = {
        # Football
        'Real Madrid': ('#FFFFFF', '#FEBE10'),  # White, Gold
        'Barcelona': ('#004D98', '#A50044'),   # Blue, Red
        'Bayern Munich': ('#DC052D', '#FFFFFF'), # Red, White
        'Manchester United': ('#DA020E', '#FFF0F5'), # Red, White
        'Liverpool': ('#C8102E', '#FFFFFF'),     # Red, White
        'Arsenal': ('#EF0107', '#FFFFFF'),      # Red, White
        'Chelsea': ('#034694', '#FFFFFF'),      # Blue, White
        'Manchester City': ('#6CABDD', '#1C2C5B'), # Sky Blue, Navy
        
        # Cricket
        'India': ('#FF6600', '#138808'),        # Orange, Green
        'Australia': ('#FFD700', '#00843D'),     # Gold, Green
        'England': ('#FFFFFF', '#00224D'),      # White, Navy
        'Pakistan': ('#006400', '#FFFFFF'),      # Green, White
        
        # Basketball
        'Los Angeles Lakers': ('#552583', '#FDB927'), # Purple, Gold
        'Boston Celtics': ('#007A33', '#FFFFFF'),     # Green, White
        'Golden State Warriors': ('#1D428A', '#FFC72C'), # Navy, Gold
        
        # Default colors
        'default': ('#0066CC', '#FFFFFF'),
    }
    
    # Get team colors or use default
    colors = team_colors.get(team_name, team_colors['default'])
    bg_color, text_color = colors
    
    # Create image
    img = Image.new('RGB', (120, 120), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Add team name initials
    words = team_name.split()
    if len(words) >= 2:
        initials = words[0][0] + words[1][0]
    else:
        initials = words[0][:2] if len(words[0]) >= 2 else words[0][:1]
    
    initials = initials.upper()
    
    # Draw initials
    try:
        # Try to use a larger font
        font_size = 36
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Use default font
        try:
            font = ImageFont.load_default()
        except:
            font = None
    
    # Calculate text position
    if font:
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width = len(initials) * 10
        text_height = 20
    
    x = (120 - text_width) // 2
    y = (120 - text_height) // 2
    
    # Draw text
    draw.text((x, y), initials, fill=text_color, font=font, anchor='lt')
    
    # Add a subtle border
    border_color = tuple(int(c * 0.8) for c in Image.new('RGB', (1, 1), bg_color).getpixel((0, 0)))
    draw.rectangle([2, 2, 118, 118], outline=border_color, width=2)
    
    return img

if __name__ == '__main__':
    add_official_team_logos()
