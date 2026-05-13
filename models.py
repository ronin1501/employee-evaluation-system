import os

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MPL_CONFIG_DIR = os.path.join(BASE_DIR, ".matplotlib")
os.makedirs(MPL_CONFIG_DIR, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", MPL_CONFIG_DIR)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

db = SQLAlchemy()

# --- МОДЕЛИ ДАННЫХ ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    staff_members = db.relationship('Staff', backref='department', lazy=True)

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    is_active = db.Column(db.Integer, default=1)
    soft_skills = db.Column(db.Float, default=0.0)
    hard_skills = db.Column(db.Float, default=0.0)
    efficiency = db.Column(db.Float, default=0.0)

# --- ЛОГИКА ОЦЕНКИ ---
def calculate_assessment(soft, hard, eff):
    total = (soft * 0.3) + (hard * 0.4) + (eff * 0.3)
    if total >= 4.5:
        verdict = "Лидер (Категория A)"
    elif total >= 3.5:
        verdict = "Профессионал (Категория B)"
    elif total >= 2.5:
        verdict = "Средний уровень (Категория C)"
    else:
        verdict = "Требуется план развития (Категория D)"
    return round(total, 2), verdict

# --- ГЕНЕРАЦИЯ ДИАГРАММЫ КАК НА СКРИНШОТЕ ---
def generate_chart(staff_name, values):
    # Для эффекта "шестиугольника" со скриншота дублируем 3 параметра в 6 осей
    labels = ['Soft Skills', '', 'Hard Skills', '', 'Efficiency', '']
    # Значения: [Soft, Soft/2, Hard, Hard/2, Eff, Eff/2] для имитации объема
    expanded_values = [values[0], values[0]*0.8, values[1], values[1]*0.8, values[2], values[2]*0.8]
    num_vars = len(labels)
    
    # Цвета сегментов фона (RGB)
    colors = ['#4A90E2', '#50E3C2', '#50E3C2', '#F5A623', '#F5A623', '#4A90E2']
    
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    plot_values = expanded_values + [expanded_values[0]]
    plot_angles = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True), dpi=120)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    # 1. Цветная подложка (сегменты)
    for i in range(num_vars):
        ax.fill([angles[i], angles[(i+1)%num_vars], angles[(i+1)%num_vars], angles[i]], 
                [0, 0, 5, 5], color=colors[i], alpha=0.12, zorder=1)

    # 2. Основная фигура компетенций
    # Темная заливка в центре
    ax.fill(plot_angles, plot_values, color='#2c3e50', alpha=0.25, zorder=3)
    # Яркая линия контура
    ax.plot(plot_angles, plot_values, color='#34495e', linewidth=2, zorder=4)

    # 3. Круглые "иконки" на вершинах (как на скриншоте)
    main_indices = [0, 2, 4] # Индексы основных осей
    for i in main_indices:
        # Внешний белый круг
        ax.scatter(angles[i], expanded_values[i], color='white', s=250, zorder=10, edgecolor='#e2e8f0')
        # Внутренний цветной круг с буквой/иконкой (имитация)
        ax.scatter(angles[i], expanded_values[i], color=colors[i], s=100, zorder=11)

    # Настройки осей
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    plt.xticks(angles, labels, color='#2c3e50', size=10, fontweight='bold')
    plt.yticks([1, 2, 3, 4, 5], ["", "", "", "", ""], alpha=0) # Скрываем цифры осей
    plt.ylim(0, 5)

    # Сетка (белые линии как в UI)
    ax.grid(True, color='white', linewidth=1.5, zorder=2)
    ax.spines['polar'].set_visible(False)

    chart_dir = os.path.join('static', 'charts')
    if not os.path.exists(chart_dir):
        os.makedirs(chart_dir)
        
    filename = f"{staff_name.replace(' ', '_')}.png"
    path = os.path.join(chart_dir, filename)
    plt.savefig(path, transparent=True, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    return filename
