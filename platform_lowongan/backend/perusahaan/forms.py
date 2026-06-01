from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField, SelectField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Konfirmasi Password', validators=[DataRequired(), EqualTo('password')])
    nama_perusahaan = StringField('Nama Perusahaan', validators=[DataRequired(), Length(max=100)])
    bidang = StringField('Bidang Usaha', validators=[DataRequired(), Length(max=100)])
    deskripsi = TextAreaField('Deskripsi Perusahaan')
    website = StringField('Website')
    alamat = TextAreaField('Alamat')
    submit = SubmitField('Daftar')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Ingat Saya')
    submit = SubmitField('Masuk')

class ProfilForm(FlaskForm):
    nama_perusahaan = StringField('Nama Perusahaan', validators=[DataRequired(), Length(max=100)])
    bidang = StringField('Bidang Usaha', validators=[DataRequired(), Length(max=100)])
    deskripsi = TextAreaField('Deskripsi Perusahaan')
    website = StringField('Website')
    alamat = TextAreaField('Alamat')
    no_telepon = StringField('No Telepon', validators=[Length(max=20)])
    logo = FileField('Upload Logo Perusahaan')
    submit = SubmitField('Simpan Profil')

class LowonganForm(FlaskForm):
    judul = StringField('Judul Lowongan', validators=[DataRequired(), Length(max=100)])
    deskripsi = TextAreaField('Deskripsi Pekerjaan', validators=[DataRequired()])
    persyaratan = TextAreaField('Persyaratan', validators=[DataRequired()])
    lokasi = StringField('Lokasi', validators=[DataRequired(), Length(max=100)])
    tipe_pekerjaan = SelectField('Tipe Pekerjaan', 
                                choices=[('full_time', 'Full Time'), 
                                        ('part_time', 'Part Time'), 
                                        ('contract', 'Contract'), 
                                        ('internship', 'Internship')],
                                validators=[DataRequired()])
    gaji_min = DecimalField('Gaji Minimum (Opsional)', validators=[Optional()], places=2)
    gaji_max = DecimalField('Gaji Maximum (Opsional)', validators=[Optional()], places=2)
    submit = SubmitField('Buat Lowongan')