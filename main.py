from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash
import pdb

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Rickee@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'yzXK27&&Fyr76sLLwD8'

#Classes aka MODEL
class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title    
        self.body = body
        self.owner = owner

    

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username    
        self.pw_hash = make_pw_hash(password)

#Checking for session

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


#Routes/functions aka Controller

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('main.html')


@app.route('/blog')
def blog():
   

    blog_id = request.args.get('id')
    if (blog_id):
        post = Blog.query.get(blog_id)
        return render_template('post.html', title="Blog Entry", post=post)
    posts = Blog.query.all()
    return render_template('blog.html',title="BLOG-MANIA",
        posts=posts)


@app.route('/userposts')
def singleUser():

    active_user = session['username']
    active = User.query.filter_by(username = active_user ).first()
    posts = Blog.query.filter_by(owner_id = active.id).all()

    return render_template('singleUser.html', title="User Posts", posts=posts)




@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    owner = User.query.filter_by(username=session['username']).first() # how does this get the user id for the owner
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if title == '' or body == '':
            flash('Title and Body cannt be blank' , 'error')
            return render_template('newpost.html', titleb=title, bodyb=body)
        else:
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()
            post =  {
                    "title": title,
                    "body": body
                    }
            return render_template('post.html', post=post)
    else:
        return render_template('newpost.html', title="New Post")


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']

        #Validation
        general_err = ""

        if username and password and password2:
            if password != password2:
                general_err = general_err + 'Password does not Match. '
            if len(username) > 3:
                user_exists = User.query.filter_by(username=username).first()
                if user_exists:
                    general_err = general_err + 'User already exists, login or create new an account. '
            else: 
                general_err = general_err + 'Username must be longer than 3 characters. '
            if len(password) < 3:
                general_err = general_err + 'Password Cannot be less an 3 characters. '     
        else:
            general_err = general_err + "username or password cannot be blank. "
        if not general_err:
            # pass_hash = make_pw_hash(password)
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash(general_err , 'error')
            return render_template('signup.html')

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        active_user = User.query.filter_by(username=username).first()
        general_err = ''
        print(f"{active_user} {active_user.pw_hash}")
        print(f"{make_pw_hash(password)}")
        if active_user and check_pw_hash(password, active_user.pw_hash):
            flash('Logged In')
            session['username']=username
            return redirect('/newpost')
        else: 
            general_err = 'User does not exist or Password not correct. '
            flash(general_err, 'error')
        return render_template('/login.html')
    
    return render_template('login.html')


@app.route('/posts/<int:page_num>')
def post(page_num):
    posts = Blog.query.paginate(per_page=4, page=page_num, error_out=True)
    #error_out means that the page will 404 error if set to True it will desplay an empty page. 
    return render_template('paginate.html', posts=posts)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


if __name__ == '__main__':
    app.run()