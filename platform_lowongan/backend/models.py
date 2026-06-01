from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# Association table for many-to-many relationship between User and Lowongan (saved jobs)
saved_jobs = db.Table('saved_jobs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('lowongan_id', db.Integer, db.ForeignKey('lowongan.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'pencari_kerja', 'perusahaan'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    perusahaan = db.relationship('Perusahaan', backref='user', uselist=False, cascade='all, delete-orphan')
    lamaran = db.relationship('Lamaran', backref='pencari_kerja', lazy='dynamic', cascade='all, delete-orphan')
    saved_lowongan = db.relationship('Lowongan', secondary=saved_jobs, lazy='subquery',
                                     backref=db.backref('saved_by', lazy='dynamic'))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.email}>'


class Perusahaan(db.Model):
    __tablename__ = 'perusahaan'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    nama_perusahaan = db.Column(db.String(150), nullable=False)
    bidang = db.Column(db.String(100))
    deskripsi = db.Column(db.Text)
    alamat = db.Column(db.String(255))
    website = db.Column(db.String(200))
    logo = db.Column(db.String(255))  # Path to logo file
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lowongan = db.relationship('Lowongan', backref='perusahaan', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Perusahaan {self.nama_perusahaan}>'


class Lowongan(db.Model):
    __tablename__ = 'lowongan'
    
    id = db.Column(db.Integer, primary_key=True)
    perusahaan_id = db.Column(db.Integer, db.ForeignKey('perusahaan.id'), nullable=False, index=True)
    judul = db.Column(db.String(150), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    persyaratan = db.Column(db.Text, nullable=False)
    lokasi = db.Column(db.String(100))
    gaji_min = db.Column(db.Numeric(12, 2))
    gaji_max = db.Column(db.Numeric(12, 2))
    tipe_pekerjaan = db.Column(db.String(50))  # Full-time, Part-time, Contract, Internship
    status = db.Column(db.String(20), default='aktif')  # aktif, tutup, draft
    deadline = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lamaran = db.relationship('Lamaran', backref='lowongan', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Lowongan {self.judul}>'


class Lamaran(db.Model):
    __tablename__ = 'lamaran'
    
    id = db.Column(db.Integer, primary_key=True)
    lowongan_id = db.Column(db.Integer, db.ForeignKey('lowongan.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(30), default='menunggu')  # menunggu, diterima, ditolak, dilihat
    cv_file = db.Column(db.String(255))  # Path to uploaded CV
    surat_lamaran = db.Column(db.Text)
    tanggal_lamar = db.Column(db.DateTime, default=datetime.utcnow)
    tanggal_review = db.Column(db.DateTime)
    catatan = db.Column(db.Text)  # Notes from company
    
    def __repr__(self):
        return f'<Lamaran {self.id} - {self.status}>'