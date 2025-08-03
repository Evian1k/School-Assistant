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
  
  // Grades (to be implemented)
  grades: '/api/v1/grades',
  myGrades: '/api/v1/grades/my-grades',
  studentGrades: (studentId) => `/api/v1/grades/student/${studentId}`,
};

export default api;