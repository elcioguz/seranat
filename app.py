from flask import Flask, render_template, flash, request, url_for, redirect
from sqlalchemy.orm import backref
from werkzeug.utils import redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PasswordForm, PostForm, UserForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os

#Create a flask instance
app = Flask(__name__)
#Add CKEditor
ckeditor=CKEditor(app)
#Add database
#app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sierran4@localhost:5432/personel'
#Secret key
app.config['SECRET_KEY'] ="bu gizli anahtardır"

#Upload folder for images
UPLOAD_FOLDER='static/images'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

#Initialize the db
db=SQLAlchemy(app)
migrate = Migrate(app, db)  # This enables the 'flask db' commands
#Flask login stuff
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

    @property
    def password(self):
        raise AttributeError ('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    # Create a String
    def __repr__(self):
        return '<Name %r>' % self.name

#Create model
class Users (db.Model, UserMixin):
    __tablename__='personel'
    id = db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20),nullable=False,unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favourite_colour=db.Column(db.String(120))
    about_author=db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(hours=3))
    profile_pic=db.Column(db.String(), nullable=True)
    #password check
    password_hash = db.Column(db.String(200))
    #User can have many posts
    posts=db.relationship('Posts', backref='poster', cascade='all, delete-orphan') #cascade kısmı, silinen userlarla ilişkili postlarında beraber silinmesi için eklendi

#Create a blog post model
class Posts (db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(255))
    content=db.Column(db.Text())
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(hours=3))
    slug=db.Column(db.String(255))
    #Foreign key to link users (refer to the primary key of the user)
    poster_id=db.Column(db.Integer, db.ForeignKey('personel.id',ondelete='CASCADE')) #ondelete kısmı silinen userlarla ilişkili postlarında beraber silinmesi için eklendi

#Json
@app.route('/date')

def get_current_date():
    return {"Date": date.today()}

#Create login page
@app.route('/login', methods=['GET','POST'])

def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(username=form.username.data).first()
        if user:
            #Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Login successful!')
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong password -try again!')
        else:
            flash('That user does not exist - try again!')
    return render_template('login.html', form=form)

#Create logout page
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out!')
    return redirect(url_for('login'))

#Create dashboard page
@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    form = UserForm()
    id=current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_colour = request.form['favourite_colour']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']
        if request.files['profile_pic']:
            name_to_update.profile_pic = request.files['profile_pic']

            #Grab image name
            pic_filename=secure_filename(name_to_update.profile_pic.filename)
            #Set UUID
            pic_name=str(uuid.uuid1()) + "_" + pic_filename
            #Save that image
            saver=request.files['profile_pic']
            #Change it to a string to save to db
            name_to_update.profile_pic=pic_name
            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                flash('User updated successfully!')
                return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)
            except:
                flash('Oops smthg went wrong! Try again!')
                return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)
        else:
            db.session.commit()
            flash('User updated successfully!')
            return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)
    else:
        return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)
    return render_template('dashboard.html')

@app.route('/user/add', methods=['GET','POST'])
def add_user():
    name=None
    form=UserForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(email=form.email.data).first()
        if user is None:
            #Hash the password
            hashed_pw=generate_password_hash(form.password_hash.data)
            user=Users(username=form.username.data, name=form.name.data, email=form.email.data, favourite_colour=form.favourite_colour.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name=form.name.data
        form.name.data=''
        form.username.data = ''
        form.email.data=''
        form.favourite_colour.data=''
        form.password_hash=''
        flash('User added successfully!')
    our_users=Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)

#Update database record
@app.route('/update/<int:id>',methods=['GET','POST'])
@login_required
def update(id):
    form=UserForm()
    name_to_update=Users.query.get_or_404(id)
    if request.method=='POST':
        name_to_update.name=request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_colour = request.form['favourite_colour']
        name_to_update.username=request.form['username']
        try:
            db.session.commit()
            flash('User updated successfully!')
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
        except:
            flash('Oops smthg went wrong! Try again!')
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update,id =id)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if id==current_user.id:

        user_to_delete = Users.query.get_or_404(id)
        name = None
        form = UserForm()
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash('User deleted successfully!')
            our_users = Users.query.order_by(Users.date_added)
            return render_template("add_user.html", form=form, name=name, our_users=our_users)
        except:
            flash('Oops there is a problem deleting the user! Try again!')
            return render_template("add_user.html", form=form, name=name, our_users=our_users)
    else:
        flash('Sorry you can not delete that user!')
        return redirect(url_for('dashboard'))
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete=Posts.query.get_or_404(id)
    id=current_user.id
    if id==post_to_delete.poster.id or id == 23:

        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            #Return a message
            flash("Blog post was deleted!")
            # Grab all the posts from the database
            posts = Posts.query.order_by(Posts.date_posted)
            return (render_template("posts.html", posts=posts))
        except:
            #Return an error message
            flash("Oops,there is a problem deleting the post, please try again!")
            # Grab all the posts from the database
            posts = Posts.query.order_by(Posts.date_posted)
            return (render_template("posts.html", posts=posts))
    else:
        # Return a message
        flash("You aren't authorized to delete that post!")
        # Grab all the posts from the database
        posts = Posts.query.order_by(Posts.date_posted)
        return (render_template("posts.html", posts=posts))
#Add posts page
@app.route('/add_post', methods=['GET','POST'])
#@login_required
def add_post():
    form=PostForm()

    if form.validate_on_submit():
        poster=current_user.id
        post=Posts(title=form.title.data,content=form.content.data,poster_id=poster,slug=form.slug.data)
        #Clear the form
        form.title.data=''
        form.content.data=''
        #form.author.data=''
        form.slug.data=''

        #Add post data in to db
        db.session.add(post)
        db.session.commit()
        flash('Blog post submitted succesfully!')
    #Redirect to the web-page
    return (render_template("add_post.html", form=form))

@app.route('/posts')

def posts():
    #Grab all the posts from the database
    posts=Posts.query.order_by(Posts.date_posted)
    return (render_template("posts.html", posts=posts))

@app.route('/posts/<int:id>')

def post(id):
    post=Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

@app.route('/posts/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title=form.title.data
        #post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        #Add to db
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated!")
        return redirect(url_for('post',id=post.id ))

    if current_user.id==post.poster_id or current_user.id == 23:
        form.title.data=post.title
        #form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You aren't authorized to edit this post!")
        posts = Posts.query.order_by(Posts.date_posted)
        return (render_template("posts.html", posts=posts))

#Pass stuff to Navbar
@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

#Create a search function
@app.route('/search', methods=["POST"])
def search():
    form=SearchForm()
    posts=Posts.query
    if form.validate_on_submit():
        #Get data from submitted form
        post.searched=form.searched.data
        #Query the database
        posts=posts.filter(Posts.content.like('%'+ post.searched + '%'))
        posts=posts.order_by(Posts.title).all()
        return render_template('search.html', form=form, searched=post.searched, posts=posts)

#Create a route decorator
@app.route('/admin')
@login_required
def admin():
    id=current_user.id
    if id==23:
        return render_template("admin.html")
    else:
        flash("Sorry, you must be the admin to access the admin page..")
        return redirect(url_for('dashboard'))

#Create a route decorator
@app.route('/')

def index():
    first_name='Oğuz'
    stuff='This is bold text'
    kullanicilar=["Ahmet","Mehmet","Ali","Ayşe", 41]
    return render_template("index.html",
                           first_name=first_name,
                           stuff=stuff,
                           kullanicilar=kullanicilar)

@app.route('/user/<name>')

def user(name):
    return render_template("user.html", user_name=name)

#Create custom error pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

#Create a password test page
@app.route('/test_pw', methods=['GET','POST'])

def test_pw():
    email=None
    password=None
    pw_to_check=None
    passed=None
    form=PasswordForm()
    if form.validate_on_submit():
        email=form.email.data
        password=form.password_hash.data

        form.email.data=''
        form.password_hash.data = ''

        #Lookup user by email address
        pw_to_check=Users.query.filter_by(email=email).first()

        # Check hashed password
        passed= check_password_hash(pw_to_check.password_hash, password)

    return render_template('test_pw.html',email=email, password=password, pw_to_check=pw_to_check, passed=passed, form=form)

#Create a name page
@app.route('/name', methods=['GET','POST'])

def name():
    name=None
    form=NamerForm()
    if form.validate_on_submit():
        name=form.name.data
        form.name.data=''
        flash("Form başarı ile yüklendi!")
    return render_template('name.html',name=name, form=form)

