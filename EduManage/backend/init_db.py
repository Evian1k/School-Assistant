#!/usr/bin/env python3
"""
Database initialization script with sample data for EduManage
Run this script to set up the database with test users and data
"""

import os
import sys
from datetime import datetime, date, timedelta
import json

# Add the current directory to Python path to import our app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.guardian import Guardian
from app.models.attendance import Attendance
from app.models.grade import Grade
from app.models.fee import Fee
from app.models.notification import Notification

def init_database():
    """Initialize database with sample data"""
    
    print("🔄 Initializing EduManage database...")
    
    # Create all tables
    db.create_all()
    print("✅ Database tables created")
    
    # Clear existing data for fresh start
    clear_existing_data()
    
    # Create sample data
    create_admin_users()
    create_teachers()
    create_guardians()
    create_students()
    create_attendance_records()
    create_fees()
    create_grades()
    create_notifications()
    
    print("🎉 Database initialization completed successfully!")
    print("\n📝 Demo Credentials:")
    print("Admin: admin@school.edu / admin123")
    print("Teacher: teacher@school.edu / teacher123")
    print("Student: student@school.edu / student123")
    print("Parent: parent@school.edu / parent123")

def clear_existing_data():
    """Clear existing data for fresh initialization"""
    try:
        db.session.query(Notification).delete()
        db.session.query(Grade).delete()
        db.session.query(Fee).delete()
        db.session.query(Attendance).delete()
        db.session.query(Student).delete()
        db.session.query(Teacher).delete()
        db.session.query(Guardian).delete()
        db.session.query(User).delete()
        db.session.commit()
        print("🧹 Cleared existing data")
    except Exception as e:
        print(f"⚠️  Warning: Could not clear existing data: {e}")
        db.session.rollback()

def create_admin_users():
    """Create admin users"""
    print("👑 Creating admin users...")
    
    admin_user = User(
        email='admin@school.edu',
        name='School Administrator',
        role='admin',
        phone='+1234567890'
    )
    admin_user.set_password('admin123')
    db.session.add(admin_user)
    
    db.session.commit()
    print("✅ Admin users created")

def create_teachers():
    """Create teacher users and profiles"""
    print("👨‍🏫 Creating teachers...")
    
    teachers_data = [
        {
            'email': 'teacher@school.edu',
            'name': 'John Smith',
            'phone': '+1234567891',
            'teacher_id': 'TCH001',
            'subjects': json.dumps(['Mathematics', 'Physics']),
            'classes_assigned': json.dumps(['10A', '10B', '11A']),
            'qualification': 'M.Sc. Mathematics',
            'experience_years': 8
        },
        {
            'email': 'sarah.wilson@school.edu',
            'name': 'Sarah Wilson',
            'phone': '+1234567892',
            'teacher_id': 'TCH002',
            'subjects': json.dumps(['English', 'Literature']),
            'classes_assigned': json.dumps(['9A', '9B', '10A']),
            'qualification': 'M.A. English Literature',
            'experience_years': 6
        },
        {
            'email': 'mike.brown@school.edu',
            'name': 'Michael Brown',
            'phone': '+1234567893',
            'teacher_id': 'TCH003',
            'subjects': json.dumps(['Chemistry', 'Biology']),
            'classes_assigned': json.dumps(['11A', '11B', '12A']),
            'qualification': 'M.Sc. Chemistry',
            'experience_years': 10
        }
    ]
    
    for teacher_data in teachers_data:
        # Create user account
        user = User(
            email=teacher_data['email'],
            name=teacher_data['name'],
            role='teacher',
            phone=teacher_data['phone']
        )
        user.set_password('teacher123')
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create teacher profile
        teacher = Teacher(
            user_id=user.id,
            teacher_id=teacher_data['teacher_id'],
            name=teacher_data['name'],
            email=teacher_data['email'],
            phone=teacher_data['phone'],
            subjects=teacher_data['subjects'],
            classes_assigned=teacher_data['classes_assigned'],
            qualification=teacher_data['qualification'],
            experience_years=teacher_data['experience_years']
        )
        db.session.add(teacher)
    
    db.session.commit()
    print("✅ Teachers created")

def create_guardians():
    """Create guardian users and profiles"""
    print("👨‍👩‍👧‍👦 Creating guardians...")
    
    guardians_data = [
        {
            'email': 'parent@school.edu',
            'name': 'Robert Johnson',
            'phone': '+1234567894',
            'address': '123 Main St, Anytown, USA',
            'relationship': 'Father',
            'occupation': 'Engineer',
            'emergency_contact': '+1234567895'
        },
        {
            'email': 'mary.davis@email.com',
            'name': 'Mary Davis',
            'phone': '+1234567896',
            'address': '456 Oak Ave, Anytown, USA',
            'relationship': 'Mother',
            'occupation': 'Teacher',
            'emergency_contact': '+1234567897'
        },
        {
            'email': 'james.wilson@email.com',
            'name': 'James Wilson',
            'phone': '+1234567898',
            'address': '789 Pine St, Anytown, USA',
            'relationship': 'Father',
            'occupation': 'Doctor',
            'emergency_contact': '+1234567899'
        }
    ]
    
    for guardian_data in guardians_data:
        # Create user account
        user = User(
            email=guardian_data['email'],
            name=guardian_data['name'],
            role='parent',
            phone=guardian_data['phone']
        )
        user.set_password('parent123')
        db.session.add(user)
        db.session.flush()
        
        # Create guardian profile
        guardian = Guardian(
            user_id=user.id,
            name=guardian_data['name'],
            email=guardian_data['email'],
            phone=guardian_data['phone'],
            address=guardian_data['address'],
            relationship=guardian_data['relationship'],
            occupation=guardian_data['occupation'],
            emergency_contact=guardian_data['emergency_contact']
        )
        db.session.add(guardian)
    
    db.session.commit()
    print("✅ Guardians created")

def create_students():
    """Create student users and profiles"""
    print("👥 Creating students...")
    
    # Get guardian IDs for assignment
    guardians = Guardian.query.all()
    
    students_data = [
        {
            'email': 'student@school.edu',
            'name': 'Emily Johnson',
            'student_id': 'STU001',
            'class_name': '10A',
            'grade_level': 'Grade 10',
            'date_of_birth': date(2008, 5, 15),
            'guardian_id': guardians[0].id if guardians else None
        },
        {
            'email': 'alex.davis@student.edu',
            'name': 'Alex Davis',
            'student_id': 'STU002',
            'class_name': '10A',
            'grade_level': 'Grade 10',
            'date_of_birth': date(2008, 8, 22),
            'guardian_id': guardians[1].id if len(guardians) > 1 else None
        },
        {
            'email': 'sophia.wilson@student.edu',
            'name': 'Sophia Wilson',
            'student_id': 'STU003',
            'class_name': '10B',
            'grade_level': 'Grade 10',
            'date_of_birth': date(2008, 3, 10),
            'guardian_id': guardians[2].id if len(guardians) > 2 else None
        },
        {
            'email': 'david.brown@student.edu',
            'name': 'David Brown',
            'student_id': 'STU004',
            'class_name': '11A',
            'grade_level': 'Grade 11',
            'date_of_birth': date(2007, 11, 5),
            'guardian_id': guardians[0].id if guardians else None
        },
        {
            'email': 'lisa.miller@student.edu',
            'name': 'Lisa Miller',
            'student_id': 'STU005',
            'class_name': '9A',
            'grade_level': 'Grade 9',
            'date_of_birth': date(2009, 1, 18),
            'guardian_id': guardians[1].id if len(guardians) > 1 else None
        }
    ]
    
    for student_data in students_data:
        # Create user account
        user = User(
            email=student_data['email'],
            name=student_data['name'],
            role='student',
            phone=''
        )
        user.set_password('student123')
        db.session.add(user)
        db.session.flush()
        
        # Create student profile
        student = Student(
            user_id=user.id,
            student_id=student_data['student_id'],
            name=student_data['name'],
            email=student_data['email'],
            class_name=student_data['class_name'],
            grade_level=student_data['grade_level'],
            date_of_birth=student_data['date_of_birth'],
            guardian_id=student_data['guardian_id']
        )
        db.session.add(student)
    
    db.session.commit()
    print("✅ Students created")

def create_attendance_records():
    """Create sample attendance records"""
    print("📅 Creating attendance records...")
    
    students = Student.query.all()
    teachers = Teacher.query.all()
    
    if not students or not teachers:
        print("⚠️  Skipping attendance records - no students or teachers found")
        return
    
    # Create attendance for the last 30 days
    for i in range(30):
        attendance_date = date.today() - timedelta(days=i)
        
        for student in students:
            # 90% attendance rate simulation
            import random
            status = 'present' if random.random() > 0.1 else random.choice(['absent', 'late'])
            
            attendance = Attendance(
                student_id=student.id,
                date=attendance_date,
                status=status,
                marked_by=teachers[0].user_id,  # First teacher marks attendance
                remarks=f'Marked by system for {attendance_date}'
            )
            db.session.add(attendance)
    
    db.session.commit()
    print("✅ Attendance records created")

def create_fees():
    """Create sample fee records"""
    print("💰 Creating fee records...")
    
    students = Student.query.all()
    current_year = datetime.now().year
    
    fee_types = ['Tuition', 'Transport', 'Activity', 'Laboratory', 'Library']
    
    for student in students:
        for i, fee_type in enumerate(fee_types):
            # Create fees for current academic year
            due_date = date(current_year, 3 + i, 15)  # Spread throughout the year
            
            fee = Fee(
                student_id=student.id,
                fee_type=fee_type,
                amount=500.0 + (i * 100),  # Different amounts for different fee types
                discount=0.0,
                due_date=due_date,
                term=f'Term {(i % 3) + 1}',
                academic_year=f'{current_year}-{current_year + 1}',
                status='pending' if i < 2 else 'paid',  # Some paid, some pending
                paid_date=due_date - timedelta(days=5) if i >= 2 else None,
                payment_method='bank_transfer' if i >= 2 else None,
                receipt_number=f'REC-{student.id}-{i+1}' if i >= 2 else None
            )
            fee.calculate_final_amount()
            db.session.add(fee)
    
    db.session.commit()
    print("✅ Fee records created")

def create_grades():
    """Create sample grade records"""
    print("📊 Creating grade records...")
    
    students = Student.query.all()
    teachers = Teacher.query.all()
    current_year = datetime.now().year
    
    subjects = ['Mathematics', 'English', 'Science', 'History', 'Geography']
    assignment_types = ['Quiz', 'Test', 'Assignment', 'Project', 'Exam']
    
    for student in students:
        for subject in subjects:
            for assignment_type in assignment_types:
                # Generate realistic grades (70-95 range)
                import random
                score = random.uniform(70, 95)
                max_score = 100.0
                
                grade = Grade(
                    student_id=student.id,
                    subject=subject,
                    assignment_type=assignment_type,
                    score=score,
                    max_score=max_score,
                    term='Term 1',
                    academic_year=f'{current_year}-{current_year + 1}',
                    recorded_by=teachers[0].user_id if teachers else 1,
                    date_recorded=date.today() - timedelta(days=random.randint(1, 60))
                )
                grade.calculate_percentage()
                db.session.add(grade)
    
    db.session.commit()
    print("✅ Grade records created")

def create_notifications():
    """Create sample notifications"""
    print("🔔 Creating notifications...")
    
    users = User.query.all()
    admin_user = User.query.filter_by(role='admin').first()
    
    if not admin_user or len(users) < 2:
        print("⚠️  Skipping notifications - insufficient users")
        return
    
    notifications_data = [
        {
            'title': 'Welcome to EduManage',
            'message': 'Welcome to the new school management system!',
            'notification_type': 'announcement',
            'priority': 'normal'
        },
        {
            'title': 'Fee Payment Reminder',
            'message': 'Your school fees are due next week. Please make payment to avoid late charges.',
            'notification_type': 'fee_reminder',
            'priority': 'high'
        },
        {
            'title': 'Attendance Alert',
            'message': 'Your child was marked absent today. Please contact the school if this is incorrect.',
            'notification_type': 'attendance_alert',
            'priority': 'normal'
        }
    ]
    
    for user in users:
        if user.role != 'admin':  # Don't send notifications to admin from admin
            for notif_data in notifications_data:
                notification = Notification(
                    recipient_id=user.id,
                    sender_id=admin_user.id,
                    title=notif_data['title'],
                    message=notif_data['message'],
                    notification_type=notif_data['notification_type'],
                    priority=notif_data['priority'],
                    delivery_method='in_app'
                )
                db.session.add(notification)
    
    db.session.commit()
    print("✅ Notifications created")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        init_database()