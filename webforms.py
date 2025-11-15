from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

class UserForm(FlaskForm):
    name= StringField ('Name',validators=[DataRequired()])
    username=StringField ('Username',validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    favourite_colour =StringField('Favourite Colour')
    about_author = TextAreaField('About Author')
    password_hash=PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords must match!')])
    password_hash2=PasswordField('Confirm password', validators=[DataRequired()])
    profile_pic=FileField("Profile Pic")
    submit = SubmitField("Submit")

#Create a posts form
class PostForm(FlaskForm):
    title=StringField("Başlık",validators=[DataRequired()])
    #content=StringField("İçerik",validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Content',validators=[DataRequired()])
    author=StringField("Yazar")
    slug=StringField("Slug",validators=[DataRequired()])
    submit=SubmitField("Submit")

class PasswordForm(FlaskForm):
    email= StringField ("What is your email?", validators=[DataRequired()])
    password_hash = PasswordField("What is your password?", validators=[DataRequired()])
    submit= SubmitField ("Submit")

class NamerForm(FlaskForm):
    name= StringField ("What is your name?", validators=[DataRequired()])
    submit= SubmitField ("Submit")

#Create a login form
class LoginForm(FlaskForm):
    username=StringField ("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

#Create a search form
class SearchForm(FlaskForm):
    searched=StringField ("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")