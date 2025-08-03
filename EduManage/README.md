# 🎓 EduManage - Complete School Management System

A comprehensive, secure, and scalable school management system built with Flask, PostgreSQL, React, and Tailwind CSS. EduManage features complete role-based access control, ensuring students, parents, teachers, and administrators can only access their authorized information.

## 🌟 Key Features

### 🔐 Role-Based Security Architecture
- **Strict Data Privacy**: Users can only access their own data or data they're authorized to view
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Routes**: Frontend and backend routes protected by user roles
- **Access Control**: Students see only their data, parents see only their children's data, teachers see only their assigned classes

### 👥 User Management
- **Admin Dashboard**: Complete system management and analytics
- **Teacher Portal**: Class management, grade entry, attendance marking
- **Student Portal**: Personal grades, attendance, fee status, profile
- **Parent Portal**: Children's academic progress, fee status, attendance tracking

### 📊 Academic Management
- **Attendance System**: Daily attendance tracking with role-based access
- **Grade Management**: Comprehensive grading with automatic calculations
- **Fee Management**: Fee tracking, payment processing, overdue alerts
- **Report Generation**: Academic reports and analytics

### 🎨 Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Modern Interface**: Clean, professional design with Tailwind CSS
- **Role-Specific Dashboards**: Customized interfaces for each user type
- **Real-time Updates**: Dynamic data loading and updates

## 🏗️ System Architecture

### Backend (Flask + PostgreSQL)
```
EduManage/backend/
├── app/
│   ├── models/           # Database models with relationships
│   ├── routes/           # API endpoints with role-based access
│   ├── auth/            # Authentication and authorization decorators
│   └── __init__.py      # Flask app initialization
├── config.py            # Configuration settings
├── run.py              # Application entry point
├── init_db.py          # Database initialization script
└── requirements.txt     # Python dependencies
```

### Frontend (React + Vite + Tailwind)
```
EduManage/frontend/
├── src/
│   ├── components/      # Reusable React components
│   ├── context/         # Authentication context
│   ├── config/          # API configuration
│   ├── pages/           # Role-specific dashboard pages
│   └── App.jsx         # Main application component
├── public/             # Static assets
├── index.html          # HTML template
└── package.json        # Node.js dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+

### 1. Clone the Repository
```bash
git clone <repository-url>
cd EduManage
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SECRET_KEY="your-secret-key"
export JWT_SECRET_KEY="your-jwt-secret"
export DATABASE_URL="postgresql://user:password@localhost/edumanage"

# Initialize database with sample data
python init_db.py

# Run the Flask application
python run.py
```

### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

## 🔑 Demo Credentials

The system comes with pre-configured demo accounts:

| Role | Email | Password | Access Level |
|------|-------|----------|--------------|
| Admin | admin@school.edu | admin123 | Full system access |
| Teacher | teacher@school.edu | teacher123 | Assigned classes only |
| Student | student@school.edu | student123 | Personal data only |
| Parent | parent@school.edu | parent123 | Children's data only |

## 📊 Database Schema

### Core Models
- **User**: Base user account with role
- **Student**: Student profile linked to user account
- **Teacher**: Teacher profile with class assignments
- **Guardian**: Parent/guardian profile
- **Attendance**: Daily attendance records
- **Grade**: Academic performance tracking
- **Fee**: Financial records and payments
- **Notification**: System communications

### Security Features
- **Foreign Key Constraints**: Enforce data relationships
- **Role-Based Filtering**: Database queries filtered by user role
- **Access Validation**: Backend validates every request
- **Data Isolation**: Users cannot access unauthorized data

## 🛡️ Security Implementation

### Backend Security
- **JWT Token Validation**: Every protected route validates JWT tokens
- **Role-Based Decorators**: Custom decorators enforce role requirements
- **Data Access Control**: Functions validate user access to specific records
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries

### Frontend Security
- **Protected Routes**: React routes require authentication
- **Role-Based Navigation**: UI adapts based on user role
- **Token Management**: Automatic token refresh and logout
- **API Interceptors**: Axios interceptors handle authentication

## 🔧 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

### Students (Role-Protected)
- `GET /api/v1/students` - List students (admin/teacher)
- `GET /api/v1/students/{id}` - Get student details (with access control)
- `GET /api/v1/students/my-profile` - Get own profile (student)

### Attendance (Role-Protected)
- `POST /api/v1/attendance/mark` - Mark attendance (admin/teacher)
- `GET /api/v1/attendance/student/{id}` - Get student attendance (with access control)
- `GET /api/v1/attendance/my-attendance` - Get own attendance (student)

### Fees (Role-Protected)
- `GET /api/v1/fees/student/{id}` - Get student fees (with access control)
- `GET /api/v1/fees/my-fees` - Get own fees (student)
- `POST /api/v1/fees/{id}/pay` - Process payment (admin)

## 🎯 Role-Based Access Examples

### Student Access
```python
# Students can only see their own data
@student_access_only()
def get_my_grades():
    student = Student.query.filter_by(user_id=current_user_id).first()
    return student.grades
```

### Parent Access
```python
# Parents can only see their children's data
@guardian_access_only()
def get_children_fees(guardian_id, accessible_student_ids):
    fees = Fee.query.filter(Fee.student_id.in_(accessible_student_ids)).all()
    return fees
```

### Teacher Access
```python
# Teachers can only see students in their assigned classes
@teacher_class_access()
def get_class_students(teacher_classes):
    students = Student.query.filter(Student.class_name.in_(teacher_classes)).all()
    return students
```

## 🚀 Deployment

### Environment Configuration
Create `.env` files for production:

**Backend `.env`:**
```env
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-production-jwt-secret
DATABASE_URL=postgresql://user:password@host:port/database
FLASK_ENV=production
```

**Frontend `.env`:**
```env
REACT_APP_API_URL=https://your-api-domain.com
```

### Deployment Platforms
- **Backend**: Render, Heroku, or DigitalOcean
- **Frontend**: Netlify, Vercel, or Render
- **Database**: Render PostgreSQL, ElephantSQL, or AWS RDS

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📈 Future Enhancements

### Planned Features
- **SMS/WhatsApp Integration**: Twilio integration for notifications
- **Report Card Generation**: PDF report card generation
- **Multi-language Support**: Internationalization
- **Mobile App**: React Native mobile application
- **Advanced Analytics**: AI-powered insights and predictions

### Scalability Features
- **Microservices Architecture**: Break into smaller services
- **Caching Layer**: Redis caching for performance
- **Load Balancing**: Handle increased user load
- **Database Optimization**: Query optimization and indexing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- 📧 Email: support@edumanage.school
- 📱 Phone: +1 (555) 123-4567
- 💬 Discord: [EduManage Community](https://discord.gg/edumanage)

---

**EduManage** - Empowering Education Through Technology 🎓