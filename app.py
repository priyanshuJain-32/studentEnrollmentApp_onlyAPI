import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

from flask_restful import fields, marshal_with
from flask_restful import Resource, Api

from flask_cors import CORS
import jsonify
import json

current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "api_database.sqlite3")

# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///api_database.sqlite3"
CORS(app)
api.init_app(app)
db.init_app(app)
app.app_context().push()

class Course(db.Model):
	__tablename__ = 'course'
	course_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	course_name = db.Column(db.String, nullable = False)
	course_code = db.Column(db.String, unique = True, nullable = False)
	course_description = db.Column(db.String)

class Student(db.Model):
	__tablename__ = 'student'
	student_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	roll_number = db.Column(db.String, unique = True, nullable = False)
	first_name = db.Column(db.String, nullable = False)
	last_name = db.Column(db.String)

class Enrollment(db.Model):
	__tablename__ = 'enrollment'
	enrollment_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	estudent_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), primary_key = True, nullable = False)
	ecourse_id = db.Column(db.Integer, db.ForeignKey("course.course_id"), primary_key = True, nullable = False)

# ==============================Validation================================================
from werkzeug.exceptions import HTTPException
from flask import make_response

#-------------------------COURSE VALIDATIONS-------------------------------------------------------------
class CourseNotFoundError(HTTPException):
	def __init__(self, status_code):
		self.response = make_response('', status_code)

class CourseCodeAlreadyExistsError(HTTPException):
	def __init__(self, status_code):
		self.response = make_response('', status_code)

class CourseSuccessfullyUpdated(HTTPException):
	def __init__(self, _course_update,status_code):
		message = {"course_id": _course_update.course_id, "course_name":_course_update.course_name,
			"course_code":_course_update.course_code,"course_description":_course_update.course_description}
		self.response = make_response(json.dumps(message), status_code)

class CourseSuccessfullyCreated(HTTPException):
	def __init__(self, _course_created, status_code):
		message = {"course_id": _course_created.course_id, "course_name":_course_created.course_name,
			"course_code":_course_created.course_code,"course_description":_course_created.course_description}
		self.response = make_response(json.dumps(message), status_code)

#---------------------STUDENT VALIDATIONS-----------------------------------------------------------------
class StudentSuccessfullyUpdated(HTTPException):
	def __init__(self, _student_updated, status_code):
		message = {"student_id": _student_updated.student_id, "first_name":_student_updated.first_name,
			"last_name":_student_updated.last_name,"roll_number":_student_updated.roll_number}
		self.response = make_response(json.dumps(message), status_code)

class StudentSuccessfullyCreated(HTTPException):
	def __init__(self, _student_created, status_code):
		message = {"student_id": _student_created.student_id, "first_name":_student_created.first_name,
			"last_name":_student_created.last_name,"roll_number":_student_created.roll_number}
		self.response = make_response(json.dumps(message), status_code)

class StudentNotFoundError(HTTPException):
	def __init__(self, status_code):
		self.response = make_response('Student not found', status_code)

class StudentAlreadyExistsError(HTTPException):
	def __init__(self, status_code):
		self.response = make_response('Student already exist', status_code)

# -----------------------COMMON VALIDATIONS---------------------------------------------------------------
class BadRequest(HTTPException):
	def __init__(self, status_code, error_code, error_message):
		message = {"error_code": error_code, "error_message": error_message}
		self.response = make_response(json.dumps(message), status_code)

class SuccessfullyDeleted(HTTPException):
	def __init__(self, status_code):
		self.response = make_response({"status":"Successfully Deleted"}, status_code)

# -------------------------ENROLLMENT VALIDATIONS----------------------------------------------------------

class EnrollmentNotFound(HTTPException):
	def __init__(self, status_code):
		self.response = make_response({"status":"Enrollment for the student not found"}, status_code)

class EnrollmentSuccessfullyCreated(HTTPException):
	def __init__(self, _enrollment_created, status_code):
		message = {"enrollment_id": _enrollment_created.enrollment_id, "student_id":_enrollment_created.estudent_id,
			"course_id":_enrollment_created.ecourse_id}
		self.response = make_response(json.dumps(message), status_code)

class InvalidStudentORCourse(HTTPException):
	def __init__(self, status_code):
		self.response = make_response('Invalid Student Id or Course Id', status_code)

class InvalidStudent(HTTPException):
	def __init__(self, status_code):
		self.response = make_response('Invalid Student Id', status_code)

class StudentNotEnrolled(HTTPException):
	def __init__(self, status_code):
		self.response = make_response('Student is not enrolled in any course', status_code)
#=================================API's====================================================



course_output_fields = {
	"course_id" : fields.Integer,
	"course_name" : fields.String,
	"course_code" : fields.String,
	"course_description" : fields.String
}

# --------------------------------Course API's-----------------------------------------------

class CourseAPI(Resource):

# -----------------------------GET COURSE_ID------------------------------------------
	# @marshal_with(course_output_fields)
	def get(self, course_id):
		_course = db.session.query(Course).filter(Course.course_id == course_id).first()
		if _course:
			return { "course_id": _course.course_id, "course_name":_course.course_name,
			"course_code":_course.course_code,"course_description":_course.course_description, "status":"Request Successful" }, 200
		return {"status":"Course not found"}, 404

# ---------------------------PUT COURSE_ID------------------------------------------
	def put(self, course_id):
		_course = db.session.query(Course).filter(Course.course_id == course_id).first()
		if _course:
			_course_name = request.json['course_name']
			_course_code = request.json['course_code']
			if _course_name == None:
				return {"error_code": "COURSE001", "error_message":"Course Name is required", "status":"Bad Request"}, 400
			if _course_code == None:
				return {"error_code": "COURSE002", "error_message": "Course Code is required", "status":"Bad Request"}, 400
			_course_check = db.session.query(Course).filter(Course.course_code == _course_code).first()
			if _course_check.course_id == course_id:	
				_course.course_name = _course_name
				_course.course_code = _course_code
				_course.course_description = request.json['course_description']
				db.session.add(_course)
				db.session.commit()
				_course_update = db.session.query(Course).filter(Course.course_id == course_id).first()
				return {"status":"Successfully updated"}, 200
			else:
				return {"error_code": "COURSE002", "error_message": "Course Code is required", "status":"Bad Request"}, 400

		else:
			return {"status":"Course not found"}, 404

# ---------------------------DELETE COURSE_ID------------------------------------------
	def delete(self, course_id):
		_course = db.session.query(Course).filter(Course.course_id == course_id).first()
		if _course:
			db.session.delete(_course)
			db.session.commit()
			raise SuccessfullyDeleted(200)
		else:
			raise CourseNotFoundError(404)

# ---------------------------POST COURSE_ID------------------------------------------
	def post(self):
		_course_name = request.json['course_name']
		_course_code = request.json['course_code']
		if _course_name == None:
			raise BadRequest(status_code = 400,error_code= 'COURSE001',error_message= 'Course Name is required')
		if _course_code == None:
			raise BadRequest(status_code = 400,error_code= 'COURSE002',error_message= 'Course Code is required')
		_course_check = db.session.query(Course).filter(Course.course_code == _course_code).first()
		if not _course_check:
			_course = Course(course_id = None, course_name = _course_name, 
				course_code = _course_code, course_description=request.json["course_description"])
			db.session.add(_course)
			db.session.commit()
			_course_created = db.session.query(Course).filter(Course.course_code == _course_code).first() 
			raise CourseSuccessfullyCreated(_course_created ,201)				
		else:
			raise CourseCodeAlreadyExistsError(409)

api.add_resource(CourseAPI, "/api/course", "/api/course/<int:course_id>")
# ---------------------------END COURSE API CLASS------------------------------------------

# ===========================Student API's===========================================================

class StudentAPI(Resource):

# -------------------------------GET STUDENT API-----------------------------------------------------------------	
	def get(self, student_id):
		_student = db.session.query(Student).filter(Student.student_id == student_id).first()
		if _student:
			return { "student_id": _student.student_id, "first_name": _student.first_name,
			"last_name": _student.last_name,"roll_number": _student.roll_number }, 200
		raise StudentNotFoundError(404)

# -------------------------------PUT STUDENT API-----------------------------------------------------------------
	def put(self, student_id):
		_student = db.session.query(Student).filter(Student.student_id == student_id).first()
		if _student:
			_student_roll = request.json['roll_number']
			_student_name = request.json['first_name']
			if _student_roll == None:
				raise BadRequest(status_code = 400,error_code= 'STUDENT001',error_message= 'Roll Number required')
			if _student_name == None:
				raise BadRequest(status_code = 400,error_code= 'STUDENT002',error_message= 'First Name is required')
			_student_check = db.session.query(Student).filter(Student.roll_number == _student_roll).first()
			if _student_check.student_id==student_id:
				_student.roll_number = _student_roll
				_student.first_name = _student_name
				_student.last_name = request.json['last_name']
				db.session.add(_student)
				db.session.commit()
				_student_update = db.session.query(Student).filter(Student.student_id == student_id).first()
				raise StudentSuccessfullyUpdated(_student_update, 200)
			else:
				raise BadRequest(status_code = 400,error_code = 'STUDENT002',error_message= 'Roll Number is required')
		else:
			raise StudentNotFoundError(404)

# -------------------------------DELETE STUDENT API-----------------------------------------------------------------
	def delete(self, student_id):
		_student = db.session.query(Student).filter(Student.student_id == student_id).first()
		if _student:
			db.session.delete(_student)
			db.session.commit()
			raise SuccessfullyDeleted(200)
		else:
			raise StudentNotFoundError(404)

# ------------------------------------------POST STUDENT API-----------------------------------------------------------	
	def post(self):
		_student_roll = request.json['roll_number']
		_student_name = request.json['first_name']
		if _student_roll == None:
			raise BadRequest(status_code = 400,error_code= 'STUDENT001',error_message= 'Roll Number required')
		if _student_name == None:
			raise BadRequest(status_code = 400,error_code= 'STUDENT002',error_message= 'First Name is required')
		_student_check = db.session.query(Student).filter(Student.roll_number == _student_roll).first()
		if not _student_check:
			_student = Student(student_id = None, first_name = _student_name, 
				last_name = request.json["last_name"], roll_number = _student_roll)
			db.session.add(_student)
			db.session.commit()
			_student_created = db.session.query(Student).filter(Student.roll_number == _student_roll).first() 
			raise StudentSuccessfullyCreated(_student_created ,201)
		else:
			raise StudentAlreadyExistsError(409)

api.add_resource(StudentAPI, "/api/student" ,"/api/student/<int:student_id>")

# ----------------------------------------END STUDENT API -----------------------------------------------------


# ========================================ENROLLMENTS========================================================		

class StudentCourseAPI(Resource):

#----------------------------------------GET ENROLLMENTS API-------------------------------------------------------
	def get(self, student_id):
		_student = db.session.query(Student).filter(Student.student_id == student_id).first()
		if _student:
			_enrollment = db.session.query(Enrollment).filter(Enrollment.estudent_id==student_id).all()
			if _enrollment:
				returnlist = []
				for i in _enrollment:
					_enroll_details = {"enrollment_id":i.enrollment_id,"student_id":i.estudent_id,"course_id":i.ecourse_id}
					returnlist.append(_enroll_details)
				return returnlist, 200
			else:
				raise StudentNotEnrolled(404)
		else:
			raise InvalidStudent(400)
#----------------------------------------POST ENROLLMENTS API-------------------------------------------------------
	def post(self, student_id):
		_student = db.session.query(Student).filter(Student.student_id == student_id).first()
		if _student:
			_ecourse_id = request.json["course_id"]
			_course = db.session.query(Course).filter(Course.course_id == _ecourse_id).first()
			if _course:
				_enrollment = Enrollment(enrollment_id = None, estudent_id = student_id, ecourse_id = _ecourse_id)
				db.session.add(_enrollment)
				db.session.commit()
				_enrollment_created = db.session.query(Enrollment).filter(Enrollment.estudent_id==student_id,Enrollment.ecourse_id==_ecourse_id).first() 
				raise EnrollmentSuccessfullyCreated(_enrollment_created, 201)
			else:
				raise BadRequest(status_code = 400,error_code= 'ENROLLMENT001',error_message= 'Course does not exist')

		else:
			raise BadRequest(status_code = 400,error_code= 'ENROLLMENT002',error_message= 'Student does not exist')
#----------------------------------------DELETE ENROLLMENTS API-------------------------------------------------------
	def delete(self, student_id,course_id):
		_student = db.session.query(Student).filter(Student.student_id == student_id).first()
		_course = db.session.query(Course).filter(Course.course_id == course_id).first()
		_enrollment = db.session.query(Enrollment).filter(Enrollment.estudent_id==student_id,Enrollment.ecourse_id==course_id).first()
		if _student and _course:
			if _enrollment:
				db.session.delete(_enrollment)
				db.session.commit()
				raise SuccessfullyDeleted(200)
			else:
				raise EnrollmentNotFound(404)
		else:
			raise InvalidStudentORCourse(400)

api.add_resource(StudentCourseAPI, "/api/student/<int:student_id>/course" ,"/api/student/<int:student_id>/course/<int:course_id>")
#----------------------------------------END ENROLLMENTS API-------------------------------------------------------

if __name__=='__main__':
	app.run()