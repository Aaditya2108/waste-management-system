from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# ===== Configuration =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
class Config:
    SECRET_KEY = 'dev-secret-key-change-in-production'
    # FIX: Use 'instance' folder instead of 'data' for cloud deployment
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'waste.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# ===== Database Models =====
db = SQLAlchemy()

class CollectionSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(100), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    waste_type = db.Column(db.String(50), nullable=False)
    collection_time = db.Column(db.String(20), nullable=False)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(200), nullable=False)
    waste_type = db.Column(db.String(50), nullable=False)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')

# ===== Routes =====
from flask import Blueprint, render_template, request, redirect, url_for, flash

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/schedule')
def schedule():
    schedules = CollectionSchedule.query.all()
    areas = {}
    for s in schedules:
        if s.area not in areas:
            areas[s.area] = []
        areas[s.area].append(s)
    return render_template('schedule.html', areas=areas)

@main_bp.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        new_report = Report(address=request.form['address'], waste_type=request.form['waste_type'])
        db.session.add(new_report)
        db.session.commit()
        flash('Report submitted successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('report.html')

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
ADMIN_PASSWORD = 'admin123'

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            return redirect(url_for('admin.dashboard'))
        flash('Invalid password', 'error')
    return render_template('admin_login.html')

@admin_bp.route('/dashboard')
def dashboard():
    return render_template('admin.html', 
        total_reports=Report.query.count(),
        pending_reports=Report.query.filter_by(status='Pending').count(),
        schedules=CollectionSchedule.query.all(),
        reports=Report.query.order_by(Report.reported_at.desc()).limit(10).all())

@admin_bp.route('/resolve/<int:report_id>')
def resolve_report(report_id):
    report = Report.query.get_or_404(report_id)
    report.status = 'Resolved'
    db.session.commit()
    flash('Report marked as resolved!', 'success')
    return redirect(url_for('admin.dashboard'))

# ===== Application Factory =====
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    return app

app = create_app()

# ===== Create database and sample data =====
with app.app_context():
    # CRITICAL: Create instance directory before database operations
    instance_dir = os.path.join(BASE_DIR, 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    
    db.create_all()
    if not CollectionSchedule.query.first():
        sample_data = [
            CollectionSchedule(area="North District", day="Monday", waste_type="General", collection_time="7:00 AM"),
            CollectionSchedule(area="North District", day="Wednesday", waste_type="Recycling", collection_time="7:00 AM"),
            CollectionSchedule(area="South District", day="Tuesday", waste_type="General", collection_time="8:00 AM"),
            CollectionSchedule(area="South District", day="Friday", waste_type="Organic", collection_time="8:00 AM"),
        ]
        db.session.add_all(sample_data)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, port=5000)