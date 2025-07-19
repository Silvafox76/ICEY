from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.job import Job
from src.models.assignment import InventoryAssignment
from src.models.media import Media
from datetime import datetime

jobs_bp = Blueprint('jobs', __name__)

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

@jobs_bp.route('/jobs', methods=['GET'])
@jwt_required()
def get_jobs():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Get query parameters for filtering
        status = request.args.get('status')
        priority = request.args.get('priority')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Build query based on user role
        query = Job.query
        
        # Technicians can only see jobs they're assigned to
        if user.role == 'technician':
            query = query.join(InventoryAssignment).filter(
                InventoryAssignment.user_id == current_user_id
            ).distinct()
        # Foremen can see jobs they're assigned to manage
        elif user.role == 'foreman':
            query = query.filter(
                (Job.assigned_foreman == current_user_id) |
                (Job.created_by == current_user_id)
            )
        # Admin and Finance can see all jobs
        
        if status:
            query = query.filter(Job.status == status)
        if priority:
            query = query.filter(Job.priority == priority)
        if search:
            query = query.filter(
                Job.name.contains(search) |
                Job.claim_id.contains(search) |
                Job.description.contains(search) |
                Job.customer_name.contains(search)
            )
        
        # Order by priority and creation date
        query = query.order_by(
            Job.priority.desc(),
            Job.created_at.desc()
        )
        
        # Paginate results
        jobs = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'jobs': [job.to_dict() for job in jobs.items],
            'total': jobs.total,
            'pages': jobs.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/jobs/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job(job_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        job = Job.query.get_or_404(job_id)
        
        # Check permissions
        if user.role == 'technician':
            # Check if user has assignments for this job
            assignment = InventoryAssignment.query.filter_by(
                job_id=job_id, user_id=current_user_id
            ).first()
            if not assignment:
                return jsonify({'error': 'Access denied'}), 403
        elif user.role == 'foreman':
            if job.assigned_foreman != current_user_id and job.created_by != current_user_id:
                return jsonify({'error': 'Access denied'}), 403
        
        # Include assignments and media
        job_data = job.to_dict()
        job_data['assignments'] = [assignment.to_dict() for assignment in job.assignments]
        job_data['media'] = [media.to_dict() for media in job.media]
        
        return jsonify(job_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/jobs', methods=['POST'])
@jwt_required()
@check_permission(['admin', 'foreman'])
def create_job():
    try:
        current_user_id = get_jwt_identity()
        data = request.json
        
        # Validate required fields
        required_fields = ['name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if claim_id already exists (if provided)
        if data.get('claim_id'):
            if Job.query.filter_by(claim_id=data['claim_id']).first():
                return jsonify({'error': 'Claim ID already exists'}), 400
        
        # Create new job
        job = Job(
            claim_id=data.get('claim_id'),
            xactimate_id=data.get('xactimate_id'),
            name=data['name'],
            description=data.get('description'),
            location=data.get('location'),
            address=data.get('address'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
            end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None,
            estimated_completion=datetime.fromisoformat(data['estimated_completion']) if data.get('estimated_completion') else None,
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium'),
            customer_name=data.get('customer_name'),
            customer_phone=data.get('customer_phone'),
            customer_email=data.get('customer_email'),
            created_by=current_user_id,
            assigned_foreman=data.get('assigned_foreman')
        )
        
        db.session.add(job)
        db.session.commit()
        
        return jsonify({
            'message': 'Job created successfully',
            'job': job.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/jobs/<int:job_id>', methods=['PUT'])
@jwt_required()
@check_permission(['admin', 'foreman'])
def update_job(job_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        job = Job.query.get_or_404(job_id)
        
        # Check permissions for foremen
        if user.role == 'foreman':
            if job.assigned_foreman != current_user_id and job.created_by != current_user_id:
                return jsonify({'error': 'Access denied'}), 403
        
        data = request.json
        
        # Update fields
        updatable_fields = [
            'name', 'description', 'location', 'address', 'latitude', 'longitude',
            'status', 'priority', 'customer_name', 'customer_phone', 'customer_email',
            'assigned_foreman', 'xactimate_id'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field in ['start_date', 'end_date', 'estimated_completion'] and data[field]:
                    setattr(job, field, datetime.fromisoformat(data[field]))
                else:
                    setattr(job, field, data[field])
        
        job.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Job updated successfully',
            'job': job.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
@jwt_required()
@check_permission(['admin'])
def delete_job(job_id):
    try:
        job = Job.query.get_or_404(job_id)
        
        # Check if job has active assignments
        active_assignments = InventoryAssignment.query.filter_by(
            job_id=job_id, status='checked_out'
        ).first()
        
        if active_assignments:
            return jsonify({'error': 'Cannot delete job with active inventory assignments'}), 400
        
        db.session.delete(job)
        db.session.commit()
        
        return jsonify({'message': 'Job deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/jobs/<int:job_id>/assignments', methods=['GET'])
@jwt_required()
def get_job_assignments(job_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        job = Job.query.get_or_404(job_id)
        
        # Check permissions
        if user.role == 'technician':
            assignment = InventoryAssignment.query.filter_by(
                job_id=job_id, user_id=current_user_id
            ).first()
            if not assignment:
                return jsonify({'error': 'Access denied'}), 403
        elif user.role == 'foreman':
            if job.assigned_foreman != current_user_id and job.created_by != current_user_id:
                return jsonify({'error': 'Access denied'}), 403
        
        assignments = InventoryAssignment.query.filter_by(job_id=job_id).all()
        
        return jsonify([assignment.to_dict() for assignment in assignments]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/jobs/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        stats = {}
        
        if user.role in ['admin', 'finance']:
            # Admin/Finance can see all stats
            stats['total_jobs'] = Job.query.count()
            stats['active_jobs'] = Job.query.filter_by(status='active').count()
            stats['pending_jobs'] = Job.query.filter_by(status='pending').count()
            stats['completed_jobs'] = Job.query.filter_by(status='completed').count()
            stats['total_assignments'] = InventoryAssignment.query.count()
            stats['active_assignments'] = InventoryAssignment.query.filter_by(status='checked_out').count()
            
        elif user.role == 'foreman':
            # Foremen see stats for their jobs
            foreman_jobs = Job.query.filter(
                (Job.assigned_foreman == current_user_id) |
                (Job.created_by == current_user_id)
            )
            stats['total_jobs'] = foreman_jobs.count()
            stats['active_jobs'] = foreman_jobs.filter_by(status='active').count()
            stats['pending_jobs'] = foreman_jobs.filter_by(status='pending').count()
            stats['completed_jobs'] = foreman_jobs.filter_by(status='completed').count()
            
            job_ids = [job.id for job in foreman_jobs.all()]
            stats['total_assignments'] = InventoryAssignment.query.filter(
                InventoryAssignment.job_id.in_(job_ids)
            ).count()
            stats['active_assignments'] = InventoryAssignment.query.filter(
                InventoryAssignment.job_id.in_(job_ids),
                InventoryAssignment.status == 'checked_out'
            ).count()
            
        else:  # technician
            # Technicians see stats for their assignments
            user_assignments = InventoryAssignment.query.filter_by(user_id=current_user_id)
            stats['total_assignments'] = user_assignments.count()
            stats['active_assignments'] = user_assignments.filter_by(status='checked_out').count()
            
            job_ids = [assignment.job_id for assignment in user_assignments.all()]
            stats['total_jobs'] = len(set(job_ids))
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/jobs/dashboard-temp', methods=['GET'])
def get_dashboard_stats_temp():
    """Temporary dashboard endpoint without JWT for testing"""
    try:
        stats = {}
        
        # Return basic stats for testing
        stats['total_jobs'] = Job.query.count()
        stats['active_jobs'] = Job.query.filter_by(status='active').count()
        stats['pending_jobs'] = Job.query.filter_by(status='pending').count()
        stats['completed_jobs'] = Job.query.filter_by(status='completed').count()
        stats['total_assignments'] = InventoryAssignment.query.count()
        stats['active_assignments'] = InventoryAssignment.query.filter_by(status='checked_out').count()
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

