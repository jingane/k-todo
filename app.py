from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedule.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    internal_today = db.Column(db.Text, nullable=True)
    external_today = db.Column(db.Text, nullable=True)
    internal_tomorrow = db.Column(db.Text, nullable=True)
    external_tomorrow = db.Column(db.Text, nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    today = datetime.now(pytz.timezone('Europe/Berlin')).date()
    schedule = Schedule.query.filter_by(date=today).first()
    if not schedule:
        schedule = Schedule(date=today)
        db.session.add(schedule)
        db.session.commit()
    return render_template('index.html', schedule=schedule)

@app.route('/update', methods=['POST'])
@login_required
def update():
    today = datetime.now(pytz.timezone('Europe/Berlin')).date()
    schedule = Schedule.query.filter_by(date=today).first()
    if schedule:
        schedule.internal_today = request.form['internal_today']
        schedule.external_today = request.form['external_today']
        schedule.internal_tomorrow = request.form['internal_tomorrow']
        schedule.external_tomorrow = request.form['external_tomorrow']
        db.session.commit()
    return '', 204

def update_schedule():
    today = datetime.now(pytz.timezone('Europe/Berlin')).date()
    tomorrow = today + timedelta(days=1)
    today_schedule = Schedule.query.filter_by(date=today).first()
    tomorrow_schedule = Schedule.query.filter_by(date=tomorrow).first()
    if not tomorrow_schedule:
        tomorrow_schedule = Schedule(date=tomorrow)
        db.session.add(tomorrow_schedule)
    if today_schedule:
        tomorrow_schedule.internal_today = today_schedule.internal_tomorrow
        tomorrow_schedule.external_today = today_schedule.external_tomorrow
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
