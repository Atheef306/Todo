from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Get database URL from environment - SIMPLIFIED AND TESTED
database_url = os.getenv("DATABASE_URL")

if database_url and "postgres" in database_url:
    # Use the EXACT connection string from Render environment
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    print("Using PostgreSQL database from environment variable")
else:
    # Fallback to SQLite
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
    print("Using SQLite database")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    try:
        if request.method == 'POST':
            title = request.form['title']
            desc = request.form['desc']
            todo = Todo(title=title, desc=desc)
            db.session.add(todo)
            db.session.commit()
            return redirect("/")
        
        allTodo = Todo.query.all() 
        return render_template('index.html', allTodo=allTodo)
    
    except Exception as e:
        return f"Database error: {str(e)}", 500

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    try:
        if request.method == 'POST':
            title = request.form['title']
            desc = request.form['desc']
            todo = Todo.query.filter_by(sno=sno).first()
            if todo:
                todo.title = title
                todo.desc = desc
                db.session.commit()
            return redirect("/")
            
        todo = Todo.query.filter_by(sno=sno).first()
        if todo:
            return render_template('update.html', todo=todo)
        return redirect("/")
    
    except Exception as e:
        return f"Database error: {str(e)}", 500

@app.route('/delete/<int:sno>')
def delete(sno):
    try:
        todo = Todo.query.filter_by(sno=sno).first()
        if todo:
            db.session.delete(todo)
            db.session.commit()
        return redirect("/")
    
    except Exception as e:
        return f"Database error: {str(e)}", 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=10000)


