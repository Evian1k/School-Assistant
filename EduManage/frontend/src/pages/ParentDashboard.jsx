import React from 'react';

function ParentDashboard() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Parent Dashboard</h2>
        <p className="text-gray-600">Monitor your children's academic progress, attendance, and school fees.</p>
      </div>

      {/* Children Overview */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">My Children</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <span className="text-2xl mr-3">👧</span>
              <div>
                <h4 className="font-medium text-gray-900">Sarah Johnson</h4>
                <p className="text-sm text-gray-500">Grade 10 - Class 10A</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div>
                <p className="text-lg font-bold text-green-600">95%</p>
                <p className="text-xs text-gray-500">Attendance</p>
              </div>
              <div>
                <p className="text-lg font-bold text-blue-600">A</p>
                <p className="text-xs text-gray-500">Avg Grade</p>
              </div>
              <div>
                <p className="text-lg font-bold text-red-600">$200</p>
                <p className="text-xs text-gray-500">Pending</p>
              </div>
            </div>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <span className="text-2xl mr-3">👦</span>
              <div>
                <h4 className="font-medium text-gray-900">Michael Johnson</h4>
                <p className="text-sm text-gray-500">Grade 8 - Class 8B</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div>
                <p className="text-lg font-bold text-green-600">88%</p>
                <p className="text-xs text-gray-500">Attendance</p>
              </div>
              <div>
                <p className="text-lg font-bold text-blue-600">B+</p>
                <p className="text-xs text-gray-500">Avg Grade</p>
              </div>
              <div>
                <p className="text-lg font-bold text-green-600">$0</p>
                <p className="text-xs text-gray-500">Pending</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">💰</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Total Fees Due</h3>
              <p className="text-3xl font-bold text-red-600">$200</p>
              <p className="text-sm text-gray-500">Across all children</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">📅</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Average Attendance</h3>
              <p className="text-3xl font-bold text-green-600">91%</p>
              <p className="text-sm text-gray-500">This month</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">📊</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Academic Performance</h3>
              <p className="text-3xl font-bold text-blue-600">A-</p>
              <p className="text-sm text-gray-500">Overall average</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Notifications */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Notifications</h3>
        <div className="space-y-3">
          <div className="flex items-center p-3 bg-blue-50 rounded-lg">
            <span className="text-lg mr-3">📊</span>
            <div>
              <p className="text-sm font-medium">Sarah's Math test results are available</p>
              <p className="text-xs text-gray-500">2 hours ago</p>
            </div>
          </div>
          <div className="flex items-center p-3 bg-yellow-50 rounded-lg">
            <span className="text-lg mr-3">💰</span>
            <div>
              <p className="text-sm font-medium">School fee payment reminder for Sarah</p>
              <p className="text-xs text-gray-500">1 day ago</p>
            </div>
          </div>
          <div className="flex items-center p-3 bg-green-50 rounded-lg">
            <span className="text-lg mr-3">✅</span>
            <div>
              <p className="text-sm font-medium">Michael's attendance: Present today</p>
              <p className="text-xs text-gray-500">Today</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ParentDashboard;