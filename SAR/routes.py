from flask import render_template, request, redirect, url_for, flash, abort, jsonify, Blueprint
from flask_login import login_required, current_user, login_user, logout_user
from models import Teacher, Student, Class, db
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = str(request.form["username"])
        password = str(request.form["password"])
        user = Teacher.query.filter_by(name=username).first()
        if user is not None and user.password == password:
            login_user(user, remember=True)
            return redirect(url_for("main.index"))
        else:
            flash("Invalid username or password.", "danger")
            return abort(401, description="Invalid username or password.")
    else:
        return render_template("login.html")

@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = str(request.form["username"])
        password = str(request.form["password"])
        existing_user = Teacher.query.filter_by(name=username).first()
        if existing_user is None:
            new_user = Teacher(name=username, password=password, subjects=[])
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for("main.index"))
        else:
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for("main.register"))
    else:
        return render_template("register.html")
    '''
    user_id = Teacher.query.filter_by(id="1").first()
    flash(user_id, "info")
    if user_id:
        return render_template("index.html")
    else:
        new_user = Teacher(name="admin", password="admin.1337", subjects=[])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("main.login"))
    '''
    
@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))

@main_bp.route("/students/view", methods=["GET"])
@login_required
def view_students():
    users = Student.query.all()
    return render_template("view_students.html", user=current_user, users=users)

@main_bp.route("/students/add", methods=['GET'])
@login_required
def add_students():
    if request.method == 'GET':
        users = Student.query.all()
        return render_template("add_student.html", user=current_user, users=users)
    
@main_bp.route("/student/attendance", methods=["GET"])
@login_required
def attendance():
    students = Student.query.all()
    class_ids = [i for i in range(1, 5)]
    return render_template("attendance.html", class_ids=class_ids, user=current_user, students=students)

@main_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        user = Teacher.query.filter_by(id=current_user.id).first()
        user.name = request.form["name"]
        db.session.commit()
        return redirect(url_for("index"))
    else:
        return render_template("edit_profile.html", user=current_user)
