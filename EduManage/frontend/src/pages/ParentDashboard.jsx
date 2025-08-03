import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api, { endpoints } from '../config/api';

// Parent sub-components
const ParentHome = () => {
  const [children, setChildren] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [childrenRes, statsRes] = await Promise.all([
        api.get(endpoints.myChildren),
        api.get(endpoints.guardianDashboardStats)
      ]);

      setChildren(childrenRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
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
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Parent Dashboard</h2>
        <p className="text-gray-600">Monitor your children's academic progress, attendance, and school fees.</p>
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
              <p className="text-3xl font-bold text-red-600">${stats?.total_pending_fees?.toFixed(2) || '0.00'}</p>
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
              <p className="text-3xl font-bold text-green-600">{stats?.overall_attendance || 0}%</p>
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
              <p className="text-3xl font-bold text-blue-600">{stats?.academic_performance || 0}%</p>
              <p className="text-sm text-gray-500">Overall average</p>
            </div>
          </div>
        </div>
      </div>

      {/* Children Overview */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">My Children</h3>
        {children.length === 0 ? (
          <p className="text-gray-500">No children found. Please contact the administration to link your children to your account.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {children.map((child) => (
              <div key={child.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <span className="text-2xl mr-3">👧</span>
                  <div>
                    <h4 className="font-medium text-gray-900">{child.name}</h4>
                    <p className="text-sm text-gray-500">{child.grade_level} - {child.class_name}</p>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center mb-3">
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
                <Link
                  to={`/parent/child/${child.id}`}
                  className="block w-full text-center bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  View Details
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent Notifications */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Notifications</h3>
        <div className="space-y-3">
          <div className="flex items-center p-3 bg-blue-50 rounded-lg">
            <span className="text-lg mr-3">📊</span>
            <div>
              <p className="text-sm font-medium">New grades have been posted</p>
              <p className="text-xs text-gray-500">2 hours ago</p>
            </div>
          </div>
          <div className="flex items-center p-3 bg-yellow-50 rounded-lg">
            <span className="text-lg mr-3">💰</span>
            <div>
              <p className="text-sm font-medium">School fee payment reminder</p>
              <p className="text-xs text-gray-500">1 day ago</p>
            </div>
          </div>
          <div className="flex items-center p-3 bg-green-50 rounded-lg">
            <span className="text-lg mr-3">✅</span>
            <div>
              <p className="text-sm font-medium">Attendance updated</p>
              <p className="text-xs text-gray-500">Today</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const ChildDetails = ({ childId }) => {
  const [child, setChild] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('summary');

  useEffect(() => {
    if (childId) {
      fetchChildData();
    }
  }, [childId]);

  const fetchChildData = async () => {
    try {
      const summaryRes = await api.get(endpoints.childSummary(childId));
      setSummary(summaryRes.data);
      setChild(summaryRes.data.student);
    } catch (error) {
      console.error('Error fetching child data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse">Loading child details...</div>;
  }

  if (!child) {
    return <div className="text-red-600">Child not found or access denied.</div>;
  }

  return (
    <div className="space-y-6">
      {/* Child Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center">
          <span className="text-4xl mr-4">👧</span>
          <div>
            <h2 className="text-2xl font-bold text-gray-800">{child.name}</h2>
            <p className="text-gray-600">{child.grade_level} - {child.class_name}</p>
            <p className="text-sm text-gray-500">Student ID: {child.student_id}</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {['summary', 'attendance', 'grades', 'fees'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'summary' && summary && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-800 mb-2">Attendance</h3>
                <p className="text-2xl font-bold text-blue-600">{summary.attendance.percentage}%</p>
                <p className="text-sm text-gray-600">
                  {summary.attendance.present_days}/{summary.attendance.total_days} days present
                </p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-semibold text-green-800 mb-2">Academic</h3>
                <p className="text-2xl font-bold text-green-600">{summary.academic.average_percentage}%</p>
                <p className="text-sm text-gray-600">
                  {summary.academic.total_grades} assignments across {summary.academic.subjects_count} subjects
                </p>
              </div>
              <div className="bg-red-50 p-4 rounded-lg">
                <h3 className="font-semibold text-red-800 mb-2">Finances</h3>
                <p className="text-2xl font-bold text-red-600">${summary.financial.pending_fees.toFixed(2)}</p>
                <p className="text-sm text-gray-600">
                  ${summary.financial.overdue_fees.toFixed(2)} overdue
                </p>
              </div>
            </div>
          )}

          {activeTab === 'attendance' && (
            <div>
              <h3 className="text-lg font-medium mb-4">Attendance Records</h3>
              <p className="text-gray-600">Attendance details would be loaded here...</p>
            </div>
          )}

          {activeTab === 'grades' && (
            <div>
              <h3 className="text-lg font-medium mb-4">Grade Records</h3>
              <p className="text-gray-600">Grade details would be loaded here...</p>
            </div>
          )}

          {activeTab === 'fees' && (
            <div>
              <h3 className="text-lg font-medium mb-4">Fee Records</h3>
              <p className="text-gray-600">Fee details would be loaded here...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

function ParentDashboard() {
  return (
    <div>
      <Routes>
        <Route path="/" element={<ParentHome />} />
        <Route path="/child/:childId" element={<ChildDetailsWrapper />} />
      </Routes>
    </div>
  );
}

// Wrapper component to pass childId as prop
const ChildDetailsWrapper = () => {
  const { childId } = useParams();
  return <ChildDetails childId={parseInt(childId)} />;
};

export default ParentDashboard;