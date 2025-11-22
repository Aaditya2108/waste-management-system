from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import db, CollectionSchedule, Report

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Simple admin authentication (demo purpose only)
ADMIN_PASSWORD = 'admin123'

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            # In production, use Flask-Login with proper session management
            return redirect(url_for('admin.dashboard'))
        flash('Invalid password', 'error')
    return render_template('admin_login.html')

@admin_bp.route('/dashboard')
def dashboard():
    # Show stats and reports
    total_reports = Report.query.count()
    pending_reports = Report.query.filter_by(status='Pending').count()
    schedules = CollectionSchedule.query.all()
    recent_reports = Report.query.order_by(Report.reported_at.desc()).limit(10).all()
    
    return render_template('admin.html', 
                         total_reports=total_reports,
                         pending_reports=pending_reports,
                         schedules=schedules,
                         reports=recent_reports)

@admin_bp.route('/resolve/<int:report_id>')
def resolve_report(report_id):
    report = Report.query.get_or_404(report_id)
    report.status = 'Resolved'
    db.session.commit()
    flash('Report marked as resolved!', 'success')
    return redirect(url_for('admin.dashboard'))