import React, { useState, useEffect } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api, { endpoints } from '../config/api';

// Admin sub-components
const AdminHome = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await api.get(endpoints.adminDashboardStats);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Admin Dashboard</h2>
        <p className="text-gray-600">Complete system overview and management tools.</p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">👥</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Total Users</h3>
              <p className="text-3xl font-bold text-blue-600">{stats?.total_users || 0}</p>
              <p className="text-sm text-gray-500">Active accounts</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">🎓</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Students</h3>
              <p className="text-3xl font-bold text-green-600">{stats?.total_students || 0}</p>
              <p className="text-sm text-gray-500">Enrolled students</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">👨‍🏫</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Teachers</h3>
              <p className="text-3xl font-bold text-purple-600">{stats?.total_teachers || 0}</p>
              <p className="text-sm text-gray-500">Teaching staff</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">👨‍👩‍👧‍👦</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Parents</h3>
              <p className="text-3xl font-bold text-orange-600">{stats?.total_guardians || 0}</p>
              <p className="text-sm text-gray-500">Guardian accounts</p>
            </div>
          </div>
        </div>
      </div>

      {/* Financial Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">💰</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Collected Fees</h3>
              <p className="text-3xl font-bold text-green-600">${stats?.collected_fees?.toFixed(2) || '0.00'}</p>
              <p className="text-sm text-gray-500">Total collected</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">⏳</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Pending Fees</h3>
              <p className="text-3xl font-bold text-yellow-600">${stats?.pending_fees?.toFixed(2) || '0.00'}</p>
              <p className="text-sm text-gray-500">Awaiting payment</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">🚨</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Overdue Fees</h3>
              <p className="text-3xl font-bold text-red-600">${stats?.overdue_fees?.toFixed(2) || '0.00'}</p>
              <p className="text-sm text-gray-500">Past due date</p>
            </div>
          </div>
        </div>
      </div>

      {/* Attendance Overview */}
      {stats?.attendance_today && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Today's Attendance</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{stats.attendance_today.present}</p>
              <p className="text-sm text-gray-500">Present</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">{stats.attendance_today.absent}</p>
              <p className="text-sm text-gray-500">Absent</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{stats.attendance_today.percentage}%</p>
              <p className="text-sm text-gray-500">Attendance Rate</p>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            to="/admin/users"
            className="block p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
          >
            <div className="flex items-center">
              <span className="text-2xl mr-3">👤</span>
              <div>
                <h4 className="font-medium text-blue-900">Manage Users</h4>
                <p className="text-sm text-blue-700">Add, edit, or deactivate users</p>
              </div>
            </div>
          </Link>

          <Link
            to="/admin/reports"
            className="block p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
          >
            <div className="flex items-center">
              <span className="text-2xl mr-3">📊</span>
              <div>
                <h4 className="font-medium text-green-900">View Reports</h4>
                <p className="text-sm text-green-700">Generate system reports</p>
              </div>
            </div>
          </Link>

          <Link
            to="/admin/notifications"
            className="block p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
          >
            <div className="flex items-center">
              <span className="text-2xl mr-3">📢</span>
              <div>
                <h4 className="font-medium text-purple-900">Send Notifications</h4>
                <p className="text-sm text-purple-700">Bulk messaging system</p>
              </div>
            </div>
          </Link>

          <Link
            to="/admin/system"
            className="block p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors"
          >
            <div className="flex items-center">
              <span className="text-2xl mr-3">⚙️</span>
              <div>
                <h4 className="font-medium text-orange-900">System Info</h4>
                <p className="text-sm text-orange-700">Monitor system health</p>
              </div>
            </div>
          </Link>
        </div>
      </div>

      {/* Grade Distribution */}
      {stats?.grade_distribution && Object.keys(stats.grade_distribution).length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Grade Distribution</h3>
          <div className="grid grid-cols-5 gap-4">
            {Object.entries(stats.grade_distribution).map(([grade, count]) => (
              <div key={grade} className="text-center">
                <p className="text-2xl font-bold text-gray-800">{count}</p>
                <p className="text-sm text-gray-500">Grade {grade}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    role: '',
    search: '',
    page: 1
  });

  useEffect(() => {
    fetchUsers();
  }, [filters]);

  const fetchUsers = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.role) params.append('role', filters.role);
      if (filters.search) params.append('search', filters.search);
      params.append('page', filters.page);
      params.append('per_page', 20);

      const response = await api.get(`${endpoints.allUsers}?${params.toString()}`);
      setUsers(response.data.users || []);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleUserStatus = async (userId) => {
    try {
      await api.patch(endpoints.toggleUserStatus(userId));
      alert('User status updated successfully');
      fetchUsers();
    } catch (error) {
      console.error('Error toggling user status:', error);
      alert('Error updating user status');
    }
  };

  const resetPassword = async (userId) => {
    try {
      const response = await api.post(endpoints.resetUserPassword(userId));
      alert(`Password reset to: ${response.data.new_password}`);
    } catch (error) {
      console.error('Error resetting password:', error);
      alert('Error resetting password');
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">User Management</h2>
        
        {/* Filters */}
        <div className="flex gap-4 mb-6">
          <select
            value={filters.role}
            onChange={(e) => setFilters(prev => ({ ...prev, role: e.target.value, page: 1 }))}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">All Roles</option>
            <option value="admin">Admin</option>
            <option value="teacher">Teacher</option>
            <option value="student">Student</option>
            <option value="parent">Parent</option>
          </select>
          
          <input
            type="text"
            placeholder="Search by name or email..."
            value={filters.search}
            onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value, page: 1 }))}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>

        {loading ? (
          <div className="animate-pulse">Loading users...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {user.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        user.role === 'admin' ? 'bg-red-100 text-red-800' :
                        user.role === 'teacher' ? 'bg-blue-100 text-blue-800' :
                        user.role === 'student' ? 'bg-green-100 text-green-800' :
                        'bg-purple-100 text-purple-800'
                      }`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button
                        onClick={() => toggleUserStatus(user.id)}
                        className={`mr-3 ${
                          user.is_active ? 'text-red-600 hover:text-red-800' : 'text-green-600 hover:text-green-800'
                        }`}
                      >
                        {user.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                      <button
                        onClick={() => resetPassword(user.id)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        Reset Password
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

const BulkNotifications = () => {
  const [notification, setNotification] = useState({
    title: '',
    message: '',
    notification_type: 'general',
    priority: 'normal',
    recipient_roles: []
  });
  const [sending, setSending] = useState(false);

  const handleRoleChange = (role, checked) => {
    setNotification(prev => ({
      ...prev,
      recipient_roles: checked
        ? [...prev.recipient_roles, role]
        : prev.recipient_roles.filter(r => r !== role)
    }));
  };

  const sendNotification = async () => {
    if (!notification.title || !notification.message || notification.recipient_roles.length === 0) {
      alert('Please fill in all required fields and select at least one recipient role');
      return;
    }

    setSending(true);
    try {
      const response = await api.post(endpoints.bulkNotifications, notification);
      alert(`Notification sent successfully to ${response.data.recipients} users`);
      setNotification({
        title: '',
        message: '',
        notification_type: 'general',
        priority: 'normal',
        recipient_roles: []
      });
    } catch (error) {
      console.error('Error sending notification:', error);
      alert('Error sending notification');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Send Bulk Notifications</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
            <input
              type="text"
              value={notification.title}
              onChange={(e) => setNotification(prev => ({ ...prev, title: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="Notification title"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Message</label>
            <textarea
              value={notification.message}
              onChange={(e) => setNotification(prev => ({ ...prev, message: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md h-32"
              placeholder="Your message here..."
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
              <select
                value={notification.notification_type}
                onChange={(e) => setNotification(prev => ({ ...prev, notification_type: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="general">General</option>
                <option value="academic">Academic</option>
                <option value="financial">Financial</option>
                <option value="attendance">Attendance</option>
                <option value="emergency">Emergency</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
              <select
                value={notification.priority}
                onChange={(e) => setNotification(prev => ({ ...prev, priority: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="low">Low</option>
                <option value="normal">Normal</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Recipients</label>
            <div className="space-y-2">
              {['admin', 'teacher', 'student', 'parent'].map((role) => (
                <label key={role} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={notification.recipient_roles.includes(role)}
                    onChange={(e) => handleRoleChange(role, e.target.checked)}
                    className="mr-2"
                  />
                  <span className="capitalize">{role}s</span>
                </label>
              ))}
            </div>
          </div>

          <button
            onClick={sendNotification}
            disabled={sending}
            className={`w-full py-2 px-4 rounded-md text-white ${
              sending ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'
            } transition-colors`}
          >
            {sending ? 'Sending...' : 'Send Notification'}
          </button>
        </div>
      </div>
    </div>
  );
};

const SystemInfo = () => {
  const [systemInfo, setSystemInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSystemInfo();
  }, []);

  const fetchSystemInfo = async () => {
    try {
      const response = await api.get(endpoints.systemInfo);
      setSystemInfo(response.data);
    } catch (error) {
      console.error('Error fetching system info:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse">Loading system information...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">System Information</h2>
        
        {systemInfo && (
          <div className="space-y-6">
            {/* Database Stats */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Database Statistics</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(systemInfo.database_stats).map(([key, value]) => (
                  <div key={key} className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-2xl font-bold text-gray-800">{value}</p>
                    <p className="text-sm text-gray-600 capitalize">{key.replace(/_/g, ' ')}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Activity */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity (Last 7 Days)</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">{systemInfo.recent_activity.recent_logins}</p>
                  <p className="text-sm text-blue-700">User Logins</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">{systemInfo.recent_activity.recent_grades}</p>
                  <p className="text-sm text-green-700">Grades Added</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <p className="text-2xl font-bold text-purple-600">{systemInfo.recent_activity.recent_attendance}</p>
                  <p className="text-sm text-purple-700">Attendance Records</p>
                </div>
              </div>
            </div>

            {/* System Health */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">System Health</h3>
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">✅</span>
                  <div>
                    <p className="font-medium text-green-900">System Status: {systemInfo.system_health}</p>
                    <p className="text-sm text-green-700">Last updated: {new Date(systemInfo.last_updated).toLocaleString()}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

function AdminDashboard() {
  return (
    <div>
      <Routes>
        <Route path="/" element={<AdminHome />} />
        <Route path="/users" element={<UserManagement />} />
        <Route path="/notifications" element={<BulkNotifications />} />
        <Route path="/system" element={<SystemInfo />} />
        <Route path="/reports" element={<div className="p-6">Reports coming soon...</div>} />
      </Routes>
    </div>
  );
}

export default AdminDashboard;