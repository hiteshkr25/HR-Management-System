import os
import io
import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from ranking import calculate_fit_score, rank_students
from email_service import send_shortlist_email, send_bulk_emails, is_email_configured

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SESSION_SECRET', 'dev-secret-key-change-in-production')
bcrypt = Bcrypt(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    """Create database connection"""
    return psycopg2.connect(os.getenv('DATABASE_URL'), cursor_factory=RealDictCursor)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    """Decorator to require login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    """Decorator to require specific role"""
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                flash('Access denied. Insufficient permissions.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))
        
        if role not in ['HR', 'Recruiter']:
            flash('Invalid role selected!', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                (username, email, hashed_password, role)
            )
            conn.commit()
            cur.close()
            conn.close()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except psycopg2.IntegrityError:
            flash('Username or email already exists!', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            flash(f'Welcome back, {user["username"]}!', 'success')
            
            if user['role'] == 'HR':
                return redirect(url_for('hr_dashboard'))
            else:
                return redirect(url_for('recruiter_dashboard'))
        else:
            flash('Invalid email or password!', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


# ==================== HR ROUTES ====================

@app.route('/hr/dashboard')
@login_required
@role_required('HR')
def hr_dashboard():
    """HR dashboard with analytics"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get stats
    cur.execute("SELECT COUNT(*) as count FROM student")
    total_students = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) as count FROM job_request")
    total_jobs = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) as count FROM notifications WHERE user_id = %s AND is_read = FALSE", (session['user_id'],))
    unread_notifications = cur.fetchone()['count']
    
    cur.execute("SELECT AVG(gpa) as avg_gpa FROM student")
    avg_gpa = cur.fetchone()['avg_gpa'] or 0
    
    # Recent notifications
    cur.execute("""
        SELECT * FROM notifications 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT 5
    """, (session['user_id'],))
    notifications = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('hr_dashboard.html',
                         total_students=total_students,
                         total_jobs=total_jobs,
                         unread_notifications=unread_notifications,
                         avg_gpa=round(avg_gpa, 2),
                         notifications=notifications)


@app.route('/hr/students')
@login_required
@role_required('HR')
def hr_students():
    """View all students"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM student ORDER BY gpa DESC")
    students = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('hr_students.html', students=students)


@app.route('/hr/students/add', methods=['GET', 'POST'])
@login_required
@role_required('HR')
def hr_add_student():
    """Add new student"""
    if request.method == 'POST':
        name = request.form.get('name')
        branch = request.form.get('branch')
        gpa = float(request.form.get('gpa'))
        email = request.form.get('email')
        phone = request.form.get('phone')
        skills = request.form.get('skills')
        
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO student (name, branch, gpa, email, phone, skills)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, branch, gpa, email, phone, skills))
            conn.commit()
            cur.close()
            conn.close()
            
            flash('Student added successfully!', 'success')
            return redirect(url_for('hr_students'))
        except Exception as e:
            flash(f'Error adding student: {str(e)}', 'danger')
    
    return render_template('hr_add_student.html')


@app.route('/hr/students/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
@role_required('HR')
def hr_edit_student(student_id):
    """Edit student"""
    conn = get_db()
    cur = conn.cursor()
    
    if request.method == 'POST':
        name = request.form.get('name')
        branch = request.form.get('branch')
        gpa = float(request.form.get('gpa'))
        email = request.form.get('email')
        phone = request.form.get('phone')
        skills = request.form.get('skills')
        
        cur.execute("""
            UPDATE student 
            SET name=%s, branch=%s, gpa=%s, email=%s, phone=%s, skills=%s
            WHERE student_id=%s
        """, (name, branch, gpa, email, phone, skills, student_id))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Student updated successfully!', 'success')
        return redirect(url_for('hr_students'))
    
    cur.execute("SELECT * FROM student WHERE student_id = %s", (student_id,))
    student = cur.fetchone()
    cur.close()
    conn.close()
    
    return render_template('hr_edit_student.html', student=student)


@app.route('/hr/students/delete/<int:student_id>')
@login_required
@role_required('HR')
def hr_delete_student(student_id):
    """Delete student"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM student WHERE student_id = %s", (student_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('hr_students'))


@app.route('/hr/upload-resume/<int:student_id>', methods=['GET', 'POST'])
@login_required
@role_required('HR')
def hr_upload_resume(student_id):
    """Upload student resume"""
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file selected!', 'danger')
            return redirect(request.url)
        
        file = request.files['resume']
        
        if file.filename == '':
            flash('No file selected!', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(f"student_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO resume (student_id, resume_file)
                VALUES (%s, %s)
            """, (student_id, filename))
            conn.commit()
            cur.close()
            conn.close()
            
            flash('Resume uploaded successfully!', 'success')
            return redirect(url_for('hr_students'))
        else:
            flash('Invalid file type! Only PDF, DOC, DOCX allowed.', 'danger')
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM student WHERE student_id = %s", (student_id,))
    student = cur.fetchone()
    cur.close()
    conn.close()
    
    return render_template('hr_upload_resume.html', student=student)


@app.route('/hr/jobs')
@login_required
@role_required('HR')
def hr_jobs():
    """View all job requests"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT jr.*, u.username as recruiter_name
        FROM job_request jr
        JOIN users u ON jr.recruiter_id = u.user_id
        ORDER BY jr.created_at DESC
    """)
    jobs = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('hr_jobs.html', jobs=jobs)


@app.route('/hr/analytics')
@login_required
@role_required('HR')
def hr_analytics():
    """Analytics dashboard"""
    conn = get_db()
    cur = conn.cursor()
    
    # Students by branch
    cur.execute("""
        SELECT branch, COUNT(*) as count 
        FROM student 
        GROUP BY branch 
        ORDER BY count DESC
    """)
    branch_data = cur.fetchall()
    
    # GPA distribution
    cur.execute("""
        SELECT 
            CASE 
                WHEN gpa >= 3.5 THEN '3.5-4.0'
                WHEN gpa >= 3.0 THEN '3.0-3.5'
                WHEN gpa >= 2.5 THEN '2.5-3.0'
                ELSE 'Below 2.5'
            END as gpa_range,
            COUNT(*) as count
        FROM student
        GROUP BY gpa_range
        ORDER BY gpa_range DESC
    """)
    gpa_data = cur.fetchall()
    
    # Top skills
    cur.execute("SELECT skills FROM student")
    all_students = cur.fetchall()
    
    skill_count = {}
    for student in all_students:
        skills = [s.strip() for s in student['skills'].split(',')]
        for skill in skills:
            skill_count[skill] = skill_count.get(skill, 0) + 1
    
    top_skills = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    cur.close()
    conn.close()
    
    return render_template('hr_analytics.html',
                         branch_data=branch_data,
                         gpa_data=gpa_data,
                         top_skills=top_skills)


# ==================== RECRUITER ROUTES ====================

@app.route('/recruiter/dashboard')
@login_required
@role_required('Recruiter')
def recruiter_dashboard():
    """Recruiter dashboard"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get stats
    cur.execute("SELECT COUNT(*) as count FROM job_request WHERE recruiter_id = %s", (session['user_id'],))
    my_jobs = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) as count FROM student")
    total_students = cur.fetchone()['count']
    
    # Recent job postings
    cur.execute("""
        SELECT * FROM job_request 
        WHERE recruiter_id = %s 
        ORDER BY created_at DESC 
        LIMIT 5
    """, (session['user_id'],))
    recent_jobs = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('recruiter_dashboard.html',
                         my_jobs=my_jobs,
                         total_students=total_students,
                         recent_jobs=recent_jobs)


@app.route('/recruiter/post-job', methods=['GET', 'POST'])
@login_required
@role_required('Recruiter')
def recruiter_post_job():
    """Post new job"""
    if request.method == 'POST':
        company_name = request.form.get('company_name')
        required_skills = request.form.get('required_skills')
        min_gpa = float(request.form.get('min_gpa'))
        branch_pref = request.form.get('branch_pref')
        description = request.form.get('description')
        
        conn = get_db()
        cur = conn.cursor()
        
        # Insert job
        cur.execute("""
            INSERT INTO job_request (recruiter_id, company_name, required_skills, min_gpa, branch_pref, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING job_id
        """, (session['user_id'], company_name, required_skills, min_gpa, branch_pref, description))
        
        job_id = cur.fetchone()['job_id']
        
        # Create notification for all HR users
        cur.execute("SELECT user_id FROM users WHERE role = 'HR'")
        hr_users = cur.fetchall()
        
        for hr_user in hr_users:
            cur.execute("""
                INSERT INTO notifications (user_id, message)
                VALUES (%s, %s)
            """, (hr_user['user_id'], f"New job posted by {session['username']} for {company_name}"))
        
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Job posted successfully!', 'success')
        return redirect(url_for('recruiter_shortlist', job_id=job_id))
    
    return render_template('recruiter_post_job.html')


@app.route('/recruiter/shortlist/<int:job_id>')
@login_required
@role_required('Recruiter')
def recruiter_shortlist(job_id):
    """View ranked shortlist for a job"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get job details
    cur.execute("SELECT * FROM job_request WHERE job_id = %s", (job_id,))
    job = cur.fetchone()
    
    if not job or job['recruiter_id'] != session['user_id']:
        flash('Job not found or access denied!', 'danger')
        return redirect(url_for('recruiter_dashboard'))
    
    # Get all students
    cur.execute("SELECT * FROM student")
    students = cur.fetchall()
    
    # Rank students
    ranked_students = rank_students(students, job)
    
    # Save shortlist to database (only students with fit_score > 0)
    # Update scores if already exists to keep rankings current
    for student, fit_score in ranked_students:
        if fit_score > 0:
            cur.execute("""
                INSERT INTO shortlist (job_id, student_id, fit_score)
                VALUES (%s, %s, %s)
                ON CONFLICT (job_id, student_id) 
                DO UPDATE SET fit_score = EXCLUDED.fit_score
            """, (job_id, student['student_id'], fit_score))
    
    conn.commit()
    
    # Get saved shortlist
    cur.execute("""
        SELECT s.*, st.name, st.email, st.branch, st.gpa, st.skills, st.phone
        FROM shortlist s
        JOIN student st ON s.student_id = st.student_id
        WHERE s.job_id = %s
        ORDER BY s.fit_score DESC
    """, (job_id,))
    shortlist = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('recruiter_shortlist.html', job=job, shortlist=shortlist)


@app.route('/recruiter/my-jobs')
@login_required
@role_required('Recruiter')
def recruiter_my_jobs():
    """View all my job postings"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM job_request 
        WHERE recruiter_id = %s 
        ORDER BY created_at DESC
    """, (session['user_id'],))
    jobs = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('recruiter_my_jobs.html', jobs=jobs)


@app.route('/recruiter/send-emails/<int:job_id>', methods=['POST'])
@login_required
@role_required('Recruiter')
def send_emails_to_shortlist(job_id):
    """Send email notifications to all shortlisted students for a job"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get job details
    cur.execute("SELECT * FROM job_request WHERE job_id = %s AND recruiter_id = %s", 
                (job_id, session['user_id']))
    job = cur.fetchone()
    
    if not job:
        flash('Job not found or access denied!', 'danger')
        return redirect(url_for('recruiter_dashboard'))
    
    # Check if email is configured
    if not is_email_configured():
        flash('Email service not configured! Please add email credentials to Secrets (MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD).', 'warning')
        return redirect(url_for('recruiter_shortlist', job_id=job_id))
    
    # Get shortlisted students
    cur.execute("""
        SELECT st.name, st.email
        FROM shortlist s
        JOIN student st ON s.student_id = st.student_id
        WHERE s.job_id = %s
        ORDER BY s.fit_score DESC
    """, (job_id,))
    students = cur.fetchall()
    
    cur.close()
    conn.close()
    
    if not students:
        flash('No students in shortlist!', 'warning')
        return redirect(url_for('recruiter_shortlist', job_id=job_id))
    
    # Send emails
    results = send_bulk_emails(
        students,
        job['company_name'],
        job['description']
    )
    
    flash(f"Email notifications sent! Success: {results['success']}, Failed: {results['failed']}", 
          'success' if results['failed'] == 0 else 'warning')
    
    return redirect(url_for('recruiter_shortlist', job_id=job_id))


# ==================== UTILITY ROUTES ====================

@app.route('/export-shortlist/<int:job_id>')
@login_required
def export_shortlist(job_id):
    """Export shortlist as CSV"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT st.name, st.email, st.phone, st.branch, st.gpa, st.skills, s.fit_score
        FROM shortlist s
        JOIN student st ON s.student_id = st.student_id
        WHERE s.job_id = %s
        ORDER BY s.fit_score DESC
    """, (job_id,))
    shortlist = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Email', 'Phone', 'Branch', 'GPA', 'Skills', 'Fit Score'])
    
    for row in shortlist:
        writer.writerow([row['name'], row['email'], row['phone'], row['branch'], 
                        row['gpa'], row['skills'], row['fit_score']])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'shortlist_job_{job_id}_{datetime.now().strftime("%Y%m%d")}.csv'
    )


@app.route('/mark-notification-read/<int:notif_id>')
@login_required
def mark_notification_read(notif_id):
    """Mark notification as read"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE notifications SET is_read = TRUE WHERE notif_id = %s", (notif_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    return redirect(request.referrer or url_for('hr_dashboard'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
