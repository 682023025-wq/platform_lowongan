from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Konfirmasi Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Daftar')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Ingat Saya')
    submit = SubmitField('Masuk')

class ProfileForm(FlaskForm):
    nama_lengkap = StringField('Nama Lengkap', validators=[DataRequired(), Length(max=100)])
    no_telepon = StringField('No Telepon', validators=[Length(max=20)])
    alamat = TextAreaField('Alamat')
    cv = FileField('Upload CV (PDF)')
    submit = SubmitField('Simpan Profil')

class LamaranForm(FlaskForm):
    surat_lamaran = TextAreaField('Surat Lamaran', validators=[DataRequired()])
    cv = FileField('Upload CV (PDF)', validators=[DataRequired()])
    submit = SubmitField('Kirim Lamaran')