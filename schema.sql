PRAGMA foreign_keys=off;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    uid integer not null PRIMARY KEY CHECK (uid BETWEEN 10000000 AND 99999999),
    password varchar(50) not null,
    typeid varchar(50) not null CHECK (typeid IN ('Student', 'Alumni', 'Graduate Secretary', 'Systems Administration', 'Faculty Advisor'))
);

DROP TABLE IF EXISTS gradstudents;
CREATE TABLE gradstudents (
    uid integer not null PRIMARY KEY,
    fname varchar(50) not null,
    lname varchar(50) not null,
    email varchar(50) not null,
    address varchar(50) not null,
    enrollmentin_m_or_phd varchar(50) not null,
    appliedforgrad BOOLEAN DEFAULT 0,
    suspensioncheck BOOLEAN DEFAULT 0,
    FOREIGN KEY (uid) REFERENCES users(uid)
);


DROP TABLE IF EXISTS alumni;
CREATE TABLE alumni (
    uid integer not null PRIMARY KEY,
    fname varchar(50) not null,
    lname varchar(50) not null,
    email varchar(50) not null,
    address varchar(50) not null,
    transcript varchar(50) not null
);

DROP TABLE IF EXISTS facultyadvisor;
CREATE TABLE facultyadvisor (
    uid integer not null PRIMARY KEY,
    fname varchar(50) not null,
    lname varchar(50) not null,
    FOREIGN KEY (uid) REFERENCES users(uid)
);


DROP TABLE IF EXISTS advisor_student;
CREATE TABLE advisor_student(
    advisoruid integer not null,
    studentuid integer not null,
    thesisapproval BOOLEAN DEFAULT 0,
    PRIMARY KEY (advisoruid, studentuid),
    FOREIGN KEY (advisoruid) REFERENCES facultyadvisor(uid),
    FOREIGN KEY (studentuid) REFERENCES gradstudents(uid)
);

DROP TABLE IF EXISTS gradsecretary;
CREATE TABLE gradsecretary (
    uid integer not null PRIMARY KEY,
    FOREIGN KEY (uid) REFERENCES users(uid)
);


DROP TABLE IF EXISTS systemsadmin;
CREATE TABLE systemsadmin (
    uid integer not null PRIMARY KEY,
    FOREIGN KEY (uid) REFERENCES users(uid)
);



DROP TABLE IF EXISTS enrollment;
CREATE TABLE enrollment (
    uid integer not null,
    coursetype varchar(50) not null,
    coursenumber integer not null,
    finalgrade varchar(50) not null,
    semester varchar(50) not null,
    year integer not null,
    credithours integer,
    FOREIGN KEY (uid) REFERENCES gradstudents(uid),
    FOREIGN KEY (coursenumber) REFERENCES course_catalog(coursenumber)
);



DROP TABLE IF EXISTS course_catalog;
CREATE TABLE course_catalog (
    dept varchar(50) not null,
    coursenumber integer not null,
    coursename varchar(50) not null,
    credits integer not null,
    prereq1 varchar(50) not null,
    prereq2 varchar(50) not null
);


DROP TABLE IF EXISTS form1;
CREATE TABLE form1 (
    uid integer not null,
    formnum integer not null,
    fname varchar(50) not null,
    lname varchar(50) not null,
    enrollmentin_m_or_phd varchar(50) not null,
    coursetype varchar(50) not null,
    coursenumber integer not null,
    FOREIGN KEY (coursenumber) REFERENCES course_catalog(coursenumber)
);

DROP TABLE IF EXISTS form1_approval;
CREATE TABLE form1_approval (
    formnum integer not null PRIMARY KEY,
    uid integer not null,
    approved BOOLEAN DEFAULT 0
);



-- starting state entries

INSERT INTO users VALUES (10010011, 'naraharipassword', 'Faculty Advisor');
INSERT INTO facultyadvisor VALUES (10010011, 'Bhagirath', 'Narahari');


INSERT INTO users VALUES (22222223, 'parmerpassword', 'Faculty Advisor');
INSERT INTO facultyadvisor VALUES (22222223, 'Gabriel', 'Parmer');


INSERT INTO users VALUES (33333333, 'gsecpassword', 'Graduate Secretary');
INSERT INTO gradsecretary VALUES (33333333);

INSERT INTO users VALUES (21212121, 'systemsadminpassword', 'Systems Administration');
INSERT INTO systemsadmin VALUES (21212121);



INSERT INTO users VALUES (55555555, 'paulpasswor_d', 'Student');
INSERT INTO gradstudents VALUES (55555555, 'Paul', 'McCartney', 'paul.mccartney@gwu.edu', '123 McCartney Rd', 'MS', 0, 0);


INSERT INTO enrollment VALUES (55555555, 'CSCI', '6221', 'A', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (55555555, 'CSCI', '6212', 'A', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (55555555, 'CSCI', '6461', 'A', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (55555555, 'CSCI', '6232', 'A', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (55555555, 'CSCI', '6233', 'A', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (55555555, 'CSCI', '6241', 'B', 'Spring', 2025, 3);
INSERT INTO enrollment VALUES (55555555, 'CSCI', '6246', 'B', 'Spring', 2025, 3);
INSERT INTO enrollment VALUES (55555555, 'CSCI', '6262', 'B', 'Spring', 2025, 3);
INSERT INTO enrollment VALUES (55555555, 'CSCI', '6283', 'B', 'Spring', 2025, 3);
INSERT INTO enrollment VALUES (55555555, 'CSCI', '6242', 'B', 'Spring', 2025, 3);
INSERT INTO enrollment VALUES (55555555, 'ECE', '6241', 'A', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (55555555, 'ECE', '6242', 'A', 'Fall', 2024, 2);

INSERT INTO advisor_student VALUES (10010011, 55555555, 0);

-- suspension check entry
INSERT INTO users VALUES (99999999, 'suspendeduser_password', 'Student');
INSERT INTO gradstudents VALUES (99999999, 'Suspended', 'Suspendypants', 'suspended@gwu.edu', '123 Suspended Rd', 'MS', 0, 0);

INSERT INTO enrollment VALUES (99999999, 'CSCI', '6221', 'A', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (99999999, 'CSCI', '6212', 'A', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (99999999, 'CSCI', '6461', 'C', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (99999999, 'CSCI', '6232', 'A', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (99999999, 'CSCI', '6233', 'A', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (99999999, 'CSCI', '6241', 'C', 'Spring', 2025, 3);
INSERT INTO enrollment VALUES (99999999, 'CSCI', '6246', 'C', 'Spring', 2025, 3);
INSERT INTO enrollment VALUES (99999999, 'CSCI', '6262', 'C', 'Spring', 2025, 3);
INSERT INTO enrollment VALUES (99999999, 'CSCI', '6283', 'D', 'Spring', 2025, 3);
INSERT INTO enrollment VALUES (99999999, 'CSCI', '6242', 'D', 'Spring', 2025, 3);
INSERT INTO enrollment VALUES (99999999, 'ECE', '6241', 'C', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (99999999, 'ECE', '6242', 'A', 'Fall', 2024, 2);

INSERT INTO advisor_student VALUES (10010011, 99999999, 0);

INSERT INTO users VALUES (66666666, 'georgepassword', 'Student');
INSERT INTO gradstudents VALUES (66666666, 'George', 'Harrison', 'george.harrison@gwu.edu', '567 Harrison Rd', 'MS', 0, 0);


INSERT INTO enrollment VALUES (66666666, 'ECE', '6242', 'C', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (66666666, 'CSCI', '6221', 'B', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (66666666, 'CSCI', '6461', 'B', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (66666666, 'CSCI', '6212', 'B', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (66666666, 'CSCI', '6232', 'B', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (66666666, 'CSCI', '6233', 'B', 'Spring', 2025, 3);
INSERT INTO enrollment VALUES (66666666, 'CSCI', '6241', 'B', 'Spring', 2025, 3);
INSERT INTO enrollment VALUES (66666666, 'CSCI', '6242', 'B', 'Spring', 2025, 3);
INSERT INTO enrollment VALUES (66666666, 'CSCI', '6283', 'B', 'Spring', 2025, 3);
INSERT INTO enrollment VALUES (66666666, 'CSCI', '6284', 'B', 'Spring', 2025, 3);


INSERT INTO advisor_student VALUES (22222223, 66666666, 0);


-- advisor has not yet approved his thesis
INSERT INTO users VALUES (55665566, 'starrpassword', 'Student');
INSERT INTO gradstudents VALUES (55665566, 'Ringo', 'Starr', 'ringo.starr@gwu.edu', '667 Starr Rd', 'PhD', 0, 0);


INSERT INTO enrollment VALUES (55665566, 'CSCI', '6221', 'A', 'Spring', 2024, 3);
INSERT INTO enrollment VALUES (55665566, 'CSCI', '6461', 'A', 'Spring', 2024, 3);
INSERT INTO enrollment VALUES (55665566, 'CSCI', '6212', 'A', 'Spring', 2024, 3);
INSERT INTO enrollment VALUES (55665566, 'CSCI', '6220', 'A', 'Spring', 2024, 3);
INSERT INTO enrollment VALUES (55665566, 'CSCI', '6232', 'A', 'Spring', 2024, 3);
INSERT INTO enrollment VALUES (55665566, 'CSCI', '6233', 'A', 'Spring', 2024, 3);
INSERT INTO enrollment VALUES (55665566, 'CSCI', '6241', 'A', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (55665566, 'CSCI', '6242', 'A', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (55665566, 'CSCI', '6246', 'A', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (55665566, 'CSCI', '6260', 'A', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (55665566, 'CSCI', '6251', 'A', 'Fall', 2024, 3);
INSERT INTO enrollment VALUES (55665566, 'CSCI', '6283', 'A', 'Fall', 2024, 3);


INSERT INTO advisor_student VALUES (22222223, 55665566, 0);


-- graduated in 2018 with an MS
INSERT INTO users VALUES (77777777, 'ericpassword', 'Alumni');
INSERT INTO alumni VALUES (77777777, 'Eric', 'Clapton', 'eric.clapton@gwu.edu', '867 Clapton Rd', 'MS in 2014');


INSERT INTO enrollment VALUES (77777777, 'CSCI', '6221', 'B', 'Fall', 2013, 3);
INSERT INTO enrollment VALUES (77777777, 'CSCI', '6212', 'B', 'Fall', 2013, 3);
INSERT INTO enrollment VALUES (77777777, 'CSCI', '6461', 'B', 'Fall', 2013, 3);
INSERT INTO enrollment VALUES (77777777, 'CSCI', '6232', 'B', 'Fall', 2013, 3);
INSERT INTO enrollment VALUES (77777777, 'CSCI', '6233', 'B', 'Fall', 2013, 3);
INSERT INTO enrollment VALUES (77777777, 'CSCI', '6241', 'B', 'Fall', 2013, 3);
INSERT INTO enrollment VALUES (77777777, 'CSCI', '6242', 'B', 'Spring', 2014, 3);
INSERT INTO enrollment VALUES (77777777, 'CSCI', '6283', 'A', 'Spring', 2014, 3);
INSERT INTO enrollment VALUES (77777777, 'CSCI', '6284', 'A', 'Spring', 2014, 3);
INSERT INTO enrollment VALUES (77777777, 'CSCI', '6286', 'A', 'Spring', 2014, 3);


INSERT INTO course_catalog VALUES('CSCI', 6221, 'SW Paradigms', 3, 'None', 'None');
INSERT INTO course_catalog VALUES('CSCI', 6461, 'Computer Architecture', 3, 'None', 'None');
INSERT INTO course_catalog VALUES('CSCI', 6212, 'Algorithms', 3, 'None', 'None');
INSERT INTO course_catalog VALUES('CSCI', 6220, 'Machine Learning', 3, 'None', 'None');
INSERT INTO course_catalog VALUES('CSCI', 6232, 'Networks 1', 3, 'None', 'None');
INSERT INTO course_catalog VALUES('CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', 'None');
INSERT INTO course_catalog VALUES('CSCI', 6241, 'Database 1', 3, 'None', 'None');
INSERT INTO course_catalog VALUES('CSCI', 6242, 'Database 2', 3, 'CSCI 6241', 'None');
INSERT INTO course_catalog VALUES('CSCI', 6246, 'Compilers', 3, 'CSCI 6461', 'CSCI 6212');
INSERT INTO course_catalog VALUES('CSCI', 6260, 'Multimedia', 3, 'None', 'None');
INSERT INTO course_catalog VALUES('CSCI', 6251, 'Cloud Computing', 3, 'CSCI 6461', 'None');
INSERT INTO course_catalog VALUES('CSCI', 6254, 'SW Engineering', 3, 'CSCI 6221', 'None');
INSERT INTO course_catalog VALUES('CSCI', 6262, 'Graphics 1', 3, 'None', 'None');
INSERT INTO course_catalog VALUES('CSCI', 6283, 'Security 1', 3, 'CSCI 6212', 'None');
INSERT INTO course_catalog VALUES('CSCI', 6284, 'Cryptography', 3, 'CSCI 6212', 'None');
INSERT INTO course_catalog VALUES('CSCI', 6286, 'Network Security', 3, 'CSCI 6283', 'CSCI 6232');
INSERT INTO course_catalog VALUES('CSCI', 6325, 'Algorithms 2', 3, 'CSCI 6212', 'None');
INSERT INTO course_catalog VALUES('CSCI', 6339, 'Embedded Systems', 3, 'CSCI 6461', 'CSCI 6212');
INSERT INTO course_catalog VALUES('CSCI', 6384, 'Cryptography 2', 3, 'CSCI 6284', 'None');
INSERT INTO course_catalog VALUES('ECE', 6241, 'Communication Theory', 3, 'None', 'None');
INSERT INTO course_catalog VALUES('ECE', 6242, 'Information Theory', 2, 'None', 'None');
INSERT INTO course_catalog VALUES('MATH', 6210, 'Logic', 2, 'None', 'None');









