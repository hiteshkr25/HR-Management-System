"""
Email notification service for HR Management System
Supports optional SMTP configuration for sending emails to shortlisted students
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


def is_email_configured():
    """Check if email service is configured"""
    return all([
        os.getenv('MAIL_SERVER'),
        os.getenv('MAIL_PORT'),
        os.getenv('MAIL_USERNAME'),
        os.getenv('MAIL_PASSWORD')
    ])


def send_shortlist_email(student_name, student_email, company_name, job_description):
    """
    Send email notification to shortlisted student
    
    Args:
        student_name: Name of the student
        student_email: Email address of the student
        company_name: Name of the company
        job_description: Brief job description
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not is_email_configured():
        return False, "Email service not configured. Please add MAIL credentials to Secrets."
    
    try:
        # Email configuration
        mail_server = os.getenv('MAIL_SERVER')
        mail_port = int(os.getenv('MAIL_PORT', 587))
        mail_username = os.getenv('MAIL_USERNAME')
        mail_password = os.getenv('MAIL_PASSWORD')
        mail_from = os.getenv('MAIL_FROM', mail_username)
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Shortlist Notification - {company_name}'
        msg['From'] = mail_from
        msg['To'] = student_email
        
        # Email body
        text_body = f"""
Dear {student_name},

Congratulations! You have been shortlisted for the role posted by {company_name}.

Job Details:
{job_description}

Please wait for further instructions from the recruitment team.

Best regards,
HR Management System
        """
        
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
        <div style="background: linear-gradient(135deg, #DC143C 0%, #A0102A 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center;">
            <h2 style="margin: 0;">Shortlist Notification</h2>
        </div>
        <div style="padding: 20px;">
            <p>Dear <strong>{student_name}</strong>,</p>
            <p>Congratulations! You have been shortlisted for the role posted by <strong>{company_name}</strong>.</p>
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #DC143C; margin: 20px 0;">
                <h4 style="margin-top: 0; color: #DC143C;">Job Details:</h4>
                <p style="margin-bottom: 0;">{job_description}</p>
            </div>
            <p>Please wait for further instructions from the recruitment team.</p>
            <p style="margin-top: 30px;">Best regards,<br><strong>HR Management System</strong></p>
        </div>
        <div style="background-color: #f8f9fa; padding: 10px; text-align: center; font-size: 12px; color: #666;">
            <p style="margin: 0;">Smart Recruitment, Simplified.</p>
        </div>
    </div>
</body>
</html>
        """
        
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(msg)
        
        return True, f"Email sent successfully to {student_email}"
        
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"


def send_bulk_emails(students, company_name, job_description):
    """
    Send emails to multiple students
    
    Args:
        students: List of student dicts with 'name' and 'email' keys
        company_name: Name of the company
        job_description: Brief job description
    
    Returns:
        dict: {'success': int, 'failed': int, 'messages': list}
    """
    results = {'success': 0, 'failed': 0, 'messages': []}
    
    for student in students:
        success, message = send_shortlist_email(
            student['name'],
            student['email'],
            company_name,
            job_description
        )
        
        if success:
            results['success'] += 1
        else:
            results['failed'] += 1
        
        results['messages'].append(message)
    
    return results
def send_email(to_email, subject, body):
    """
    General-purpose email sender (for testing or custom messages)
    """
    if not is_email_configured():
        return False, "Email service not configured."

    try:
        mail_server = os.getenv('MAIL_SERVER')
        mail_port = int(os.getenv('MAIL_PORT', 587))
        mail_username = os.getenv('MAIL_USERNAME')
        mail_password = os.getenv('MAIL_PASSWORD')
        mail_from = os.getenv('MAIL_FROM', mail_username)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = mail_from
        msg['To'] = to_email

        part = MIMEText(body, 'html')
        msg.attach(part)

        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(msg)

        return True, f"✅ Email sent successfully to {to_email}"
    except Exception as e:
        return False, f"❌ Failed to send email: {str(e)}"
