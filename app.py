from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime
import json
import os
from functools import wraps
import hashlib

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Файлы для хранения данных (в реальном приложении использовалась бы БД)
DATA_FILE = 'data.json'
USERS_FILE = 'users.json'

def load_data():
    """Загрузка данных из файла"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'students': [],
        'classes': [],
        'grades': []
    }

def save_data(data):
    """Сохранение данных в файл"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_users():
    """Загрузка пользователей из файла"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'users': []
    }

def save_users(users_data):
    """Сохранение пользователей в файл"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)

def hash_password(password):
    """Хеширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    """Декоратор для защиты админских маршрутов"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему для доступа к этой странице', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Публичная главная страница"""
    return render_template('public_index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if 'user_id' in session:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        users_data = load_users()
        user = next((u for u in users_data['users'] if u['email'] == email), None)
        
        if user and user['password'] == hash_password(password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Неверный email или пароль', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if 'user_id' in session:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('register.html')
        
        users_data = load_users()
        
        # Проверка на существующего пользователя
        if any(u['email'] == email for u in users_data['users']):
            flash('Пользователь с таким email уже существует', 'error')
            return render_template('register.html')
        
        # Создание нового пользователя
        new_user = {
            'id': len(users_data['users']) + 1,
            'name': name,
            'email': email,
            'password': hash_password(password),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        users_data['users'].append(new_user)
        save_users(users_data)
        
        flash('Регистрация успешна! Теперь вы можете войти', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Выход из системы"""
    session.clear()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    """Админская панель"""
    data = load_data()
    stats = {
        'total_students': len(data['students']),
        'total_classes': len(data['classes']),
        'recent_grades': len([g for g in data['grades'] if g.get('date', '') == datetime.now().strftime('%Y-%m-%d')])
    }
    return render_template('admin/index.html', stats=stats)

@app.route('/admin/students')
@login_required
def students():
    """Список студентов"""
    data = load_data()
    return render_template('students.html', students=data['students'])

@app.route('/admin/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    """Добавление студента"""
    if request.method == 'POST':
        data = load_data()
        student = {
            'id': len(data['students']) + 1,
            'name': request.form['name'],
            'surname': request.form['surname'],
            'class_id': int(request.form['class_id']) if request.form['class_id'] else None,
            'email': request.form['email'],
            'phone': request.form['phone'],
            'birth_date': request.form['birth_date']
        }
        data['students'].append(student)
        save_data(data)
        flash('Студент успешно добавлен!', 'success')
        return redirect(url_for('students'))
    
    data = load_data()
    return render_template('add_student.html', classes=data['classes'])

@app.route('/admin/classes')
@login_required
def classes():
    """Список классов"""
    data = load_data()
    return render_template('classes.html', classes=data['classes'])

@app.route('/admin/classes/add', methods=['GET', 'POST'])
@login_required
def add_class():
    """Добавление класса"""
    if request.method == 'POST':
        data = load_data()
        class_item = {
            'id': len(data['classes']) + 1,
            'name': request.form['name'],
            'teacher': request.form['teacher'],
            'room': request.form['room'],
            'schedule': request.form['schedule']
        }
        data['classes'].append(class_item)
        save_data(data)
        flash('Класс успешно добавлен!', 'success')
        return redirect(url_for('classes'))
    
    return render_template('add_class.html')

@app.route('/admin/grades')
@login_required
def grades():
    """Список оценок"""
    data = load_data()
    # Обогащаем оценки информацией о студентах и предметах
    enriched_grades = []
    for grade in data['grades']:
        student = next((s for s in data['students'] if s['id'] == grade['student_id']), None)
        enriched_grades.append({
            **grade,
            'student_name': f"{student['name']} {student['surname']}" if student else 'Неизвестно'
        })
    return render_template('grades.html', grades=enriched_grades)

@app.route('/admin/grades/add', methods=['GET', 'POST'])
@login_required
def add_grade():
    """Добавление оценки"""
    if request.method == 'POST':
        data = load_data()
        grade = {
            'id': len(data['grades']) + 1,
            'student_id': int(request.form['student_id']),
            'subject': request.form['subject'],
            'grade': int(request.form['grade']),
            'date': request.form['date'],
            'comment': request.form['comment']
        }
        data['grades'].append(grade)
        save_data(data)
        flash('Оценка успешно добавлена!', 'success')
        return redirect(url_for('grades'))
    
    data = load_data()
    return render_template('add_grade.html', students=data['students'])

@app.route('/admin/api/stats')
@login_required
def api_stats():
    """API для статистики"""
    data = load_data()
    return jsonify({
        'students': len(data['students']),
        'classes': len(data['classes']),
        'grades': len(data['grades']),
        'avg_grade': sum(g['grade'] for g in data['grades']) / len(data['grades']) if data['grades'] else 0
    })

def init_default_admin():
    """Создание администратора по умолчанию при первом запуске"""
    users_data = load_users()
    if len(users_data['users']) == 0:
        default_admin = {
            'id': 1,
            'name': 'Администратор',
            'email': 'admin@school.ru',
            'password': hash_password('admin123'),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'is_admin': True
        }
        users_data['users'].append(default_admin)
        save_users(users_data)
        print("=" * 50)
        print("Создан администратор по умолчанию:")
        print("Email: admin@school.ru")
        print("Пароль: admin123")
        print("=" * 50)

if __name__ == '__main__':
    init_default_admin()
    app.run(debug=True)

