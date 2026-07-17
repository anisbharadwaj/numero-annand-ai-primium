from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, CMSPage, BlogPost, FAQ, Testimonial, AdminUser, AuditLog
from datetime import datetime
from slugify import slugify
import re

cms_bp = Blueprint('cms', __name__, url_prefix='/admin/cms')

def log_audit(action, resource_type, resource_id, ip_address, old_values=None, new_values=None):
    """Helper to log CMS actions"""
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

# ============ PAGES ============

@cms_bp.route('/pages')
@login_required
def pages():
    """List all CMS pages"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', None)
    
    query = CMSPage.query
    if status:
        query = query.filter_by(status=status)
    
    pages_list = query.order_by(CMSPage.updated_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/cms/pages.html', pages=pages_list, status=status)

@cms_bp.route('/pages/new', methods=['GET', 'POST'])
@login_required
def page_new():
    """Create new CMS page"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = slugify(request.form.get('slug', title))
        content = request.form.get('content', '')
        status = request.form.get('status', 'draft')
        
        # Check slug uniqueness
        if CMSPage.query.filter_by(slug=slug).first():
            flash('Slug already exists', 'warning')
            return redirect(url_for('cms.page_new'))
        
        page = CMSPage(
            slug=slug,
            title=title,
            content=content,
            status=status,
            seo_title=request.form.get('seo_title', title),
            seo_description=request.form.get('seo_description', ''),
            author_id=current_user.id,
            published_at=datetime.utcnow() if status == 'published' else None
        )
        
        db.session.add(page)
        db.session.commit()
        
        log_audit('create', 'page', str(page.id), request.remote_addr, None, page.__dict__)
        flash('Page created successfully', 'success')
        return redirect(url_for('cms.page_edit', page_id=page.id))
    
    return render_template('admin/cms/page_form.html', page=None)

@cms_bp.route('/pages/<int:page_id>/edit', methods=['GET', 'POST'])
@login_required
def page_edit(page_id):
    """Edit CMS page"""
    page = CMSPage.query.get_or_404(page_id)
    
    if request.method == 'POST':
        old_values = {k: getattr(page, k) for k in ['title', 'content', 'status', 'seo_title', 'seo_description']}
        
        page.title = request.form.get('title', page.title)
        page.content = request.form.get('content', page.content)
        page.status = request.form.get('status', page.status)
        page.seo_title = request.form.get('seo_title', page.seo_title)
        page.seo_description = request.form.get('seo_description', page.seo_description)
        
        if page.status == 'published' and not page.published_at:
            page.published_at = datetime.utcnow()
        
        db.session.commit()
        
        new_values = {k: getattr(page, k) for k in ['title', 'content', 'status', 'seo_title', 'seo_description']}
        log_audit('update', 'page', str(page_id), request.remote_addr, old_values, new_values)
        
        flash('Page updated successfully', 'success')
        return redirect(url_for('cms.page_edit', page_id=page_id))
    
    return render_template('admin/cms/page_form.html', page=page)

@cms_bp.route('/pages/<int:page_id>/delete', methods=['POST'])
@login_required
def page_delete(page_id):
    """Delete CMS page"""
    page = CMSPage.query.get_or_404(page_id)
    slug = page.slug
    
    db.session.delete(page)
    db.session.commit()
    
    log_audit('delete', 'page', str(page_id), request.remote_addr, page.__dict__, None)
    flash(f'Page "{slug}" deleted', 'success')
    
    return redirect(url_for('cms.pages'))

# ============ BLOG ============

@cms_bp.route('/blog')
@login_required
def blog():
    """List all blog posts"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', None)
    category = request.args.get('category', None)
    
    query = BlogPost.query
    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)
    
    posts = query.order_by(BlogPost.updated_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/cms/blog.html', posts=posts, status=status, category=category)

@cms_bp.route('/blog/new', methods=['GET', 'POST'])
@login_required
def blog_new():
    """Create new blog post"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = slugify(request.form.get('slug', title))
        
        if BlogPost.query.filter_by(slug=slug).first():
            flash('Slug already exists', 'warning')
            return redirect(url_for('cms.blog_new'))
        
        post = BlogPost(
            slug=slug,
            title=title,
            excerpt=request.form.get('excerpt', ''),
            content=request.form.get('content', ''),
            category=request.form.get('category', 'tips'),
            status=request.form.get('status', 'draft'),
            author_id=current_user.id,
            published_at=datetime.utcnow() if request.form.get('status') == 'published' else None
        )
        
        db.session.add(post)
        db.session.commit()
        
        log_audit('create', 'blog_post', str(post.id), request.remote_addr, None, post.__dict__)
        flash('Blog post created successfully', 'success')
        return redirect(url_for('cms.blog_edit', post_id=post.id))
    
    return render_template('admin/cms/blog_form.html', post=None)

@cms_bp.route('/blog/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def blog_edit(post_id):
    """Edit blog post"""
    post = BlogPost.query.get_or_404(post_id)
    
    if request.method == 'POST':
        old_values = {k: getattr(post, k) for k in ['title', 'content', 'status', 'category']}
        
        post.title = request.form.get('title', post.title)
        post.excerpt = request.form.get('excerpt', post.excerpt)
        post.content = request.form.get('content', post.content)
        post.category = request.form.get('category', post.category)
        post.status = request.form.get('status', post.status)
        
        if post.status == 'published' and not post.published_at:
            post.published_at = datetime.utcnow()
        
        db.session.commit()
        
        new_values = {k: getattr(post, k) for k in ['title', 'content', 'status', 'category']}
        log_audit('update', 'blog_post', str(post_id), request.remote_addr, old_values, new_values)
        
        flash('Blog post updated successfully', 'success')
        return redirect(url_for('cms.blog_edit', post_id=post_id))
    
    return render_template('admin/cms/blog_form.html', post=post)

@cms_bp.route('/blog/<int:post_id>/delete', methods=['POST'])
@login_required
def blog_delete(post_id):
    """Delete blog post"""
    post = BlogPost.query.get_or_404(post_id)
    
    db.session.delete(post)
    db.session.commit()
    
    log_audit('delete', 'blog_post', str(post_id), request.remote_addr, post.__dict__, None)
    flash('Blog post deleted', 'success')
    
    return redirect(url_for('cms.blog'))

# ============ FAQ ============

@cms_bp.route('/faq')
@login_required
def faqs():
    """List all FAQs"""
    category = request.args.get('category', None)
    
    query = FAQ.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category)
    
    faqs_list = query.order_by(FAQ.display_order).all()
    
    return render_template('admin/cms/faq.html', faqs=faqs_list, category=category)

@cms_bp.route('/faq/new', methods=['GET', 'POST'])
@login_required
def faq_new():
    """Create new FAQ"""
    if request.method == 'POST':
        faq = FAQ(
            question=request.form.get('question', ''),
            answer=request.form.get('answer', ''),
            category=request.form.get('category', 'general'),
            display_order=request.form.get('display_order', 0, type=int)
        )
        
        db.session.add(faq)
        db.session.commit()
        
        log_audit('create', 'faq', str(faq.id), request.remote_addr, None, faq.__dict__)
        flash('FAQ created successfully', 'success')
        return redirect(url_for('cms.faqs'))
    
    return render_template('admin/cms/faq_form.html', faq=None)

@cms_bp.route('/faq/<int:faq_id>/edit', methods=['GET', 'POST'])
@login_required
def faq_edit(faq_id):
    """Edit FAQ"""
    faq = FAQ.query.get_or_404(faq_id)
    
    if request.method == 'POST':
        faq.question = request.form.get('question', faq.question)
        faq.answer = request.form.get('answer', faq.answer)
        faq.category = request.form.get('category', faq.category)
        faq.display_order = request.form.get('display_order', faq.display_order, type=int)
        
        db.session.commit()
        
        log_audit('update', 'faq', str(faq_id), request.remote_addr)
        flash('FAQ updated successfully', 'success')
        return redirect(url_for('cms.faqs'))
    
    return render_template('admin/cms/faq_form.html', faq=faq)

# ============ TESTIMONIALS ============

@cms_bp.route('/testimonials')
@login_required
def testimonials():
    """List all testimonials"""
    status = request.args.get('status', 'pending')
    
    testimonials_list = Testimonial.query.filter_by(status=status).order_by(Testimonial.created_at.desc()).all()
    
    return render_template('admin/cms/testimonials.html', testimonials=testimonials_list, status=status)

@cms_bp.route('/testimonials/<int:testimonial_id>/approve', methods=['POST'])
@login_required
def testimonial_approve(testimonial_id):
    """Approve testimonial"""
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    
    testimonial.status = 'approved'
    testimonial.approved_at = datetime.utcnow()
    testimonial.approved_by = current_user.id
    
    db.session.commit()
    
    log_audit('update', 'testimonial', str(testimonial_id), request.remote_addr, {'status': 'pending'}, {'status': 'approved'})
    flash('Testimonial approved', 'success')
    
    return redirect(request.referrer or url_for('cms.testimonials'))

@cms_bp.route('/testimonials/<int:testimonial_id>/reject', methods=['POST'])
@login_required
def testimonial_reject(testimonial_id):
    """Reject testimonial"""
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    
    db.session.delete(testimonial)
    db.session.commit()
    
    log_audit('delete', 'testimonial', str(testimonial_id), request.remote_addr)
    flash('Testimonial rejected', 'success')
    
    return redirect(request.referrer or url_for('cms.testimonials'))
