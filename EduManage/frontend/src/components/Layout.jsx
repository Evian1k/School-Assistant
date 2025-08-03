import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getNavigationItems = () => {
    const baseItems = [
      { name: 'Dashboard', href: '/dashboard', icon: '🏠' }
    ];

    switch (user?.role) {
      case 'admin':
        return [
          ...baseItems,
          { name: 'Students', href: '/admin/students', icon: '👥' },
          { name: 'Teachers', href: '/admin/teachers', icon: '👨‍🏫' },
          { name: 'Parents', href: '/admin/parents', icon: '👨‍👩‍👧‍👦' },
          { name: 'Attendance', href: '/admin/attendance', icon: '📅' },
          { name: 'Fees', href: '/admin/fees', icon: '💰' },
          { name: 'Grades', href: '/admin/grades', icon: '📊' },
          { name: 'Reports', href: '/admin/reports', icon: '📋' },
        ];
      case 'teacher':
        return [
          ...baseItems,
          { name: 'My Classes', href: '/teacher/classes', icon: '🏫' },
          { name: 'Attendance', href: '/teacher/attendance', icon: '📅' },
          { name: 'Grades', href: '/teacher/grades', icon: '📊' },
          { name: 'Students', href: '/teacher/students', icon: '👥' },
        ];
      case 'student':
        return [
          ...baseItems,
          { name: 'My Grades', href: '/student/grades', icon: '📊' },
          { name: 'Attendance', href: '/student/attendance', icon: '📅' },
          { name: 'Fees', href: '/student/fees', icon: '💰' },
          { name: 'Profile', href: '/student/profile', icon: '👤' },
        ];
      case 'parent':
        return [
          ...baseItems,
          { name: 'My Children', href: '/parent/children', icon: '👶' },
          { name: 'Fees', href: '/parent/fees', icon: '💰' },
          { name: 'Reports', href: '/parent/reports', icon: '📋' },
        ];
      default:
        return baseItems;
    }
  };

  const navigationItems = getNavigationItems();

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-200 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}>
        <div className="flex items-center justify-center h-16 bg-blue-600">
          <h1 className="text-white text-xl font-bold">EduManage</h1>
        </div>
        <nav className="mt-8">
          {navigationItems.map((item) => (
            <Link
              key={item.name}
              to={item.href}
              className="flex items-center px-6 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors duration-200"
              onClick={() => setSidebarOpen(false)}
            >
              <span className="mr-3 text-lg">{item.icon}</span>
              {item.name}
            </Link>
          ))}
        </nav>
      </div>

      {/* Main content */}
      <div className="lg:ml-64">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <h2 className="ml-4 text-xl font-semibold text-gray-800 capitalize">
                {user?.role} Dashboard
              </h2>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                Welcome, <span className="font-medium">{user?.email}</span>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
              >
                Logout
              </button>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          {children}
        </main>
      </div>

      {/* Sidebar overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}
    </div>
  );
};

export default Layout;