from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models import db, AdminUser, Role, AdminRole, AuditLog
from datetime import datetime

users_bp = Blueprint('admin_users', __name__, url_prefix='/admin/users')

def log_audit(action, resource_type, resource_id, ip_address, old_values=None, new_values=None):
    """Helper to log admin actions"""
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
    except Exception:
        pass

@users_bp.route('/')
@login_required
def list_users():
    """List all admin users"""
    page = request.args.get('page', 1, type=int)
    
    admins = AdminUser.query.paginate(page=page, per_page=20)
    
    log_audit('list', 'admin_users', None, request.remote_addr)
    
    return render_template('admin/users/list.html', admins=admins)

@users_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_user():
    """Create new admin user"""
    if request.method == 'GET':
        roles_list = Role.query.all()
        return render_template('admin/users/form.html', admin=None, roles=roles_list)
    
    # POST - Create admin
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    selected_roles = request.form.getlist('roles')
    
    # Validation
    if not username or len(username) < 3:
        flash('Username must be at least 3 characters', 'warning')
        return redirect(url_for('admin_users.create_user'))
    
    if AdminUser.query.filter_by(username=username).first():
        flash('Username already exists', 'warning')
        return redirect(url_for('admin_users.create_user'))
    
    if not password or len(password) < 6:
        flash('Password must be at least 6 characters', 'warning')
        return redirect(url_for('admin_users.create_user'))
    
    # Create admin
    admin = AdminUser(
        username=username,
        password_hash=generate_password_hash(password)
    )
    
    db.session.add(admin)
    db.session.flush()  # Get the ID
    
    # Assign roles
    for role_id in selected_roles:
        role = Role.query.get(int(role_id))
        if role:
            admin_role = AdminRole(
                admin_id=admin.id,
                role_id=role.id,
                assigned_by=current_user.id
            )
            db.session.add(admin_role)
    
    db.session.commit()
    
    log_audit('create', 'admin_user', str(admin.id), request.remote_addr, None, {
        'username': username,
        'roles': selected_roles
    })
    
    flash(f'Admin user "{username}" created successfully', 'success')
    return redirect(url_for('admin_users.list_users'))

@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edit admin user"""
    admin = AdminUser.query.get_or_404(user_id)
    
    if request.method == 'GET':
        roles_list = Role.query.all()
        admin_roles = AdminRole.query.filter_by(admin_id=user_id).all()
        selected_role_ids = [ar.role_id for ar in admin_roles]
        return render_template('admin/users/form.html', admin=admin, roles=roles_list, selected_role_ids=selected_role_ids)
    
    # POST - Update admin
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    selected_roles = request.form.getlist('roles')
    
    # Validation
    if not username or len(username) < 3:
        flash('Username must be at least 3 characters', 'warning')
        return redirect(url_for('admin_users.edit_user', user_id=user_id))
    
    # Check if username is taken (by another user)
    existing = AdminUser.query.filter(
        AdminUser.username == username,
        AdminUser.id != user_id
    ).first()
    
    if existing:
        flash('Username already taken by another user', 'warning')
        return redirect(url_for('admin_users.edit_user', user_id=user_id))
    
    old_values = {
        'username': admin.username,
        'roles': [ar.role_id for ar in AdminRole.query.filter_by(admin_id=user_id).all()]
    }
    
    admin.username = username
    
    if password and len(password) >= 6:
        admin.password_hash = generate_password_hash(password)
    
    # Update roles
    AdminRole.query.filter_by(admin_id=user_id).delete()
    for role_id in selected_roles:
        role = Role.query.get(int(role_id))
        if role:
            admin_role = AdminRole(
                admin_id=admin.id,
                role_id=role.id,
                assigned_by=current_user.id
            )
            db.session.add(admin_role)
    
    db.session.commit()
    
    new_values = {
        'username': admin.username,
        'roles': selected_roles
    }
    
    log_audit('update', 'admin_user', str(user_id), request.remote_addr, old_values, new_values)
    
    flash(f'Admin user updated successfully', 'success')
    return redirect(url_for('admin_users.list_users'))

@users_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete admin user"""
    # Prevent deleting yourself
    if user_id == current_user.id:
        flash('You cannot delete your own account', 'warning')
        return redirect(url_for('admin_users.list_users'))
    
    admin = AdminUser.query.get_or_404(user_id)
    username = admin.username
    
    # Delete associated roles and logs
    AdminRole.query.filter_by(admin_id=user_id).delete()
    
    db.session.delete(admin)
    db.session.commit()
    
    log_audit('delete', 'admin_user', str(user_id), request.remote_addr, {
        'username': username
    }, None)
    
    flash(f'Admin user "{username}" deleted', 'success')
    return redirect(url_for('admin_users.list_users'))

@users_bp.route('/<int:user_id>/roles', methods=['GET', 'POST'])
@login_required
def manage_roles(user_id):
    """Manage roles for an admin user"""
    admin = AdminUser.query.get_or_404(user_id)
    
    if request.method == 'POST':
        selected_roles = request.form.getlist('roles')
        
        # Clear existing roles
        AdminRole.query.filter_by(admin_id=user_id).delete()
        
        # Add new roles
        for role_id in selected_roles:
            role = Role.query.get(int(role_id))
            if role:
                admin_role = AdminRole(
                    admin_id=admin.id,
                    role_id=role.id,
                    assigned_by=current_user.id
                )
                db.session.add(admin_role)
        
        db.session.commit()
        
        log_audit('update', 'admin_user', str(user_id), request.remote_addr, {
            'action': 'roles_updated'
        }, {
            'roles': selected_roles
        })
        
        flash('Roles updated successfully', 'success')
        return redirect(url_for('admin_users.list_users'))
    
    roles_list = Role.query.all()
    admin_roles = AdminRole.query.filter_by(admin_id=user_id).all()
    selected_role_ids = [ar.role_id for ar in admin_roles]
    
    return render_template('admin/users/manage_roles.html', admin=admin, roles=roles_list, selected_role_ids=selected_role_ids)

# ============ ROLES MANAGEMENT ============

@users_bp.route('/roles')
@login_required
def roles():
    """List all roles"""
    roles_list = Role.query.all()
    
    return render_template('admin/users/roles.html', roles=roles_list)

@users_bp.route('/roles/new', methods=['GET', 'POST'])
@login_required
def create_role():
    """Create new role"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        permissions_str = request.form.get('permissions', '{}')
        
        if not name:
            flash('Role name is required', 'warning')
            return redirect(url_for('admin_users.create_role'))
        
        if Role.query.filter_by(name=name).first():
            flash('Role name already exists', 'warning')
            return redirect(url_for('admin_users.create_role'))
        
        try:
            import json
            permissions = json.loads(permissions_str)
        except:
            permissions = {}
        
        role = Role(
            name=name,
            description=description,
            permissions=permissions
        )
        
        db.session.add(role)
        db.session.commit()
        
        log_audit('create', 'role', str(role.id), request.remote_addr, None, {
            'name': name,
            'permissions': permissions
        })
        
        flash(f'Role "{name}" created successfully', 'success')
        return redirect(url_for('admin_users.roles'))
    
    return render_template('admin/users/role_form.html', role=None)

@users_bp.route('/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_role(role_id):
    """Edit role"""
    role = Role.query.get_or_404(role_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        permissions_str = request.form.get('permissions', '{}')
        
        if not name:
            flash('Role name is required', 'warning')
            return redirect(url_for('admin_users.edit_role', role_id=role_id))
        
        # Check if name is taken by another role
        existing = Role.query.filter(
            Role.name == name,
            Role.id != role_id
        ).first()
        
        if existing:
            flash('Role name already taken', 'warning')
            return redirect(url_for('admin_users.edit_role', role_id=role_id))
        
        try:
            import json
            permissions = json.loads(permissions_str)
        except:
            permissions = role.permissions
        
        old_values = {
            'name': role.name,
            'permissions': role.permissions
        }
        
        role.name = name
        role.description = description
        role.permissions = permissions
        
        db.session.commit()
        
        new_values = {
            'name': role.name,
            'permissions': role.permissions
        }
        
        log_audit('update', 'role', str(role_id), request.remote_addr, old_values, new_values)
        
        flash('Role updated successfully', 'success')
        return redirect(url_for('admin_users.roles'))
    
    return render_template('admin/users/role_form.html', role=role)

@users_bp.route('/roles/<int:role_id>/delete', methods=['POST'])
@login_required
def delete_role(role_id):
    """Delete role"""
    role = Role.query.get_or_404(role_id)
    
    # Check if role is assigned to any users
    admin_roles = AdminRole.query.filter_by(role_id=role_id).count()
    if admin_roles > 0:
        flash('Cannot delete role that is assigned to users', 'warning')
        return redirect(url_for('admin_users.roles'))
    
    name = role.name
    
    db.session.delete(role)
    db.session.commit()
    
    log_audit('delete', 'role', str(role_id), request.remote_addr, {
        'name': name
    }, None)
    
    flash(f'Role "{name}" deleted', 'success')
    return redirect(url_for('admin_users.roles'))
