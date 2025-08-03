import React, { useState, useEffect } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api, { endpoints } from '../config/api';

// Student sub-components
const StudentHome = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      // Fetch student profile and summary data
      const [profileRes, attendanceRes, feesRes] = await Promise.all([
        api.get(endpoints.studentProfile),
        api.get(endpoints.myAttendance + '?start_date=' + new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0]),
        api.get(endpoints.myFees)
      ]);

      setSummary({
        profile: profileRes.data,
        attendance: attendanceRes.data,
        fees: feesRes.data
      });
    } catch (error) {
      console.error('Error fetching summary:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse">Loading...</div>;
  }

  const calculateAttendancePercentage = () => {
    if (!summary?.attendance?.length) return 0;
    const presentDays = summary.attendance.filter(record => record.status === 'present').length;
    return Math.round((presentDays / summary.attendance.length) * 100);
  };

  const getPendingFees = () => {
    if (!summary?.fees?.length) return 0;
    return summary.fees.filter(fee => fee.status === 'pending').reduce((total, fee) => total + fee.final_amount, 0);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Welcome Back!</h2>
        <p className="text-gray-600">Here's an overview of your academic progress.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">📅</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Attendance</h3>
              <p className="text-3xl font-bold text-blue-600">{calculateAttendancePercentage()}%</p>
              <p className="text-sm text-gray-500">This academic year</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">💰</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Pending Fees</h3>
              <p className="text-3xl font-bold text-red-600">${getPendingFees().toFixed(2)}</p>
              <p className="text-sm text-gray-500">Total outstanding</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">📊</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Academic Status</h3>
              <p className="text-3xl font-bold text-green-600">Active</p>
              <p className="text-sm text-gray-500">Current enrollment</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/student/grades"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <span className="text-xl mr-3">📊</span>
            <span>View Grades</span>
          </Link>
          <Link
            to="/student/attendance"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <span className="text-xl mr-3">📅</span>
            <span>View Attendance</span>
          </Link>
          <Link
            to="/student/fees"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <span className="text-xl mr-3">💰</span>
            <span>View Fees</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

const StudentGrades = () => {
  const [grades, setGrades] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedTerm, setSelectedTerm] = useState('');

  useEffect(() => {
    fetchGrades();
  }, [selectedSubject, selectedTerm]);

  const fetchGrades = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedSubject) params.append('subject', selectedSubject);
      if (selectedTerm) params.append('term', selectedTerm);

      const [gradesRes, summaryRes] = await Promise.all([
        api.get(`${endpoints.myGrades}?${params.toString()}`),
        api.get(endpoints.myGrades.replace('/my-grades', '/student/1/summary')) // Will be dynamic based on student ID
      ]);

      setGrades(gradesRes.data);
      setSummary(summaryRes.data);
    } catch (error) {
      console.error('Error fetching grades:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse">Loading grades...</div>;
  }

  const uniqueSubjects = [...new Set(grades.map(grade => grade.subject))];
  const uniqueTerms = [...new Set(grades.map(grade => grade.term))];

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">My Grades</h2>
        
        {/* Filters */}
        <div className="flex gap-4 mb-4">
          <select
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">All Subjects</option>
            {uniqueSubjects.map(subject => (
              <option key={subject} value={subject}>{subject}</option>
            ))}
          </select>
          
          <select
            value={selectedTerm}
            onChange={(e) => setSelectedTerm(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">All Terms</option>
            {uniqueTerms.map(term => (
              <option key={term} value={term}>{term}</option>
            ))}
          </select>
        </div>

        {/* Summary Stats */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-800">Overall Average</h3>
              <p className="text-2xl font-bold text-blue-600">{summary.overall_average}%</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="font-semibold text-green-800">Total Subjects</h3>
              <p className="text-2xl font-bold text-green-600">{summary.total_subjects}</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <h3 className="font-semibold text-purple-800">Total Assignments</h3>
              <p className="text-2xl font-bold text-purple-600">{summary.total_assignments}</p>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h3 className="font-semibold text-yellow-800">Grade Level</h3>
              <p className="text-2xl font-bold text-yellow-600">
                {summary.overall_average >= 90 ? 'A' : 
                 summary.overall_average >= 80 ? 'B' : 
                 summary.overall_average >= 70 ? 'C' : 
                 summary.overall_average >= 60 ? 'D' : 'F'}
              </p>
            </div>
          </div>
        )}

        {/* Grades Table */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Subject
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Assignment Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Grade
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Term
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {grades.map((grade) => (
                <tr key={grade.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {grade.subject}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {grade.assignment_type}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {grade.score}/{grade.max_score} ({grade.percentage}%)
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      grade.grade_letter === 'A' ? 'bg-green-100 text-green-800' :
                      grade.grade_letter === 'B' ? 'bg-blue-100 text-blue-800' :
                      grade.grade_letter === 'C' ? 'bg-yellow-100 text-yellow-800' :
                      grade.grade_letter === 'D' ? 'bg-orange-100 text-orange-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {grade.grade_letter}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {grade.term}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(grade.date_recorded).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const StudentAttendance = () => {
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAttendance();
  }, []);

  const fetchAttendance = async () => {
    try {
      const response = await api.get(endpoints.myAttendance);
      setAttendance(response.data);
    } catch (error) {
      console.error('Error fetching attendance:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse">Loading attendance...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">My Attendance</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Remarks
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {attendance.map((record) => (
              <tr key={record.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {new Date(record.date).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    record.status === 'present' ? 'bg-green-100 text-green-800' :
                    record.status === 'absent' ? 'bg-red-100 text-red-800' :
                    record.status === 'late' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {record.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {record.remarks || '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const StudentFees = () => {
  const [fees, setFees] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFees();
  }, []);

  const fetchFees = async () => {
    try {
      const response = await api.get(endpoints.myFees);
      setFees(response.data);
    } catch (error) {
      console.error('Error fetching fees:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse">Loading fees...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">My Fees</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Fee Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Due Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {fees.map((fee) => (
              <tr key={fee.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {fee.fee_type}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${fee.final_amount.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {new Date(fee.due_date).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    fee.status === 'paid' ? 'bg-green-100 text-green-800' :
                    fee.is_overdue ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {fee.is_overdue && fee.status === 'pending' ? 'Overdue' : fee.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const StudentProfile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get(endpoints.studentProfile);
      setProfile(response.data);
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse">Loading profile...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">My Profile</h2>
      {profile && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Student ID</label>
            <p className="mt-1 text-sm text-gray-900">{profile.student_id}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Name</label>
            <p className="mt-1 text-sm text-gray-900">{profile.name}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <p className="mt-1 text-sm text-gray-900">{profile.email}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Class</label>
            <p className="mt-1 text-sm text-gray-900">{profile.class_name}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Grade Level</label>
            <p className="mt-1 text-sm text-gray-900">{profile.grade_level}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Admission Date</label>
            <p className="mt-1 text-sm text-gray-900">
              {profile.admission_date ? new Date(profile.admission_date).toLocaleDateString() : 'N/A'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

function StudentDashboard() {
  return (
    <div>
      <Routes>
        <Route path="/" element={<StudentHome />} />
        <Route path="/grades" element={<StudentGrades />} />
        <Route path="/attendance" element={<StudentAttendance />} />
        <Route path="/fees" element={<StudentFees />} />
        <Route path="/profile" element={<StudentProfile />} />
      </Routes>
    </div>
  );
}

export default StudentDashboard;