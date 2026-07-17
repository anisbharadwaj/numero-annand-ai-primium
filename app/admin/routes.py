from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func, and_
from app.models import db, Order, User, AdminUser, AuditLog, Role, AdminRole
from datetime import datetime, timedelta
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='../templates')

def require_admin(*required_permissions):
    """Decorator to check admin role and permissions"""
    def decorator(f):
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated or not isinstance(current_user, AdminUser):
                flash('Admin access required', 'danger')
                return redirect(url_for('auth.login'))
            
            # Check if user has any of the required permissions
            if required_permissions:
                admin_roles = AdminRole.query.filter_by(admin_id=current_user.id).all()
                has_permission = False
                for ar in admin_roles:
                    role = Role.query.get(ar.role_id)
                    for perm in required_permissions:
                        if role and role.permissions.get(perm.split(':')[0], []) and perm.split(':')[1] in role.permissions.get(perm.split(':')[0], []):
                            has_permission = True
                            break
                if not has_permission and 'admin' not in [r.role.name for r in admin_roles]:
                    flash('Insufficient permissions', 'warning')
                    return redirect(url_for('admin.dashboard'))
            
            return f(*args, **kwargs)
        wrapped.__name__ = f.__name__
        return wrapped
    return decorator

@admin_bp.route('/dashboard')
@login_required
@require_admin()
def dashboard():
    """Admin dashboard with key metrics and analytics"""
    
    # Calculate 30-day metrics
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Key metrics
    total_orders = Order.query.count()
    orders_30d = Order.query.filter(Order.created_at >= thirty_days_ago).count()
    completed_orders = Order.query.filter_by(payment_status='completed').count()
    pending_orders = Order.query.filter_by(payment_status='pending').count()
    
    # Revenue
    total_revenue = db.session.query(func.sum(Order.amount)).filter(
        Order.payment_status == 'completed'
    ).scalar() or 0
    revenue_30d = db.session.query(func.sum(Order.amount)).filter(
        and_(Order.payment_status == 'completed', Order.created_at >= thirty_days_ago)
    ).scalar() or 0
    
    # Users
    total_users = User.query.count()
    users_30d = User.query.filter(User.created_at >= thirty_days_ago).count()
    
    # Premium subscribers
    premium_users = User.query.filter_by(subscription_tier='premium').count()
    
    # Report generation status
    reports_pending = Order.query.filter(
        and_(Order.payment_status == 'completed', Order.verified_at == None)
    ).count()
    
    # Order status breakdown
    status_breakdown = db.session.query(
        Order.payment_status,
        func.count(Order.id).label('count')
    ).group_by(Order.payment_status).all()
    
    # Recent orders (last 10)
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    # Revenue trend (daily for last 30 days)
    revenue_trend = db.session.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.amount).label('revenue'),
        func.count(Order.id).label('orders')
    ).filter(
        and_(Order.created_at >= thirty_days_ago, Order.payment_status == 'completed')
    ).group_by(func.date(Order.created_at)).order_by('date').all()
    
    metrics = {
        'total_orders': total_orders,
        'orders_30d': orders_30d,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'total_revenue': float(total_revenue),
        'revenue_30d': float(revenue_30d),
        'total_users': total_users,
        'users_30d': users_30d,
        'premium_users': premium_users,
        'reports_pending': reports_pending,
        'status_breakdown': [{'status': status, 'count': count} for status, count in status_breakdown],
        'revenue_trend': [
            {'date': date.isoformat() if date else None, 'revenue': float(revenue or 0), 'orders': orders}
            for date, revenue, orders in revenue_trend
        ]
    }
    
    # Log dashboard access
    log_audit('view', 'dashboard', None, request.remote_addr)
    
    return render_template('admin/dashboard.html', metrics=metrics, recent_orders=recent_orders)

@admin_bp.route('/orders')
@login_required
@require_admin('orders:view')
def orders():
    """List all orders with filtering and search"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', None)
    search = request.args.get('search', None)
    
    query = Order.query
    
    if status:
        query = query.filter_by(payment_status=status)
    
    if search:
        query = query.filter(
            db.or_(
                Order.name.ilike(f'%{search}%'),
                Order.email.ilike(f'%{search}%'),
                Order.mobile.ilike(f'%{search}%'),
                Order.utr.ilike(f'%{search}%')
            )
        )
    
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=20)
    
    log_audit('list', 'orders', None, request.remote_addr)
    
    return render_template('admin/orders.html', orders=orders, status=status, search=search)

@admin_bp.route('/orders/<int:order_id>')
@login_required
@require_admin('orders:view')
def order_detail(order_id):
    """View order details and manage payment verification"""
    order = Order.query.get_or_404(order_id)
    
    log_audit('view', 'order', str(order_id), request.remote_addr)
    
    return render_template('admin/order_detail.html', order=order)

@admin_bp.route('/orders/<int:order_id>/verify', methods=['POST'])
@login_required
@require_admin('orders:edit')
def verify_order(order_id):
    """Verify order payment and approve report generation"""
    order = Order.query.get_or_404(order_id)
    
    old_status = order.payment_status
    order.payment_status = 'completed'
    order.verified_at = datetime.utcnow()
    order.verified_by = current_user.id
    
    db.session.commit()
    
    log_audit('update', 'order', str(order_id), request.remote_addr, 
              {'payment_status': old_status}, {'payment_status': 'completed'})
    
    flash(f'Order #{order_id} verified successfully', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))

@admin_bp.route('/users')
@login_required
@require_admin('users:view')
def users():
    """List all users"""
    page = request.args.get('page', 1, type=int)
    tier = request.args.get('tier', None)
    search = request.args.get('search', None)
    
    query = User.query
    
    if tier:
        query = query.filter_by(subscription_tier=tier)
    
    if search:
        query = query.filter(
            db.or_(
                User.name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.mobile.ilike(f'%{search}%')
            )
        )
    
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    
    log_audit('list', 'users', None, request.remote_addr)
    
    return render_template('admin/users.html', users=users, tier=tier, search=search)

@admin_bp.route('/audit-logs')
@login_required
@require_admin('admin:view')
def audit_logs():
    """View audit logs of all admin actions"""
    page = request.args.get('page', 1, type=int)
    action = request.args.get('action', None)
    resource_type = request.args.get('resource_type', None)
    
    query = AuditLog.query
    
    if action:
        query = query.filter_by(action=action)
    
    if resource_type:
        query = query.filter_by(resource_type=resource_type)
    
    logs = query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=50)
    
    return render_template('admin/audit_logs.html', logs=logs, action=action, resource_type=resource_type)

def log_audit(action, resource_type, resource_id, ip_address, old_values=None, new_values=None):
    """Helper function to log admin actions"""
    try:
        log = AuditLog(
            admin_id=current_user.id if current_user.is_authenticated else None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            old_values=old_values,
            new_values=new_values
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"[v0] Audit log error: {e}")
