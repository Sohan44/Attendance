import tkinter as tk
from tkinter import *
import os
import cv2
import pandas as pd
import datetime
import time
import csv
from PIL import ImageTk, Image

haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = "TrainingImageLabel\\Trainner.yml"
trainimage_path = "TrainingImage"
studentdetail_path = "StudentDetails\\studentdetails.csv"
attendance_path = "Attendance"


def subjectChoose(text_to_speech):
    def FillAttendance():
        sub = tx.get()
        if sub == "":
            t = "Please enter the subject name!!!"
            text_to_speech(t)
            return

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        try:
            recognizer.read(trainimagelabel_path)
        except:
            e = "Model not found, please train the model"
            Notifica.configure(text=e, bg="black", fg="yellow", width=33, font=("times", 15, "bold"))
            Notifica.place(x=20, y=250)
            text_to_speech(e)
            return

        faceCascade = cv2.CascadeClassifier(haarcasecade_path)
        try:
            df = pd.read_csv(studentdetail_path)
        except:
            text_to_speech("Student details file not found!")
            return

        cam = cv2.VideoCapture(0)
        font_cv = cv2.FONT_HERSHEY_SIMPLEX
        col_names = ["Enrollment", "Name"]
        attendance = pd.DataFrame(columns=col_names)

        start_time = time.time()
        duration = 20  # seconds
        end_time = start_time + duration

        while True:
            ret, im = cam.read()
            if not ret:
                continue
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.2, 5)

            for (x, y, w, h) in faces:
                Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
                if conf < 70:
                    aa = df.loc[df["Enrollment"] == Id]["Name"].values
                    name_text = str(Id) + "-" + str(aa[0]) if len(aa) > 0 else str(Id)
                    attendance.loc[len(attendance)] = [Id, aa[0] if len(aa) > 0 else "Unknown"]
                    cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 4)
                    cv2.putText(im, name_text, (x, y - 10), font_cv, 1, (255, 255, 0), 2)
                else:
                    cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 4)
                    cv2.putText(im, "Unknown", (x, y - 10), font_cv, 1, (0, 0, 255), 2)

            cv2.imshow("Filling Attendance...", im)
            if cv2.waitKey(30) & 0xFF == 27 or time.time() > end_time:
                break

        cam.release()
        cv2.destroyAllWindows()

        if attendance.empty:
            text_to_speech("No Face found for attendance")
            return

        # Save attendance
        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H-%M-%S")
        path = os.path.join(attendance_path, sub)
        os.makedirs(path, exist_ok=True)
        fileName = f"{path}/{sub}_{date}_{timeStamp}.csv"
        attendance = attendance.drop_duplicates(["Enrollment"], keep="first")
        attendance[date] = 1
        attendance.to_csv(fileName, index=False)

        m = f"Attendance Filled Successfully for {sub}"
        Notifica.configure(text=m, bg="black", fg="yellow", width=33, font=("times", 15, "bold"))
        Notifica.place(x=20, y=250)
        text_to_speech(m)

        # Display attendance sheet
        show_csv_in_tk(fileName, f"Attendance of {sub}")

    # helper function to show CSV in Tkinter
    def show_csv_in_tk(file_path, title="CSV Viewer"):
        root = tk.Tk()
        root.title(title)
        root.configure(background="black")

        with open(file_path, newline="") as file:
            reader = csv.reader(file)
            for r, row in enumerate(reader):
                for c, val in enumerate(row):
                    label = tk.Label(root, text=val, width=12, height=1, fg="yellow",
                                     font=("times", 15, "bold"), bg="black", relief=RIDGE)
                    label.grid(row=r, column=c)
        root.mainloop()

    # Fixed function for viewing attendance
    def Attf():
        sub_name = tx.get()
        if sub_name == "":
            text_to_speech("Please enter the subject name!!!")
            return

        path_to_open = os.path.join(attendance_path, sub_name)
        if not os.path.exists(path_to_open):
            text_to_speech("No attendance sheets found for this subject")
            return

        # get latest CSV file
        csv_files = [f for f in os.listdir(path_to_open) if f.endswith(".csv")]
        if not csv_files:
            text_to_speech("No attendance sheets found for this subject")
            return

        latest_file = max([os.path.join(path_to_open, f) for f in csv_files], key=os.path.getctime)
        show_csv_in_tk(latest_file, f"Attendance of {sub_name}")

    # Tkinter GUI for subject input
    subject = Tk()
    subject.title("Subject")
    subject.geometry("580x320")
    subject.resizable(0, 0)
    subject.configure(background="black")

    titl = tk.Label(subject, text="Enter the Subject Name", bg="black", fg="green", font=("arial", 25))
    titl.place(x=160, y=12)

    Notifica = tk.Label(subject, text="", bg="yellow", fg="black", width=33, height=2, font=("times", 15, "bold"))

    tx = tk.Entry(subject, width=15, bd=5, bg="black", fg="yellow", relief=RIDGE, font=("times", 30, "bold"))
    tx.place(x=190, y=100)

    fill_a = tk.Button(subject, text="Fill Attendance", command=FillAttendance, bd=7,
                       font=("times new roman", 15), bg="black", fg="yellow", height=2, width=12, relief=RIDGE)
    fill_a.place(x=195, y=170)

    attf = tk.Button(subject, text="Check Sheets", command=Attf, bd=7,
                     font=("times new roman", 15), bg="black", fg="yellow", height=2, width=10, relief=RIDGE)
    attf.place(x=360, y=170)

    subject.mainloop()
