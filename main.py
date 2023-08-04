from flask import Flask , render_template , request , session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_mail import Message
import json
from datetime import datetime



with open('config.json' , 'r') as c:
    params = json.load(c)["params"]

local_server = True

db = SQLAlchemy()
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail_user'],
    MAIL_PASSWORD = params['gmail_password']
)

mail = Mail(app)

if(local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']

db.init_app(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String, nullable=False)
    date = db.Column(db.String(12), nullable = True)
    email = db.Column(db.String(30), nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(30), nullable=False)
    content = db.Column(db.String(300), nullable=False)
    date = db.Column(db.String(12), nullable = True)
    img_file = db.Column(db.String(12), nullable = False)
    tagline = db.Column(db.String(12), nullable = False)
  
 
 
@app.route("/")
def home():
    posts = Posts.query.all()[0:params['no_of_posts']]
    # posts = db.get_or_404(Posts,id)
    return render_template('index.html', params=params, posts=posts)
  
@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/dashboard", methods = ['GET' , 'POST'])
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        posts = Posts.query.all()
        return render_template('dashboard.html',params=params,posts=posts)

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if username == params['admin_user'] and userpass == params['admin_password']:
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html',params=params, post=posts)
    
    return render_template('login.html', params=params)
  
@app.route("/post/<string:post_slug>",methods = ['GET'])
def posts_route(post_slug):
    # post = Posts.query.filter_by(slug=post_slug)
    post = db.one_or_404(db.select(Posts).filter_by(slug = post_slug))
    return render_template('post.html', params=params, post = post)
 
@app.route("/contact" , methods = ['GET' , 'POST'])
def contact():
    if(request.method == 'POST'):
        # Add entry to the database
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name = name, phone_num = phone, msg = message , date = datetime.now(), email = email)
        db.session.add(entry)
        db.session.commit()
        # msg = Message('New message from: ' + name, 
        #               sender = [params['gmail_user']],
        #               recipients = [params['gmail_user']],
        #               body = message + "\n" + phone + "\n" + email
        #               )
        # mail.send(msg)



        mail.send_message('New message from: ' + name, 
                        sender = ("Me",[params['gmail_user']]),
                        recipients = [params['gmail_user']],
                        body = message + "\n" + phone + "\n" + email
                        
                        )

    return render_template('contact.html', params=params)

app.run(debug = True)