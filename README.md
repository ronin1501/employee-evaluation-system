# Employee Evaluation System

A full-stack web application for employee evaluation, HR workflow automation, and personnel performance management.

## Features

- Employee management
- Department management
- Personnel evaluation
- Competency analysis
- Role-based authentication
- PDF report generation
- Competency charts and analytics
- SQLite database integration

## Tech Stack

- Python
- Flask
- SQLite
- SQLAlchemy
- Flask-Login
- Jinja2
- HTML/CSS
- Matplotlib
- ReportLab
- NumPy

## 📁 Project Structure

```text
employee-evaluation-system/
│── app.py                # Application entry point and routing
│── database.py           # Database layer and SQLite connection
│── models.py             # Evaluation logic and chart generation
│── database.db           # SQLite database

├── static/
│   └── charts/           # Generated charts storage

└── templates/
    ├── base.html         # Base layout template
    ├── index.html        # Main dashboard page
    └── assessment.html   # Personnel assessment form
```

## 📸 Screenshots

### 🔐 Login Page
![Login](screenshots/login.png)

### 🏠 Dashboard
![Dashboard](screenshots/dashboard.png)

### 👥 Employee Management
![Employees](screenshots/employees.png)

### 📋 Personnel Assessment
![Assessment](screenshots/assessment.png)

### 📊 Charts & Analytics
![Charts](screenshots/charts_1.png)
![Charts](screenshots/charts_2.png)

## 🚀 Usage

The system allows users to:

- authenticate and manage user sessions;
- manage employee records;
- perform personnel evaluation;
- analyze employee performance;
- generate charts and analytical reports;
- manage departments and employee data;
- export reports in PDF format.

The application is intended for HR process automation and personnel assessment workflows.

## ⚙️ Installation

### Clone repository

```bash
git clone https://github.com/ronin1501/employee-evaluation-system.git
cd employee-evaluation-system
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run application

Using Python:

```bash
python app.py
```

or using shell script on macOS/Linux:

```bash
chmod +x start.sh
./start.sh
```

### Local server

After running the application, it will be available at:

```text
http://127.0.0.1:5000/
```

---

## 💻 Environment

The project was developed and tested on:

- macOS
- Python 3.x
- Flask

## 📌 Project Status

The project is completed as an educational full-stack web application and can be extended with additional HR analytics features.

## 👩‍💻 Author

Elena Schetchikova

GitHub: https://github.com/ronin1501
