
import os
from datetime import datetime, timedelta

DATA_FOLDER = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(DATA_FOLDER, "users.txt")
STUDENTS_FILE = os.path.join(DATA_FOLDER, "students.txt")
ATTENDANCE_FILE = os.path.join(DATA_FOLDER, "attendance_records.txt")

users = []
students = []
attendance_records = []


def save_data():
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as file:
            for user in users:
                file.write("|".join(str(value) for value in user) + "\n")

        with open(STUDENTS_FILE, "w", encoding="utf-8") as file:
            for student in students:
                file.write("|".join(str(value) for value in student) + "\n")

        with open(ATTENDANCE_FILE, "w", encoding="utf-8") as file:
            for record in attendance_records:
                file.write("|".join(str(value) for value in record) + "\n")

        return True
    except OSError:
        return False


def load_data():
    global users, students, attendance_records

    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as file:
                users = [
                    line.rstrip("\n").split("|")
                    for line in file
                    if line.strip()
                ]

        if os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, "r", encoding="utf-8") as file:
                students = [
                    line.rstrip("\n").split("|")
                    for line in file
                    if line.strip()
                ]

        if os.path.exists(ATTENDANCE_FILE):
            with open(ATTENDANCE_FILE, "r", encoding="utf-8") as file:
                attendance_records = [
                    line.rstrip("\n").split("|")
                    for line in file
                    if line.strip()
                ]

        for record in attendance_records:
            if len(record) == 5:
                record.insert(4, "--:--:--")
            elif len(record) > 6:
                del record[6:]

    except OSError:
        print("\nSaved data could not be loaded.")
        print("Check that the text files exist and can be read.")

def confirm_saved():
    if not save_data():
        print("\nWarning: Changes are in memory but could not be saved.")
        print("Check that the program folder allows file writing.")


def get_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")


def get_student_id(prompt="Enter Student ID: ", allow_back=False):
    while True:
        student_id = input(prompt).strip()

        if allow_back and student_id.casefold() == "b":
            return None

        if student_id.isdigit():
            return student_id

        print("Student ID must contain numbers only.")


def get_choice(prompt, valid_choices):
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        print("Invalid choice. Please try again.")


def get_valid_date(prompt="Enter Date (YYYY-MM-DD): ", allow_back=False):
    while True:
        value = input(prompt).strip()

        if allow_back and value.casefold() == "b":
            return None

        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD, for example 2026-10-11.")


def print_table(headers, rows):
    if not rows:
        print("\nNo records to display.")
        return

    headers = [str(item) for item in headers]
    rows = [[str(item) for item in row] for row in rows]

    widths = []
    for i, header in enumerate(headers):
        widths.append(max(len(header), *(len(row[i]) for row in rows)))

    line = "-+-".join("-" * width for width in widths)

    print()
    print(" | ".join(
        headers[i].ljust(widths[i])
        for i in range(len(headers))
    ))
    print(line)

    for row in rows:
        print(" | ".join(
            row[i].ljust(widths[i])
            for i in range(len(headers))
        ))

    print(line)


def find_student(student_id):
    for student in students:
        if student[0] == student_id:
            return student
    return None


def find_user_by_username(username):
    for user in users:
        if user[0].casefold() == username.casefold():
            return user
    return None


def create_account():
    while True:
        print("\n========== CREATE ACCOUNT ==========")
        print("1. Student")
        print("2. Instructor")
        print("3. Back")

        choice = get_choice("Choose account type: ", ["1", "2", "3"])

        if choice == "3":
            return

        role = {"1": "Student", "2": "Instructor"}[choice]
        student = None

        if role == "Student":
            print("\n========== STUDENT REGISTRATION ==========")

            student_id = get_student_id(
                "Enter Student ID (or B to go back): ",
                allow_back=True
            )

            if student_id is None:
                continue

            student = find_student(student_id)

            if student is None:
                print("Student is not registered.")
                print("Ask the instructor to add your information first.")
                continue

            name = get_nonempty("Enter Student Name: ")
            section = get_nonempty("Enter Section: ")

            if name.casefold() != student[1].casefold():
                print("Student name does not match the registered record.")
                continue

            if section.casefold() != student[2].casefold():
                print("Section does not match the registered record.")
                continue

            account_exists = any(
                user[2] == "Student" and user[3] == student_id
                for user in users
            )

            if account_exists:
                print("A student account already exists.")
                continue

        print("\n========== ACCOUNT INFORMATION ==========")
        username = get_nonempty("Enter Username: ")

        if find_user_by_username(username):
            print("Username already exists.")
            continue

        password = get_nonempty("Enter Password: ")

        if role == "Student":
            users.append([
                username, password, role,
                student[0], student[1], student[2]
            ])
        else:
            users.append([username, password, role, "", "", ""])

        confirm_saved()
        print(role + " account created.")
        return


def user_login():
    print("\n========== USER LOGIN ==========")
    username = get_nonempty("Username: ")
    password = get_nonempty("Password: ")

    for user in users:
        if user[0] == username and user[1] == password:
            if user[2] not in ["Student", "Instructor"]:
                print("This account type is no longer supported.")
                print("Please create a Student or Instructor account.")
                return None

            if user[2] == "Student":
                student = find_student(user[3])

                if student is None:
                    print("Student is no longer registered.")
                    return None

                if (
                    student[1].casefold() != user[4].casefold()
                    or student[2].casefold() != user[5].casefold()
                ):
                    print("Student information does not match.")
                    return None

            print("\nLogin successful.")
            print("Account Type:", user[2])
            return user

    print("Invalid username or password.")
    return None


def add_student():
    print("\n========== ADD STUDENT INFORMATION ==========")

    student_id = get_student_id(
        "Enter Student ID (or B to go back): ",
        allow_back=True
    )

    if student_id is None:
        return

    if find_student(student_id):
        print("Student ID already exists.")
        return

    name = get_nonempty("Enter Student Name: ")
    section = get_nonempty("Enter Section: ")

    students.append([student_id, name, section])
    confirm_saved()

    print("\nStudent information:")
    print_table(
        ["Student ID", "Student Name", "Section"],
        [[student_id, name, section]]
    )


def list_students_by_section():
    print("\n========== STUDENT LIST BY SECTION ==========")

    section = input("Enter Section (or B to go back): ").strip()

    if section.casefold() == "b":
        return

    if not section:
        print("Section cannot be empty.")
        return

    section_students = [
        student for student in students
        if student[2].casefold() == section.casefold()
    ]
    section_students.sort(key=lambda student: student[1].casefold())

    if not section_students:
        print("No students found in that section.")
        return

    print("\nSection:", section)
    print("Total Registered Students:", len(section_students))

    rows = [
        [i, student[0], student[1], student[2]]
        for i, student in enumerate(section_students, start=1)
    ]

    print_table(
        ["No.", "Student ID", "Student Name", "Section"],
        rows
    )


def record_attendance():
    print("\n========== RECORD ATTENDANCE ==========")

    student_id = get_student_id(
        "Enter Student ID (or B to go back): ",
        allow_back=True
    )

    if student_id is None:
        return

    student = find_student(student_id)

    if student is None:
        print("Student is not registered.")
        return

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    print_table(
        ["Student ID", "Student Name", "Section", "Date", "Time"],
        [[student[0], student[1], student[2], date, time]]
    )

    for record in attendance_records:
        if record[0] == student_id and record[3] == date:
            print("Attendance for this student has already been recorded today.")
            return

    print("\n1. Present")
    print("2. Absent")
    print("3. Back")

    choice = get_choice("Choose attendance status: ", ["1", "2", "3"])

    if choice == "3":
        return

    status = "Present" if choice == "1" else "Absent"

    attendance_records.append([
        student[0], student[1], student[2], date, time, status
    ])

    confirm_saved()

    print("\nAttendance result:")
    print_table(
        ["Student ID", "Student Name", "Section", "Date", "Time", "Status"],
        [[student[0], student[1], student[2], date, time, status]]
    )


def view_attendance_records():
    print("\n========== VIEW ATTENDANCE RECORDS ==========")
    print("1. View all dates")
    print("2. View a specific date")
    print("3. View a specific week")
    print("4. Back")

    choice = get_choice("Choose an option: ", ["1", "2", "3", "4"])

    if choice == "4":
        return

    section = input("Enter Section (or B to go back): ").strip()

    if section.casefold() == "b":
        return

    if not section:
        print("Section cannot be empty.")
        return

    selected_date = None
    week_start = None
    week_end = None

    if choice == "2":
        selected_date = get_valid_date(
            "Enter Date (YYYY-MM-DD, or B to go back): ",
            allow_back=True
        )

        if selected_date is None:
            return

    elif choice == "3":
        week_date = get_valid_date(
            "Enter any date in the week (YYYY-MM-DD, or B to go back): ",
            allow_back=True
        )

        if week_date is None:
            return

        parsed_date = datetime.strptime(week_date, "%Y-%m-%d").date()
        week_start = parsed_date - timedelta(days=parsed_date.weekday())
        week_end = week_start + timedelta(days=6)

    records = [
        record for record in attendance_records
        if record[2].casefold() == section.casefold()
        and (selected_date is None or record[3] == selected_date)
        and (
            week_start is None
            or week_start <= datetime.strptime(record[3], "%Y-%m-%d").date() <= week_end
        )
    ]

    records.sort(key=lambda record: (record[3], record[1].casefold()))

    print("\nSection:", section)

    if selected_date:
        print("Date:", selected_date)
    elif week_start is not None:
        print(
            "Week:",
            week_start.strftime("%Y-%m-%d"),
            "to",
            week_end.strftime("%Y-%m-%d")
        )

    print_table(
        ["Student ID", "Student Name", "Section", "Date", "Time", "Status"],
        records
    )


def search_attendance():
    print("\n========== SEARCH ATTENDANCE ==========")

    student_id = get_student_id(
        "Enter Student ID (or B to go back): ",
        allow_back=True
    )

    if student_id is None:
        return

    student = find_student(student_id)

    if student is None:
        print("Student not found.")
        return

    print("\nStudent Information:")
    print_table(
        ["Student ID", "Student Name", "Section"],
        [[student[0], student[1], student[2]]]
    )

    records = [
        record for record in attendance_records
        if record[0] == student_id
    ]
    records.sort(key=lambda record: record[3])

    print("\nAttendance History:")
    print_table(
        ["Date", "Time", "Status"],
        [[record[3], record[4], record[5]] for record in records]
    )


def attendance_summary():
    print("\n========== ATTENDANCE SUMMARY ==========")

    section = input("Enter Section (or B to go back): ").strip()

    if section.casefold() == "b":
        return

    if not section:
        print("Section cannot be empty.")
        return

    selected_date = get_valid_date(
        "Enter Date (YYYY-MM-DD, or B to go back): ",
        allow_back=True
    )

    if selected_date is None:
        return

    section_students = [
        student for student in students
        if student[2].casefold() == section.casefold()
    ]
    section_students.sort(key=lambda student: student[1].casefold())

    if not section_students:
        print("No students found in that section.")
        return

    daily_records = {
        record[0]: record
        for record in attendance_records
        if record[2].casefold() == section.casefold()
        and record[3] == selected_date
    }

    summary_rows = []
    present_count = 0
    absent_count = 0
    no_record_count = 0

    for student in section_students:
        record = daily_records.get(student[0])

        if record is None:
            status = "No Record"
            present = 0
            absent = 0
            no_record_count += 1
        elif record[5] == "Present":
            status = "Present"
            present = 1
            absent = 0
            present_count += 1
        else:
            status = "Absent"
            present = 0
            absent = 1
            absent_count += 1

        summary_rows.append([
            student[0], student[1], present, absent, status
        ])

    print("\nSection:", section)
    print("Date:", selected_date)
    print("Registered Students:", len(section_students))

    print_table(
        ["Student ID", "Student Name", "Present", "Absent", "Status"],
        summary_rows
    )

    print("\n========== DAILY TOTALS ==========")
    print_table(
        ["Category", "Total"],
        [
            ["Registered Students", len(section_students)],
            ["Present", present_count],
            ["Absent", absent_count],
            ["No Attendance Record", no_record_count],
            ["Total Records Saved", present_count + absent_count]
        ]
    )

    print("\nNote: No Record means attendance has not been recorded for that date.")
    print("It does not automatically mean the student is absent.")


def student_view_attendance(user):
    print("\n========== MY ATTENDANCE RECORDS ==========")

    print_table(
        ["Student Name", "Student ID", "Section"],
        [[user[4], user[3], user[5]]]
    )

    records = [
        record for record in attendance_records
        if record[0] == user[3]
    ]
    records.sort(key=lambda record: record[3])

    print("\nMy Attendance History:")
    print_table(
        ["Date", "Time", "Status"],
        [[record[3], record[4], record[5]] for record in records]
    )


def instructor_menu():
    while True:
        print("\n========== INSTRUCTOR MENU ==========")
        print("1. Add Student Information")
        print("2. Record Attendance")
        print("3. View Attendance Records")
        print("4. Search Attendance")
        print("5. Attendance Summary by Date and Section")
        print("6. List Students by Section")
        print("7. Back / Logout")

        choice = get_choice(
            "Choose an option: ",
            ["1", "2", "3", "4", "5", "6", "7"]
        )

        if choice == "1":
            add_student()
        elif choice == "2":
            record_attendance()
        elif choice == "3":
            view_attendance_records()
        elif choice == "4":
            search_attendance()
        elif choice == "5":
            attendance_summary()
        elif choice == "6":
            list_students_by_section()
        elif choice == "7":
            print("Returning to the main menu...")
            break


def student_menu(user):
    while True:
        print("\n========== STUDENT MENU ==========")
        print("1. View My Attendance")
        print("2. Back / Logout")

        choice = get_choice("Choose an option: ", ["1", "2"])

        if choice == "1":
            student_view_attendance(user)
        elif choice == "2":
            print("Returning to the main menu...")
            break


def main_menu():
    while True:
        print("\n==========================================")
        print("     CLASSROOM ATTENDANCE MONITORING")
        print("==========================================")
        print("1. Create Account")
        print("2. User Login")
        print("3. Exit")

        choice = get_choice("Choose an option: ", ["1", "2", "3"])

        if choice == "1":
            create_account()

        elif choice == "2":
            user = user_login()

            if user is not None:
                if user[2] == "Instructor":
                    instructor_menu()
                elif user[2] == "Student":
                    student_menu(user)

        elif choice == "3":
            print("\nThank you for using the system.")
            break


load_data()
main_menu()
