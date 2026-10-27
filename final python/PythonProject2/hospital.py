import sqlite3
from datetime import datetime

DB_NAME = "hospital.db"


# ---------------- DATABASE SETUP ----------------

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    with connect_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                disease TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                phone TEXT NOT NULL,
                fee REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                appointment_date TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Scheduled',
                FOREIGN KEY(patient_id) REFERENCES patients(id)
                    ON DELETE CASCADE,
                FOREIGN KEY(doctor_id) REFERENCES doctors(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                bill_date TEXT NOT NULL,
                payment_status TEXT NOT NULL DEFAULT 'Unpaid',
                FOREIGN KEY(patient_id) REFERENCES patients(id)
                    ON DELETE CASCADE
            );
        """)


# ---------------- INPUT HELPERS ----------------

def read_int(prompt, minimum=None):
    while True:
        try:
            value = int(input(prompt))
            if minimum is not None and value < minimum:
                print(f"Enter a number greater than or equal to {minimum}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid whole number.")


def read_float(prompt, minimum=0):
    while True:
        try:
            value = float(input(prompt))
            if value < minimum:
                print(f"Value must be at least {minimum}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid amount.")


def read_text(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def patient_exists(patient_id):
    with connect_db() as conn:
        return conn.execute(
            "SELECT 1 FROM patients WHERE id = ?", (patient_id,)
        ).fetchone() is not None


def doctor_exists(doctor_id):
    with connect_db() as conn:
        return conn.execute(
            "SELECT 1 FROM doctors WHERE id = ?", (doctor_id,)
        ).fetchone() is not None


# ---------------- PATIENT MANAGEMENT ----------------

def add_patient():
    print("\n--- Register Patient ---")
    name = read_text("Patient name: ")
    age = read_int("Age: ", 0)
    gender = read_text("Gender: ")
    phone = read_text("Phone number: ")
    address = read_text("Address: ")
    disease = read_text("Disease / complaint: ")

    with connect_db() as conn:
        cur = conn.execute("""
            INSERT INTO patients
            (name, age, gender, phone, address, disease)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, age, gender, phone, address, disease))
        patient_id = cur.lastrowid

    print(f"Patient registered successfully. Patient ID: {patient_id}")


def view_patients():
    with connect_db() as conn:
        rows = conn.execute("""
            SELECT id, name, age, gender, phone, disease
            FROM patients ORDER BY id
        """).fetchall()

    print("\n--- Patient List ---")
    if not rows:
        print("No patient records found.")
        return

    print(f"{'ID':<5}{'Name':<22}{'Age':<6}"
          f"{'Gender':<12}{'Phone':<16}{'Disease'}")
    print("-" * 80)
    for row in rows:
        print(f"{row[0]:<5}{row[1]:<22}{row[2]:<6}"
              f"{row[3]:<12}{row[4]:<16}{row[5]}")


def search_patient():
    patient_id = read_int("Enter patient ID: ", 1)

    with connect_db() as conn:
        row = conn.execute("""
            SELECT * FROM patients WHERE id = ?
        """, (patient_id,)).fetchone()

    if not row:
        print("Patient not found.")
        return

    print("\n--- Patient Details ---")
    labels = ["ID", "Name", "Age", "Gender", "Phone",
              "Address", "Disease"]
    for label, value in zip(labels, row):
        print(f"{label}: {value}")


def update_patient():
    patient_id = read_int("Enter patient ID to update: ", 1)

    with connect_db() as conn:
        patient = conn.execute(
            "SELECT * FROM patients WHERE id = ?", (patient_id,)
        ).fetchone()

    if not patient:
        print("Patient not found.")
        return

    print("Enter the new details:")
    name = read_text("Patient name: ")
    age = read_int("Age: ", 0)
    gender = read_text("Gender: ")
    phone = read_text("Phone number: ")
    address = read_text("Address: ")
    disease = read_text("Disease / complaint: ")

    with connect_db() as conn:
        conn.execute("""
            UPDATE patients
            SET name=?, age=?, gender=?, phone=?, address=?, disease=?
            WHERE id=?
        """, (name, age, gender, phone, address, disease, patient_id))

    print("Patient details updated successfully.")


def delete_patient():
    patient_id = read_int("Enter patient ID to delete: ", 1)

    if not patient_exists(patient_id):
        print("Patient not found.")
        return

    confirm = input(
        "Delete this patient and related appointments/bills? (yes/no): "
    ).strip().lower()

    if confirm == "yes":
        with connect_db() as conn:
            conn.execute(
                "DELETE FROM patients WHERE id = ?", (patient_id,)
            )
        print("Patient and related records deleted.")
    else:
        print("Deletion cancelled.")


# ---------------- DOCTOR MANAGEMENT ----------------

def add_doctor():
    print("\n--- Register Doctor ---")
    name = read_text("Doctor name: ")
    specialization = read_text("Specialization: ")
    phone = read_text("Phone number: ")
    fee = read_float("Consultation fee: ")

    with connect_db() as conn:
        cur = conn.execute("""
            INSERT INTO doctors (name, specialization, phone, fee)
            VALUES (?, ?, ?, ?)
        """, (name, specialization, phone, fee))
        doctor_id = cur.lastrowid

    print(f"Doctor registered successfully. Doctor ID: {doctor_id}")


def view_doctors():
    with connect_db() as conn:
        rows = conn.execute("""
            SELECT id, name, specialization, phone, fee
            FROM doctors ORDER BY id
        """).fetchall()

    print("\n--- Doctor List ---")
    if not rows:
        print("No doctors registered.")
        return

    print(f"{'ID':<5}{'Name':<22}{'Specialization':<22}"
          f"{'Phone':<16}{'Fee':>10}")
    print("-" * 75)
    for row in rows:
        print(f"{row[0]:<5}{row[1]:<22}{row[2]:<22}"
              f"{row[3]:<16}{row[4]:>10.2f}")


# ---------------- APPOINTMENT MANAGEMENT ----------------

def book_appointment():
    print("\n--- Book Appointment ---")
    view_patients()
    patient_id = read_int("\nPatient ID: ", 1)

    if not patient_exists(patient_id):
        print("Invalid patient ID.")
        return

    view_doctors()
    doctor_id = read_int("\nDoctor ID: ", 1)

    if not doctor_exists(doctor_id):
        print("Invalid doctor ID.")
        return

    while True:
        date_text = read_text("Appointment date (YYYY-MM-DD): ")
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD.")

    reason = read_text("Reason for appointment: ")

    with connect_db() as conn:
        cur = conn.execute("""
            INSERT INTO appointments
            (patient_id, doctor_id, appointment_date, reason)
            VALUES (?, ?, ?, ?)
        """, (patient_id, doctor_id, date_text, reason))
        appointment_id = cur.lastrowid

    print(f"Appointment booked. Appointment ID: {appointment_id}")


def view_appointments():
    with connect_db() as conn:
        rows = conn.execute("""
            SELECT a.id, p.name, d.name, a.appointment_date,
                   a.reason, a.status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            ORDER BY a.appointment_date, a.id
        """).fetchall()

    print("\n--- Appointment List ---")
    if not rows:
        print("No appointments found.")
        return

    for row in rows:
        print(
            f"\nAppointment ID: {row[0]}\n"
            f"Patient: {row[1]}\n"
            f"Doctor: {row[2]}\n"
            f"Date: {row[3]}\n"
            f"Reason: {row[4]}\n"
            f"Status: {row[5]}"
        )


def update_appointment_status():
    appointment_id = read_int("Appointment ID: ", 1)

    with connect_db() as conn:
        row = conn.execute(
            "SELECT id FROM appointments WHERE id = ?",
            (appointment_id,)
        ).fetchone()

    if not row:
        print("Appointment not found.")
        return

    print("1. Scheduled\n2. Completed\n3. Cancelled")
    choice = input("Select new status: ").strip()
    statuses = {
        "1": "Scheduled",
        "2": "Completed",
        "3": "Cancelled"
    }

    if choice not in statuses:
        print("Invalid status.")
        return

    with connect_db() as conn:
        conn.execute("""
            UPDATE appointments SET status = ? WHERE id = ?
        """, (statuses[choice], appointment_id))

    print("Appointment status updated.")


# ---------------- BILLING MANAGEMENT ----------------

def generate_bill():
    print("\n--- Generate Patient Bill ---")
    view_patients()
    patient_id = read_int("\nPatient ID: ", 1)

    if not patient_exists(patient_id):
        print("Invalid patient ID.")
        return

    description = read_text("Bill description: ")
    amount = read_float("Amount: ")

    bill_date = datetime.now().strftime("%Y-%m-%d")

    with connect_db() as conn:
        cur = conn.execute("""
            INSERT INTO bills
            (patient_id, description, amount, bill_date)
            VALUES (?, ?, ?, ?)
        """, (patient_id, description, amount, bill_date))
        bill_id = cur.lastrowid

    print(f"Bill generated successfully. Bill ID: {bill_id}")
    print(f"Total amount: Rs. {amount:.2f}")


def view_bills():
    with connect_db() as conn:
        rows = conn.execute("""
            SELECT b.id, p.name, b.description, b.amount,
                   b.bill_date, b.payment_status
            FROM bills b
            JOIN patients p ON b.patient_id = p.id
            ORDER BY b.id DESC
        """).fetchall()

    print("\n--- Billing Records ---")
    if not rows:
        print("No bills found.")
        return

    print(f"{'Bill ID':<9}{'Patient':<20}{'Description':<23}"
          f"{'Amount':>11}  {'Date':<12}{'Status'}")
    print("-" * 90)

    for row in rows:
        print(f"{row[0]:<9}{row[1]:<20}{row[2][:22]:<23}"
              f"{row[3]:>11.2f}  {row[4]:<12}{row[5]}")


def update_payment_status():
    bill_id = read_int("Enter bill ID: ", 1)

    with connect_db() as conn:
        row = conn.execute(
            "SELECT id FROM bills WHERE id = ?", (bill_id,)
        ).fetchone()

    if not row:
        print("Bill not found.")
        return

    print("1. Paid\n2. Unpaid")
    choice = input("Select payment status: ").strip()

    statuses = {"1": "Paid", "2": "Unpaid"}
    if choice not in statuses:
        print("Invalid choice.")
        return

    with connect_db() as conn:
        conn.execute("""
            UPDATE bills SET payment_status = ? WHERE id = ?
        """, (statuses[choice], bill_id))

    print("Payment status updated.")


# ---------------- REPORTS ----------------

def dashboard():
    with connect_db() as conn:
        patients = conn.execute(
            "SELECT COUNT(*) FROM patients"
        ).fetchone()[0]

        doctors = conn.execute(
            "SELECT COUNT(*) FROM doctors"
        ).fetchone()[0]

        appointments = conn.execute(
            "SELECT COUNT(*) FROM appointments"
        ).fetchone()[0]

        bills = conn.execute(
            "SELECT COUNT(*) FROM bills"
        ).fetchone()[0]

        unpaid = conn.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM bills WHERE payment_status = 'Unpaid'
        """).fetchone()[0]

    print("\n========== HOSPITAL DASHBOARD ==========")
    print(f"Total patients:       {patients}")
    print(f"Total doctors:        {doctors}")
    print(f"Total appointments:   {appointments}")
    print(f"Total bills:          {bills}")
    print(f"Outstanding bills:    Rs. {unpaid:.2f}")
    print("========================================")


# ---------------- MAIN MENU ----------------

def main():
    create_tables()

    while True:
        print("""
================================================
         HOSPITAL MANAGEMENT SYSTEM
================================================
1.  Register Patient
2.  View All Patients
3.  Search Patient
4.  Update Patient
5.  Delete Patient
6.  Register Doctor
7.  View All Doctors
8.  Book Appointment
9.  View Appointments
10. Update Appointment Status
11. Generate Bill
12. View Bills
13. Update Payment Status
14. Dashboard / Reports
0.  Exit
================================================
""")

        choice = input("Enter your choice: ").strip()

        actions = {
            "1": add_patient,
            "2": view_patients,
            "3": search_patient,
            "4": update_patient,
            "5": delete_patient,
            "6": add_doctor,
            "7": view_doctors,
            "8": book_appointment,
            "9": view_appointments,
            "10": update_appointment_status,
            "11": generate_bill,
            "12": view_bills,
            "13": update_payment_status,
            "14": dashboard
        }

        if choice == "0":
            print("Thank you for using Hospital Management System.")
            break

        action = actions.get(choice)
        if action:
            try:
                action()
            except sqlite3.Error as error:
                print(f"Database error: {error}")
            except (EOFError, KeyboardInterrupt):
                print("\nOperation interrupted.")
                return
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

