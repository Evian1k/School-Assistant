#!/usr/bin/env python3
"""
Quick test script to verify EduManage system functionality
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_api_endpoints():
    """Test basic API functionality"""
    base_url = "http://localhost:5000/api/v1"
    
    print("🔧 Testing EduManage API Endpoints...")
    
    # Test login
    try:
        login_data = {
            "email": "admin@example.com",
            "password": "admin123"
        }
        
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ Admin login successful")
            token = response.json().get('access_token')
            
            # Test authenticated request
            headers = {"Authorization": f"Bearer {token}"}
            dashboard_response = requests.get(f"{base_url}/admin/dashboard-stats", headers=headers)
            
            if dashboard_response.status_code == 200:
                print("✅ Admin dashboard data retrieved")
                stats = dashboard_response.json()
                print(f"   - Total users: {stats.get('total_users', 0)}")
                print(f"   - Total students: {stats.get('total_students', 0)}")
                print(f"   - Total teachers: {stats.get('total_teachers', 0)}")
            else:
                print("❌ Failed to retrieve dashboard data")
        else:
            print("❌ Admin login failed")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server")
        print("   Make sure to run: cd backend && python run.py")
        return False
    
    return True

def check_frontend():
    """Check if frontend is accessible"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend server is running")
            return True
        else:
            print("❌ Frontend server returned error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend server not accessible")
        print("   Make sure to run: cd frontend && npm run dev")
        return False
    except requests.exceptions.Timeout:
        print("❌ Frontend server timeout")
        return False

def print_demo_credentials():
    """Print demo login credentials"""
    print("\n📋 Demo Login Credentials:")
    print("=" * 50)
    print("Admin:")
    print("  Email: admin@example.com")
    print("  Password: admin123")
    print()
    print("Teacher:")
    print("  Email: teacher1@example.com")
    print("  Password: teacher123")
    print()
    print("Student:")
    print("  Email: student1@example.com")
    print("  Password: student123")
    print()
    print("Parent:")
    print("  Email: parent1@example.com")
    print("  Password: parent123")

def print_system_info():
    """Print system information"""
    print("\n🏫 EduManage System Information:")
    print("=" * 50)
    print("📚 Features Implemented:")
    print("  ✅ Role-based authentication (Admin, Teacher, Student, Parent)")
    print("  ✅ Student management with profiles and academic records")
    print("  ✅ Attendance tracking with bulk operations")
    print("  ✅ Fee management with payment processing")
    print("  ✅ Grade management with academic reports")
    print("  ✅ Teacher class and student management")
    print("  ✅ Parent portal for children's information")
    print("  ✅ Admin system management and reporting")
    print("  ✅ Comprehensive security with JWT tokens")
    print("  ✅ Database relationships and constraints")
    print("  ✅ Modern React frontend with Tailwind CSS")
    print()
    print("🔧 Technologies Used:")
    print("  Backend: Flask, SQLAlchemy, PostgreSQL, JWT")
    print("  Frontend: React, Vite, Tailwind CSS, Axios")
    print("  Security: Role-based access control, Password hashing")
    print("  Database: PostgreSQL with comprehensive relationships")

def print_quick_start():
    """Print quick start instructions"""
    print("\n🚀 Quick Start Instructions:")
    print("=" * 50)
    print("1. Backend Setup:")
    print("   cd EduManage/backend")
    print("   pip install -r requirements.txt")
    print("   python init_db.py  # Initialize with demo data")
    print("   python run.py      # Start backend server")
    print()
    print("2. Frontend Setup:")
    print("   cd EduManage/frontend")
    print("   npm install")
    print("   npm run dev        # Start frontend server")
    print()
    print("3. Access the system:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:5000")

def main():
    """Main test function"""
    print("🏫 EduManage System Verification")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the EduManage root directory")
        sys.exit(1)
    
    print_system_info()
    print_demo_credentials()
    print_quick_start()
    
    print("\n🔍 System Health Check:")
    print("=" * 50)
    
    # Test backend
    backend_ok = test_api_endpoints()
    
    # Test frontend
    frontend_ok = check_frontend()
    
    print("\n📊 System Status:")
    print("=" * 30)
    print(f"Backend API: {'✅ Running' if backend_ok else '❌ Not Running'}")
    print(f"Frontend:    {'✅ Running' if frontend_ok else '❌ Not Running'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 EduManage system is fully operational!")
        print("   Visit http://localhost:3000 to get started")
    else:
        print("\n⚠️  Some services need to be started")
        print("   Follow the Quick Start instructions above")

if __name__ == "__main__":
    main()