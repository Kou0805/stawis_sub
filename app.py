from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz, os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stawis.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

# データベースのモデル 内容
class Stawis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ログインページのエンドポイント
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

@app.route('/')
def index():
  # データベースからデータを取得
  stawis = Stawis.query.all()
  return render_template('index.html', stawises=stawis)

# ログインページ
@app.route('/login', methods=['GET','POST'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if check_password_hash(user.password, password):
      login_user(user)
      return redirect('/')
  else:
    return render_template('login.html')

@app.route('/logout')
def logout():
  logout_user()
  return redirect('/login')


#updateページ
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
  #引数idに一致するデータをDBから取得
  stawis = Stawis.query.get(id)
  if request.method == 'GET':
    return render_template('update.html', stawis=stawis)
  else:
    stawis.title = request.form['title']
    stawis.body = request.form['body']
    db.session.commit()
    return redirect(url_for('index'))

#signupページ
@app.route('/signup', methods=['GET','POST'])
def signup():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    user = User(username=username, password=generate_password_hash(password, method='sha256'))
    db.session.add(user)
    db.session.commit()
    return redirect('/login')
  else:
    return render_template('signup.html')

# 登録ページ create
@app.route('/create', methods=['GET','POST'])
@login_required
def create():
# POSTの時の処理
  if request.method == 'POST':
    # データベースに保存
    stawis = Stawis(title=request.form['title'], body=request.form['body'])
    db.session.add(stawis)
    db.session.commit()
    # トップページにリダイレクト
    return redirect(url_for('index'))
  # GETの時の処理
  else:
    return render_template('create.html')

if __name__ == "__main__":
  app.run(debug=True)
