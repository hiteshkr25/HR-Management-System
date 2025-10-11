# HR Management System

## Project Overview

A professional HR Management System built with Flask and PostgreSQL, featuring dual-role authentication (HR and Recruiter), smart candidate ranking, resume management, and comprehensive analytics.

**Status**: MVP Complete (October 11, 2025)

**Tagline**: Smart Recruitment, Simplified.

## Recent Changes

### October 11, 2025 - Initial Build
- Created complete Flask-based HR Management System
- Implemented PostgreSQL database with 6 tables and 10 sample student records
- Built dual-role authentication system (HR and Recruiter)
- Developed smart ranking algorithm with weighted scoring (50% skills, 30% GPA, 20% branch)
- Created professional Crimson-themed UI with Bootstrap 5
- Added analytics dashboard with Chart.js visualizations
- Implemented resume upload functionality
- Set up notification system for HR users
- Added CSV export for shortlisted candidates

## Project Architecture

### Database Schema (PostgreSQL)
1. **users** - User accounts (HR and Recruiter roles)
2. **student** - Student records (10 sample records included)
3. **resume** - Uploaded resume files
4. **job_request** - Recruiter job postings
5. **shortlist** - Ranked candidates per job
6. **notifications** - Real-time alerts for HR

### Application Structure
```
main.py           # Flask app with all routes and authentication
ranking.py        # Smart ranking algorithm
db_init.py        # Database initialization
templates/        # HTML templates (Jinja2)
static/css/       # Crimson-themed CSS
uploads/          # Resume storage
```

### Key Features Implemented
1. **Authentication**: Flask-Bcrypt with role-based access control
2. **HR Module**: Student CRUD, resume upload, job monitoring, analytics
3. **Recruiter Module**: Job posting, ranked shortlists, CSV export
4. **Smart Ranking**: Weighted algorithm for candidate matching
5. **Analytics**: Chart.js visualizations for insights
6. **UI**: Professional Bootstrap 5 with Crimson (#DC143C) theme

### Technology Stack
- Python 3.11 + Flask
- PostgreSQL (Replit managed)
- Bootstrap 5 + Chart.js
- Flask-Bcrypt for security

## User Preferences

None specified yet.

## Current Configuration

- **Server**: Flask dev server on port 5000
- **Database**: PostgreSQL (development instance)
- **Workflow**: `python main.py` configured to run on startup

## Next Steps / Future Enhancements

1. **Email Integration**: Set up Resend/SendGrid for automated emails to shortlisted students
2. **AI Upgrade**: Replace basic ranking with Sentence-BERT for semantic matching
3. **Enhanced Analytics**: Add trend charts and historical recruitment data
4. **Bulk Import**: CSV/Excel upload for student records
5. **Student Profiles**: Detailed pages with resume preview
6. **Advanced Search**: Filtering across students and jobs

## Notes

- LSP warnings in main.py are type checking issues only (runtime works perfectly)
- Sample data includes diverse branches and skill sets
- Production deployment would require production WSGI server (gunicorn)
