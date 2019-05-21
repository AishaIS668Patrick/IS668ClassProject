from flask import Flask, url_for, redirect, render_template, request
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import current_user, login_required, login_user, LoginManager, logout_user, UserMixin
from werkzeug.security import check_password_hash
import logging

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

class Database(object):
    def __init__(self, database_name):
        self.database_name = database_name

    def execute(self, query, args=None, commit=False):
        cur = self.con.cursor()
        cur.execute(query, args or ())
        logging.debug(str(query) + "; " + str(args))
        if commit:
            self.con.commit()
        return cur

class Model(object):
    _table_name = None
    _default_order = None
    _column_names = None

    def __init__(self, **kwargs):
        for column in self._column_names + ['id']:
            setattr(self, column, kwargs.get(column))
        self._in_db = False

    def __repr__(self):
        return "<{0}: {1}>".format(self.__class__.__name__, self.id)

    @classmethod
    def _from_row(cls, row_dict):
        obj = cls(**row_dict)
        obj._in_db = True
        return obj

    @classmethod
    def get(cls, id=None):
        query = "SELECT * FROM {0} WHERE id=? LIMIT 1".format(cls._table_name)
        cur = db.execute(query, (id, ))
        row = cur.fetchone()
        obj = cls._from_row(row)
        return obj

    @classmethod
    def where(cls, **kwargs):
        items = kwargs.items()
        columns = [i[0] for i in items]
        values = [i[1] for i in items]
        conditions = '=? and '.join(columns) + '=?'
        query = "SELECT * FROM {0} WHERE {1}".format(cls._table_name,
                conditions)
        cur = db.execute(query, values)
        rows = cur.fetchall()
        objs = [cls._from_row(row) for row in rows]
        return objs

    @classmethod
    def all(cls, order=None):
        order = order or cls._default_order
        if order:
            query = "SELECT * FROM {0} ORDER BY {1} COLLATE NOCASE"
            query = query.format(cls._table_name, order)
        else:
            query = "SELECT * FROM {0}".format(cls._table_name)
        cur = db.execute(query)
        rows = cur.fetchall()
        objs = [cls._from_row(row) for row in rows]
        return objs

    def delete(self):
        if self._in_db:
            query = "DELETE FROM {0} WHERE id=?".format(
                    self.__class__._table_name)
            args = (self.id, )
        db.execute(query, args)

    def invisible_none(value):
        if value is None:
            return ''
        return value

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


    def save(self):
        if self._in_db:
            query = """UPDATE student SET first_name=?, last_name=?,
            student_major=?, email=?  WHERE id=?"""
            args = [self.first_name, self.last_name, self.student_major,
                    self.email, self.id]
            db.execute(query, args)
        else:
            query = """INSERT INTO student (first_name, last_name,
            student_major, email) VALUES (?, ?, ?, ?)"""
            args = [self.first_name, self.last_name, self.student_major,
                   self.email]
            cur = db.execute(query, args)
            self.id = cur.lastrowid

    def get_grades(self):
        return Grade.where(id=self.id)

class Assignment(db.Model):

    __tablename__= "assignment"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.String(128))
    due_date = db.Column(db.Date)
    points = db.Column(db.Integer)

    def __repr__(self):
        return "<{0}: {1}>".format(self.__class__.__name__, self.id)

    def get_grades(self):
        return Grade.where(assignment_id=self.id)

    def save(self):
        if self._in_db:
            query = """UPDATE assignment SET name=?, description=?,
            due_date=?, points=?, WHERE id=?"""
            args = [self.name, self.description, self.due_date, self.points,
                    self.id]
            db.execute(query, args)
        else:
            query = """INSERT INTO assignment (name, description, due_date,
            points) VALUES (?, ?, ?, ?)"""
            args = [self.name, self.description, self.due_date, self.points]
            cur = db.execute(query, args)
            self.id = cur.lastrowid

class Grade(db.Model):

    __tablename__= "grade"

    pk = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    points = db.Column(db.Integer)
    comment = db.Column(db.String(128))

    def save(self):
        if self._in_db:
            query = """UPDATE grade SET student_id=?, assignment_id=?,
            users_id=?, points=?, comment=? WHERE id=?"""
            args = [self.student_id, self.assignment_id, self.points,
                    self.comment, self.pk]
            db.execute(query, args)
        else:
            query = """INSERT INTO grade (student_id, assignment_id, users_id,
            points, comment)
            VALUES (?, ?, ?, ?, ?)"""
            args = [self.student_id, self.assignment_id, self.points,
            self.users_id, self.comment]
            cur = db.execute(query, args)
            self.pk = cur.lastrowid

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
        student=students)

@app.route('/roster/', methods=["GET"])
@login_required
def roster():
    students = Student.query.all()
    return render_template('roster.html', students=students)

@app.route('/add_student/', methods=["GET", "POST"])
def add_student():
    if request.method == "GET":
        return render_template("add_student.html")
    elif request.method == "POST":
        student = Student(
            id = request.form["id"],
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            student_major=request.form["student_major"],
            email=request.form["email"],
        )
        db.session.add(student)
        db.session.commit()
        if "create_and_add" in request.form:
            return render_template('add_student.html')
        elif "create" in request.form:
            return redirect(url_for('roster'))

@app.route('/roster/delete', methods=["POST"])
def delete():
    id = request.form.get("id")
    student = Student.query.filter_by(id=id).first()
    db.session.delete(student)
    db.session.commit()
    return redirect (url_for('roster'))
