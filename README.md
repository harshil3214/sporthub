# Sports Hub - Flashscore Style Website

A modern, responsive sports scores website inspired by Flashscore.in, built with Django and Bootstrap. Features real-time match updates, comprehensive sports coverage, and an intuitive user interface.

## 🚀 Features

### Core Features
- **Live Scores**: Real-time match updates across multiple sports
- **Multi-Sport Support**: Football, Cricket, Basketball, Tennis, Kabaddi, Volleyball, Badminton, and more
- **Responsive Design**: Mobile-first design that works on all devices
- **Advanced Filtering**: Filter by sport, date, and search for teams/competitions
- **Modern UI**: Dark theme with glassmorphism effects and smooth animations
- **Auto-Refresh**: Live scores update automatically every 30 seconds

### Sports Covered
- ⚽ **Football**: Premier League, Champions League, ISL, and more
- 🏏 **Cricket**: IPL, World Cup, Test matches, T20 leagues
- 🏀 **Basketball**: NBA, international competitions
- 🎾 **Tennis**: ATP/WTA tournaments, Grand Slams
- 🤼 **Kabaddi**: Pro Kabaddi, international matches
- 🏐 **Volleyball**: International leagues and tournaments
- 🏸 **Badminton**: BWF tournaments and championships
- And many more sports!

## 🛠️ Technology Stack

- **Backend**: Django 5.2.10 with Python
- **Frontend**: Bootstrap 5.3.0, Font Awesome 6.4.0
- **Database**: SQLite (development ready, easily switchable to PostgreSQL/MySQL)
- **Styling**: Custom CSS with glassmorphism and modern design patterns
- **JavaScript**: Vanilla JS for real-time updates and interactions

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sports_hub
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Create requirements.txt with `pip freeze > requirements.txt` after setup)*

4. **Set up the database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create sample data (optional)**
   ```bash
   python create_sample_data.py
   ```
   This will create sample teams, matches, and a superuser account (admin/admin123).

6. **Create superuser account**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Homepage: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/
   - Live Scores: http://127.0.0.1:8000/scores/

## 🏗️ Project Structure

```
sports_hub/
├── config/                 # Django configuration
│   ├── settings.py        # Main settings
│   ├── urls.py           # Root URL configuration
│   └── wsgi.py           # WSGI configuration
├── core/                  # Core application
│   ├── models.py          # Data models (Teams, Matches, etc.)
│   ├── views.py           # Main views and business logic
│   ├── urls.py           # Core app URLs
│   ├── templates/        # HTML templates
│   │   └── core/         # Core templates
│   │       ├── home.html     # Homepage
│   │       ├── scores.html   # Live scores page
│   │       └── dashboard.html # User dashboard
│   └── static/           # Static files (CSS, JS, images)
├── cricket/              # Cricket-specific app
├── football/             # Football-specific app
├── volleyball/           # Volleyball-specific app
├── media/                # User-uploaded media
├── staticfiles/          # Collected static files
├── manage.py             # Django management script
├── create_sample_data.py # Sample data creation script
└── README.md            # This file
```

## 🎯 Key Features Explained

### 1. Homepage (Flashscore-style)
- Live match ticker with real-time updates
- Quick statistics dashboard
- Today's matches overview
- Sport navigation menu
- Responsive design with smooth animations

### 2. Live Scores Page
- Comprehensive match listings
- Filter by sport, date, and search functionality
- Competition-wise grouping
- Live match indicators
- Score display with match status

### 3. Match Detail Pages
- Detailed match information
- Team statistics
- Live score updates
- Match metadata (venue, competition, etc.)

### 4. Admin Dashboard
- User management with role-based access
- Match management
- Team management
- Competition organization

## 🔧 Configuration

### Timezone Settings
The application is configured for Indian Standard Time (Asia/Kolkata) by default. To change the timezone:

1. Open `config/settings.py`
2. Find the `TIME_ZONE` setting
3. Change to your desired timezone (e.g., `'UTC'`, `'America/New_York'`)

### Database Configuration
For production, switch from SQLite to PostgreSQL or MySQL:

1. Install the appropriate database adapter
2. Update `DATABASES` setting in `config/settings.py`
3. Run migrations

### Static Files Configuration
For production deployment:

1. Set `DEBUG = False` in settings
2. Configure `STATIC_ROOT` and `MEDIA_ROOT`
3. Run `python manage.py collectstatic`

## 🚀 Deployment

### Production Deployment Steps

1. **Environment Setup**
   ```bash
   export DEBUG=False
   export SECRET_KEY='your-secret-key'
   export DATABASE_URL='your-database-url'
   ```

2. **Install production dependencies**
   ```bash
   pip install gunicorn psycopg2-binary
   ```

3. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Run with Gunicorn**
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:8000
   ```

5. **Set up reverse proxy** (Nginx/Apache)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 API Endpoints

### Public Endpoints
- `GET /` - Homepage
- `GET /scores/` - Live scores page
- `GET /matches/<sport>/<match_id>/` - Match details

### API Endpoints
- `GET /get-live-scores/` - JSON data for live matches and statistics

### Admin Endpoints (Authentication Required)
- `/admin/` - Django admin panel
- `/dashboard/` - User dashboard
- `/my-students/` - Teacher's student management

## 🎨 Customization

### Adding New Sports
1. Add sport choice to `Team.SPORT_CHOICES` in `core/models.py`
2. Create corresponding match models or use `UniversalMatch`
3. Update templates and views as needed

### Customizing Themes
1. Modify CSS variables in templates
2. Update color schemes in `<style>` sections
3. Add custom logos and branding

## 🐛 Troubleshooting

### Common Issues

1. **Server not starting**
   - Check if port 8000 is available
   - Ensure virtual environment is activated
   - Verify all dependencies are installed

2. **Database errors**
   - Run `python manage.py migrate`
   - Check database file permissions

3. **Static files not loading**
   - Run `python manage.py collectstatic`
   - Verify `STATIC_URL` and `STATICFILES_DIRS` settings

4. **Live scores not updating**
   - Check JavaScript console for errors
   - Verify `/get-live-scores/` endpoint is accessible

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Team

- **Developer**: [Your Name]
- **Design**: Inspired by Flashscore.in

## 🙏 Acknowledgments

- Flashscore.in for design inspiration
- Django framework for robust backend
- Bootstrap for responsive frontend components
- Font Awesome for icons

---

**Note**: This is a development project. For production use, ensure proper security measures, database optimization, and performance tuning.
