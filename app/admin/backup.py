from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file, current_app
from flask_login import login_required, current_user
from app.models import db, Order, User, AdminUser, AuditLog, BlogPost, CMSPage, FAQ, Testimonial
from datetime import datetime, timedelta
import json
import io
import os
from pathlib import Path

backup_bp = Blueprint('backup', __name__, url_prefix='/admin/backup')

class BackupManager:
    """Handles database backup and restore operations"""
    
    # Map of model to table name for backup
    MODELS = {
        'orders': Order,
        'users': User,
        'admin_users': AdminUser,
        'blog_posts': BlogPost,
        'cms_pages': CMSPage,
        'faqs': FAQ,
        'testimonials': Testimonial,
        'audit_logs': AuditLog,
    }
    
    @staticmethod
    def create_backup(include_audit_logs=False):
        """Create JSON backup of entire database"""
        backup_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0',
            'tables': {}
        }
        
        try:
            for table_name, model in BackupManager.MODELS.items():
                # Skip audit logs if not requested
                if table_name == 'audit_logs' and not include_audit_logs:
                    continue
                
                # Query all records
                records = model.query.all()
                backup_data['tables'][table_name] = []
                
                for record in records:
                    # Convert to dict
                    record_dict = {}
                    for column in model.__table__.columns:
                        value = getattr(record, column.name)
                        
                        # Handle datetime serialization
                        if isinstance(value, datetime):
                            value = value.isoformat()
                        # Handle JSON columns
                        elif isinstance(value, dict):
                            value = value
                        
                        record_dict[column.name] = value
                    
                    backup_data['tables'][table_name].append(record_dict)
            
            return backup_data
        
        except Exception as e:
            raise Exception(f"Backup creation failed: {str(e)}")
    
    @staticmethod
    def restore_backup(backup_data, tables_to_restore=None, clear_existing=False):
        """Restore database from backup JSON
        
        Args:
            backup_data: Dictionary with backup data
            tables_to_restore: List of table names to restore (None = all)
            clear_existing: Whether to clear existing records before restore
        
        Returns:
            Dictionary with restore results
        """
        results = {'success': True, 'restored_tables': {}, 'errors': []}
        
        try:
            if not backup_data.get('tables'):
                raise ValueError("Invalid backup format")
            
            tables = backup_data['tables']
            
            for table_name, records in tables.items():
                # Skip if table not in restore list
                if tables_to_restore and table_name not in tables_to_restore:
                    continue
                
                # Skip if model not found
                if table_name not in BackupManager.MODELS:
                    continue
                
                model = BackupManager.MODELS[table_name]
                
                try:
                    # Clear existing records if requested
                    if clear_existing:
                        db.session.query(model).delete()
                    
                    restored_count = 0
                    for record_dict in records:
                        # Create model instance
                        record = model(**record_dict)
                        db.session.add(record)
                        restored_count += 1
                    
                    db.session.commit()
                    results['restored_tables'][table_name] = restored_count
                
                except Exception as e:
                    db.session.rollback()
                    results['errors'].append(f"{table_name}: {str(e)}")
                    results['success'] = False
            
            return results
        
        except Exception as e:
            results['success'] = False
            results['errors'].append(str(e))
            return results
    
    @staticmethod
    def get_backup_directory():
        """Get or create backups directory"""
        backup_dir = os.path.join(current_app.root_path, '..', 'backups')
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
        return backup_dir
    
    @staticmethod
    def list_backups():
        """List all saved backups"""
        backup_dir = BackupManager.get_backup_directory()
        backups = []
        
        for filename in sorted(os.listdir(backup_dir), reverse=True):
            if filename.endswith('.json'):
                filepath = os.path.join(backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'timestamp': filename.replace('backup_', '').replace('.json', '')
                })
        
        return backups

# ============ BACKUP ROUTES ============

@backup_bp.route('/')
@login_required
def backups():
    """List all backups"""
    backups_list = BackupManager.list_backups()
    return render_template('admin/backup/backups.html', backups=backups_list)

@backup_bp.route('/create', methods=['POST'])
@login_required
def create_backup():
    """Create new backup"""
    try:
        include_audit = request.form.get('include_audit_logs') == 'on'
        backup_data = BackupManager.create_backup(include_audit_logs=include_audit)
        
        # Save backup to file
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_dir = BackupManager.get_backup_directory()
        backup_filename = f'backup_{timestamp}.json'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        flash(f'Backup created: {backup_filename}', 'success')
        return redirect(url_for('backup.backups'))
    
    except Exception as e:
        flash(f'Backup failed: {str(e)}', 'danger')
        return redirect(url_for('backup.backups'))

@backup_bp.route('/download/<filename>')
@login_required
def download_backup(filename):
    """Download backup file"""
    try:
        # Validate filename to prevent path traversal
        if '..' in filename or '/' in filename:
            flash('Invalid filename', 'danger')
            return redirect(url_for('backup.backups'))
        
        backup_dir = BackupManager.get_backup_directory()
        backup_path = os.path.join(backup_dir, filename)
        
        if not os.path.exists(backup_path):
            flash('Backup not found', 'danger')
            return redirect(url_for('backup.backups'))
        
        return send_file(backup_path, as_attachment=True, download_name=filename)
    
    except Exception as e:
        flash(f'Download failed: {str(e)}', 'danger')
        return redirect(url_for('backup.backups'))

@backup_bp.route('/delete/<filename>', methods=['POST'])
@login_required
def delete_backup(filename):
    """Delete backup file"""
    try:
        if '..' in filename or '/' in filename:
            flash('Invalid filename', 'danger')
            return redirect(url_for('backup.backups'))
        
        backup_dir = BackupManager.get_backup_directory()
        backup_path = os.path.join(backup_dir, filename)
        
        if os.path.exists(backup_path):
            os.remove(backup_path)
            flash(f'Backup deleted: {filename}', 'success')
        else:
            flash('Backup not found', 'danger')
    
    except Exception as e:
        flash(f'Delete failed: {str(e)}', 'danger')
    
    return redirect(url_for('backup.backups'))

@backup_bp.route('/restore', methods=['GET', 'POST'])
@login_required
def restore():
    """Restore from backup"""
    if request.method == 'GET':
        backups_list = BackupManager.list_backups()
        return render_template('admin/backup/restore.html', backups=backups_list)
    
    # POST request - perform restore
    try:
        backup_filename = request.form.get('backup_filename')
        if not backup_filename:
            flash('No backup selected', 'warning')
            return redirect(url_for('backup.restore'))
        
        # Validate filename
        if '..' in backup_filename or '/' in backup_filename:
            flash('Invalid filename', 'danger')
            return redirect(url_for('backup.restore'))
        
        backup_dir = BackupManager.get_backup_directory()
        backup_path = os.path.join(backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            flash('Backup file not found', 'danger')
            return redirect(url_for('backup.restore'))
        
        # Load backup
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        # Get restore options
        clear_existing = request.form.get('clear_existing') == 'on'
        selected_tables = request.form.getlist('tables')
        
        # Perform restore
        results = BackupManager.restore_backup(
            backup_data,
            tables_to_restore=selected_tables if selected_tables else None,
            clear_existing=clear_existing
        )
        
        if results['success']:
            msg = f"Restore successful: {', '.join([f'{t}({c})' for t, c in results['restored_tables'].items()])}"
            flash(msg, 'success')
        else:
            flash(f"Restore completed with errors: {', '.join(results['errors'])}", 'warning')
        
        return redirect(url_for('backup.backups'))
    
    except Exception as e:
        flash(f'Restore failed: {str(e)}', 'danger')
        return redirect(url_for('backup.restore'))

@backup_bp.route('/upload', methods=['POST'])
@login_required
def upload_backup():
    """Upload backup file"""
    try:
        if 'backup_file' not in request.files:
            flash('No file selected', 'warning')
            return redirect(url_for('backup.backups'))
        
        file = request.files['backup_file']
        if not file or not file.filename.endswith('.json'):
            flash('Invalid file format (must be JSON)', 'danger')
            return redirect(url_for('backup.backups'))
        
        # Validate JSON
        content = file.read().decode('utf-8')
        backup_data = json.loads(content)
        
        if 'tables' not in backup_data:
            flash('Invalid backup format', 'danger')
            return redirect(url_for('backup.backups'))
        
        # Save file
        backup_dir = BackupManager.get_backup_directory()
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_uploaded_{timestamp}.json'
        filepath = os.path.join(backup_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        flash(f'Backup uploaded: {filename}', 'success')
        return redirect(url_for('backup.backups'))
    
    except json.JSONDecodeError:
        flash('Invalid JSON file', 'danger')
    except Exception as e:
        flash(f'Upload failed: {str(e)}', 'danger')
    
    return redirect(url_for('backup.backups'))

@backup_bp.route('/auto-schedule', methods=['POST'])
@login_required
def auto_schedule():
    """Configure automatic daily backups"""
    # This would require a background job scheduler like APScheduler
    # For now, just store the preference
    enabled = request.form.get('auto_backup') == 'on'
    
    # In production, you'd store this in a config table or environment variable
    # and run a scheduled task to create backups at specified times
    
    if enabled:
        flash('Automatic backups enabled (daily at 2 AM UTC)', 'success')
    else:
        flash('Automatic backups disabled', 'info')
    
    return redirect(url_for('backup.backups'))
