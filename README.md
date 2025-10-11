# HR Management System

A professional, production-style HR Management System built with Flask and PostgreSQL. Features dual roles (HR & Recruiter), smart candidate ranking, resume management, and comprehensive analytics.

## Features

### For HR Professionals
- **Student Database Management**: Add, edit, delete, and view student records
- **Resume Management**: Upload and organize student resumes (PDF/DOC/DOCX)
- **Job Request Monitoring**: View all recruiter job postings
- **Analytics Dashboard**: Visual insights with Chart.js (GPA distribution, branch statistics, top skills)
- **CSV Export**: Export shortlisted candidates for any job
- **Notifications**: Real-time alerts when recruiters post new jobs

### For Recruiters
- **Job Posting**: Create detailed job requirements with skills, GPA threshold, and branch preferences
- **Smart Ranking**: AI-powered fit scores (0-100) based on:
  - 50% Skill matching
  - 30% GPA relevance
  - 20% Branch relevance
- **Ranked Shortlists**: View candidates sorted by fit score
- **Email Notifications**: Send automated emails to shortlisted students (integration ready)
- **Job Management**: Track all your job postings

## Technology Stack

- **Backend**: Flask (Python 3.11)
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5 + Custom Crimson Theme
- **Charts**: Chart.js
- **Authentication**: Flask-Bcrypt with secure password hashing
- **File Upload**: Resume storage with validation

## Sample Data

The database includes 10 pre-populated student records across different branches:
- Computer Science
- Information Technology
- Electronics
- Mechanical

## Quick Start

### On Replit (Recommended)

1. The application is already configured and ready to run!
2. Click the **Run** button to start the server
3. Access the app in the webview panel

### Initial Setup (If needed)

```bash
# Initialize database (already done on first run)
python db_init.py

# Run the application
python main.py
```

### Default Access

The system uses role-based authentication:

1. **Register** at `/register` - Choose either HR or Recruiter role
2. **Login** at `/login` with your credentials
3. Access your role-specific dashboard

## Project Structure

```
.
├── main.py                 # Flask application with all routes
├── ranking.py              # Smart ranking algorithm
├── db_init.py             # Database initialization script
├── schema.sql             # PostgreSQL schema
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── hr_*.html         # HR-specific templates
│   └── recruiter_*.html  # Recruiter-specific templates
├── static/
│   └── css/
│       └── style.css     # Crimson-themed custom CSS
└── uploads/              # Resume storage directory
```

## Key Routes

### Public
- `/` - Homepage
- `/login` - User login
- `/register` - User registration

### HR Dashboard
- `/hr/dashboard` - Main dashboard with statistics
- `/hr/students` - View all students
- `/hr/students/add` - Add new student
- `/hr/students/edit/<id>` - Edit student
- `/hr/upload-resume/<id>` - Upload student resume
- `/hr/jobs` - View all job requests
- `/hr/analytics` - Analytics dashboard

### Recruiter Dashboard
- `/recruiter/dashboard` - Main dashboard
- `/recruiter/post-job` - Post new job
- `/recruiter/shortlist/<job_id>` - View ranked shortlist
- `/recruiter/my-jobs` - View all my jobs

## Smart Ranking Algorithm

The system uses a weighted scoring algorithm to match candidates:

```python
Fit Score = (Skill Match × 0.5) + (GPA Score × 0.3) + (Branch Match × 0.2)
```

### Skill Matching
- Exact keyword matches from student skills vs required skills
- Partial substring matching for related skills
- Case-insensitive comparison

### GPA Scoring
- 0 points if below minimum threshold
- 50-100 points scaled based on excellence above minimum

### Branch Matching
- 100 points for exact match
- 70 points for related branches (CS/IT, Electronics/Electrical, etc.)
- 0 points for unrelated branches

## Database Schema

- **users**: User accounts (HR and Recruiter)
- **student**: Student records with skills and academic info
- **resume**: Uploaded resume files linked to students
- **job_request**: Recruiter job postings
- **shortlist**: Ranked candidates for each job
- **notifications**: System notifications for HR users

## Security Features

- Password hashing with Flask-Bcrypt
- Session-based authentication
- Role-based access control
- File upload validation (type and size limits)
- SQL injection protection via parameterized queries

## Future Enhancements

- **AI Ranking**: Upgrade to Sentence-BERT for semantic skill matching
- **Advanced Analytics**: Trend analysis and historical data
- **Bulk Import**: CSV/Excel upload for students
- **Enhanced Notifications**: Full email integration with Resend/SendGrid
- **Student Profiles**: Detailed profile pages with resume preview
- **Advanced Search**: Filtering and search across all data

## Environment Variables

Required environment variables (auto-configured on Replit):
- `DATABASE_URL` - PostgreSQL connection string
- `SESSION_SECRET` - Flask session secret key

Optional environment variables (for email notifications):
- `MAIL_SERVER` - SMTP server (e.g., smtp.gmail.com)
- `MAIL_PORT` - SMTP port (e.g., 587)
- `MAIL_USERNAME` - Email account username
- `MAIL_PASSWORD` - Email account password (use app password for Gmail)
- `MAIL_FROM` - From email address

**Note**: The system works fully without email configuration. Email notifications will simply show a message indicating they need to be configured in Secrets.

## Color Theme

The application uses a professional **Crimson (#DC143C)** color palette:
- Primary: `#DC143C`
- Dark: `#A0102A`
- Light: `#FF6B8A`

## Support

Built for Replit with ❤️

**Tagline**: Smart Recruitment, Simplified.
