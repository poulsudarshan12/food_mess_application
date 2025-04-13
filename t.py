import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ---- App Setup ----
st.set_page_config(page_title="Mess Attendance", layout="centered")

STUDENT_FILE = "students.csv"
ATTENDANCE_FILE = "mess_attendance.csv"

# ---- File Safety Functions ----
def ensure_students_file():
    try:
        if not os.path.exists(STUDENT_FILE):
            raise FileNotFoundError
        df = pd.read_csv(STUDENT_FILE)
        if list(df.columns) != ["ID", "Name"]:
            raise ValueError("Invalid student file structure.")
    except Exception:
        pd.DataFrame(columns=["ID", "Name"]).to_csv(STUDENT_FILE, index=False)
        st.warning("Student file was reset due to an error.")

def ensure_attendance_file():
    try:
        if not os.path.exists(ATTENDANCE_FILE):
            raise FileNotFoundError
        df = pd.read_csv(ATTENDANCE_FILE)
        expected_columns = ["ID", "Name", "Meal", "Date", "Time"]
        if list(df.columns) != expected_columns:
            raise ValueError("Invalid attendance file structure.")
    except Exception:
        pd.DataFrame(columns=["ID", "Name", "Meal", "Date", "Time"]).to_csv(ATTENDANCE_FILE, index=False)
        st.warning("Attendance file was reset due to an error.")

ensure_students_file()
ensure_attendance_file()

# ---- Sidebar Menu ----
menu = st.sidebar.radio("🔧 Menu", ["Add Student", "Search & Mark Attendance", "View Today's Attendance", "Delete Student"])

# ---- Add New Student ----
if menu == "Add Student":
    st.header("➕ Add New Student")
    new_name = st.text_input("Enter new student name")
    if st.button("Add Student"):
        if new_name.strip() == "":
            st.warning("Name cannot be empty.")
        else:
            students_df = pd.read_csv(STUDENT_FILE)
            if new_name.strip() in students_df["Name"].values:
                st.warning("Student already exists.")
            else:
                new_id = 1 if students_df.empty else students_df["ID"].max() + 1
                new_entry = pd.DataFrame({"ID": [new_id], "Name": [new_name.strip()]})
                new_entry.to_csv(STUDENT_FILE, mode='a', header=False, index=False)
                st.success(f"✅ Student '{new_name}' added with ID: {new_id}")

# ---- Search & Mark Attendance ----
elif menu == "Search & Mark Attendance":
    st.header("🔍 Search Student by ID & Mark Attendance")

    search_id = st.text_input("Enter Student ID to search", max_chars=10)

    if search_id:
        try:
            search_id = int(search_id)
            students_df = pd.read_csv(STUDENT_FILE)
            match = students_df[students_df["ID"] == search_id]

            if not match.empty:
                student_name = match.iloc[0]["Name"]
                st.success(f"✅ Student Found: {student_name}")

                # Show attendance count
                attendance_df = pd.read_csv(ATTENDANCE_FILE)
                student_records = attendance_df[attendance_df["ID"] == search_id]
                total_attended = len(student_records)
                breakfast_count = len(student_records[student_records["Meal"] == "Breakfast"])
                lunch_count = len(student_records[student_records["Meal"] == "Lunch"])

                st.info(f"🍽️ Total Attendances: {total_attended} | 🥐 Breakfast: {breakfast_count} | 🍛 Lunch: {lunch_count}")

                meal = st.radio("Select Meal to Mark Attendance", ["Breakfast", "Lunch"])
                if st.button("Mark Attendance"):
                    now = datetime.now()
                    record = {
                        "ID": search_id,
                        "Name": student_name,
                        "Meal": meal,
                        "Date": now.date(),
                        "Time": now.strftime("%H:%M:%S")
                    }
                    pd.DataFrame([record]).to_csv(ATTENDANCE_FILE, mode='a', header=False, index=False)
                    st.success(f"✅ Attendance marked for {student_name} ({meal})")
            else:
                st.error("❌ No student found with that ID.")
        except ValueError:
            st.error("❌ ID must be a number.")

# ---- Show Today's Attendance ----
elif menu == "View Today's Attendance":
    st.header("📋 Today's Attendance Log")
    if st.checkbox("Show Attendance Table"):
        try:
            df = pd.read_csv(ATTENDANCE_FILE)
            today = pd.Timestamp(datetime.now().date())
            df["Date"] = pd.to_datetime(df["Date"])
            today_df = df[df["Date"] == today]

            if not today_df.empty:
                attendance_summary = today_df.groupby("ID").agg(
                    Total_Attendance=("ID", "count"),
                    Name=("Name", "first"),
                    Breakfast=("Meal", lambda x: (x == "Breakfast").sum()),
                    Lunch=("Meal", lambda x: (x == "Lunch").sum())
                ).reset_index()

                st.dataframe(attendance_summary)
            else:
                st.info("ℹ️ No attendance records for today.")
        except Exception as e:
            st.error("❌ Unable to read attendance file.")

# ---- Delete Student ----
elif menu == "Delete Student":
    st.header("🗑️ Delete Student")
    delete_id = st.text_input("Enter Student ID to delete", max_chars=10)

    if delete_id:
        try:
            delete_id = int(delete_id)
            students_df = pd.read_csv(STUDENT_FILE)
            match = students_df[students_df["ID"] == delete_id]

            if not match.empty:
                student_name = match.iloc[0]["Name"]
                st.success(f"✅ Student Found: {student_name}")

                if st.button(f"Delete {student_name}"):
                    students_df = students_df[students_df["ID"] != delete_id]
                    students_df.to_csv(STUDENT_FILE, index=False)

                    attendance_df = pd.read_csv(ATTENDANCE_FILE)
                    attendance_df = attendance_df[attendance_df["ID"] != delete_id]
                    attendance_df.to_csv(ATTENDANCE_FILE, index=False)

                    st.success(f"✅ Student '{student_name}' and all related attendance records have been deleted.")
            else:
                st.error("❌ No student found with that ID.")
        except ValueError:
            st.error("❌ ID must be a number.")
