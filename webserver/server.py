import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, flash

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

app.secret_key = os.environ.get("SECRET_KEY")

# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "wsh2117"
DB_PASSWORD = "Database2020!"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"

CURRENT_SEMESTER = "FA_2022"

# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
# engine.execute("""DROP TABLE IF EXISTS test;""")
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


@app.route('/')
def home():
  """
  request is a special object that Flask provides to access web request information:
  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  if not session.get('logged_in'):
    return render_template('login.html')

  return render_template("home.html")


@app.route('/schedule/')
def schedule():

<<<<<<< HEAD
  if not session.get('logged_in'):
    return render_template('login.html')

  cursor = g.conn.execute("SELECT Co.name as course_name, Co.course_id, P.name as professor_name, T.start_time, T.end_time, T.days_of_week, Cl.class_id \
                          FROM Class Cl, Registers R, Course Co, Professor P, Timeslot T  \
                          WHERE R.email = %s AND R.class_id = Cl.class_id AND Cl.professor_id = P.professor_id AND Cl.course_id = Co.course_id \
                            AND T.timeslot_id = Cl.timeslot_id", 
                          session['email'])
=======
  cursor = g.conn.execute("SELECT Co.name as course_name, Co.course_id, P.name as professor_name, T.start_time, T.end_time, T.days_of_week, Cl.class_id, S.semester_id \
                          FROM Class Cl, Registers R, Course Co, Professor P, Timeslot T, Semester S  \
                          WHERE R.email = %s AND R.class_id = Cl.class_id AND Cl.professor_id = P.professor_id AND \
                          Cl.course_id = Co.course_id AND S.semester_id=Cl.semester_id AND T.timeslot_id = Cl.timeslot_id", 
                          USER_ID)
>>>>>>> 1f0105d (Add registration status and semester information to class.)
  classes = []
  for result in cursor:
    classes.append(result)
  cursor.close()

  cursor = g.conn.execute("SELECT S.semester_id \
                          FROM Semester S")
  semesters=[]
  for result in cursor:
    semesters.append(result)
  cursor.close()

  context = dict(classes = classes, semesters=semesters)
  return render_template("schedule.html", **context)


@app.route('/class/<classID>/')
def classID(classID):

<<<<<<< HEAD
  if not session.get('logged_in'):
    return render_template('login.html')

  cursor = g.conn.execute("SELECT Co.name as course_name, Co.course_id, P.name as professor_name, T.start_time, T.end_time, T.days_of_week\
                          FROM Class Cl, Course Co, Professor P, Timeslot T \
                          WHERE Cl.class_id = %s AND Co.course_id = Cl.course_id AND Cl.professor_id = P.professor_id and T.timeslot_id = Cl.timeslot_id", int(classID))
=======
  cursor = g.conn.execute("SELECT Co.name as course_name, Co.course_id, P.name as professor_name, T.start_time, T.end_time, T.days_of_week, S.semester_id\
                          FROM Class Cl, Course Co, Professor P, Timeslot T, Semester S \
                          WHERE Cl.class_id = %s AND Co.course_id = Cl.course_id AND Cl.professor_id = P.professor_id AND \
                          T.timeslot_id = Cl.timeslot_id AND S.semester_id=Cl.semester_id", int(classID))
>>>>>>> 1f0105d (Add registration status and semester information to class.)

  classes = []
  for result in cursor:
    classes.append(result)

  cursor = g.conn.execute("SELECT S.email, S.first_name, S.last_name\
                          FROM Class Cl, Registers R, Student S, Befriends B \
                          WHERE Cl.class_id = %s AND R.class_id = Cl.class_id AND R.email = S.email AND ((R.email = B.email1 AND B.email2 = %s) OR \
                            (R.email = B.email2 AND B.email1 = %s))", classID, session['email'], session['email'])

  friends = []
  for result in cursor:
    friends.append(result)

  cursor = g.conn.execute("SELECT M.major_id, M.name, M.department\
                          FROM Class Cl, Course Co, Major M, Fulfills F \
                          WHERE Cl.class_id = %s AND Cl.course_id = Co.course_id AND Co.course_id = F.course_id AND F.major_id = M.major_id", classID)

  majors = []
  for result in cursor:
    majors.append(result)

  cursor = g.conn.execute("SELECT R.prerequisite\
                          FROM Requires R, Course Co, Class Cl \
                          WHERE Cl.class_id=%s AND Co.course_id=Cl.course_id AND R.dependent_course=Co.course_id", classID)
  prerequs=[]
  for result in cursor:
    prerequs.append(result)

  cursor = g.conn.execute("SELECT R.email, R.on_waitlist\
                          FROM Registers R, Class Cl \
                          WHERE Cl.class_id=%s AND R.email=%s AND R.class_id=Cl.class_id", classID, USER_ID)

  user_class_status=[]
  for result in cursor:
    user_class_status.append(result)


  context = dict(classes = classes, friends = friends, majors = majors, prerequs=prerequs, user_stat=user_class_status)

  return render_template("class.html", **context)


@app.route('/friends/')
def friends():

  if not session.get('logged_in'):
    return render_template('login.html')
  
  cursor = g.conn.execute("SELECT S.email, S.first_name, S.last_name, S.graduating_class FROM Befriends B, Student S WHERE B.email1 = %s AND S.email=B.email2", session['email'])
  names = []
  for result in cursor:
    names.append(result)
  cursor.close()

  context = dict(data = names)
  return render_template("friends.html", **context)


@app.route('/friend/<friendID>/')
def friendID(friendID):

  cursor = g.conn.execute("SELECT R.class_id FROM Registers R WHERE R.email=%s", friendID)
  friend_classes=[]
  for result in cursor:
    friend_classes.append(result)
  
  #print(friend_classes)

  cursor = g.conn.execute("SELECT Cl.class_id, Co.name as course_name, Co.course_id, P.name as professor_name, T.start_time, T.end_time, T.days_of_week, S.semester_id\
                          FROM Class Cl, Course Co, Professor P, Timeslot T, Registers R, Semester S\
                          WHERE R.email=%s AND R.class_id IN (SELECT R.class_id FROM Registers R WHERE R.email=%s) AND R.class_id=Cl.class_id \
                          AND Co.course_id = Cl.course_id AND Cl.professor_id = P.professor_id and T.timeslot_id = Cl.timeslot_id AND S.semester_id=Cl.semester_id \
                          ORDER BY S.semester_id DESC", 
                          USER_ID, friendID)

  classes = []
  for result in cursor:
    classes.append(result)

  print(classes)
  # cursor = g.conn.execute("SELECT S.first_name, S.last_name\
  #                         FROM Student S, Befriends B \
  #                         WHERE Cl.class_id = %s AND R.class_id = Cl.class_id AND R.email = S.email AND ((R.email = B.email1 AND B.email2 = %s) OR \
  #                           (R.email = B.email2 AND B.email1 = %s))", classId, USER_ID, USER_ID)

  cursor = g.conn.execute("SELECT S.first_name, S.last_name \
                          FROM Befriends B, Student S WHERE B.email1 = %s AND B.email2=%s AND S.email=B.email2", session['email'], friendID)
  friends = []
  for result in cursor:
    friends.append(result)

  print(friends)
  context = dict(classes = classes, friends = friends)

  return render_template("friend.html", **context)


@app.route('/majors/')
def majors():

  if not session.get('logged_in'):
    return render_template('login.html')
  
  cursor = g.conn.execute("SELECT M.name, M.department, M.major_id FROM Major M, Declares D WHERE D.email=%s", session['email'])
  names = []
  for result in cursor:
    names.append(result)
  cursor.close()

  context = dict(data = names)
  return render_template("majors.html", **context)


@app.route('/major/<majorID>/')
def majorID(majorID):

  if not session.get('logged_in'):
    return render_template('login.html')
  
  cursor = g.conn.execute("SELECT C.name, C.department, C.course_id FROM Course C, Fulfills F WHERE F.major_id=%s AND C.course_id=F.course_id", majorID)
  fufill_courses = []
  for result in cursor:
    fufill_courses.append(result)
  cursor.close()

  cursor = g.conn.execute("SELECT M.name, M.department, M.major_id FROM Major M WHERE M.major_id=%s", majorID)
  major_info = []
  for result in cursor:
    major_info.append(result)
  cursor.close()

  context = dict(search_major=major_info, courses = fufill_courses)
  return render_template("major.html", **context)


@app.route('/courses/')
def courses():

  if not session.get('logged_in'):
    return render_template('login.html')
  
  cursor = g.conn.execute("SELECT Co.name, Co.course_id, Co.department \
                          FROM Course Co")
  names = []
  for result in cursor:
    names.append(result)
  cursor.close()

  context = dict(data = names)
  return render_template("courses.html", **context)


@app.route('/course/<courseID>/')
def courseID(courseID):

  if not session.get('logged_in'):
    return render_template('login.html')
  
  cursor = g.conn.execute("SELECT Co.name as course_name, Co.course_id, P.name as professor_name, T.start_time, T.end_time, T.days_of_week, Cl.class_id\
                          FROM Class Cl, Course Co, Professor P, Timeslot T  \
                          WHERE Cl.semester_id = %s AND Cl.course_id=%s AND Cl.course_id = Co.course_id AND T.timeslot_id = Cl.timeslot_id AND P.professor_id = Cl.professor_id", CURRENT_SEMESTER, courseID)
  classes = []
  for result in cursor:
    classes.append(result)
  cursor.close()

  cursor = g.conn.execute("SELECT Co.course_id, Co.name as course_name \
                          FROM Course Co \
                          WHERE Co.course_id=%s", courseID)
  course = None
  for result in cursor:
    course = result
    break
  cursor.close()

  context = dict(classes = classes, course = course)
  return render_template("course.html", **context)


@app.route('/classes/')
def classes():

  if not session.get('logged_in'):
    return render_template('login.html')
  
  cursor = g.conn.execute("SELECT Cl.class_id, Co.name as course_name, Co.course_id, P.name as professor_name, T.start_time, T.end_time, T.days_of_week \
                          FROM Class Cl, Course Co, Professor P, Timeslot T\
                          WHERE Cl.semester_id = %s AND Cl.course_id = Co.course_id AND Cl.professor_id = P.professor_id AND Cl.timeslot_id = T.timeslot_id", CURRENT_SEMESTER)
  classes = []
  for result in cursor:
    classes.append(result)
  cursor.close()

  context = dict(data = classes, semester = CURRENT_SEMESTER)
  return render_template("classes.html", **context)


@app.route('/professors/')
def professors():

  if not session.get('logged_in'):
    return render_template('login.html')
  
  cursor = g.conn.execute("SELECT P.name, P.professor_id, P.department \
                          FROM Professor P")
  names = []
  for result in cursor:
    names.append(result)
  cursor.close()

  context = dict(data = names)
  return render_template("professors.html", **context)

@app.route('/professor/<professorID>/')
def professorID(professorID):

  if not session.get('logged_in'):
    return render_template('login.html')
  
  cursor = g.conn.execute("SELECT Co.name as course_name, Co.course_id, P.name as professor_name, T.start_time, T.end_time, T.days_of_week, Cl.class_id \
                          FROM Class Cl, Course Co, Professor P, Timeslot T  \
                          WHERE Cl.semester_id = %s AND P.professor_id=%s AND Cl.course_id = Co.course_id AND T.timeslot_id = Cl.timeslot_id AND P.professor_id = Cl.professor_id", CURRENT_SEMESTER, professorID)
  classes = []
  for result in cursor:
    classes.append(result)
  cursor.close()

  cursor = g.conn.execute("SELECT P.name, P.department \
                          FROM Professor P \
                          WHERE P.professor_id=%s", professorID)
  professor = None
  for result in cursor:
    professor = result
    break
  cursor.close()

  context = dict(classes = classes, professor = professor, semester = CURRENT_SEMESTER)
  return render_template("professor.html", **context)


# Example of adding new data to the database
@app.route('/add/', methods=['POST'])
def add():

  if not session.get('logged_in'):
    return render_template('login.html')

  name = request.form['name']
  print(name)
  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
  g.conn.execute(text(cmd), name1 = name, name2 = name);
  return redirect('/')


@app.route('/login/', methods=['POST'])
def do_admin_login():

  cursor = g.conn.execute("SELECT COUNT(*) as count\
                          FROM Student S \
                          WHERE S.email = %s", request.form['email'])

  for result in cursor:
    if result["count"] > 0:
      flash('You have logged in.')
      session['logged_in'] = True
      session['email'] = request.form['email']
      return home()
    else:
      flash('This login email does not exist')
      return home()
    
  flash('You are not logged in.')
  return home()


@app.route("/logout")
def logout():
  session['logged_in'] = False
  return home()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print("running on "+ str(HOST) +":"+ str(PORT)+"")
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()