from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from perusahaan.forms import RegisterForm, LoginForm, ProfilForm, LowonganForm
from models import db, User, Perusahaan, Lowongan, Lamaran
from config import Config

perusahaan_bp = Blueprint('perusahaan', __name__, url_prefix='/perusahaan')

@perusahaan_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('perusahaan.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Cek apakah username atau email sudah ada
        if User.query.filter_by(username=form.username.data).first():
            flash('Username sudah digunakan.', 'error')
        elif User.query.filter_by(email=form.email.data).first():
            flash('Email sudah terdaftar.', 'error')
        else:
            # Buat user terlebih dahulu
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=generate_password_hash(form.password.data),
                role='perusahaan'
            )
            db.session.add(user)
            db.session.commit()
            
            # Buat profil perusahaan
            perusahaan = Perusahaan(
                user_id=user.id,
                nama_perusahaan=form.nama_perusahaan.data,
                bidang=form.bidang.data,
                deskripsi=form.deskripsi.data,
                website=form.website.data,
                alamat=form.alamat.data
            )
            db.session.add(perusahaan)
            db.session.commit()
            
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('perusahaan.login'))
    return render_template('perusahaan/register.html', form=form)

@perusahaan_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.role == 'perusahaan':
        return redirect(url_for('perusahaan.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data) and user.role == 'perusahaan':
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('perusahaan.dashboard'))
        flash('Login gagal. Periksa username dan password Anda.', 'error')
    return render_template('perusahaan/login.html', form=form)

@perusahaan_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'perusahaan':
        flash('Akses ditolak.', 'error')
        return redirect(url_for('index'))
    
    perusahaan = Perusahaan.query.filter_by(user_id=current_user.id).first()
    if not perusahaan:
        flash('Profil perusahaan belum dibuat.', 'warning')
        return redirect(url_for('perusahaan.profil_perusahaan'))
    
    # Ambil lowongan milik perusahaan
    lowongan_list = Lowongan.query.filter_by(perusahaan_id=perusahaan.id).all()
    
    # Hitung total lamaran untuk setiap lowongan
    stats = []
    for lowongan in lowongan_list:
        jumlah_lamaran = Lamaran.query.filter_by(lowongan_id=lowongan.id).count()
        stats.append({
            'lowongan': lowongan,
            'jumlah_lamaran': jumlah_lamaran
        })
    
    return render_template('perusahaan/dashboard.html', 
                         perusahaan=perusahaan,
                         stats=stats)

@perusahaan_bp.route('/profil_perusahaan', methods=['GET', 'POST'])
@login_required
def profil_perusahaan():
    if current_user.role != 'perusahaan':
        flash('Akses ditolak.', 'error')
        return redirect(url_for('index'))
    
    perusahaan = Perusahaan.query.filter_by(user_id=current_user.id).first()
    
    if not perusahaan:
        # Buat profil baru jika belum ada
        perusahaan = Perusahaan(user_id=current_user.id)
        db.session.add(perusahaan)
        db.session.commit()
    
    form = ProfilForm(obj=perusahaan)
    if form.validate_on_submit():
        perusahaan.nama_perusahaan = form.nama_perusahaan.data
        perusahaan.bidang = form.bidang.data
        perusahaan.deskripsi = form.deskripsi.data
        perusahaan.website = form.website.data
        perusahaan.alamat = form.alamat.data
        perusahaan.no_telepon = form.no_telepon.data
        
        # Handle upload logo
        if form.logo.data:
            filename = secure_filename(form.logo.data.filename)
            import uuid
            unique_filename = f"{uuid.uuid4()}_{filename}"
            logo_path = os.path.join(Config.UPLOAD_FOLDER_LOGO, unique_filename)
            os.makedirs(Config.UPLOAD_FOLDER_LOGO, exist_ok=True)
            form.logo.data.save(logo_path)
            perusahaan.logo_path = unique_filename
        
        db.session.commit()
        flash('Profil perusahaan berhasil diperbarui.', 'success')
        return redirect(url_for('perusahaan.dashboard'))
    
    return render_template('perusahaan/profil_perusahaan.html', form=form, perusahaan=perusahaan)

@perusahaan_bp.route('/buat_lowongan', methods=['GET', 'POST'])
@login_required
def buat_lowongan():
    if current_user.role != 'perusahaan':
        flash('Akses ditolak.', 'error')
        return redirect(url_for('index'))
    
    perusahaan = Perusahaan.query.filter_by(user_id=current_user.id).first()
    if not perusahaan:
        flash('Buat profil perusahaan terlebih dahulu.', 'warning')
        return redirect(url_for('perusahaan.profil_perusahaan'))
    
    form = LowonganForm()
    if form.validate_on_submit():
        lowongan = Lowongan(
            perusahaan_id=perusahaan.id,
            judul=form.judul.data,
            deskripsi=form.deskripsi.data,
            persyaratan=form.persyaratan.data,
            lokasi=form.lokasi.data,
            tipe_pekerjaan=form.tipe_pekerjaan.data,
            gaji_min=form.gaji_min.data,
            gaji_max=form.gaji_max.data
        )
        db.session.add(lowongan)
        db.session.commit()
        flash('Lowongan berhasil dibuat.', 'success')
        return redirect(url_for('perusahaan.kelola_lamaran', lowongan_id=lowongan.id))
    
    return render_template('perusahaan/buat_lowongan.html', form=form)

@perusahaan_bp.route('/kelola_lamaran/<int:lowongan_id>')
@login_required
def kelola_lamaran(lowongan_id):
    if current_user.role != 'perusahaan':
        flash('Akses ditolak.', 'error')
        return redirect(url_for('index'))
    
    perusahaan = Perusahaan.query.filter_by(user_id=current_user.id).first()
    lowongan = Lowongan.query.get_or_404(lowongan_id)
    
    if lowongan.perusahaan_id != perusahaan.id:
        flash('Anda tidak memiliki akses ke lowongan ini.', 'error')
        return redirect(url_for('perusahaan.dashboard'))
    
    lamaran_list = Lamaran.query.filter_by(lowongan_id=lowongan_id).all()
    
    return render_template('perusahaan/kelola_lamaran.html', 
                         lowongan=lowongan,
                         lamaran_list=lamaran_list)

@perusahaan_bp.route('/update_status_lamaran/<int:lamaran_id>', methods=['POST'])
@login_required
def update_status_lamaran(lamaran_id):
    if current_user.role != 'perusahaan':
        flash('Akses ditolak.', 'error')
        return redirect(url_for('index'))
    
    lamaran = Lamaran.query.get_or_404(lamaran_id)
    perusahaan = Perusahaan.query.filter_by(user_id=current_user.id).first()
    lowongan = Lowongan.query.get(lamaran.lowongan_id)
    
    if lowongan.perusahaan_id != perusahaan.id:
        flash('Anda tidak memiliki akses ke lamaran ini.', 'error')
        return redirect(url_for('perusahaan.dashboard'))
    
    status_baru = request.form.get('status')
    if status_baru in ['pending', 'diterima', 'ditolak']:
        lamaran.status = status_baru
        db.session.commit()
        flash(f'Status lamaran berhasil diubah menjadi {status_baru}.', 'success')
    else:
        flash('Status tidak valid.', 'error')
    
    return redirect(url_for('perusahaan.kelola_lamaran', lowongan_id=lowongan.id))

@perusahaan_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('perusahaan.login'))