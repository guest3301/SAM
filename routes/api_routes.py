from flask import jsonify, request, abort,flash, jsonify, Blueprint
from flask_login import login_required, current_user
from models import db, Student, Attendance, Class, Teacher
from datetime import datetime
import pytz, os
import openpyxl
from werkzeug.utils import secure_filename
from flask import current_app

import random
from datetime import timedelta

api_bp = Blueprint('api', __name__)

def validate_student_data(data):
    errors = []
    if not data.get('full_name'):
        errors.append("Full name is required")
    if not data.get('class_id') or not data.get('class_id').isdigit():
        errors.append("Class id must be a positive number")
    if not data.get('roll_no') or not data.get('roll_no').isdigit():
        errors.append("Roll no. must be a number")
    return errors

def format_date(date):
    if not date: return None
    return date.strptime('%Y-%m-%d')

def validate_date_string(date_string):
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        return None

ALLOWED_EXTENSIONS = {'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route("/api/add-students-bulk", methods=["POST"])
@login_required
def add_students_bulk():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        file.save(filepath)
        
        try:
            # Process the Excel file
            wb = openpyxl.load_workbook(filepath)
            sheet = wb.active
            students_added = []
            for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip the header row
                sr_no, roll_no, name = row
                if roll_no and name:  # Ensure there's data to process
                    new_student = Student(name=name, roll_no=roll_no, class_id=request.form['class_id'])
                    db.session.add(new_student)
                    students_added.append({"roll_no": roll_no, "name": name})

            db.session.commit()
            return jsonify({"success": True, "message": "Students added successfully", "students": students_added}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": str(e)}), 500
        finally:
            os.remove(filepath)  # Clean up uploaded file
    else:
        return jsonify({"success": False, "message": "Invalid file format"}), 400

@api_bp.route("/api/add-student", methods=["POST"])
@login_required
def add_student():
    try:
        data = request.get_json()
        errors = validate_student_data(data)
        if errors:
            return jsonify({'success': False, 'message': errors}), 400
        full_name = data["full_name"]
        class_id = data["class_id"]
        roll_no = data["roll_no"]
        new_student = Student(name=full_name, roll_no=roll_no, class_id=int(class_id))
        db.session.add(new_student)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@api_bp.route("/api/edit-student/<int:student_id>", methods=["POST"])
@login_required
def edit_student(student_id):
    data = request.get_json()
    student = Student.query.get(student_id)
    if student:
        student.name = data["name"]
        student.roll_no = data["roll_no"]
        student.class_id = data["class_id"]
        db.session.commit()
        return jsonify({"success": True, "message": "Student updated successfully.",
                            "data": {"id": student.id,"name": student.name, "roll_no": student.roll_no, "class_id": student.class_id}
                            }), 200
    return jsonify({"success": False, "message": "Student not found."}), 404

@api_bp.route("/api/delete-student/<int:student_id>", methods=["DELETE"])
@login_required
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify({"success": True, "message": "Student deleted successfully."}), 200
    return jsonify({"success": False, "message": "Student not found."}), 404

@api_bp.route("/api/students")
@login_required
def search_students():
    class_id = request.args.get("class_id")
    query = Student.query
    if class_id:
        query = query.filter_by(class_id=class_id)
    students = query.all()
    return jsonify({"students": [{"id": student.id, "name": student.name, "class_id": student.class_id, "roll_no": student.roll_no} for student in students]})

@api_bp.route("/attendance", methods=["GET"])
def get_attendance():
    date_str = request.args.get("date")
    class_id = request.args.get("class_id")
    subject = request.args.get("subject")
    if not date_str or not class_id or not subject:
        return jsonify({"error": "Date, subject & class are required"}), 400
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    attendance_records = Attendance.query.join(Student).filter(Attendance.date == date, Student.class_id == class_id, Attendance.subject == subject).all()
    if len(attendance_records) == 0:
        return jsonify("No records were found."), 404
    records = [{"id": record.student.id,"roll_no": record.student.roll_no, "name": record.student.name, "present": record.present} for record in attendance_records]
    return jsonify(records), 200

@api_bp.route("/api/attendance/students", methods=["GET"])
@login_required
def get_students_by_grade():
    class_id = request.args.get("class_id")
    students = Student.query.filter_by(class_id=class_id).all()
    if not students:
        return jsonify({"error": "No students found for the given class."}), 404
    current_date = datetime.now(pytz.timezone('Asia/Kolkata')).date()
    students_data = []
    for student in students:
        attendance_record = next((att for att in student.attendance_records if att.date == current_date), None)
        present_status = attendance_record.present if attendance_record else False
        students_data.append({"id": student.id, "roll_no": student.roll_no, "name": student.name, "present": present_status})
    return jsonify(students_data), 200

@api_bp.route('/api/attendance', methods=['POST'])
@login_required
def update_attendance():
    data = request.json
    class_id = data.get('class_id')
    attendance_data = data.get('attendance')
    subject = data.get('subject')
    if subject not in current_user.subjects:
        abort(403, description="You are not authorized to handle this subject.")

    assigned_class = Class.query.join(Teacher).filter(Class.id == class_id, Teacher.id == current_user.id).first()
    if not assigned_class:
        abort(403, description="You do not have permission to modify/view attendance for this class.")
    for record in attendance_data:
        student_id = record.get('student_id')
        present = record.get('present')
        note = record.get('note', f'{current_user.name} - {assigned_class.name}')
        student = Student.query.filter_by(id=student_id, class_id=class_id).first()
        if not student: continue
        existing_record = Attendance.query.filter_by(student_id=student.id, date=datetime.now(pytz.timezone('Asia/Kolkata')).date(),teacher_id=current_user.id,note=f'{current_user.name} - {assigned_class.name}', subject=subject).first()
        if existing_record is None:
            attendance = Attendance(student_id=student.id, date=datetime.now(pytz.timezone('Asia/Kolkata')).date(), present=present, note=note, teacher_id=current_user.id, subject=subject)
            db.session.add(attendance)
    db.session.commit()
    return jsonify({"message": "Attendance updated successfully"}), 200


@api_bp.route("/attendance/low-attendance", methods=["GET"])
@login_required
def get_low_attendance_students():
    class_id = request.args.get("class_id")
    subject = request.args.get("subject")
    year = request.args.get("year", datetime.now().year)
    month = request.args.get("month", datetime.now().month)
    
    if not class_id or not subject:
        return jsonify({"error": "Class ID and subject are required"}), 400
    
    if subject not in current_user.subjects:
        abort(403, description="You are not authorized to handle this subject.")

    assigned_class = Class.query.join(Teacher).filter(Class.id == class_id, Teacher.id == current_user.id).first()
    if not assigned_class:
        abort(403, description="You do not have permission to modify/view attendance for this class.")
    students = Student.query.filter_by(class_id=class_id).all()
    
    low_attendance_students = []
    
    for student in students:
        total_attendance_days = Attendance.query.filter(
            Attendance.student_id == student.id,
            Attendance.subject == subject,
            db.extract('year', Attendance.date) == year,
            db.extract('month', Attendance.date) == month
        ).count()

        present_days = Attendance.query.filter(
            Attendance.student_id == student.id,
            Attendance.present == True,
            Attendance.subject == subject,
            db.extract('year', Attendance.date) == year,
            db.extract('month', Attendance.date) == month
        ).count()
        
        if total_attendance_days > 0:
            attendance_percentage = (present_days / total_attendance_days) * 100
            if attendance_percentage < 50:
                low_attendance_students.append({
                    "id": student.id,
                    "roll_no": student.roll_no,
                    "name": student.name,
                    "attendance_percentage": attendance_percentage
                })

    return jsonify({"students": low_attendance_students}), 200


@api_bp.route("/attendance/populate-dummy", methods=["POST"])
@login_required
def populate_dummy_data():
    class_id = request.form.get("class_id")
    subject = request.form.get("subject")
    teacher_id = current_user.id
    days_in_month = int(request.form.get("days", 30))  # Defaults to 30 days

    if not class_id or not subject:
        return jsonify({"error": "Class ID and subject are required"}), 400
    students = Student.query.filter_by(class_id=class_id).all()
    
    try:
        for day_offset in range(days_in_month):
            date = datetime.now() - timedelta(days=(days_in_month - day_offset))

            for student in students:
                present = random.choice([True, False])  # Randomly decide if the student was present
                new_attendance = Attendance(
                    date=date.date(),
                    present=present,
                    subject=subject,
                    student_id=student.id,
                    teacher_id=teacher_id
                )
                db.session.add(new_attendance)
        
        db.session.commit()
        return jsonify({"success": True, "message": "Dummy data added successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

