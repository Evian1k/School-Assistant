import React, { useState, useEffect } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api, { endpoints } from '../config/api';

// Teacher sub-components
const TeacherHome = () => {
  const [stats, setStats] = useState(null);
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, classesRes] = await Promise.all([
        api.get(endpoints.teacherDashboardStats),
        api.get(endpoints.teacherClasses)
      ]);

      setStats(statsRes.data);
      setClasses(classesRes.data);
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
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Teacher Dashboard</h2>
        <p className="text-gray-600">Manage your classes, track student progress, and record grades.</p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">🏫</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">My Classes</h3>
              <p className="text-3xl font-bold text-blue-600">{stats?.total_classes || 0}</p>
              <p className="text-sm text-gray-500">Classes assigned</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">👥</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">My Students</h3>
              <p className="text-3xl font-bold text-green-600">{stats?.total_students || 0}</p>
              <p className="text-sm text-gray-500">Total students</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">📚</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Subjects</h3>
              <p className="text-3xl font-bold text-purple-600">{stats?.total_subjects || 0}</p>
              <p className="text-sm text-gray-500">Subjects taught</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/teacher/attendance"
            className="block p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
          >
            <div className="flex items-center">
              <span className="text-2xl mr-3">✅</span>
              <div>
                <h4 className="font-medium text-blue-900">Mark Attendance</h4>
                <p className="text-sm text-blue-700">Record student attendance</p>
              </div>
            </div>
          </Link>

          <Link
            to="/teacher/grades"
            className="block p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
          >
            <div className="flex items-center">
              <span className="text-2xl mr-3">📊</span>
              <div>
                <h4 className="font-medium text-green-900">Record Grades</h4>
                <p className="text-sm text-green-700">Enter student grades</p>
              </div>
            </div>
          </Link>

          <Link
            to="/teacher/students"
            className="block p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
          >
            <div className="flex items-center">
              <span className="text-2xl mr-3">👥</span>
              <div>
                <h4 className="font-medium text-purple-900">View Students</h4>
                <p className="text-sm text-purple-700">Manage your students</p>
              </div>
            </div>
          </Link>
        </div>
      </div>

      {/* My Classes */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">My Classes</h3>
        {classes.length === 0 ? (
          <p className="text-gray-500">No classes assigned yet.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {classes.map((classData, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <span className="text-2xl mr-3">📚</span>
                  <div>
                    <h4 className="font-medium text-gray-900">{classData.class_name}</h4>
                    <p className="text-sm text-gray-500">{classData.student_count} students</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Link
                    to={`/teacher/class/${classData.class_name}/attendance`}
                    className="flex-1 text-center bg-blue-600 text-white py-2 px-3 rounded text-sm hover:bg-blue-700 transition-colors"
                  >
                    Attendance
                  </Link>
                  <Link
                    to={`/teacher/class/${classData.class_name}/grades`}
                    className="flex-1 text-center bg-green-600 text-white py-2 px-3 rounded text-sm hover:bg-green-700 transition-colors"
                  >
                    Grades
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center p-3 bg-blue-50 rounded-lg">
            <span className="text-lg mr-3">✅</span>
            <div>
              <p className="text-sm font-medium">Attendance marked for Class 10A</p>
              <p className="text-xs text-gray-500">2 hours ago</p>
            </div>
          </div>
          <div className="flex items-center p-3 bg-green-50 rounded-lg">
            <span className="text-lg mr-3">📊</span>
            <div>
              <p className="text-sm font-medium">Math quiz grades entered for Class 9B</p>
              <p className="text-xs text-gray-500">1 day ago</p>
            </div>
          </div>
          <div className="flex items-center p-3 bg-purple-50 rounded-lg">
            <span className="text-lg mr-3">👥</span>
            <div>
              <p className="text-sm font-medium">Reviewed student progress reports</p>
              <p className="text-xs text-gray-500">2 days ago</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const AttendanceManagement = () => {
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [students, setStudents] = useState([]);
  const [attendance, setAttendance] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchClasses();
  }, []);

  useEffect(() => {
    if (selectedClass) {
      fetchStudents();
    }
  }, [selectedClass]);

  const fetchClasses = async () => {
    try {
      const response = await api.get(endpoints.teacherClasses);
      setClasses(response.data);
      if (response.data.length > 0) {
        setSelectedClass(response.data[0].class_name);
      }
    } catch (error) {
      console.error('Error fetching classes:', error);
    }
  };

  const fetchStudents = async () => {
    if (!selectedClass) return;
    
    setLoading(true);
    try {
      const response = await api.get(endpoints.classStudents(selectedClass));
      setStudents(response.data);
      
      // Initialize attendance state
      const initialAttendance = {};
      response.data.forEach(student => {
        initialAttendance[student.id] = 'present';
      });
      setAttendance(initialAttendance);
    } catch (error) {
      console.error('Error fetching students:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAttendanceChange = (studentId, status) => {
    setAttendance(prev => ({
      ...prev,
      [studentId]: status
    }));
  };

  const submitAttendance = async () => {
    try {
      const attendanceData = students.map(student => ({
        student_id: student.id,
        date: selectedDate,
        status: attendance[student.id] || 'present'
      }));

      await api.post(endpoints.bulkMarkAttendance, {
        attendance_records: attendanceData
      });

      alert('Attendance submitted successfully!');
    } catch (error) {
      console.error('Error submitting attendance:', error);
      alert('Error submitting attendance');
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Mark Attendance</h2>
        
        <div className="flex gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Class</label>
            <select
              value={selectedClass}
              onChange={(e) => setSelectedClass(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">Select Class</option>
              {classes.map((classData, index) => (
                <option key={index} value={classData.class_name}>
                  {classData.class_name} ({classData.student_count} students)
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
        </div>

        {loading ? (
          <div className="animate-pulse">Loading students...</div>
        ) : students.length > 0 ? (
          <div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Student
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Student ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Attendance
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {students.map((student) => (
                    <tr key={student.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {student.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {student.student_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex gap-4">
                          {['present', 'absent', 'late'].map((status) => (
                            <label key={status} className="flex items-center">
                              <input
                                type="radio"
                                name={`attendance-${student.id}`}
                                value={status}
                                checked={attendance[student.id] === status}
                                onChange={() => handleAttendanceChange(student.id, status)}
                                className="mr-2"
                              />
                              <span className="capitalize text-sm">{status}</span>
                            </label>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            <div className="mt-6">
              <button
                onClick={submitAttendance}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
              >
                Submit Attendance
              </button>
            </div>
          </div>
        ) : selectedClass ? (
          <p className="text-gray-500">No students found in this class.</p>
        ) : (
          <p className="text-gray-500">Please select a class to mark attendance.</p>
        )}
      </div>
    </div>
  );
};

const GradeManagement = () => {
  const [classes, setClasses] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [selectedClass, setSelectedClass] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');
  const [students, setStudents] = useState([]);
  const [gradeForm, setGradeForm] = useState({
    assignment_type: '',
    max_score: '',
    term: '',
    academic_year: '2024-2025'
  });
  const [grades, setGrades] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchClasses();
    fetchSubjects();
  }, []);

  useEffect(() => {
    if (selectedClass) {
      fetchStudents();
    }
  }, [selectedClass]);

  const fetchClasses = async () => {
    try {
      const response = await api.get(endpoints.teacherClasses);
      setClasses(response.data);
    } catch (error) {
      console.error('Error fetching classes:', error);
    }
  };

  const fetchSubjects = async () => {
    try {
      const response = await api.get(endpoints.teacherSubjects);
      setSubjects(response.data);
    } catch (error) {
      console.error('Error fetching subjects:', error);
    }
  };

  const fetchStudents = async () => {
    if (!selectedClass) return;
    
    setLoading(true);
    try {
      const response = await api.get(endpoints.classStudents(selectedClass));
      setStudents(response.data);
      
      // Initialize grades state
      const initialGrades = {};
      response.data.forEach(student => {
        initialGrades[student.id] = '';
      });
      setGrades(initialGrades);
    } catch (error) {
      console.error('Error fetching students:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGradeChange = (studentId, score) => {
    setGrades(prev => ({
      ...prev,
      [studentId]: score
    }));
  };

  const submitGrades = async () => {
    if (!selectedSubject || !gradeForm.assignment_type || !gradeForm.max_score || !gradeForm.term) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      const gradeData = students
        .filter(student => grades[student.id] !== '')
        .map(student => ({
          student_id: student.id,
          subject: selectedSubject,
          assignment_type: gradeForm.assignment_type,
          score: parseFloat(grades[student.id]),
          max_score: parseFloat(gradeForm.max_score),
          term: gradeForm.term,
          academic_year: gradeForm.academic_year
        }));

      if (gradeData.length === 0) {
        alert('Please enter at least one grade');
        return;
      }

      await api.post(endpoints.bulkCreateGrades, {
        grades: gradeData
      });

      alert('Grades submitted successfully!');
      setGrades({});
      setGradeForm({
        assignment_type: '',
        max_score: '',
        term: '',
        academic_year: '2024-2025'
      });
    } catch (error) {
      console.error('Error submitting grades:', error);
      alert('Error submitting grades');
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Record Grades</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Class</label>
            <select
              value={selectedClass}
              onChange={(e) => setSelectedClass(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">Select Class</option>
              {classes.map((classData, index) => (
                <option key={index} value={classData.class_name}>
                  {classData.class_name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Subject</label>
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">Select Subject</option>
              {subjects.map((subject, index) => (
                <option key={index} value={subject}>
                  {subject}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Assignment Type</label>
            <select
              value={gradeForm.assignment_type}
              onChange={(e) => setGradeForm(prev => ({ ...prev, assignment_type: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">Select Type</option>
              <option value="quiz">Quiz</option>
              <option value="test">Test</option>
              <option value="homework">Homework</option>
              <option value="project">Project</option>
              <option value="exam">Exam</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Max Score</label>
            <input
              type="number"
              value={gradeForm.max_score}
              onChange={(e) => setGradeForm(prev => ({ ...prev, max_score: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="100"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Term</label>
            <select
              value={gradeForm.term}
              onChange={(e) => setGradeForm(prev => ({ ...prev, term: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">Select Term</option>
              <option value="First Term">First Term</option>
              <option value="Second Term">Second Term</option>
              <option value="Third Term">Third Term</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Academic Year</label>
            <input
              type="text"
              value={gradeForm.academic_year}
              onChange={(e) => setGradeForm(prev => ({ ...prev, academic_year: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
        </div>

        {loading ? (
          <div className="animate-pulse">Loading students...</div>
        ) : students.length > 0 ? (
          <div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Student
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Student ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Score
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {students.map((student) => (
                    <tr key={student.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {student.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {student.student_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <input
                          type="number"
                          value={grades[student.id] || ''}
                          onChange={(e) => handleGradeChange(student.id, e.target.value)}
                          className="w-20 px-3 py-2 border border-gray-300 rounded-md"
                          placeholder="0"
                          min="0"
                          max={gradeForm.max_score || 100}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            <div className="mt-6">
              <button
                onClick={submitGrades}
                className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors"
              >
                Submit Grades
              </button>
            </div>
          </div>
        ) : selectedClass ? (
          <p className="text-gray-500">No students found in this class.</p>
        ) : (
          <p className="text-gray-500">Please select a class to record grades.</p>
        )}
      </div>
    </div>
  );
};

const MyStudents = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = async () => {
    try {
      const response = await api.get(endpoints.teacherStudents);
      setStudents(response.data);
    } catch (error) {
      console.error('Error fetching students:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse">Loading students...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">My Students</h2>
        
        {students.length === 0 ? (
          <p className="text-gray-500">No students assigned to your classes.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Student ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Class
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Grade Level
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {students.map((student) => (
                  <tr key={student.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {student.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {student.student_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {student.class_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {student.grade_level}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button className="text-blue-600 hover:text-blue-800 mr-3">
                        View Grades
                      </button>
                      <button className="text-green-600 hover:text-green-800">
                        View Attendance
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

function TeacherDashboard() {
  return (
    <div>
      <Routes>
        <Route path="/" element={<TeacherHome />} />
        <Route path="/attendance" element={<AttendanceManagement />} />
        <Route path="/grades" element={<GradeManagement />} />
        <Route path="/students" element={<MyStudents />} />
        <Route path="/class/:className/attendance" element={<AttendanceManagement />} />
        <Route path="/class/:className/grades" element={<GradeManagement />} />
      </Routes>
    </div>
  );
}

export default TeacherDashboard;