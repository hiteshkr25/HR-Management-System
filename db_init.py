import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Initialize database with schema and sample data"""
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    # Read and execute schema
    with open('schema.sql', 'r') as f:
        cur.execute(f.read())
    
    # Insert 10 sample students (CGPA out of 10)
    sample_students = [
        ('Rahul Sharma', 'Computer Science', 9.5, 'rahul.sharma@university.edu', '+1-555-0101', 'Python, Java, Machine Learning, SQL, React'),
        ('Priya Patel', 'Information Technology', 9.0, 'priya.patel@university.edu', '+1-555-0102', 'JavaScript, Node.js, MongoDB, HTML, CSS'),
        ('Amit Kumar', 'Computer Science', 9.75, 'amit.kumar@university.edu', '+1-555-0103', 'C++, Python, Data Structures, Algorithms, AI'),
        ('Sneha Gupta', 'Electronics', 8.75, 'sneha.gupta@university.edu', '+1-555-0104', 'Embedded Systems, C, IoT, Circuit Design'),
        ('Vikram Singh', 'Computer Science', 9.25, 'vikram.singh@university.edu', '+1-555-0105', 'Java, Spring Boot, Microservices, Docker, AWS'),
        ('Anjali Reddy', 'Information Technology', 8.5, 'anjali.reddy@university.edu', '+1-555-0106', 'PHP, Laravel, MySQL, Git, REST APIs'),
        ('Rohan Mehta', 'Computer Science', 9.625, 'rohan.mehta@university.edu', '+1-555-0107', 'Python, Django, PostgreSQL, Linux, DevOps'),
        ('Kavya Iyer', 'Mechanical', 8.25, 'kavya.iyer@university.edu', '+1-555-0108', 'CAD, SolidWorks, MATLAB, 3D Printing'),
        ('Arjun Nair', 'Information Technology', 9.375, 'arjun.nair@university.edu', '+1-555-0109', 'React, Angular, TypeScript, GraphQL, Firebase'),
        ('Deepika Shah', 'Computer Science', 9.875, 'deepika.shah@university.edu', '+1-555-0110', 'Python, TensorFlow, Deep Learning, NLP, Computer Vision')
    ]
    
    for student in sample_students:
        cur.execute("""
            INSERT INTO student (name, branch, cgpa, email, phone, skills)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, student)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized successfully with 10 sample students!")

if __name__ == '__main__':
    init_database()
