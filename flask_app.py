from flask import Flask, url_for, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
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

app.secret_key = b'1234thwyvytnewkifdkim'
login_manager = LoginManager()
login_manager.init_app(app)

class Model(object):

    def __init__(self, **kwargs):
        for column in self._column_names + ['pk']:
            setattr(self, column, kwargs.get(column))
        self._in_db = False

    def __repr__(self):
        return "<{0}: {1}>".format(self.__class__.__name__, self.pk)

    @classmethod
    def _from_row(cls, row_dict):
        obj = cls(**row_dict)
        obj._in_db = True
        return obj

    @classmethod
    def get(cls, pk=None):
        query = "SELECT * FROM {0} WHERE pk=? LIMIT 1".format(cls._table_name)
        cur = db.execute(query, (pk, ))
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
            query = "DELETE FROM {0} WHERE pk=?".format(
                    self.__class__._table_name)
            args = (self.pk, )
        db.execute(query, args)

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

    pk = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    student_major = db.Column(db.String(128))
    email = db.Column(db.String(128))

    @property
    def full_name(self):
        full_name = ' '.join([self.first_name, self.last_name])
        return full_name.strip()

    def save(self):
        if self._in_db:
            query = """UPDATE student SET first_name=?, last_name=?, student_major=?,
            email=?  WHERE pk=?"""
            args = [self.first_name, self.last_name, self.student_major,
                    self.email, self.pk]
            db.execute(query, args)
        else:
            query = """INSERT INTO student (first_name, last_name, student_major,
            email) VALUES (?, ?, ?, ?, ?)"""
            args = [self.first_name, self.last_name, self.student_major,
                    self.email]
            cur = db.execute(query, args)
            self.pk = cur.lastrowid

    def get_grades(self):
        return Grade.where(student_pk=self.pk)

class Assignment(db.Model):

    __tablename__= "assignment"

    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.String(128))
    comment = db.Column(db.String(128))
    due_date = db.Column(db.String(128))
    points = db.Column(db.Integer)
    is_public = db.Column(db.Boolean)

    def save(self):
        if self._in_db:
            query = """UPDATE assignment SET name=?, description=?,
            due_date=?, points=?, comment=?, is_public=? WHERE pk=?"""
            args = [self.name, self.description, self.due_date, self.points,
                    self.comment, self.is_public, self.pk]
            db.execute(query, args)
        else:
            query = """INSERT INTO assignment (name, description, due_date,
            points, comment, is_public) VALUES (?, ?, ?, ?, ?, ?)"""
            args = [self.name, self.description, self.due_date, self.points,
                    self.comment, self.is_public]
            cur = db.execute(query, args)
            self.pk = cur.lastrowid

    def get_grades(self):
        return Grade.where(assignment_pk=self.pk)

class Grade(db.Model):

    __tablename__= "grade"

    pk = db.Column(db.Integer, primary_key=True)
    student_pk = db.Column(db.Integer)
    assignment_pk = db.Column(db.Integer)
    points = db.Column(db.Integer)
    comment = db.Column(db.String(128))

    def save(self):
        if self._in_db:
            query = """UPDATE grade SET student_pk=?, assignment_pk=?,
            points=?, comment=? WHERE pk=?"""
            args = [self.student_pk, self.assignment_pk, self.points,
                    self.comment, self.pk]
            db.execute(query, args)
        else:
            query = """INSERT INTO grade (student_pk, assignment_pk, points,
            comment) VALUES (?, ?, ?, ?)"""
            args = [self.student_pk, self.assignment_pk, self.points,
                    self.comment]
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

@app.route('/gradebook/')
def gradebook():
    students = Student.all()
    assignments = Assignment.all()
    assignment_pks = [a.pk for a in assignments]
    for student in students:
        grades = student.get_grades()
        by_assignment_pk = dict([(g.assignment_pk, g) for g in grades])
        student.grades = [by_assignment_pk.get(pk) for pk in assignment_pks]
    return render_template(
        "main_page.html",
        assignments=assignments,
        students=students
    )

@app.route('/students/')
def students():
    students = Student.all()
    return render_template('roster.html', students=students)


@app.route('/students/view/<int:student_pk>/')
def student_view(student_pk):
    student = Student.get(pk=student_pk)
    return render_template("student_view.html", student=student)


@app.route('/students/add_student/', methods=["GET", "POST"])
def add_student():
    if current_user.is_authenticated:
        if request.method == "GET":
            return render_template("add_student.html")
        elif request.method == "POST":
            student = Student(
                student_id=request.form['student_id'],
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                major=request.form['student_major'],
                email=request.form['email'],
            )
            student.save()
            if "create_and_add" in request.form:
                return render_template('add_student.html')
            elif "create" in request.form:
                return redirect(url_for('student_view', student_pk=student.pk))
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route('/students/update_student/<int:student_pk>/', methods=['GET', 'POST'])
def update_student(student_pk):
    student = Student.get(pk=student_pk)
    if request.method == 'GET':
        return render_template('update_student.html', student=student)
    elif request.method == 'POST':
        student.first_name = request.form['first_name']
        student.last_name = request.form['last_name']
        student.student_major = request.form['student_major']
        student.email = request.form['email']
        student.save()
        return redirect(url_for('student_view', student_pk=student_pk))


@app.route('/students/delete_student/<int:student_pk>/', methods=["GET", "POST"])
def delete_student(student_pk):
    student = Student.get(pk=student_pk)
    if request.method == 'GET':
        return render_template('delete_student.html', student=student)
    if request.method == 'POST':
        student.delete()
        return redirect(url_for('students'))


@app.route('/assignments/')
def assignments():
    assignments = Assignment.all()
    return render_template('assignment_list.html', assignments=assignments)


@app.route('/assignments/view/<int:assignment_pk>/')
def assignment_view(assignment_pk):
    assignment = Assignment.get(pk=assignment_pk)
    students = Student.all()
    grades = assignment.get_grades()
    g_by_student_pk = dict([(g.student_pk, g) for g in grades])
    for s in students:
        s.grade = g_by_student_pk.get(s.pk)
    return render_template(
        'assignment_view.html', assignment=assignment, students=students
    )

@app.route('/add_assignment/', methods=['GET', 'POST'])
def assignment_create():
    if request.method == 'GET':
        return render_template('add_assignment.html')
    elif request.method == 'POST':
        assignment = Assignment(
            name=request.form['name'],
            description=request.form['description'],
            comment=request.form['comment'],
            due_date=request.form['due_date'],
            points=request.form['points'],
            is_public=request.form.get('is_public', False, bool)
        )
        assignment.save()
        if "create_and_add" in request.form:
            return render_template('assignment_create.html')
        elif "create" in request.form:
            return redirect(
                url_for('assignment_view', assignment_pk=assignment.pk)
            )


@app.route('/update_assignment/<int:assignment_pk>/', methods=['GET', 'POST'])
def assignment_update(assignment_pk):
    assignment = Assignment.get(pk=assignment_pk)
    if request.method == 'GET':
        return render_template('update_assignment.html', assignment=assignment)
    elif request.method == 'POST':
        assignment.name = request.form['name']
        assignment.description = request.form['description']
        assignment.comment = request.form['comment']
        assignment.due_date = request.form['due_date']
        assignment.points = request.form['points']
        assignment.is_public = request.form.get('is_public', False, bool)
        assignment.save()
        return redirect(url_for('assignment_view', assignment_pk=assignment.pk))


@app.route('/delete_assignment/<int:assignment_pk>/', methods=['GET', 'POST'])
def assignment_delete(assignment_pk):
    assignment = Assignment.get(pk=assignment_pk)
    if request.method == 'GET':
        return render_template('delete_assignment.html', assignment=assignment)
    if request.method == 'POST':
        assignment.delete()
        return redirect(url_for('assignments'))


@app.route('/update_grade/<int:assignment_pk>/', methods=['GET', 'POST'])
def assignment_grades_update(assignment_pk):
    assignment = Assignment.get(pk=assignment_pk)
    students = Student.all()
    grades = assignment.get_grades()
    g_by_student_pk = dict([(grade.student_pk, grade) for grade in grades])
    for s in students:
        s.grade = g_by_student_pk.get(s.pk)

    if request.method == 'GET':
        return render_template(
            "update_grade.html",
            assignment=assignment,
            students=students
        )

    if request.method == 'POST':
        for student in students:
            points_key = "student_{0}_points".format(student.pk)
            comment_key = "student_{0}_comment".format(student.pk)
            try:
                points = request.form[points_key].strip()
                comment = request.form[comment_key].strip()
            except KeyError:
                continue
            try:
                points = int(points.strip())
            except ValueError:
                points = None
            comment = comment.strip()

            if student.grade is None:
                student.grade = Grade(
                    student_pk=student.pk,
                    assignment_pk=assignment.pk,
                    points=points,
                    comment=comment
                )
            else:
                student.grade.points = points
                student.grade.comment = comment
            student.grade.save()
        return redirect(url_for('assignment_view', assignment_pk=assignment_pk))


if __name__ == '__main__':
    app.run(debug=True)