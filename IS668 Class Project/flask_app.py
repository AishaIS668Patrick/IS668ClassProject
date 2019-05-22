from flask import Flask, url_for, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import date
from flask_login import current_user, login_required, login_user, LoginManager, logout_user, UserMixin
from werkzeug.security import check_password_hash

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="AishaIS668Patric",
    password="IS668ClassProject",
    hostname="AishaIS668Patrick.mysql.pythonanywhere-services.com",
    databasename="AishaIS668Patric$users",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config["SQLALCHEMY_POOL_RECYCLE"] = 280

app.secret_key = b'NotSecure'
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))
    class_id = db.Column(db.Integer)
    class_name = db.Column(db.String(128))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.username

class Student(db.Model):

    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    student_major = db.Column(db.String(128))
    email = db.Column(db.String(128))

    @property
    def full_name(self):
        full_name = ' '.join([self.first_name, self.last_name])
        return full_name.strip()

    def __repr__(self):
        return "<{0}: {1}>".format(self.__class__.__name__, self.id)

    def __init__(self, id, first_name, last_name, student_major, email):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.student_major = student_major
        self.email = email

class Assignment(db.Model):

    __tablename__= "assignment"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.String(128))
    due_date = db.Column(db.Date)
    points = db.Column(db.Integer)

    def __repr__(self):
        return "<{0}: {1}>".format(self.__class__.__name__, self.id)

    def __init__(self, id, name, description, due_date, points):
        self.id = id
        self.name = name
        self.description = description
        self.due_date = date
        self.points = points

class Grade(db.Model):

    __tablename__= "grade"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
    points = db.Column(db.Integer)
    comment = db.Column(db.String(128))
    student = db.relationship("Student", backref="grade")
    assignment = db.relationship("Assignment", backref="grade")

    def __repr__(self):
        return "<{0}: {1}>".format(self.__class__.__name__, self.id)

    def __init__(self, id, student_id, assignment_id, points, comment):
        self.id = id
        self.student_id = student_id
        self.assignment_id = assignment_id
        self.points = points
        self.comment = comment

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html")
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login_page.html", error=False)

    user = load_user(request.form["username"])
    if user is None:
       return render_template("login_page.html", error=True)

    if not user.check_password(request.form["password"]):
        return render_template("login_page.html", error=True)

    login_user(user)
    return redirect(url_for('index'))

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/gradebook/', methods=["GET"])
@login_required
def gradebook():
    user = User.query.all()
    assignments = Assignment.query.all()
    students = Student.query.all()
    grades = db.engine.execute("SELECT grade.id, grade.student_id, grade.points, student.first_name, student.last_name FROM grade, student WHERE grade.student_id = student.id;")
    return render_template('gradebook.html', students=students, assignments=assignments, user=user, grades=grades)

@app.route('/roster/', methods=["GET"])
@login_required
def roster():
    students = Student.query.all()
    return render_template('roster.html', students=students)

@app.route("/students/view/<int:student_id>")
@login_required
def student_view(student_id):
    student = Student.query.filter_by(id=student_id).first()
    grades = db.engine.execute("SELECT grade.id, grade.student_id, grade.points, student.first_name, student.last_name FROM grade, student WHERE grade.student_id = student.id;")
    return render_template("student_view.html", student=student, grades=grades)

@app.route("/assignments/view/<int:assignment_id>")
@login_required
def assignment_view(assignment_id):
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    return render_template("assignment_view.html", assignment=assignment)

@app.route('/assignments/')
@login_required
def assignments():
    assignments = Assignment.query.all()
    return render_template('assignment_list.html', assignments=assignments)

@app.route('/add_student/', methods=["GET", "POST"])
@login_required
def add_student():
    if request.method == "GET":
        return render_template("add_student.html")
    elif request.method == "POST":
        student = Student(
            id = request.form["id"],
            first_name = request.form["first_name"],
            last_name = request.form["last_name"],
            student_major = request.form["student_major"],
            email = request.form["email"],
        )
        db.session.add(student)
        db.session.commit()
        if "create_and_add" in request.form:
            return render_template('add_student.html')
        elif "create" in request.form:
            return redirect(url_for('roster'))

@app.route('/roster/delete', methods=["POST"])
@login_required
def delete():
    id = request.form.get("id")
    student = Student.query.filter_by(id=id).first()
    db.session.delete(student)
    db.session.commit()
    return redirect (url_for('roster'))

@app.route('/gradebook/update', methods=["POST"])
@login_required
def update():
    oldgrade = request.form.get("oldgrade")
    newgrade = request.form.get("newgrade")
    grades = Grade.query.filter_by(points=oldgrade).first()
    grades.points = newgrade
    db.session.commit()
    return redirect (url_for('gradebook'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
