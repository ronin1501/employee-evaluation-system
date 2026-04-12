from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from database import init_db, get_db_connection
from models import calculate_assessment, generate_chart, db
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import io
import sqlite3
from functools import wraps

app = Flask(__name__)
# Секретный ключ для сессий
app.secret_key = os.environ.get('SECRET_KEY') or 'vkr_2026_secure_key'

# Настройка базы данных SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- ДЕКОРАТОРЫ БЕЗОПАСНОСТИ ---
def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Доступ запрещен: требуются права администратора")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return wrapped

# --- РЕГИСТРАЦИЯ РУССКОГО ШРИФТА ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "arialmt.ttf")

try:
    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont('RussianFont', FONT_PATH))
        USE_RUSSIAN = True
        print(f"[*] Шрифт успешно зарегистрирован: {FONT_PATH}")
    else:
        print("[!] ВНИМАНИЕ: arialmt.ttf не найден!")
        USE_RUSSIAN = False
except Exception as e:
    print(f"[!] Ошибка шрифта: {e}")
    USE_RUSSIAN = False

# --- АВТОРИЗАЦИЯ ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        
        flash('Неверное имя пользователя или пароль')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- ГЛАВНАЯ СТРАНИЦА ---
@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    # Статистика
    total_staff = conn.execute('SELECT COUNT(*) FROM staff WHERE is_active = 1').fetchone()[0]
    total_assessments = conn.execute('SELECT COUNT(*) FROM results').fetchone()[0]
    avg_score = conn.execute('SELECT ROUND(AVG(total_score), 2) FROM results').fetchone()[0] or 0
    
    # ИСПРАВЛЕНО: Берем только уникальные имена тех, кто прошел оценку, чтобы работало сравнение
    staff_list = conn.execute('''
        SELECT DISTINCT s.name 
        FROM staff s
        JOIN results r ON s.id = r.staff_id
        WHERE s.is_active = 1
    ''').fetchall()
    
    conn.close()
    return render_template('index.html', 
                           total_staff=total_staff, 
                           total_assessments=total_assessments, 
                           avg_score=avg_score, 
                           staff_list=staff_list)

# --- УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ (ADMIN) ---
@app.route('/users')
@login_required
@admin_required
def users_list():
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, role FROM users').fetchall()
    conn.close()
    return render_template('users_list.html', users=users)

@app.route('/add_user', methods=['POST'])
@login_required
@admin_required
def add_user():
    username = request.form.get('username', '').strip()
    password = request.form.get('password')
    role = request.form.get('role') or 'manager'
    if username and password:
        hashed_pw = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_pw, role))
            conn.commit()
            flash(f'Пользователь {username} добавлен')
        except sqlite3.IntegrityError:
            flash('Ошибка: Такой логин уже существует.')
        conn.close()
    return redirect(url_for('users_list'))

# --- СОТРУДНИКИ ---
@app.route('/staff')
@login_required
def staff_list():
    conn = get_db_connection()
    staff = conn.execute('''
        SELECT s.*, d.name as dept_name 
        FROM staff s 
        LEFT JOIN departments d ON s.dept_id = d.id 
        WHERE s.is_active = 1
    ''').fetchall()
    depts = conn.execute('SELECT * FROM departments').fetchall()
    conn.close()
    return render_template('staff_list.html', staff=staff, depts=depts)

@app.route('/add_staff', methods=['POST'])
@login_required
@admin_required
def add_staff():
    name = request.form.get('name')
    dept_id = request.form.get('dept_id')
    if name and dept_id:
        conn = get_db_connection()
        conn.execute("INSERT INTO staff (name, dept_id) VALUES (?, ?)", (name, dept_id))
        conn.commit()
        conn.close()
    return redirect(url_for('staff_list'))

# --- ОЦЕНКА И ЖУРНАЛ ---
@app.route('/results')
@login_required
def results_list():
    conn = get_db_connection()
    results = conn.execute('''
        SELECT r.*, s.name, d.name as department 
        FROM results r 
        JOIN staff s ON r.staff_id = s.id 
        JOIN departments d ON s.dept_id = d.id 
        ORDER BY r.id DESC
    ''').fetchall()
    conn.close()
    return render_template('results_list.html', results=results)

@app.route('/assess', methods=['GET', 'POST'])
@login_required
def assess():
    conn = get_db_connection()
    if request.method == 'POST':
        staff_id = request.form.get('staff_id')
        staff = conn.execute('SELECT name FROM staff WHERE id = ?', (staff_id,)).fetchone()
        
        if staff:
            s = int(request.form.get('soft', 3))
            h = int(request.form.get('hard', 3))
            e = int(request.form.get('eff', 3))
            
            score, verdict = calculate_assessment(s, h, e)
            date_now = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            generate_chart(staff['name'], [s, h, e])
            
            conn.execute('''
                INSERT INTO results (staff_id, soft_skills, hard_skills, efficiency, total_score, verdict, date_added, evaluated_by) 
                VALUES (?,?,?,?,?,?,?,?)
            ''', (staff_id, s, h, e, score, verdict, date_now, session['user_id']))
            conn.commit()
            flash(f'Оценка для {staff["name"]} сохранена.')
        
        conn.close()
        return redirect(url_for('results_list'))
    
    staff_active = conn.execute('''
        SELECT s.id, s.name, d.name as department 
        FROM staff s 
        LEFT JOIN departments d ON s.dept_id = d.id 
        WHERE s.is_active = 1
    ''').fetchall()
    conn.close()
    return render_template('assessment.html', staff_list=staff_active)

# --- ЭКСПОРТ В PDF ---
@app.route('/export_pdf/<int:res_id>')
@login_required
def export_pdf(res_id):
    conn = get_db_connection()
    res = conn.execute('''
        SELECT r.*, s.name 
        FROM results r 
        JOIN staff s ON r.staff_id = s.id 
        WHERE r.id = ?
    ''', (res_id,)).fetchone()
    conn.close()

    if not res:
        return "Оценка не найдена", 404

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    
    if USE_RUSSIAN:
        p.setFont("RussianFont", 16)
    p.drawString(100, 810, f"ОТЧЕТ ПО СОТРУДНИКУ: {res['name']}")
    
    p.setLineWidth(1)
    p.line(100, 800, 500, 800)
    
    if USE_RUSSIAN:
        p.setFont("RussianFont", 12)
    p.drawString(100, 770, f"Дата проведения: {res['date_added']}")
    p.drawString(100, 750, f"Итоговый балл: {res['total_score']}")
    p.drawString(100, 730, f"Вердикт: {res['verdict']}")
    
    if USE_RUSSIAN:
        p.setFont("RussianFont", 10)
    p.drawString(100, 690, "ДЕТАЛИЗАЦИЯ КРИТЕРИЕВ:")
    p.drawString(120, 670, f"• Soft Skills: {res['soft_skills']}")
    p.drawString(120, 650, f"• Hard Skills: {res['hard_skills']}")
    p.drawString(120, 630, f"• Efficiency: {res['efficiency']}")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    
    filename = f"report_{res['name'].replace(' ', '_')}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

# --- ОТДЕЛЫ ---
@app.route('/departments')
@login_required
def departments_list():
    conn = get_db_connection()
    depts = conn.execute('SELECT * FROM departments').fetchall()
    conn.close()
    return render_template('departments_list.html', depts=depts)

@app.route('/add_department', methods=['POST'])
@login_required
@admin_required
def add_department():
    name = request.form.get('name', '').strip()
    if name:
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO departments (name) VALUES (?)", (name,))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('Отдел уже существует.')
        conn.close()
    return redirect(url_for('departments_list'))

@app.route('/archive_staff/<int:id>')
@login_required
@admin_required
def archive_staff(id):
    conn = get_db_connection()
    conn.execute('UPDATE staff SET is_active = 0 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Сотрудник перенесен в архив.')
    return redirect(url_for('staff_list'))

if __name__ == '__main__':
    charts_path = os.path.join(BASE_DIR, 'static', 'charts')
    if not os.path.exists(charts_path):
        os.makedirs(charts_path)
    
    init_db()
    app.run(debug=True, port=5000)