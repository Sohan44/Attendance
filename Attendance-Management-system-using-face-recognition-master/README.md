# Face-Based Attendance Management System using Python & OpenCV

## Project Overview
This project is an enhanced Face-Based Attendance Management System developed using Python and OpenCV.
It performs face recognition for attendance marking and also includes advanced attendance management features.

This repository is a modified and extended version of an open-source project.
Significant improvements have been made to support real-world academic attendance requirements.

Enhanced and maintained by: Sohan Bele

## Key Enhancements
- Subject-wise attendance tracking
- Fixed weekend holidays (Saturday and Sunday)
- Option to manually mark holidays
- Option to remove marked holidays
- Monthly attendance percentage calculation
- Improved attendance structure and logic

## Technologies Used
- Python
- OpenCV
- NumPy
- CSV File Handling

## How to Run the Project
1. Download or clone this repository.
2. Open the project in PyCharm or any Python IDE.
3. Install required dependencies using:
   pip install -r requirements.txt
4. Create a folder named TrainingImage inside the project directory.
5. Open attendance.py and automaticAttendance.py and update file paths according to your system.
6. Run the attendance.py file.

## Project Workflow
1. Register a student by capturing facial images.
2. Train the model automatically.
3. Mark attendance using face recognition.
4. Manage subject-wise attendance.
5. Mark or remove holidays.
6. Generate monthly attendance percentage reports.

## Notes
- Saturday and Sunday are treated as default holidays.
- Proper lighting is recommended while capturing facial images.

## License
This project is based on an open-source implementation and is intended for educational purposes.
