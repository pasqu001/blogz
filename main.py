from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Rickee@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'yzXK27&&Fyr76sLLwD8'

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1500))
    

    def __init__(self, title, body):
        self.title = title    
        self.body = body

@app.route('/', methods=['POST', 'GET'])
def index():

    posts = Blog.query.all()
    return render_template('blog.html',title="BLOG-MANIA",
        posts=posts)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if title == '' or body == '':
            flash('Title and Body cannt be blank' , 'error')
            return render_template('newpost.html', titleb=title, bodyb=body)
        else:
            new_post = Blog(title, body)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/')
    else:
        return render_template('newpost.html', title="New Post")
if __name__ == '__main__':
    app.run()