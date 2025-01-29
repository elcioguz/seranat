from flask import Flask, render_template

#Create a flask instance
app = Flask(__name__)

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
#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404
