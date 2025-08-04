from .user import User
from .student import Student
from .guardian import Guardian
from .teacher import Teacher
from .grade import Grade
from .attendance import Attendance
from .fee import Fee
from .notification import Notification
from .document import Document

# Import all models to ensure they are registered with SQLAlchemy
__all__ = [
    'User', 'Student', 'Guardian', 'Teacher', 
    'Grade', 'Attendance', 'Fee', 'Notification', 'Document'
]