from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from models.models import db, CollectionSchedule, Report

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/schedule')
def schedule():
    # Group schedules by area
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
        address = request.form['address']
        waste_type = request.form['waste_type']
        
        new_report = Report(address=address, waste_type=waste_type)
        db.session.add(new_report)
        db.session.commit()
        
        flash('Report submitted successfully!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('report.html')