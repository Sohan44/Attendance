import pandas as pd
from glob import glob
import os
import tkinter as tk
from tkinter import *
from tkcalendar import DateEntry
from datetime import datetime

def subjectchoose(text_to_speech):
    def get_subject():
        subject_name = tx.get()
        if subject_name == "":
            text_to_speech("Please enter the subject name.")
            return None
        return subject_name

    def load_attendance(subject_name):
        file_paths = glob(f"Attendance\\{subject_name}\\{subject_name}*.csv")
        if not file_paths:
            text_to_speech("No attendance files found for this subject.")
            return None, None, None

        # Load all CSVs
        df_list = [pd.read_csv(f) for f in file_paths]

        # Start with the first file
        df = df_list[0]

        # Instead of merge (which causes duplicate date columns),
        # use combine_first to fill missing values from other files
        for d in df_list[1:]:
            # Align on Enrollment + Name
            df = df.set_index(["Enrollment", "Name"]).combine_first(
                d.set_index(["Enrollment", "Name"])
            ).reset_index()

        df.fillna("", inplace=True)

        # Extract date columns (skip Enrollment + Name)
        date_cols = df.columns[2:]
        date_map = {col: pd.to_datetime(col, errors='coerce') for col in date_cols}
        return df, date_cols, date_map

    def show_daily_attendance():
        subject_name = get_subject()
        if not subject_name:
            return

        df, date_cols, date_map = load_attendance(subject_name)
        if df is None:
            return

        today = datetime.today().date()

        calendar_map = {}
        for col, date in date_map.items():
            if pd.notnull(date) and date.date() <= today:
                month_key = date.strftime("%B %Y")
                if month_key not in calendar_map:
                    month_start = date.replace(day=1)
                    month_end = min((month_start + pd.offsets.MonthEnd(0)).date(), today)
                    full_range = pd.date_range(start=month_start, end=month_end)
                    calendar_map[month_key] = full_range

        for month, dates in calendar_map.items():
            for date in dates:
                col = date.strftime("%Y-%m-%d")
                if col not in df.columns:
                    df[col] = ""

        for col in df.columns:
            if col in ["Enrollment", "Name"]:
                continue
            try:
                date_obj = pd.to_datetime(col)
                if date_obj.date() > today:
                    df.drop(columns=[col], inplace=True)
                    continue
                if date_obj.weekday() in [5, 6]:
                    df[col] = df[col].apply(lambda x: "H" if x == "" else x)
                else:
                    df[col] = df[col].apply(lambda x: "A" if x == "" else x)
            except:
                df[col] = df[col].apply(lambda x: "A" if x == "" else x)

        root = tk.Toplevel()
        root.title("Monthly Daily Attendance")
        root.configure(bg="black")

        canvas = tk.Canvas(root, bg="black")
        frame = tk.Frame(canvas, bg="black")
        v_scroll = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        h_scroll = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", on_configure)

        row_offset = 0
        for month, dates in calendar_map.items():
            cols = [date.strftime("%Y-%m-%d") for date in dates]
            tk.Label(frame, text=month, font=("Arial", 16, "bold"), fg="cyan", bg="black").grid(row=row_offset, column=0, columnspan=20, pady=10)
            row_offset += 1

            headers = ["Enrollment", "Name"] + cols + ["%"]
            for c, h in enumerate(headers):
                tk.Label(frame, text=h, fg="yellow", bg="black", font=("Arial", 10, "bold"), width=12).grid(row=row_offset, column=c)
            row_offset += 1

            for _, row in df.iterrows():
                tk.Label(frame, text=row["Enrollment"], fg="white", bg="black", font=("Arial", 10), width=12).grid(row=row_offset, column=0)
                tk.Label(frame, text=row["Name"], fg="white", bg="black", font=("Arial", 10), width=12).grid(row=row_offset, column=1)

                present_count = 0
                valid_days = 0
                for i, col in enumerate(cols):
                    val = row[col] if col in row else "A"
                    if isinstance(val, (int, float)):
                        val = "P" if val == 1 else "A"
                    color = "green" if val == "P" else "red" if val == "A" else "gray"
                    tk.Label(frame, text=val, fg=color, bg="black", font=("Arial", 10), width=12).grid(row=row_offset, column=i+2)

                    if val in ["P", "A"]:
                        valid_days += 1
                        if val == "P":
                            present_count += 1

                percent = round((present_count / valid_days) * 100) if valid_days > 0 else 0
                tk.Label(frame, text=f"{percent}%", fg="cyan", bg="black", font=("Arial", 10, "bold"), width=12).grid(row=row_offset, column=len(cols)+2)
                row_offset += 1
            row_offset += 1

        root.mainloop()

    def mark_holiday():
        date = holiday_entry.get_date().strftime("%Y-%m-%d")
        if date == "":
            text_to_speech("Please select a holiday date")
            return

        for folder in os.listdir("Attendance"):
            path = os.path.join("Attendance", folder)
            if os.path.isdir(path):
                for file in glob(os.path.join(path, "*.csv")):
                    df = pd.read_csv(file)
                    if date in df.columns:
                        df[date] = "H"
                        df.to_csv(file, index=False)
        text_to_speech(f"{date} marked as holiday for ALL subjects.")

    def cancel_holiday():
        date = holiday_entry.get_date().strftime("%Y-%m-%d")
        if date == "":
            text_to_speech("Please select a date to cancel holiday")
            return

        for folder in os.listdir("Attendance"):
            path = os.path.join("Attendance", folder)
            if os.path.isdir(path):
                for file in glob(os.path.join(path, "*.csv")):
                    df = pd.read_csv(file)
                    if date in df.columns:
                        df[date] = df[date].replace("H", "A")
                        df.to_csv(file, index=False)
        text_to_speech(f"Holiday on {date} has been cancelled for ALL subjects.")

    def open_subject_folder():
        subject_name = get_subject()
        if not subject_name:
            return
        folder = f"Attendance\\{subject_name}"
        if os.path.exists(folder):
            os.startfile(folder)
        else:
            text_to_speech("No attendance folder for this subject.")

    # UI
    subject = tk.Toplevel()
    subject.title("Attendance Dashboard")
    subject.geometry("750x520")
    subject.resizable(0, 0)
    subject.configure(bg="black")

    tk.Label(subject, text="Attendance Viewer", bg="black", fg="green", font=("arial", 25)).place(x=200, y=12)

    tk.Label(subject, text="Subject Name", width=12, height=2, bg="black", fg="yellow",
             bd=5, relief=RIDGE, font=("times new roman", 15)).place(x=30, y=100)

    tx = tk.Entry(subject, width=15, bd=5, bg="black", fg="yellow",
                  relief=RIDGE, font=("times", 30, "bold"))
    tx.place(x=200, y=100)

    tk.Button(subject, text="Show Daily Attendance", command=show_daily_attendance, bd=7,
              font=("times new roman", 15), bg="black", fg="yellow",
              height=2, width=20, relief=RIDGE).place(x=180, y=170)

    tk.Button(subject, text="Open Folder", command=open_subject_folder, bd=7,
              font=("times new roman", 12), bg="black", fg="yellow",
              height=1, width=12, relief=RIDGE).place(x=580, y=100)

    tk.Label(subject, text="Choose Holiday Date", bg="black", fg="yellow",
             font=("times new roman", 12)).place(x=30, y=300)

    holiday_entry =DateEntry(subject, width=15, background="black", foreground="yellow",
                              borderwidth=2, date_pattern="yyyy-mm-dd",
                              font=("times", 15, "bold"))
    holiday_entry.place(x=250, y=300)

    tk.Button(subject, text="Mark Holiday", command=mark_holiday, bd=5,
              font=("times new roman", 12), bg="red", fg="white",
              height=1, width=20, relief=RIDGE).place(x=430, y=297)

    tk.Button(subject, text="Remove Holiday", command=cancel_holiday, bd=5,
              font=("times new roman", 12), bg="orange", fg="black",
              height=1, width=20, relief=RIDGE).place(x=430, y=340)

    subject.mainloop()