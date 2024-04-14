from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
# for authentication:
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_login import LoginManager

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'somekey'

db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True)
    user_name = db.Column(db.String(150))
    password = db.Column(db.String(150))
    todos = db.relationship('ToDo')

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(200))
    due_date = db.Column(db.Date)
    completed = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


def sign_up_validation(email,user_name,password1,password2):
    if len(email) <4:
        flash("Email must be longer than 4 characters.", category='error')
    elif "@" not in email:
        flash("Email must contain '@'.", category='error')
    elif "." not in email:
        flash("Email must have a domain with '.' .", category='error')
    elif len(user_name)<3:
        flash("First name must be longer than 2 characters.", category='error')
    elif " " in user_name:
        flash("First name must not have any whitespaces in it.", category='error')
    elif password1 != password2:
        flash("Passwords don\'t match.", category='error')
    elif len(password1) <7:
        flash("Password must be longer than 7 characters.", category='error')
    else:
        flash("Account created.", category='success')
        return True
    return False



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        
        if user:
            if check_password_hash(user.password, password):
                flash("Login successful!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('index'))
            else:
                flash("Incorrect password.", category='error')
        else:
            flash("User does not exist!", category="error")

    return render_template("login.html", user = current_user)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        email = request.form.get('email')
        user_name = request.form.get('user_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash("User already exists!", category="error")

        if sign_up_validation(email, user_name, password1, password2):
            user = User(email=email, user_name=user_name, password=generate_password_hash(password1,method='sha256'))
            db.session.add(user)
            db.session.commit()
            login_user(user, remember = True)
            return redirect(url_for('index'))

    return render_template("signup.html", user = current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    tasks = ToDo.query.all()
    now = date.today()

    return render_template('home.html', todo_list = tasks, now = now, user = current_user)

@app.route('/add', methods=["POST"])
@login_required
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    due_date = request.form.get('due_date')
    task_date = datetime.strptime(due_date, '%Y-%m-%d').date()
    new_task = ToDo(title = title, description = description, due_date = task_date , completed = False, user_id = current_user.id)

    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/update/<int:task_id>')
@login_required
def update(task_id):
    to_update = ToDo.query.get(task_id)
    to_update.completed = not to_update.completed
    
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
@login_required
def delete(task_id):
    to_delete = ToDo.query.get(task_id)
    
    db.session.delete(to_delete)
    db.session.commit()
 
    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    app.run(debug=True)