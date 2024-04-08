from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(200))
    due_date = db.Column(db.Date)
    completed = db.Column(db.Boolean)


@app.route('/')
def index():
    tasks = ToDo.query.all()
    now = date.today()
    
    return render_template('base.html', todo_list = tasks, now = now)

@app.route('/add', methods=["POST"])
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    due_date = request.form.get('due_date')
    task_date = datetime.strptime(due_date, '%Y-%m-%d').date()
    new_task = ToDo(title = title, description = description, due_date = task_date , completed = False)
    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/update/<int:task_id>')
def update(task_id):
    to_update = ToDo.query.get(task_id)
    to_update.completed = not to_update.completed
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete(task_id):
    to_delete = ToDo.query.get(task_id)
    db.session.delete(to_delete)
    db.session.commit()

    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True) 
