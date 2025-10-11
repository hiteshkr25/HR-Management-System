-- HR Management System Database Schema

-- Users table (HR and Recruiter accounts)
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('HR', 'Recruiter')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Student table
CREATE TABLE IF NOT EXISTS student (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    branch VARCHAR(100) NOT NULL,
    gpa DECIMAL(3, 2) NOT NULL CHECK (gpa >= 0 AND gpa <= 4.0),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    skills TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resume table
CREATE TABLE IF NOT EXISTS resume (
    resume_id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES student(student_id) ON DELETE CASCADE,
    resume_file VARCHAR(500) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job_Request table
CREATE TABLE IF NOT EXISTS job_request (
    job_id SERIAL PRIMARY KEY,
    recruiter_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    required_skills TEXT NOT NULL,
    min_gpa DECIMAL(3, 2) NOT NULL CHECK (min_gpa >= 0 AND min_gpa <= 4.0),
    branch_pref VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shortlist table
CREATE TABLE IF NOT EXISTS shortlist (
    shortlist_id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES job_request(job_id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES student(student_id) ON DELETE CASCADE,
    fit_score DECIMAL(5, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'Shortlisted' CHECK (status IN ('Shortlisted', 'Selected', 'Rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    notif_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_student_email ON student(email);
CREATE INDEX IF NOT EXISTS idx_user_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_job_recruiter ON job_request(recruiter_id);
CREATE INDEX IF NOT EXISTS idx_shortlist_job ON shortlist(job_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
