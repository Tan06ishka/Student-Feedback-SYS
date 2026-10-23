import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import pandas as pd

# ================= DATABASE =================
def get_connection():
    return sqlite3.connect("feedback.db")

def setup_database():
    try:
        con = get_connection()
        cursor = con.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            rollno TEXT,
            teacher_rating INTEGER,
            lab_rating INTEGER,
            infra_rating INTEGER,
            comments TEXT,
            facilities TEXT
        )
        """)

        con.commit()
        con.close()

    except Exception as e:
        messagebox.showerror("DB Error", str(e))

# ================= SUBMIT =================
def submit_feedback():
    name = name_entry.get().strip()
    roll = roll_entry.get().strip()
    teacher = teacher_combo.get()
    lab = lab_combo.get()
    infra = infra_combo.get()
    comments = comment_text.get("1.0", tk.END).strip()

    if name == "" or roll == "":
        messagebox.showerror("Error", "Name and Roll No are required!")
        return

    if teacher == "" or lab == "" or infra == "":
        messagebox.showerror("Error", "Please select all ratings!")
        return

    facilities = []
    if lab_check.get(): facilities.append("Lab")
    if library_check.get(): facilities.append("Library")
    if clean_check.get(): facilities.append("Cleanliness")

    facilities_str = ", ".join(facilities) if facilities else "None"

    user_comment = comments  # ONLY USER COMMENT

    try:
        con = get_connection()
        cursor = con.cursor()

        cursor.execute("""
        INSERT INTO feedback 
        (name, rollno, teacher_rating, lab_rating, infra_rating, comments, facilities)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, roll, teacher, lab, infra, user_comment, facilities_str))

        con.commit()
        con.close()

        messagebox.showinfo("Success", "Feedback Submitted Successfully!")
        clear_fields()
        load_data()

    except Exception as e:
        messagebox.showerror("DB Error", str(e))

# ================= CLEAR =================
def clear_fields():
    name_entry.delete(0, tk.END)
    roll_entry.delete(0, tk.END)
    teacher_combo.set("")
    lab_combo.set("")
    infra_combo.set("")
    comment_text.delete("1.0", tk.END)
    lab_check.set(0)
    library_check.set(0)
    clean_check.set(0)

# ================= LOAD DATA =================
def load_data():
    try:
        for row in tree.get_children():
            tree.delete(row)

        con = get_connection()
        cursor = con.cursor()

        cursor.execute("SELECT * FROM feedback")

        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

        con.close()

    except Exception as e:
        messagebox.showerror("Load Error", str(e))

# ================= EXPORT CSV =================
def export_csv():
    try:
        con = get_connection()
        df = pd.read_sql_query("SELECT * FROM feedback", con)
        df.to_csv("feedback.csv", index=False)
        con.close()

        messagebox.showinfo("Success", "Exported to feedback.csv!")

    except Exception as e:
        messagebox.showerror("Export Error", str(e))

# ================= ANALYZE =================
def analyze():
    try:
        con = get_connection()
        df = pd.read_sql_query("SELECT * FROM feedback", con)
        con.close()

        if df.empty:
            messagebox.showwarning("Warning", "No data found!")
            return

        result = (
            f"Total Responses: {len(df)}\n"
            f"Teacher Avg: {df['teacher_rating'].mean():.2f}\n"
            f"Lab Avg: {df['lab_rating'].mean():.2f}\n"
            f"Infrastructure Avg: {df['infra_rating'].mean():.2f}"
        )

        df.describe().to_csv("summary_report.csv")

        messagebox.showinfo("Analysis Result", result)

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ================= DELETE ALL =================
def clear_all_records():
    password = simpledialog.askstring(
        "Password Required",
        "Enter admin password:",
        show="*"
    )

    if password != "admin123":
        messagebox.showerror("Access Denied", "Incorrect password!")
        return

    confirm = messagebox.askyesno("Confirm", "Delete ALL records?")
    if not confirm:
        return

    con = get_connection()
    cursor = con.cursor()

    cursor.execute("DELETE FROM feedback")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='feedback'")

    con.commit()
    con.close()

    for row in tree.get_children():
        tree.delete(row)

    messagebox.showinfo("Success", "All records deleted and ID reset!")

# ================= GUI =================
root = tk.Tk()
root.title("Tanishka Feedback System")
root.geometry("750x700")
root.configure(bg="#f5f6fa")

# TITLE
title = tk.Label(
    root,
    text="Student Feedback System",
    font=("Helvetica", 18, "bold"),
    bg="#2f3640",
    fg="white",
    pady=10
)
title.pack(fill="x")

subtitle = tk.Label(
    root,
    text="Department of Computer Engineering | AY 2025-26",
    bg="#dcdde1"
)
subtitle.pack(fill="x")

# MAIN FRAME
main_frame = tk.Frame(root, bg="#ffffff")
main_frame.pack(pady=10)

# FORM
form_frame = tk.LabelFrame(main_frame, text="Student Details", padx=20, pady=15)
form_frame.grid(row=0, column=0, padx=10, pady=10)

tk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky="w")
name_entry = ttk.Entry(form_frame, width=25)
name_entry.grid(row=0, column=1)

tk.Label(form_frame, text="Roll No:").grid(row=1, column=0, sticky="w")
roll_entry = ttk.Entry(form_frame, width=25)
roll_entry.grid(row=1, column=1)

# RATINGS
rating_frame = tk.LabelFrame(main_frame, text="Ratings", padx=20, pady=15)
rating_frame.grid(row=0, column=1, padx=10, pady=10)

ratings = ["1", "2", "3", "4", "5"]

tk.Label(rating_frame, text="Teacher:").grid(row=0, column=0)
teacher_combo = ttk.Combobox(rating_frame, values=ratings, width=10, state="readonly")
teacher_combo.grid(row=0, column=1)

tk.Label(rating_frame, text="Lab:").grid(row=1, column=0)
lab_combo = ttk.Combobox(rating_frame, values=ratings, width=10, state="readonly")
lab_combo.grid(row=1, column=1)

tk.Label(rating_frame, text="Infra:").grid(row=2, column=0)
infra_combo = ttk.Combobox(rating_frame, values=ratings, width=10, state="readonly")
infra_combo.grid(row=2, column=1)

# FACILITIES
facility_frame = tk.LabelFrame(main_frame, text="Facilities", padx=20, pady=15)
facility_frame.grid(row=1, column=0, padx=10, pady=10)

lab_check = tk.IntVar()
library_check = tk.IntVar()
clean_check = tk.IntVar()

tk.Checkbutton(facility_frame, text="Lab Facility", variable=lab_check).pack(anchor="w")
tk.Checkbutton(facility_frame, text="Library Facility", variable=library_check).pack(anchor="w")
tk.Checkbutton(facility_frame, text="Cleanliness", variable=clean_check).pack(anchor="w")

# COMMENTS
comment_frame = tk.LabelFrame(main_frame, text="Comments", padx=20, pady=15)
comment_frame.grid(row=1, column=1, padx=10, pady=10)

comment_text = tk.Text(comment_frame, height=5, width=30)
comment_text.pack()

# BUTTONS
button_frame = tk.Frame(root, bg="#f5f6fa")
button_frame.pack(pady=10)

tk.Button(button_frame, text="Submit", command=submit_feedback,
          bg="#28a745", fg="white", width=12).grid(row=0, column=0)

tk.Button(button_frame, text="Clear", command=clear_fields, width=12).grid(row=0, column=1)

tk.Button(button_frame, text="Export CSV", command=export_csv, width=12).grid(row=0, column=2)

tk.Button(button_frame, text="Analyze", command=analyze, width=12).grid(row=0, column=3)

tk.Button(button_frame, text="Delete All", command=clear_all_records,
          bg="#e74c3c", fg="white", width=12).grid(row=0, column=4)

# TABLE
table_frame = tk.Frame(root)
table_frame.pack(pady=20)

columns = ("ID", "Name", "Roll", "Teacher", "Lab", "Infra", "Comments", "Facilities")

tree = ttk.Treeview(table_frame, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)

    if col == "Comments":
        tree.column(col, width=250)
    elif col == "Facilities":
        tree.column(col, width=150)
    else:
        tree.column(col, width=100)

tree.pack()

# INIT
setup_database()
load_data()

root.mainloop()