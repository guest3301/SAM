from flask import render_template, request, redirect, url_for, flash, abort, jsonify, Blueprint
from flask_login import login_required, current_user, login_user, logout_user
from models import Teacher, Student, Class, db
from datetime import datetime

admin = Blueprint('admin', __name__)

@admin.route("/admin-panel")
@login_required
def admin_panel():
    if current_user.id != 1:
        abort(403, description="You are not authorized to access this.")
    return render_template("admin_panel.html")

@admin.route('/create_class', methods=['POST'])
@login_required
def create_class():
    if current_user.id != 1:
        abort(403, description="You are not authorized to access this.")
    data = request.json
    class_id = data.get('class_id')
    class_name = data.get('class_name')
    if not class_id:
        return jsonify({"error": "Class ID is required"}), 400
    existing_class = Class.query.filter_by(id=class_id).first()
    if existing_class:
        return jsonify({"error": "Class already exists"}), 400
    new_class = Class(id=class_id, name=class_name, teacher_id=current_user.id)
    db.session.add(new_class)
    db.session.commit()
    return jsonify({"message": f"Class '{class_id}' created successfully"}), 201

@admin.route('/assign_class_to_teacher', methods=['POST'])
@login_required
def assign_class_to_teacher():
    if current_user.id != 1:
        abort(403, description="You are not authorized to access this.")
    data = request.json
    teacher_id = data.get('teacher_id')
    class_ids = data.get('class_ids')
    if not teacher_id or not class_ids:
        return jsonify({"error": "Teacher ID and Class IDs are required"}), 400
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"error": "Teacher not found"}), 404
    for class_id in class_ids:
        class_instance = Class.query.get(class_id)
        if class_instance:
            class_instance.teacher_id = teacher.id
    db.session.commit()
    return jsonify({"message": "Classes assigned to teacher successfully"}), 200

@admin.route('/add_subjects', methods=['POST'])
def add_subjects():
    if current_user.id != 1:
        abort(403, description="You are not authorized to access this.")
    data = request.json
    teacher_id = data.get('teacher_id')
    subjects = data.get('subjects')  # Should be a list of subjects
    teacher = Teacher.query.get(teacher_id)
    if teacher:
        teacher.subjects = subjects
        db.session.commit()
        return jsonify({'message': 'Subjects added successfully'}), 200
    return jsonify({'error': 'Teacher not found'}), 404

@admin.route('/create_teacher', methods=['POST'])
def create_teacher():
    if current_user.id != 1:
        abort(403, description="You are not authorized to access this.")
    data = request.json
    username = data.get('username')
    password = data.get('password') 
    existing_user = Teacher.query.filter_by(name=username).first()
    if existing_user is None:
        new_user = Teacher(name=username, password=password, subjects=[])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Teacher created successfully'}), 201
    else:
        return jsonify({'error': 'Username already exists'}), 400