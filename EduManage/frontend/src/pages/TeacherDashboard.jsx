import React from 'react';

function TeacherDashboard() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Teacher Dashboard</h2>
        <p className="text-gray-600">Manage your classes, track student progress, and record attendance.</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">🏫</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">My Classes</h3>
              <p className="text-3xl font-bold text-blue-600">5</p>
              <p className="text-sm text-gray-500">Active classes</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">👥</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Total Students</h3>
              <p className="text-3xl font-bold text-green-600">120</p>
              <p className="text-sm text-gray-500">Across all classes</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">📅</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Today's Attendance</h3>
              <p className="text-3xl font-bold text-yellow-600">92%</p>
              <p className="text-sm text-gray-500">Average across classes</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <span className="text-xl mr-3">📅</span>
            <span>Mark Attendance</span>
          </button>
          <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <span className="text-xl mr-3">📊</span>
            <span>Enter Grades</span>
          </button>
          <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <span className="text-xl mr-3">👥</span>
            <span>View Students</span>
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center p-3 bg-gray-50 rounded-lg">
            <span className="text-lg mr-3">✅</span>
            <div>
              <p className="text-sm font-medium">Attendance marked for Class 10A</p>
              <p className="text-xs text-gray-500">2 hours ago</p>
            </div>
          </div>
          <div className="flex items-center p-3 bg-gray-50 rounded-lg">
            <span className="text-lg mr-3">📊</span>
            <div>
              <p className="text-sm font-medium">Grades entered for Math Quiz</p>
              <p className="text-xs text-gray-500">1 day ago</p>
            </div>
          </div>
          <div className="flex items-center p-3 bg-gray-50 rounded-lg">
            <span className="text-lg mr-3">📝</span>
            <div>
              <p className="text-sm font-medium">Updated lesson plan for Science</p>
              <p className="text-xs text-gray-500">2 days ago</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TeacherDashboard;