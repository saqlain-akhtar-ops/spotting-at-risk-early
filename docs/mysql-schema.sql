-- MySQL 8 operational schema. Create a dedicated database and limited user first.


CREATE TABLE subjects (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(60) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
)

;


CREATE TABLE terms (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(40) NOT NULL, 
	academic_year VARCHAR(20) NOT NULL, 
	PRIMARY KEY (id)
)

;


CREATE TABLE users (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(100) NOT NULL, 
	email VARCHAR(254) NOT NULL, 
	password_hash VARCHAR(300) NOT NULL, 
	`role` VARCHAR(20) NOT NULL, 
	active INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT valid_user_role CHECK (role IN ('admin','teacher','student','parent')), 
	UNIQUE (email)
)

;


CREATE TABLE audit_logs (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER, 
	action VARCHAR(60) NOT NULL, 
	entity VARCHAR(60) NOT NULL, 
	entity_id VARCHAR(60) NOT NULL, 
	details TEXT NOT NULL, 
	timestamp VARCHAR(40) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
)

;


CREATE TABLE classes (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(40) NOT NULL, 
	advisor_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name), 
	FOREIGN KEY(advisor_id) REFERENCES users (id)
)

;


CREATE TABLE sessions (
	token_hash VARCHAR(64) NOT NULL, 
	user_id INTEGER NOT NULL, 
	csrf VARCHAR(64) NOT NULL, 
	expires FLOAT NOT NULL, 
	PRIMARY KEY (token_hash), 
	FOREIGN KEY(user_id) REFERENCES users (id)
)

;


CREATE TABLE assignments (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	subject_id INTEGER NOT NULL, 
	teacher_id INTEGER NOT NULL, 
	class_id INTEGER NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	due_date VARCHAR(40) NOT NULL, 
	instructions TEXT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(subject_id) REFERENCES subjects (id), 
	FOREIGN KEY(teacher_id) REFERENCES users (id), 
	FOREIGN KEY(class_id) REFERENCES classes (id)
)

;


CREATE TABLE extra_classes (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	subject_id INTEGER NOT NULL, 
	teacher_id INTEGER NOT NULL, 
	class_id INTEGER NOT NULL, 
	date VARCHAR(10) NOT NULL, 
	start_time VARCHAR(5) NOT NULL, 
	end_time VARCHAR(5) NOT NULL, 
	room VARCHAR(100) NOT NULL, 
	topic VARCHAR(250) NOT NULL, 
	state VARCHAR(20) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(subject_id) REFERENCES subjects (id), 
	FOREIGN KEY(teacher_id) REFERENCES users (id), 
	FOREIGN KEY(class_id) REFERENCES classes (id)
)

;


CREATE TABLE students (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(100) NOT NULL, 
	class_id INTEGER NOT NULL, 
	academic_year VARCHAR(20) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(class_id) REFERENCES classes (id)
)

;

CREATE INDEX ix_students_class_id ON students (class_id);


CREATE TABLE extra_class_students (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	extra_class_id INTEGER NOT NULL, 
	student_id INTEGER NOT NULL, 
	attendance VARCHAR(20) NOT NULL, 
	outcome TEXT NOT NULL, 
	status_before VARCHAR(30) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (extra_class_id, student_id), 
	FOREIGN KEY(extra_class_id) REFERENCES extra_classes (id), 
	FOREIGN KEY(student_id) REFERENCES students (id)
)

;

CREATE INDEX ix_extra_class_students_student_id ON extra_class_students (student_id);


CREATE TABLE parents (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	student_id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	email VARCHAR(254) NOT NULL, 
	phone VARCHAR(30) NOT NULL, 
	relationship VARCHAR(40) NOT NULL, 
	`primary` INTEGER NOT NULL, 
	consent INTEGER NOT NULL, 
	active INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_id) REFERENCES students (id)
)

;

CREATE INDEX ix_parents_student_id ON parents (student_id);


CREATE TABLE performance (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	student_id INTEGER NOT NULL, 
	subject_id INTEGER NOT NULL, 
	term_id INTEGER NOT NULL, 
	score FLOAT, 
	attendance FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (student_id, subject_id, term_id), 
	CONSTRAINT score_range CHECK (score IS NULL OR (score >= 0 AND score <= 100)), 
	CONSTRAINT attendance_range CHECK (attendance >= 0 AND attendance <= 100), 
	FOREIGN KEY(student_id) REFERENCES students (id), 
	FOREIGN KEY(subject_id) REFERENCES subjects (id), 
	FOREIGN KEY(term_id) REFERENCES terms (id)
)

;

CREATE INDEX ix_performance_student_id ON performance (student_id);


CREATE TABLE progress_reports (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	student_id INTEGER NOT NULL, 
	term_id INTEGER NOT NULL, 
	version INTEGER NOT NULL, 
	generated_at VARCHAR(40) NOT NULL, 
	released INTEGER NOT NULL, 
	summary TEXT NOT NULL, 
	comments TEXT NOT NULL, 
	follow_up TEXT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_id) REFERENCES students (id), 
	FOREIGN KEY(term_id) REFERENCES terms (id)
)

;

CREATE INDEX ix_progress_reports_student_id ON progress_reports (student_id);


CREATE TABLE student_status (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	student_id INTEGER NOT NULL, 
	term_id INTEGER NOT NULL, 
	status VARCHAR(30) NOT NULL, 
	rule_version VARCHAR(40) NOT NULL, 
	evidence TEXT NOT NULL, 
	calculated_at VARCHAR(40) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (student_id, term_id), 
	FOREIGN KEY(student_id) REFERENCES students (id), 
	FOREIGN KEY(term_id) REFERENCES terms (id)
)

;

CREATE INDEX ix_student_status_student_id ON student_status (student_id);


CREATE TABLE submissions (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	assignment_id INTEGER NOT NULL, 
	student_id INTEGER NOT NULL, 
	original_filename VARCHAR(200) NOT NULL, 
	stored_filename VARCHAR(100) NOT NULL, 
	mime_type VARCHAR(100) NOT NULL, 
	file_size INTEGER NOT NULL, 
	version_no INTEGER NOT NULL, 
	submitted_at VARCHAR(40) NOT NULL, 
	status VARCHAR(40) NOT NULL, 
	feedback TEXT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(assignment_id) REFERENCES assignments (id), 
	FOREIGN KEY(student_id) REFERENCES students (id), 
	UNIQUE (stored_filename)
)

;

CREATE INDEX ix_submissions_student_id ON submissions (student_id);


CREATE TABLE user_access (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	student_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (user_id, student_id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(student_id) REFERENCES students (id)
)

;

CREATE INDEX ix_user_access_student_id ON user_access (student_id);

CREATE INDEX ix_user_access_user_id ON user_access (user_id);


CREATE TABLE notifications (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	student_id INTEGER NOT NULL, 
	parent_id INTEGER NOT NULL, 
	template VARCHAR(40) NOT NULL, 
	message TEXT NOT NULL, 
	status VARCHAR(30) NOT NULL, 
	attempts INTEGER NOT NULL, 
	error VARCHAR(200) NOT NULL, 
	created_at VARCHAR(40) NOT NULL, 
	sent_at VARCHAR(40), 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_id) REFERENCES students (id), 
	FOREIGN KEY(parent_id) REFERENCES parents (id)
)

;