from flask import Flask, url_for, redirect, render_template, request
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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

    student_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    student_major = db.Column(db.String(128))
    email = db.Column(db.String(128))
    id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @property
    def full_name(self):
        full_name = ' '.join([self.first_name, self.last_name])
        return full_name.strip()

    def __repr__(self):
        return '<Student %r>' % self.full_name, self.student_id

    def get_grades(self):
        return Grade.where(student_id=self.student_id)

class Assignment(db.Model):

    __tablename__= "assignment"

    assignment_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.String(128))
    due_date = db.Column(db.Date)
    points = db.Column(db.Integer)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))

    def __repr__(self):
        return '<Assignment %r>' % self.name

    def get_grades(self):
        return Grade.where(assignment_id=self.assignment_id)

class Grade(db.Model):

    __tablename__= "grade"

    pk = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.assignment_id'))
    points = db.Column(db.Integer)
    comment = db.Column(db.String(128))

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
    students = Student.query.all()
    assignments = Assignment.query.all()
    return render_template(
        "gradebook.html",
        assignment=assignments,
        student=students
    )

@app.route('/roster/', methods=["GET"])
@login_required
def roster():
    students = Student.query.all()
    return render_template('roster.html', students=students)


@app.route('/student/view/<int:student_id>/', methods=["GET"])
@login_required
def student_view(student_id):
    student = Student.query.filter_by(id=student_id).first()
    return render_template("student_view.html", student=student)


@app.route('/student/add_student/', methods=["GET", "POST"])
def add_student():
    if request.method == "GET":
        return render_template("add_student.html")
    elif request.method == "POST":
        student = Student(
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            student_major=request.form["student_major"],
            email=request.form["email"],
            id=request.form["id"],
        )
        db.session.add(student)
        db.session.commit()
        if "create_and_add" in request.form:
            return render_template('add_student.html')
        elif "create" in request.form:
            return redirect(url_for('student_view', student_id=student.student_id))

@app.route('/student/delete_student/<int:student_id>/', methods=["GET", "POST"])
def delete_student(student_id):
    student_id = Student.query.filter_by(id=student_id).first()
    if request.method == 'GET':
        return render_template('delete_student.html', student_id=student_id)
    if request.method == 'POST':
        db.session.delete(delete_student)
        db.session.commit()
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
