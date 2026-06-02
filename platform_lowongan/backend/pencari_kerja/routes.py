from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from pencari_kerja.forms import RegisterForm, LoginForm, ProfileForm, LamaranForm
from models import db, User, Perusahaan, Lowongan, Lamaran
from config import Config

pencari_kerja_bp = Blueprint('pencari_kerja', __name__, url_prefix='/pencari_kerja')

@pencari_kerja_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('pencari_kerja.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Cek apakah username atau email sudah ada
        if User.query.filter_by(username=form.username.data).first():
            flash('Username sudah digunakan.', 'error')
        elif User.query.filter_by(email=form.email.data).first():
            flash('Email sudah terdaftar.', 'error')
        else:
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=generate_password_hash(form.password.data),
                role='pencari_kerja'
            )
            db.session.add(user)
            db.session.commit()
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('pencari_kerja.login'))
    return render_template('pencari_kerja/register.html', form=form)

@pencari_kerja_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.role == 'pencari_kerja':
        return redirect(url_for('pencari_kerja.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data) and user.role == 'pencari_kerja':
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('pencari_kerja.dashboard'))
        flash('Login gagal. Periksa username dan password Anda.', 'error')
    return render_template('pencari_kerja/login.html', form=form)

@pencari_kerja_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'pencari_kerja':
        flash('Akses ditolak.', 'error')
        return redirect(url_for('index'))
    
    # Ambil lowongan terbaru
    lowongan_terbaru = Lowongan.query.order_by(Lowongan.tanggal_dibuat.desc()).limit(5).all()
    
    # Ambil lamaran pengguna
    lamaran_saya = Lamaran.query.filter_by(pencari_kerja_id=current_user.id).all()
    
    return render_template('pencari_kerja/dashboard.html', 
                         lowongan_terbaru=lowongan_terbaru,
                         lamaran_saya=lamaran_saya)

@pencari_kerja_bp.route('/cari_lowongan')
@login_required
def cari_lowongan():
    if current_user.role != 'pencari_kerja':
        flash('Akses ditolak.', 'error')
        return redirect(url_for('index'))
    
    query = request.args.get('q', '')
    lokasi = request.args.get('lokasi', '')
    tipe = request.args.get('tipe', '')
    
    # Filter lowongan
    lowongan_query = Lowongan.query.join(Perusahaan)
    
    if query:
        lowongan_query = lowongan_query.filter(Lowongan.judul.ilike(f'%{query}%'))
    if lokasi:
        lowongan_query = lowongan_query.filter(Lowongan.lokasi.ilike(f'%{lokasi}%'))
    if tipe:
        lowongan_query = lowongan_query.filter(Lowongan.tipe_pekerjaan == tipe)
    
    lowongan_list = lowongan_query.order_by(Lowongan.tanggal_dibuat.desc()).all()
    
    return render_template('pencari_kerja/cari_lowongan.html', 
                         lowongan_list=lowongan_list,
                         query=query,
                         lokasi=lokasi,
                         tipe=tipe)

@pencari_kerja_bp.route('/detail_lowongan/<int:lowongan_id>')
@login_required
def detail_lowongan(lowongan_id):
    if current_user.role != 'pencari_kerja':
        flash('Akses ditolak.', 'error')
        return redirect(url_for('index'))
    
    lowongan = Lowongan.query.get_or_404(lowongan_id)
    perusahaan = Perusahaan.query.filter_by(user_id=lowongan.perusahaan_id).first()
    
    # Cek apakah sudah melamar
    sudah_melamar = Lamaran.query.filter_by(
        pencari_kerja_id=current_user.id,
        lowongan_id=lowongan_id
    ).first() is not None
    
    return render_template('pencari_kerja/detail_lowongan.html', 
                         lowongan=lowongan,
                         perusahaan=perusahaan,
                         sudah_melamar=sudah_melamar)

@pencari_kerja_bp.route('/lamar/<int:lowongan_id>', methods=['GET', 'POST'])
@login_required
def lamar(lowongan_id):
    if current_user.role != 'pencari_kerja':
        flash('Akses ditolak.', 'error')
        return redirect(url_for('index'))
    
    lowongan = Lowongan.query.get_or_404(lowongan_id)
    
    # Cek apakah sudah melamar
    if Lamaran.query.filter_by(pencari_kerja_id=current_user.id, lowongan_id=lowongan_id).first():
        flash('Anda sudah melamar untuk lowongan ini.', 'warning')
        return redirect(url_for('pencari_kerja.detail_lowongan', lowongan_id=lowongan_id))
    
    form = LamaranForm()
    if form.validate_on_submit():
        # Handle upload CV
        cv_file = form.cv.data
        if cv_file:
            filename = secure_filename(cv_file.filename)
            # Buat nama file unik
            import uuid
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Simpan file
            cv_path = os.path.join(Config.UPLOAD_FOLDER_CV, unique_filename)
            os.makedirs(Config.UPLOAD_FOLDER_CV, exist_ok=True)
            cv_file.save(cv_path)
            
            # Buat lamaran
            lamaran = Lamaran(
                pencari_kerja_id=current_user.id,
                lowongan_id=lowongan_id,
                cv_path=unique_filename,
                surat_lamaran=form.surat_lamaran.data
            )
            db.session.add(lamaran)
            db.session.commit()
            
            flash('Lamaran berhasil dikirim!', 'success')
            return redirect(url_for('pencari_kerja.lamaran_saya'))
    
    return render_template('pencari_kerja/lamaran.html', form=form, lowongan=lowongan)

@pencari_kerja_bp.route('/lamaran_saya')
@login_required
def lamaran_saya():
    if current_user.role != 'pencari_kerja':
        flash('Akses ditolak.', 'error')
        return redirect(url_for('index'))
    
    lamaran_list = Lamaran.query.filter_by(pencari_kerja_id=current_user.id).all()
    return render_template('pencari_kerja/lamaran.html', lamaran_list=lamaran_list)

@pencari_kerja_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('pencari_kerja.login'))