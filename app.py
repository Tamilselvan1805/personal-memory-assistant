from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load Gemini API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY is missing from .env")

genai.configure(api_key=api_key)
# for model in genai.list_models():
#     print(model.name, "supports:", model.supported_generation_methods)
# Create model only after configuration
model = genai.GenerativeModel(model_name="models/gemini-2.5-pro")

app = Flask(__name__)
DB_NAME = 'memory.db'

# -------- Database Setup --------
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()

        # Memory logs
        c.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person TEXT,
                date TEXT,
                event TEXT,
                details TEXT,
                tags TEXT
            )
        ''')

        # To-Do List
        c.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                is_done INTEGER DEFAULT 0,
                due_date TEXT
            )
        ''')

        # Ideas
        c.execute('''
            CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                tags TEXT
            )
        ''')

        conn.commit()

# -------- Routes --------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/log', methods=['GET', 'POST'])
def log_memory():
    if request.method == 'POST':
        person = request.form['person']
        date = request.form['date']
        event = request.form['event']
        details = request.form['details']
        tags = request.form['tags']
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("INSERT INTO memories (person, date, event, details, tags) VALUES (?, ?, ?, ?, ?)",
                         (person, date, event, details, tags))
        return redirect(url_for('home'))
    return render_template('log_memory.html')

@app.route('/search', methods=['GET', 'POST'])
def search_memory():
    results = []
    if request.method == 'POST':
        query = request.form['query']
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM memories WHERE person LIKE ? OR event LIKE ? OR details LIKE ? OR tags LIKE ?",
                      (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
            results = c.fetchall()
    return render_template('search.html', results=results)

@app.route('/todo', methods=['GET', 'POST'])
def todo():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        if request.method == 'POST':
            task = request.form['task']
            due_date = request.form.get('due_date', '')
            c.execute("INSERT INTO todos (task, due_date) VALUES (?, ?)", (task, due_date))
        c.execute("SELECT * FROM todos")
        todos = c.fetchall()
    return render_template('todo.html', todos=todos)

@app.route('/todo/done/<int:todo_id>')
def mark_done(todo_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("UPDATE todos SET is_done = 1 WHERE id = ?", (todo_id,))
    return redirect(url_for('todo'))

@app.route('/ideas', methods=['GET', 'POST'])
def ideas():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            tags = request.form['tags']
            c.execute("INSERT INTO ideas (title, description, tags) VALUES (?, ?, ?)",
                      (title, description, tags))
        c.execute("SELECT * FROM ideas")
        ideas = c.fetchall()
    return render_template('ideas.html', ideas=ideas)

@app.route('/ai-query', methods=['POST'])
def ai_query():
    user_question = request.form['question']
    # Fetch memories from DB
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT date, event, details FROM memories")
        memory_entries = c.fetchall()

    # Format context for AI
    context = "\n".join([f"{date} - {event}: {details}" for date, event, details in memory_entries])
    prompt = f"Based on the following memory log:\n{context}\n\nQuestion: {user_question}"

    try:
        # Call Gemini model with safe structure
        response = model.generate_content([prompt])  # Gemini expects a list input
        answer = response.text.strip()
    except Exception as e:
        print("Gemini error:", e)
        answer = "⚠️ Gemini AI failed to process your question. Please try again later."

    return render_template('results.html', question=user_question, answer=answer)


# -------- Main --------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
