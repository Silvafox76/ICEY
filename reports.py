from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.inventory import InventoryItem
from src.models.job import Job
from src.models.assignment import InventoryAssignment
from datetime import datetime, timedelta
import csv
import io
import os

reports_bp = Blueprint('reports', __name__)

def check_permission(required_roles):
    """Decorator to check user permissions"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or user.role not in required_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@reports_bp.route('/reports/inventory-usage', methods=['GET'])
@jwt_required()
@check_permission(['admin', 'foreman', 'finance'])
def inventory_usage_report():
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        job_id = request.args.get('job_id')
        user_id = request.args.get('user_id')
        export_format = request.args.get('format', 'json')  # json or csv
        
        # Build query
        query = db.session.query(
            InventoryAssignment,
            InventoryItem,
            Job,
            User
        ).join(
            InventoryItem, InventoryAssignment.item_id == InventoryItem.id
        ).join(
            Job, InventoryAssignment.job_id == Job.id
        ).join(
            User, InventoryAssignment.user_id == User.id
        )
        
        # Apply filters
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(InventoryAssignment.check_out_time >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(InventoryAssignment.check_out_time <= end_dt)
        
        if job_id:
            query = query.filter(InventoryAssignment.job_id == job_id)
        
        if user_id:
            query = query.filter(InventoryAssignment.user_id == user_id)
        
        results = query.all()
        
        # Format data
        report_data = []
        for assignment, item, job, user in results:
            duration = None
            if assignment.check_in_time and assignment.check_out_time:
                duration = (assignment.check_in_time - assignment.check_out_time).total_seconds() / 3600  # hours
            
            report_data.append({
                'assignment_id': assignment.id,
                'item_sku': item.sku,
                'item_name': item.name,
                'item_category': item.category,
                'job_name': job.name,
                'job_claim_id': job.claim_id,
                'user_name': f"{user.first_name} {user.last_name}" if user.first_name else user.username,
                'user_role': user.role,
                'check_out_time': assignment.check_out_time.isoformat() if assignment.check_out_time else None,
                'check_in_time': assignment.check_in_time.isoformat() if assignment.check_in_time else None,
                'duration_hours': round(duration, 2) if duration else None,
                'status': assignment.status,
                'condition_at_checkout': assignment.condition_at_checkout,
                'condition_at_checkin': assignment.condition_at_checkin,
                'notes': assignment.notes
            })
        
        if export_format == 'csv':
            # Generate CSV
            output = io.StringIO()
            if report_data:
                writer = csv.DictWriter(output, fieldnames=report_data[0].keys())
                writer.writeheader()
                writer.writerows(report_data)
            
            # Create temporary file
            csv_content = output.getvalue()
            filename = f"inventory_usage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join('/tmp', filename)
            
            with open(filepath, 'w') as f:
                f.write(csv_content)
            
            return send_file(filepath, as_attachment=True, download_name=filename, mimetype='text/csv')
        
        return jsonify({
            'report_type': 'inventory_usage',
            'generated_at': datetime.utcnow().isoformat(),
            'filters': {
                'start_date': start_date,
                'end_date': end_date,
                'job_id': job_id,
                'user_id': user_id
            },
            'total_records': len(report_data),
            'data': report_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/reports/job-summary', methods=['GET'])
@jwt_required()
@check_permission(['admin', 'foreman', 'finance'])
def job_summary_report():
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')
        export_format = request.args.get('format', 'json')
        
        # Build query
        query = Job.query
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Job.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(Job.created_at <= end_dt)
        
        if status:
            query = query.filter(Job.status == status)
        
        jobs = query.all()
        
        # Format data with assignment counts
        report_data = []
        for job in jobs:
            assignment_count = InventoryAssignment.query.filter_by(job_id=job.id).count()
            active_assignments = InventoryAssignment.query.filter_by(
                job_id=job.id, status='checked_out'
            ).count()
            
            # Calculate job duration
            duration_days = None
            if job.start_date and job.end_date:
                duration_days = (job.end_date - job.start_date).days
            
            report_data.append({
                'job_id': job.id,
                'claim_id': job.claim_id,
                'xactimate_id': job.xactimate_id,
                'name': job.name,
                'location': job.location,
                'status': job.status,
                'priority': job.priority,
                'customer_name': job.customer_name,
                'start_date': job.start_date.isoformat() if job.start_date else None,
                'end_date': job.end_date.isoformat() if job.end_date else None,
                'duration_days': duration_days,
                'total_assignments': assignment_count,
                'active_assignments': active_assignments,
                'created_at': job.created_at.isoformat() if job.created_at else None
            })
        
        if export_format == 'csv':
            # Generate CSV
            output = io.StringIO()
            if report_data:
                writer = csv.DictWriter(output, fieldnames=report_data[0].keys())
                writer.writeheader()
                writer.writerows(report_data)
            
            # Create temporary file
            csv_content = output.getvalue()
            filename = f"job_summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join('/tmp', filename)
            
            with open(filepath, 'w') as f:
                f.write(csv_content)
            
            return send_file(filepath, as_attachment=True, download_name=filename, mimetype='text/csv')
        
        return jsonify({
            'report_type': 'job_summary',
            'generated_at': datetime.utcnow().isoformat(),
            'filters': {
                'start_date': start_date,
                'end_date': end_date,
                'status': status
            },
            'total_records': len(report_data),
            'data': report_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/reports/inventory-status', methods=['GET'])
@jwt_required()
@check_permission(['admin', 'foreman', 'finance'])
def inventory_status_report():
    try:
        export_format = request.args.get('format', 'json')
        
        # Get inventory status summary
        status_summary = db.session.query(
            InventoryItem.status,
            db.func.count(InventoryItem.id).label('count')
        ).group_by(InventoryItem.status).all()
        
        # Get category breakdown
        category_summary = db.session.query(
            InventoryItem.category,
            db.func.count(InventoryItem.id).label('count')
        ).group_by(InventoryItem.category).all()
        
        # Get items with current assignments
        items_with_assignments = db.session.query(
            InventoryItem,
            InventoryAssignment,
            Job,
            User
        ).join(
            InventoryAssignment, InventoryItem.id == InventoryAssignment.item_id
        ).join(
            Job, InventoryAssignment.job_id == Job.id
        ).join(
            User, InventoryAssignment.user_id == User.id
        ).filter(
            InventoryAssignment.status == 'checked_out'
        ).all()
        
        report_data = {
            'status_summary': [{'status': status, 'count': count} for status, count in status_summary],
            'category_summary': [{'category': category or 'Uncategorized', 'count': count} for category, count in category_summary],
            'items_in_use': []
        }
        
        for item, assignment, job, user in items_with_assignments:
            report_data['items_in_use'].append({
                'item_sku': item.sku,
                'item_name': item.name,
                'category': item.category,
                'job_name': job.name,
                'job_claim_id': job.claim_id,
                'assigned_to': f"{user.first_name} {user.last_name}" if user.first_name else user.username,
                'check_out_time': assignment.check_out_time.isoformat() if assignment.check_out_time else None,
                'expected_return': assignment.expected_return_date.isoformat() if assignment.expected_return_date else None
            })
        
        if export_format == 'csv':
            # Generate CSV for items in use
            output = io.StringIO()
            if report_data['items_in_use']:
                writer = csv.DictWriter(output, fieldnames=report_data['items_in_use'][0].keys())
                writer.writeheader()
                writer.writerows(report_data['items_in_use'])
            
            # Create temporary file
            csv_content = output.getvalue()
            filename = f"inventory_status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join('/tmp', filename)
            
            with open(filepath, 'w') as f:
                f.write(csv_content)
            
            return send_file(filepath, as_attachment=True, download_name=filename, mimetype='text/csv')
        
        return jsonify({
            'report_type': 'inventory_status',
            'generated_at': datetime.utcnow().isoformat(),
            'data': report_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/reports/overdue-items', methods=['GET'])
@jwt_required()
@check_permission(['admin', 'foreman'])
def overdue_items_report():
    try:
        current_date = datetime.utcnow()
        
        # Find overdue assignments
        overdue_assignments = db.session.query(
            InventoryAssignment,
            InventoryItem,
            Job,
            User
        ).join(
            InventoryItem, InventoryAssignment.item_id == InventoryItem.id
        ).join(
            Job, InventoryAssignment.job_id == Job.id
        ).join(
            User, InventoryAssignment.user_id == User.id
        ).filter(
            InventoryAssignment.status == 'checked_out',
            InventoryAssignment.expected_return_date < current_date
        ).all()
        
        report_data = []
        for assignment, item, job, user in overdue_assignments:
            days_overdue = (current_date - assignment.expected_return_date).days
            
            report_data.append({
                'assignment_id': assignment.id,
                'item_sku': item.sku,
                'item_name': item.name,
                'job_name': job.name,
                'job_claim_id': job.claim_id,
                'assigned_to': f"{user.first_name} {user.last_name}" if user.first_name else user.username,
                'user_email': user.email,
                'user_phone': user.phone,
                'check_out_time': assignment.check_out_time.isoformat() if assignment.check_out_time else None,
                'expected_return_date': assignment.expected_return_date.isoformat() if assignment.expected_return_date else None,
                'days_overdue': days_overdue
            })
        
        return jsonify({
            'report_type': 'overdue_items',
            'generated_at': datetime.utcnow().isoformat(),
            'total_overdue': len(report_data),
            'data': report_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/reports/overdue-items-temp', methods=['GET'])
def overdue_items_report_temp():
    """Temporary overdue items endpoint without JWT for testing"""
    try:
        # Return empty data for testing
        return jsonify({
            'report_type': 'overdue_items',
            'generated_at': datetime.utcnow().isoformat(),
            'total_overdue': 0,
            'data': []
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

