# 🎓 EduManage - Complete School Management System

EduManage is a comprehensive, secure, and scalable school management system designed with role-based architecture to ensure data privacy and appropriate access control for all users.

## ✨ Features

### 🔐 Authentication & Security
- **JWT-based authentication** with secure token management
- **Role-based access control** (Admin, Teacher, Student, Guardian)
- **Password validation** with strength requirements
- **Session management** with automatic logout on token expiry

### 👥 User Management
- **Multi-role registration** with role-specific forms
- **Profile management** with role-specific fields
- **Password change** functionality
- **Account status** tracking (active/inactive)

### 🎒 Student Management
- **Comprehensive student profiles** with academic and personal information
- **Class and section** assignment
- **Guardian linking** for parent access
- **Student ID generation** with unique identifiers
- **Soft delete** functionality for data preservation

### 📊 Academic Management
- **Grade entry** by teachers with subject and term tracking
- **Grade calculation** with automatic letter grade assignment
- **Academic year** and term management
- **Performance tracking** with historical data

### 📅 Attendance System
- **Daily attendance** marking by teachers
- **Multiple status** support (present, absent, late, excused)
- **Time tracking** with check-in/check-out times
- **Date range filtering** for reports

### 💰 Fee Management
- **Multiple fee types** (Tuition, Library, Transport, etc.)
- **Payment tracking** with partial payment support
- **Due date management** with overdue detection
- **Receipt generation** with unique numbers
- **Academic year** and term-based fee structure

### 📱 Communication System
- **Real-time notifications** with priority levels
- **Bulk messaging** capabilities for admins
- **Fee reminders** with automated alerts
- **Attendance notifications** for guardians
- **Notification filtering** and search functionality

### 📈 Dashboard Analytics
- **Role-specific dashboards** with relevant metrics
- **Real-time statistics** for admins and teachers
- **Student performance** tracking
- **Fee collection** analytics
- **Attendance reports** with visual indicators

### 🎨 Modern UI/UX
- **Responsive design** for all devices
- **Modern interface** with Tailwind CSS
- **Interactive components** with smooth animations
- **Role-based navigation** with contextual menus
- **Search and filtering** capabilities

## 🏗️ Architecture

### Backend (Flask + PostgreSQL)
- **Flask REST API** with blueprint organization
- **SQLAlchemy ORM** for database management
- **PostgreSQL** for robust data storage
- **JWT authentication** with Flask-JWT-Extended
- **CORS support** for frontend integration
- **Role-based route protection** with decorators

### Frontend (React + Vite)
- **React 18** with modern hooks and context
- **Vite** for fast development and building
- **Tailwind CSS** for utility-first styling
- **React Router** for client-side navigation
- **Axios** for HTTP client with interceptors
- **Lucide React** for beautiful icons

### Database Design
- **Normalized schema** with proper relationships
- **Foreign key constraints** for data integrity
- **Indexed fields** for optimal performance
- **Soft delete** support for data preservation
- **Audit trails** with created/updated timestamps

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EduManage/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   echo "SECRET_KEY=your-secret-key-here" > .env
   echo "DATABASE_URL=postgresql://user:password@localhost/edumanage" >> .env
   echo "JWT_SECRET_KEY=your-jwt-secret-key" >> .env
   ```

5. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb edumanage
   
   # Run migrations (tables will be created automatically)
   python run.py
   ```

6. **Start the backend server**
   ```bash
   python run.py
   ```
   The API will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

## 👥 Demo Accounts

For testing purposes, you can use these demo accounts:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@school.com | Admin123! |
| Teacher | teacher@school.com | Teacher123! |
| Student | student@school.com | Student123! |
| Guardian | parent@school.com | Parent123! |

## 📋 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/profile` - Get user profile
- `PUT /api/v1/auth/profile` - Update profile
- `POST /api/v1/auth/change-password` - Change password

### Students
- `GET /api/v1/students` - Get students (role-filtered)
- `POST /api/v1/students` - Add new student
- `GET /api/v1/students/{id}` - Get specific student
- `PUT /api/v1/students/{id}` - Update student
- `DELETE /api/v1/students/{id}` - Delete student
- `GET /api/v1/students/{id}/grades` - Get student grades
- `POST /api/v1/students/{id}/grades` - Add grade
- `GET /api/v1/students/{id}/attendance` - Get attendance
- `POST /api/v1/students/{id}/attendance` - Mark attendance
- `GET /api/v1/students/{id}/fees` - Get fees
- `POST /api/v1/students/{id}/fees` - Add fee
- `GET /api/v1/students/dashboard` - Dashboard statistics

### Notifications
- `GET /api/v1/notifications` - Get notifications
- `GET /api/v1/notifications/{id}` - Get specific notification
- `PUT /api/v1/notifications/{id}/read` - Mark as read
- `PUT /api/v1/notifications/mark-all-read` - Mark all as read
- `POST /api/v1/notifications/send` - Send notification
- `POST /api/v1/notifications/bulk-send` - Bulk send
- `POST /api/v1/notifications/fee-reminder` - Send fee reminder
- `POST /api/v1/notifications/attendance-alert` - Send attendance alert

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://username:password@localhost/edumanage
JWT_SECRET_KEY=your-jwt-secret-key-here
FLASK_ENV=development
```

### Database Configuration

The system uses PostgreSQL. Make sure to:

1. Install PostgreSQL
2. Create a database named `edumanage`
3. Update the `DATABASE_URL` in your `.env` file
4. Tables will be created automatically on first run

## 🛠️ Development

### Backend Development

```bash
cd backend
python run.py
```

The Flask development server will start with auto-reload enabled.

### Frontend Development

```bash
cd frontend
npm run dev
```

The Vite development server will start with hot module replacement.

### Building for Production

```bash
# Backend
cd backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# Frontend
cd frontend
npm run build
```

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

## 📦 Deployment

### Backend Deployment (Render/Heroku)

1. **Set up environment variables** in your hosting platform
2. **Configure PostgreSQL** database
3. **Deploy using Git** or platform-specific methods

### Frontend Deployment (Netlify/Vercel)

1. **Build the project**: `npm run build`
2. **Deploy the `dist` folder** to your hosting platform
3. **Configure environment variables** for API endpoints

## 🔒 Security Features

- **JWT token authentication** with expiration
- **Role-based access control** on all routes
- **Password hashing** with Werkzeug
- **Input validation** and sanitization
- **CORS configuration** for cross-origin requests
- **SQL injection protection** with SQLAlchemy ORM
- **XSS protection** with proper content encoding

## 📊 Database Schema

### Core Tables
- `users` - User accounts and authentication
- `students` - Student information and profiles
- `guardians` - Parent/guardian information
- `teachers` - Teacher information and subjects
- `grades` - Academic grades and performance
- `attendance` - Daily attendance records
- `fees` - Fee management and payments
- `notifications` - Communication system
- `documents` - File management system

### Key Relationships
- Students are linked to guardians (one-to-many)
- Grades are linked to students and teachers
- Attendance is linked to students and teachers
- Fees are linked to students
- Notifications are linked to users

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation for common issues

## 🚀 Roadmap

### Planned Features
- [ ] SMS/WhatsApp integration for notifications
- [ ] PDF report generation
- [ ] Advanced analytics and reporting
- [ ] Mobile app development
- [ ] Multi-language support
- [ ] Advanced file upload system
- [ ] Real-time chat functionality
- [ ] Calendar integration
- [ ] Advanced search and filtering
- [ ] Data export functionality

### Performance Optimizations
- [ ] Database query optimization
- [ ] Caching implementation
- [ ] CDN integration
- [ ] Image optimization
- [ ] Lazy loading implementation

---

**EduManage** - Empowering schools with modern, secure, and efficient management solutions.