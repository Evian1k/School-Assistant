import axios from 'axios';

// API base URL - update this for production
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const endpoints = {
  // Auth
  login: '/api/v1/auth/login',
  register: '/api/v1/auth/register',
  
  // Students
  students: '/api/v1/students',
  studentProfile: '/api/v1/students/my-profile',
  studentsByGuardian: (guardianId) => `/api/v1/students/by-guardian/${guardianId}`,
  studentById: (studentId) => `/api/v1/students/${studentId}`,
  
  // Attendance
  attendance: '/api/v1/attendance',
  markAttendance: '/api/v1/attendance/mark',
  myAttendance: '/api/v1/attendance/my-attendance',
  studentAttendance: (studentId) => `/api/v1/attendance/student/${studentId}`,
  attendanceSummary: (studentId) => `/api/v1/attendance/student/${studentId}/summary`,
  classAttendance: (className, date) => `/api/v1/attendance/class/${className}/date/${date}`,
  bulkMarkAttendance: '/api/v1/attendance/bulk-mark',
  
  // Fees
  fees: '/api/v1/fees',
  myFees: '/api/v1/fees/my-fees',
  studentFees: (studentId) => `/api/v1/fees/student/${studentId}`,
  feeSummary: (studentId) => `/api/v1/fees/student/${studentId}/summary`,
  payFee: (feeId) => `/api/v1/fees/${feeId}/pay`,
  overdueFees: '/api/v1/fees/overdue',
  bulkCreateFees: '/api/v1/fees/bulk-create',
  
  // Grades
  grades: '/api/v1/grades',
  myGrades: '/api/v1/grades/my-grades',
  studentGrades: (studentId) => `/api/v1/grades/student/${studentId}`,
  gradeSummary: (studentId) => `/api/v1/grades/student/${studentId}/summary`,
  bulkCreateGrades: '/api/v1/grades/bulk-create',
  subjects: '/api/v1/grades/subjects',
  classGrades: (className) => `/api/v1/grades/class/${className}/grades`,
  
  // Teachers
  teachers: '/api/v1/teachers',
  teacherProfile: '/api/v1/teachers/my-profile',
  teacherClasses: '/api/v1/teachers/my-classes',
  teacherStudents: '/api/v1/teachers/my-students',
  teacherSubjects: '/api/v1/teachers/my-subjects',
  teacherDashboardStats: '/api/v1/teachers/dashboard-stats',
  classStudents: (className) => `/api/v1/teachers/class/${className}/students`,
  updateTeacherProfile: '/api/v1/teachers/update-profile',
  
  // Admin
  adminDashboardStats: '/api/v1/admin/dashboard-stats',
  allUsers: '/api/v1/admin/users',
  toggleUserStatus: (userId) => `/api/v1/admin/users/${userId}/toggle-status`,
  resetUserPassword: (userId) => `/api/v1/admin/users/${userId}/reset-password`,
  bulkNotifications: '/api/v1/admin/bulk-notifications',
  attendanceReport: '/api/v1/admin/reports/attendance',
  feeReport: '/api/v1/admin/reports/fees',
  academicReport: '/api/v1/admin/reports/academic',
  systemInfo: '/api/v1/admin/system-info',
  exportData: '/api/v1/admin/backup/export',
  
  // Guardians
  guardians: '/api/v1/guardians',
  guardianProfile: '/api/v1/guardians/my-profile',
  myChildren: '/api/v1/guardians/my-children',
  childAttendance: (childId) => `/api/v1/guardians/children/${childId}/attendance`,
  childGrades: (childId) => `/api/v1/guardians/children/${childId}/grades`,
  childFees: (childId) => `/api/v1/guardians/children/${childId}/fees`,
  childSummary: (childId) => `/api/v1/guardians/children/${childId}/summary`,
  guardianDashboardStats: '/api/v1/guardians/dashboard-stats',
  updateGuardianProfile: '/api/v1/guardians/update-profile',
  linkChild: (guardianId) => `/api/v1/guardians/${guardianId}/link-child`,
  unlinkChild: (guardianId, studentId) => `/api/v1/guardians/${guardianId}/unlink-child/${studentId}`,
};

export default api;