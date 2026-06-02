from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from admin.forms import LoginForm, CreateUserForm
from models import db, User, Perusahaan, Lowongan, Lamaran
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorator untuk memastikan hanya admin yang bisa akses
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Anda tidak memiliki akses ke halaman ini.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data) and user.role == 'admin':
            from flask_login import login_user
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
        flash('Login gagal. Periksa username dan password Anda.', 'error')
    return render_template('admin/login.html', form=form)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_pencari = User.query.filter_by(role='pencari_kerja').count()
    total_perusahaan = Perusahaan.query.count()
    total_lowongan = Lowongan.query.count()
    total_lamaran = Lamaran.query.count()
    return render_template('admin/dashboard.html', 
                         total_pencari=total_pencari,
                         total_perusahaan=total_perusahaan,
                         total_lowongan=total_lowongan,
                         total_lamaran=total_lamaran)

@admin_bp.route('/kelola_pengguna', methods=['GET', 'POST'])
@login_required
@admin_required
def kelola_pengguna():
    form = CreateUserForm()
    if form.validate_on_submit():
        # Cek apakah username sudah ada
        if User.query.filter_by(username=form.username.data).first():
            flash('Username sudah digunakan.', 'error')
        else:
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=generate_password_hash(form.password.data),
                role=form.role.data
            )
            db.session.add(user)
            db.session.commit()
            flash('Pengguna berhasil ditambahkan.', 'success')
            return redirect(url_for('admin.kelola_pengguna'))
    
    # Ambil semua pengguna
    users = User.query.all()
    perusahaan_list = Perusahaan.query.all()
    return render_template('admin/kelola_pengguna.html', form=form, users=users, perusahaan_list=perusahaan_list)

@admin_bp.route('/hapus_pengguna/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def hapus_pengguna(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Tidak dapat menghapus akun admin.', 'error')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('Pengguna berhasil dihapus.', 'success')
    return redirect(url_for('admin.kelola_pengguna'))

@admin_bp.route('/kelola_lowongan')
@login_required
@admin_required
def kelola_lowongan():
    lowongan_list = Lowongan.query.join(User).join(Perusahaan).all()
    return render_template('admin/kelola_lowongan.html', lowongan_list=lowongan_list)

@admin_bp.route('/hapus_lowongan/<int:lowongan_id>', methods=['POST'])
@login_required
@admin_required
def hapus_lowongan(lowongan_id):
    lowongan = Lowongan.query.get_or_404(lowongan_id)
    db.session.delete(lowongan)
    db.session.commit()
    flash('Lowongan berhasil dihapus.', 'success')
    return redirect(url_for('admin.kelola_lowongan'))

@admin_bp.route('/logout')
@login_required
def logout():
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('admin.login'))