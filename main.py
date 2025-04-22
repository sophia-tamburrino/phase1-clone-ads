from flask import Flask, session, render_template, redirect, url_for, request
import sqlite3
import re, random, datetime

app = Flask('app')
app.debug = True
app.secret_key = "CHANGE ME"

# connection = sqlite3.connect("myDatabase.db")
# #connection.row_factory = sqlite3.Row
# cursor = connection.cursor()
# cursor.execute("SELECT * FROM students")
# data = cursor.fetchall()

@app.route('/', methods=['GET', 'POST'])
def login():
  # If the username/password is correct, log them in and redirect them to the home page. Remember to set your session variables! 
  # Else, give an error message and redirect them to the same login page 
  session.clear()
  username = 0
  if request.method == 'POST':
    #Establish connection 
    connection = sqlite3.connect("myDatabase.db")
    cursor = connection.cursor()

    #Choosing a random UID
    i = 0
    while i == 0:
        username = random.randint(10000000, 99999999)
        cursor.execute("SELECT * FROM users WHERE uid = " + str(username))
        data = cursor.fetchall()
        if not data:
          i = 1

    #Grabbing input form data 
    fname = request.form["fname"]
    lname = request.form["lname"]
    email = request.form["email"]
    address = request.form["address"]
    phd_or_masters = request.form["degree"]
    password = request.form["password"]

    #Throw error if anything is left blank
    if fname == "" or lname == "" or email == "" or address == "" or password == "":
      return render_template("createaccount.html", error = "Please do not leave any values blank!")
    
    #Insert values into gradstudents and users
    cursor.execute("INSERT INTO gradstudents VALUES (" + str(username) + ", \"" + fname + "\", \"" + lname + "\", \"" + email  + "\", \"" + address  + "\", \"" + phd_or_masters  + "\", 0, 0)")
    connection.commit()
    cursor.execute("INSERT INTO users VALUES (" + str(username) + ", \"" + password + "\", \"Student\")")
    connection.commit()
    return render_template("index.html", error = "Your new UID is " + str(username))
  return render_template("index.html", error = "")

@app.route('/createaccount', methods=['GET', 'POST'])
def createaccount():
  return render_template("createaccount.html")

@app.route('/home', methods=['GET', 'POST'])
def home():
  if request.method == 'POST':
    username = request.form["user"]
    password = request.form["pass"]
    print(username + " " + password)
    connection = sqlite3.connect("myDatabase.db")
    cursor = connection.cursor()
    if re.search('[a-zA-Z]', username):
      return render_template("index.html", error = "Please enter a number for the UID")
    cursor.execute("SELECT * FROM users WHERE uid  = " + username + " AND password = \"" + password + "\"")
    data = cursor.fetchall()
    if not data:
      return render_template("index.html", error = "This user is not in the database or the password is incorrect")
    else:
      print(data)
      session['username'] = username
      if data[0][2] == "Student":
        session['type_user'] = "Student"
        #Masters or PHD student?
        cursor.execute("SELECT enrollmentin_m_or_phd FROM gradstudents WHERE uid = " + str(session['username']))
        session['m_or_phd'] = cursor.fetchall()
        print(session['m_or_phd'][0][0])
        # FOR GPA CALCULATION
        cursor.execute("SELECT finalgrade, credithours FROM enrollment WHERE uid = " + str(session['username']))
        datagpa = cursor.fetchall()
        pts = 0
        hrs = 0
        grades_below_b = 0 #we will use this for suspension check
        for i in datagpa:
          val = 0.0
          if i[0] == "A":
            val = 4.0
          if i[0] == "A-":
            val = 3.7
          if i[0] == "B+":
            val = 3.3
          if i[0] == "B":
            val = 3.0
          if i[0] == "B-":
            val = 2.7
          if i[0] == "C+":
            val = 2.3
          if i[0] == "C":
            val = 2.0
          if i[0] == "C-":
            val = 1.7
          if i[0] == "D+":
            val = 1.3
          if i[0] == "D":
            val = 1.0
          #FOR SUSPENSION CHECK
          if val < 3.0:
            grades_below_b += 1
          pts += val*i[1]
          hrs += i[1]
        session['gpa'] = pts/hrs
        session['credithrs'] = hrs

        #SUSPENSION CHECK DETERMINATION
        if grades_below_b >= 3:
          cursor.execute("UPDATE gradstudents SET suspensioncheck = 1 WHERE uid = ?", (username,))
          connection.commit()
          return render_template("index.html", error = "This student has been placed under academic probation due to having three or more grades below B.")

      if data[0][2] == "Alumni":
        session['type_user'] = "Alumni"
      if data[0][2] == "Faculty Advisor":
        session['type_user'] = "Faculty Advisor"
      if data[0][2] == "Graduate Secretary":
        session['type_user'] = "Graduate Secretary"
      if data[0][2] == "Systems Administration":
        session['type_user'] = "Systems Administration"
      
      cursor.execute("SELECT * FROM enrollment WHERE uid = " + session['username'])
      session['enrollment'] = cursor.fetchall()
      cursor.execute("SELECT * FROM course_catalog")
      session['courses'] = cursor.fetchall()

      return render_template("home.html")
  # Display the correct information for a logged in user 
  return render_template("home.html")

@app.route('/form1', methods=['GET', 'POST'])
def form1():
  connection = sqlite3.connect("myDatabase.db")
  cursor = connection.cursor()
  cursor.execute("SELECT * FROM course_catalog")
  data = cursor.fetchall()
  session['courses'] = data
  return render_template("form1.html", error = "")

# Submitted form 1 page responses
# Thoughts: Use session variable to check PHD/Masters.
# Insert the data into form1 table. See if array  works. If not, create another table for form1 approvals and have an id. 
@app.route('/form1_submit', methods=['GET', 'POST'])
def form1_submit():
  # Grab user data for extra session variables. Might wanan move this to login so we dont have to repeat the process?
  connection = sqlite3.connect("myDatabase.db")
  cursor = connection.cursor()
  cursor.execute("SELECT * FROM course_catalog")
  data = cursor.fetchall()
  cursor.execute("SELECT * FROM gradstudents WHERE uid = " + str(session['username']))
  userdata = cursor.fetchall()
  session['fname'] = userdata[0][1]
  session['lname'] = userdata[0][2]
  session['grad-type'] = userdata[0][5]

  if request.method == 'POST':
    #Restrictions: No more than 12 courses, cannot be in courses user has already taken
    courses = []
    for i in data:
        print("" + i[0] + " " + str(i[1]))
        if request.form.get(i[0] + " " + str(i[1])) != None:
            # adds 2 non cs courses
            courses.append(i[0] + " " + str(i[1]))
    print(courses)
    if len(courses) > 12:
       return render_template("form1.html", error = "You cannot enter more than 12 courses!")
    
    if session['grad-type'] == "MS":
      # These are all CS courses so it is okay
      courses_to_grad = ["CSCI 6212", "CSCI 6221", "CSCI 6461"]
      for i in courses_to_grad:
        if i not in courses:
          return render_template("form1.html", error = "You have not selected a required course for MS graduation.")
        
    cursor.execute("SELECT * FROM form1 WHERE uid = " + str(session['username']))
    data1 = cursor.fetchall()
    if data1:
      cursor.execute("SELECT approved FROM form1_approval WHERE uid = " + str(session['username']))
      data2 = cursor.fetchall()
      if data2[0][0] == 1:
        return render_template("form1.html", error = "Your Form1 was already accepted!")
      return render_template("form1.html", error = "You have already submitted a Form 1. Please wait for approval or rejection from Faculty Advisor.")
    
    # Grab most recent formnum and increment it by 1
    cursor.execute("SELECT formnum FROM form1 ORDER BY formnum DESC")
    formdata = cursor.fetchall()
    value = 0
    if formdata:
      value = formdata[0][0] + 1
    
    # Insert remaining values into form1
    for i in courses:
        connection1 = sqlite3.connect("myDatabase.db")
        cursor1 = connection1.cursor()
        newi = i.split()
        cursor1.execute("INSERT INTO form1 VALUES (" + str(session['username']) + ", " + str(value)+ ", \"" + session['fname'] + "\", \"" + session['lname'] + "\", \"" + str(session['grad-type']) + "\", \"" + str(newi[0]) +"\", " + str(newi[1]) + ")")
        connection1.commit()
        connection1.close()
    cursor.execute("INSERT INTO form1_approval VALUES (" + str(value) + ", " + str(session['username']) + ", 0)")
    connection.commit()
    connection.close()

  return render_template("form1_submit.html")

# For advisor to find student they advise
@app.route('/form1_review', methods=['GET', 'POST'])
def form1_review():
  connection = sqlite3.connect("myDatabase.db")
  cursor = connection.cursor()
  if session["type_user"] == "Systems Administration":
    cursor.execute("SELECT studentuid FROM advisor_student")
  else:
    cursor.execute("SELECT studentuid FROM advisor_student WHERE advisoruid = " + str(session['username']))
  session['students'] = cursor.fetchall()
  return render_template("form1_review.html")

# For viewing and accepting student's form1.
@app.route('/form1_student_page', methods=['GET', 'POST'])
def form1_student_page():
  if request.method == 'POST':
    connection = sqlite3.connect("myDatabase.db")
    cursor = connection.cursor()
    the_student = request.form["selectstu"]
    cursor.execute("SELECT * FROM form1 LEFT JOIN course_catalog ON form1.coursenumber = course_catalog.coursenumber AND form1.coursetype = course_catalog.dept WHERE form1.uid = " + str(the_student))
    session['form1'] = cursor.fetchall()
    if not session['form1']:
      return render_template("form1_error.html")
    print(session['form1'])
    return render_template("form1_student_page.html")
  return render_template("form1_student_page.html")

# If user has no form 1
@app.route('/form1_error', methods=['GET', 'POST'])
def form1_error():
  return render_template("form1_error.html")

# For viewing and accepting student's form1.
@app.route('/form1_accepted', methods=['GET', 'POST'])
def form1_accepted():
  if request.method == 'POST':
    session['form1-status'] = request.form['accrej']
    connection = sqlite3.connect("myDatabase.db")
    cursor = connection.cursor()
    if session['form1-status'] == "accept":
      session['form1-status'] = "Accepted"
      cursor.execute("UPDATE form1_approval SET approved = ? WHERE uid = ?", (1, session['form1'][0][0]))
      connection.commit()
    else:
      session['form1-status'] = "Rejected"
      cursor.execute("DELETE FROM form1 WHERE uid = " + str(session['form1'][0][0]))
      cursor.execute("DELETE FROM form1_approval WHERE uid = " + str(session['form1'][0][0]))
      connection.commit()
    connection.close()
  return render_template("form1_accepted.html")

@app.route('/personalinfo')
def personalinfo():
  username= session.get('username')
  if not username:
    return redirect(url_for('index'))
  
  edit_mode = request.args.get('edit', 'false').lower() == 'true'

  connection = sqlite3.connect("myDatabase.db")
  connection.row_factory = sqlite3.Row
  cursor = connection.cursor()

  cursor.execute("SELECT * FROM users WHERE uid= ?", (username,))
  data = cursor.fetchall()


  if data[0][2] == "Student":
    cursor.execute("SELECT * FROM gradstudents WHERE uid = ?", (username,))
    info = cursor.fetchone()
  if data[0][2] == "Alumni":
    cursor.execute("SELECT * FROM alumni WHERE uid = ?", (username,))
    info = cursor.fetchone()
  if data[0][2] == "Faculty Advisor":
    cursor.execute("SELECT * FROM facultyadvisor WHERE uid = ?", (username,))
    info = cursor.fetchone()
  if data[0][2] == "Graduate Secretary":
    cursor.execute("SELECT * FROM gradsecretary WHERE uid= ?", (username,))
    info = cursor.fetchone()
#ADD SYSTEMS ADMIN HERE? (may have to include personal info for systems admin in scheme then)

  connection.close()

  if not info:
    return redirect(url_for('index'))

  return render_template("personalinfo.html", info=dict(info), edit_mode=edit_mode)

@app.route('/update_personalinfo', methods={'POST'})
def update_personalinfo():
  username= session.get('username')
  if not username:
    return redirect(url_for('index'))
  
  try:
    fname= request.form.get('fname', '').strip()
    lname = request.form.get('lname', '').strip()

    
    email = request.form.get('email', '').strip()
    address = request.form.get('address', '').strip()

    connection = sqlite3.connect("myDatabase.db")
    cursor = connection.cursor()

    cursor.execute("SELECT typeid FROM users WHERE uid=?", (username,))
    user_type = cursor.fetchone()[0]

    if user_type =="Student":
      cursor.execute("""UPDATE gradstudents SET fname=?, lname=?, email=?, address=? WHERE uid=?""", (fname, lname, email, address, username) )

    elif user_type == "Alumni":
      cursor.execute("""UPDATE alumni SET fname=?, lname=?, email=?, address=? WHERE uid=?""", (fname, lname, email, address, username) )

    elif user_type == "Faculty Advisor":
      cursor.execute("""UPDATE facultyadvisor SET fname=?, lname=? WHERE uid=?""", (fname, lname, username) )

    connection.commit()
    connection.close()

    return redirect(url_for('personalinfo'))
  
  except sqlite3.Error as e:
    print(f"Database error: {e}")
    if 'connection' in locals():
      connection.close()
    return redirect(url_for('personalinfo'))
  except Exception as e:
    print(f"Unexpected error:{e}")
    if 'connection' in locals():
      connection.close()
    return redirect(url_for('personalinfo'))
  
# For thesis approval
@app.route('/thesis_approval', methods=['GET', 'POST'])
def thesis_approval():
  connection = sqlite3.connect("myDatabase.db")
  cursor = connection.cursor()
  if session['type_user'] ==  "Systems Administration":
    cursor.execute("SELECT studentuid FROM advisor_student LEFT JOIN gradstudents ON gradstudents.uid = advisor_student.studentuid WHERE gradstudents.enrollmentin_m_or_phd = \"PhD\"")
  else:
    cursor.execute("SELECT studentuid FROM advisor_student LEFT JOIN gradstudents ON gradstudents.uid = advisor_student.studentuid WHERE advisor_student.advisoruid = " + str(session['username']) + " AND gradstudents.enrollmentin_m_or_phd = \"PhD\"")
  session['phd_students'] = cursor.fetchall()
  return render_template("thesis_approval.html")

# For thesis approval CONTINUED
@app.route('/approve', methods=['GET', 'POST'])
def approve():
  if request.method == 'POST':
    session['phd'] = request.form['selectphd']
    connection = sqlite3.connect("myDatabase.db")
    cursor = connection.cursor()
    cursor.execute("SELECT thesisapproval FROM advisor_student WHERE studentuid = " + str(session['phd']))
    data = cursor.fetchall()
    session['approval_status'] = ""
    if data[0][0] == 0:
      session['approval_status'] = "Not Approved"
    else:
      session['approval_status'] = "Approved"
  return render_template("approve.html")

# For thesis approval CONTINUED
@app.route('/approved_final', methods=['GET', 'POST'])
def approved_final():
  if request.method == 'POST':
    connection = sqlite3.connect("myDatabase.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE advisor_student SET thesisapproval = ? WHERE studentuid = ?", (1, session['phd']))
    connection.commit()
    connection.close()
  return render_template("approved_final.html")

# VIEW TRANSCRIPT
@app.route('/view_transcript', methods=['GET', 'POST'])
def view_transcript():
  connection = sqlite3.connect("myDatabase.db")
  cursor = connection.cursor()
  if session['type_user'] ==  "Systems Administration":
    cursor.execute("SELECT studentuid FROM advisor_student")
  else:
    cursor.execute("SELECT studentuid FROM advisor_student WHERE advisoruid = " + str(session['username']))
  session['students'] = cursor.fetchall()
  return render_template("view_transcript.html")

# VIEW TRANSCRIPT
@app.route('/student_transcript', methods=['GET', 'POST'])
def student_transcript():
  if request.method == 'POST':
    session['transcript_student'] = request.form['transcript']
    connection = sqlite3.connect("myDatabase.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM enrollment LEFT JOIN course_catalog ON enrollment.coursenumber = course_catalog.coursenumber WHERE uid = " + str(session['transcript_student']))
    session['transcript'] = cursor.fetchall()
    print(session['transcript'])
  return render_template("student_transcript.html")

# Faculty Assign
@app.route('/faculty_assign', methods=['GET', 'POST'])
def faculty_assign():
  connection = sqlite3.connect("myDatabase.db")
  cursor = connection.cursor()
  cursor.execute("SELECT studentuid FROM advisor_student")
  advised_students = cursor.fetchall()
  cursor.execute("SELECT * FROM gradstudents")
  all_students = cursor.fetchall()
  unadvised_students = []
  for i in all_students:
    advised = 0
    for j in advised_students:
      if i[0] == j[0]:
        advised = 1
        break
    if advised == 0:
      unadvised_students.append(i)
  session['unadvised_students'] = unadvised_students
  return render_template("faculty_assign.html")

#faculty_assign_student
@app.route('/faculty_assign_student', methods=['GET', 'POST'])
def faculty_assign_student():
  if request.method == 'POST':
    #MEOW
    session['the_student'] = request.form['advisor']
    connection = sqlite3.connect("myDatabase.db")
    cursor = connection.cursor()
    cursor.execute("SELECT uid FROM users WHERE typeid = \"Faculty Advisor\"")
    session['advisors'] = cursor.fetchall()
  return render_template("faculty_assign_student.html")

#assigned_advisor
@app.route('/assigned_advisor', methods=['GET', 'POST'])
def assigned_advisor():
  if request.method == 'POST':
    #MEOW
    advisor = request.form['chooseadv']
    connection = sqlite3.connect("myDatabase.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO advisor_student VALUES (" + str(advisor) + ", " + str(session['the_student']) + ", 0)")
    connection.commit()
    connection.close()
  return render_template("assigned_advisor.html")

#GRADUATION APPLICATION
@app.route('/graduation_app', methods=['GET', 'POST'])
def graduation_app():
  return render_template("graduation_app.html")

#GRADUATION RESULT / AUDIT
@app.route('/graduation_result', methods=['GET', 'POST'])
def graduation_result():
  # CALCULATE GPA
  if request.method == 'POST':
    connection = sqlite3.connect("myDatabase.db")
    cursor = connection.cursor()

    # MASTERS DEGREE AUDIT
    if session['m_or_phd'][0][0] == "MS":
      # Form 1 should alr have required courses.
      print(session['gpa']) # WORKS YASS PERIOD!!!
      if session['gpa'] < 3.0:
        return render_template("graduation_result.html", error = "GPA under minimum requirement.")
      if session['credithrs'] < 30:
        return render_template("graduation_result.html", error = "Credit hours under minimum requirement.")
      
      # Did they fill out the Form1?
      cursor.execute("SELECT * FROM form1_approval WHERE uid = " + str(session['username']))
      data1 = cursor.fetchall()
      if not data1:
        return render_template("graduation_result.html", error = "You have not filled out the required Form 1.")
   
      # First check to see if the user's form1 was approved
      if data1[0][2] == 0:
        return render_template("graduation_result.html", error = "Your Form1 was not yet approved by your faculty advisor.")
    
      # Check to see if courses on user's form1 match courses they have already taken 
      cursor.execute("SELECT coursenumber, coursetype FROM form1 WHERE uid = " + str(session['username']))
      form1_data = cursor.fetchall()
      cursor.execute("SELECT coursenumber, coursetype FROM enrollment WHERE uid = " + str(session['username']))
      enroll_data = cursor.fetchall()
      for i in enroll_data:
        in_data = 0
        print(i)
        for j in form1_data:
          print(j)
          if i[0] == j[0] and i[1] == j[1]:
            in_data = 1
            break
        if in_data == 0:
          return render_template("graduation_result.html", error = "Your Form1 does not match your enrolled courses.")
     
      # See if 2 courses are outside CS department
      cursor.execute("SELECT coursetype FROM enrollment WHERE coursetype != \"CSCI\" AND uid = " + str(session['username']))
      not_cs = cursor.fetchall()

      if not not_cs:
        return render_template("graduation_result.html", error = "You do not have at least 2 non-cs courses.")
      if len(not_cs) < 2:
        return render_template("graduation_result.html", error = "You do not have at least 2 non-cs courses.")
     
      # No more than 2 grades below B
      cursor.execute("SELECT finalgrade FROM enrollment WHERE finalgrade != \"A\" AND finalgrade != \"A-\" AND finalgrade != \"B+\" AND finalgrade != \"B\" AND uid = " + str(session['username']))
      all_grades = cursor.fetchall()
      if all_grades:
        if len(all_grades) > 2:
          return render_template("graduation_result.html", error = "You have more than 2 grades below B.")
      
      #Else, approve for graduation
      cursor.execute("UPDATE gradstudents SET appliedforgrad = 1 WHERE uid = " + session['username'])
      connection.commit()
      return render_template("graduation_result.html", error = "Passed the audit for graduation!")
    
    # PHD DEGREE AUDIT
    if session['m_or_phd'][0][0] == "PhD":
      #GPA check
      if session['gpa'] < 3.5:
        return render_template("graduation_result.html", error = "GPA under minimum requirement.")
      
      # Credir hr and cs hr check
      if session['credithrs'] < 36:
        return render_template("graduation_result.html", error = "Credit hours under minimum requirement.")
      cursor.execute("SELECT sum(credithours) FROM enrollment WHERE coursetype = \"CSCI\" AND uid = " + str(session['username']))
      cs_hrs = cursor.fetchall()
      if cs_hrs[0][0] < 30:
        return render_template("graduation_result.html", error = "CSCI credit hours under minimum requirement.")
      
      # No more than one grade below B
      cursor.execute("SELECT finalgrade FROM enrollment WHERE finalgrade != \"A\" AND finalgrade != \"A-\" AND finalgrade != \"B+\" AND finalgrade != \"B\" AND uid = " + str(session['username']))
      all_grades = cursor.fetchall()
      if all_grades:
        if len(all_grades) > 1:
          return render_template("graduation_result.html", error = "You have more than 1 grade below B.")
      
      # Did they fill out the Form1?
      cursor.execute("SELECT * FROM form1_approval WHERE uid = " + str(session['username']))
      data1 = cursor.fetchall()
      if not data1:
        return render_template("graduation_result.html", error = "You have not filled out the required Form 1.")
   
      # First check to see if the user's form1 was approved
      if data1[0][2] == 0:
        return render_template("graduation_result.html", error = "Your Form1 was not yet approved by your faculty advisor.")
    
      # Check to see if courses on user's form1 match courses they have already taken 
      cursor.execute("SELECT coursenumber, coursetype FROM form1 WHERE uid = " + str(session['username']))
      form1_data = cursor.fetchall()
      cursor.execute("SELECT coursenumber, coursetype FROM enrollment WHERE uid = " + str(session['username']))
      enroll_data = cursor.fetchall()
      for i in enroll_data:
        in_data = 0
        print(i)
        for j in form1_data:
          print(j)
          if i[0] == j[0] and i[1] == j[1]:
            in_data = 1
            break
        if in_data == 0:
          return render_template("graduation_result.html", error = "Your Form1 does not match your enrolled courses.")
      
      # Did they pass their thesis?
      cursor.execute("SELECT thesisapproval FROM advisor_student WHERE studentuid = " + str(session['username']))
      thesis = cursor.fetchall()
      if thesis[0][0] == 0:
        return render_template("graduation_result.html", error = "Your thesis was not approved.")
      #Else, approve for graduation
      cursor.execute("UPDATE gradstudents SET appliedforgrad = ? WHERE uid = ?", (1, str(session['username'])))
      connection.commit()
      return render_template("graduation_result.html", error = "Passed the audit for graduation!")

  return render_template("graduation_result.html")

# GRADUATE STUDENT
@app.route('/graduate_student', methods=['GET', 'POST'])
def graduate_student():
  connection = sqlite3.connect("myDatabase.db")
  cursor = connection.cursor()
  cursor.execute("SELECT * FROM gradstudents WHERE appliedforgrad = 1")
  session['graduate'] = cursor.fetchall()
  return render_template("graduate_student.html")

# GRADUATE STUDENT
@app.route('/graduated', methods=['GET', 'POST'])
def graduated():
  if request.method == 'POST':
    session['newalum'] = request.form['graduate']
    connection = sqlite3.connect("myDatabase.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM gradstudents WHERE uid = " + str(session['newalum']))
    alum_info = cursor.fetchall()
    cursor.execute("INSERT INTO alumni VALUES (" + str(session['newalum']) + ", \"" + str(alum_info[0][1]) + "\", \"" + str(alum_info[0][2]) + "\", \"" + str(alum_info[0][3]) + "\", \"" + str(alum_info[0][4]) + "\", \"" + str(alum_info[0][5]) + " in 2025\")")
    connection.commit()
    cursor.execute("DELETE FROM gradstudents WHERE uid = " + session['newalum'])
    connection.commit()
    cursor.execute("UPDATE users SET typeid = \"Alumni\" WHERE uid = " + str(session['newalum']))
    connection.commit()
  return render_template("graduated.html")

# ACCESS STUDENT DATA
@app.route('/student_data', methods=['GET', 'POST'])
def student_data():
  connection = sqlite3.connect("myDatabase.db")
  cursor = connection.cursor()
  cursor.execute("SELECT * FROM gradstudents")
  session['studata'] = cursor.fetchall()
  return render_template("student_data.html")

@app.route('/show_student_data', methods=['GET', 'POST'])
def show_student_data():
  if request.method == "POST":
    the_student = request.form['studata']
    connection = sqlite3.connect("myDatabase.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM gradstudents WHERE uid = " + str(the_student))
    session["gsec-studata"] = cursor.fetchall()
    cursor.execute("SELECT * FROM enrollment WHERE uid = " + str(the_student))
    session["gsec-enroll"] = cursor.fetchall()
  return render_template("show_student_data.html")

#SYSTEMS ADMIN FUNCTIONALITY - ABILITY TO CREATE USERS
@app.route('/createuser', methods = ['GET', 'POST'])
def createuser():
  if request.method == 'POST':
    uid = request.form['uid']
    # fname = request.form['fname']
    # lname = request.form['lname']
    # email = request.form['email']
    password = request.form['password']
    typeid = request.form['typid']

    connection = sqlite3.connect("myDatabase.db")
    cursor = connection.cursor()

    cursor.execute("INSERT INTO users (uid, password, typeid) VALUES (?, ?, ?)", (uid, password, typeid))

    if typeid == 'Graduate Student':
      fname = request.form['fname']
      lname = request.form['lname']
      email = request.form['email']
      address = request.form['address']
      phd_or_ms = request.form['program']
      suspensioncheck = request.form['suspensioncheck']
      appliedforgrad = request.form['appliedforgrad']
      cursor.execute("INSERT INTO gradstudents VALUES (" + str(uid) + ", \"" + fname + "\", \"" + lname + "\", \"" + email + "\", \"" + address + "\", " + phd_or_ms + "\", " + str(appliedforgrad) + ", " + str(suspensioncheck) + ")")
    elif typeid == 'Faculty Advisor':
      fname = request.form['fname']
      lname = request.form['lname']
      cursor.execute("INSERT INTO facultyadvisor (uid, fname, lname) VALUES (" + str(uid) + ", \"" + fname + "\", \""  + lname + "\")")
    elif typeid == 'Graduate Secretary':
      cursor.execute("INSERT INTO gradsecretary (uid) VALUES (" + str(uid) + ")")
    
    connection.commit()
    connection.close()
    return render_template("createuser.html", message = "New user created!")
  
  return render_template("createuser.html")

#SYSTEMS ADMIN FUNCTIONALITY - ABILITY TO EDIT GRADES
@app.route('/editgrades', methods = ['GET', 'POST'])
def editgrades():
  connection = sqlite3.connect("myDatabase.db")
  cursor = connection.cursor()
  cursor.execute("SELECT uid FROM gradstudents")
  students = cursor.fetchall()

  if request.method == 'POST':
    uid = request.form['student_uid']
    courseid = request.form['course_id']
    coursenumber = request.form['course_number']
    new_grade = request.form['new_grade']
    
    # Add error check :P
    cursor.execute("SELECT * FROM enrollment WHERE uid = " + str(uid) + " AND coursenumber = " + str(coursenumber) + " AND coursetype = \"" + courseid + "\"")
    data1 = cursor.fetchall()
    if not data1:
      return render_template("editgrades.html", message = "Did not find a user with that course. Please try again.", students=students)
   
    cursor.execute("UPDATE enrollment SET finalgrade = ? WHERE uid = ? AND coursetype = ? AND coursenumber = ?", (new_grade, uid, courseid, coursenumber))
    
    connection.commit()
    return render_template("editgrades.html", message = "Updated grade successfully!", students=students)
  
  return render_template("editgrades.html", students=students)

#SYSTEMS ADMIN FUNCTIONALITY - ABILITY TO CHANGE ADVISOR
@app.route('/changeadvisor', methods = ['GET', 'POST'])
def changeadvisor():
  if request.method == 'POST':
    student_uid = request.form['student_uid']
    newadvisor_uid = request.form['new_advisor_uid']
    connection = sqlite3.connect("myDatabase.db")
    cursor = connection.cursor()

    # error check :P
    cursor.execute("SELECT * FROM users WHERE uid = " + str(student_uid) + " OR uid = " + str(newadvisor_uid))
    data1 = cursor.fetchall()
    if data1:
      print(data1)
      if len(data1) < 2:
        return render_template("changeadvisor.html", message = "Incorrect inputs, try again.")
    if not data1:
      return render_template("changeadvisor.html", message = "Incorrect inputs, try again.")
    
    cursor.execute("UPDATE advisor_student SET advisoruid = ? WHERE studentuid = ?", (newadvisor_uid, student_uid))

    connection.commit()
    connection.close()
    return render_template("changeadvisor.html", message = "Advisor changed successfully!")
    
  return render_template("changeadvisor.html")



app.run(host='0.0.0.0', port=8080)