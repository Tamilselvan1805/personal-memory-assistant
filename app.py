from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime, date
import os
from dotenv import load_dotenv
import google.generativeai as genai

# ---------------- Gemini Setup ----------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY is missing from .env")

genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

app = Flask(__name__)
app.secret_key = "yoursecretkey"  # required for flash messages
DB_NAME = 'memory.db'


# ---------------- Database Setup ----------------
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()

        # Memories table
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

        # Todos table
        c.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                is_done INTEGER DEFAULT 0,
                due_date TEXT,
                priority TEXT DEFAULT 'Low'
            )
        ''')

        # Ideas table
        c.execute('''
            CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                tags TEXT
            )
        ''')

        # ---- Migration: Add priority if missing ----
        try:
            c.execute("SELECT priority FROM todos LIMIT 1")
        except sqlite3.OperationalError:
            c.execute("ALTER TABLE todos ADD COLUMN priority TEXT DEFAULT 'Low'")

        conn.commit()


# ---------------- Routes ----------------
@app.route('/')
def home():
    return render_template('index.html')


# ---- Log memory ----
@app.route('/log', methods=['GET', 'POST'])
def log_memory():
    if request.method == 'POST':
        person = request.form['person']
        date = request.form['date']
        event = request.form['event']
        details = request.form['details']
        tags = request.form['tags']
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                "INSERT INTO memories (person, date, event, details, tags) VALUES (?, ?, ?, ?, ?)",
                (person, date, event, details, tags)
            )
            conn.commit()
        return redirect(url_for('home'))
    return render_template('log_memory.html')


# ---- Search memory ----
@app.route('/search', methods=['GET', 'POST'])
def search_memory():
    results = []
    query = ""
    if request.method == 'POST':
        query = request.form['query']
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT * FROM memories 
                WHERE person LIKE ? OR event LIKE ? OR details LIKE ? OR tags LIKE ?
            """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
            results = c.fetchall()
    return render_template('search.html', results=results, query=query)

# ---- To-Do List ----
@app.route('/todo', methods=['GET', 'POST'])
def todo():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        if request.method == 'POST':
            task = request.form['task']
            due_date = request.form.get('due_date', '')
            priority = request.form.get('priority', 'Low')
            c.execute("INSERT INTO todos (task, due_date, priority) VALUES (?, ?, ?)",
                      (task, due_date, priority))
            conn.commit()

            # ✅ Redirect after POST prevents duplicate insert on refresh
            return redirect(url_for('todo'))

        c.execute("""
            SELECT * FROM todos 
            ORDER BY is_done ASC,
                CASE priority
                    WHEN 'High' THEN 3
                    WHEN 'Medium' THEN 2
                    WHEN 'Low' THEN 1
                    ELSE 0
                END DESC,
                due_date ASC
        """)
        todos = c.fetchall()
    return render_template('todo.html', todos=todos, current_date=date.today())


@app.route('/todo/done/<int:todo_id>')
def mark_done(todo_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("UPDATE todos SET is_done = 1 WHERE id = ?", (todo_id,))
        conn.commit()
    return redirect(url_for('todo'))


@app.route('/todo/delete/<int:todo_id>', methods=['POST'])
def delete_task(todo_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
    return redirect(url_for('todo'))


# ---- Ideas ----
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
            conn.commit()
            return redirect(url_for("ideas"))  # ✅ Prevents duplicate insert on refresh

        c.execute("SELECT * FROM ideas")
        ideas = c.fetchall()
    return render_template('ideas.html', ideas=ideas)


@app.route("/delete/<int:id>", methods=["POST"])
def delete_idea(id):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM ideas WHERE id = ?", (id,))
        conn.commit()
    flash("Idea deleted successfully!", "success")
    return redirect(url_for("ideas"))


# ---- AI Query ----
@app.route('/ai-query', methods=['POST'])
def ai_query():
    user_question = request.form.get('question', '').strip()
    if not user_question:
        return render_template('results.html',
                               question="",
                               answer="⚠️ No question provided. Please enter something to ask.")

    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT date, event, details FROM memories ORDER BY date DESC LIMIT 10")
        memory_entries = c.fetchall()

    context = "\n".join([f"{date} - {event}: {details}" for date, event, details in memory_entries])
    prompt = f"Based on the following memory log:\n{context}\n\nQuestion: {user_question}"

    answer = None
    for attempt in range(3):
        try:
            response = model.generate_content([prompt])
            answer = response.text.strip()
            break
        except Exception as e:
            print(f"Gemini attempt {attempt+1} failed:", e)
            import time; time.sleep(2)

    if not answer:
        answer = "⚠️ Gemini AI failed to process your question. Please try again later."

    return render_template('results.html', question=user_question, answer=answer)


# ---------------- Startup ----------------
db_initialized = False

@app.before_request
def setup():
    global db_initialized
    if not db_initialized:
        init_db()
        db_initialized = True


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5050)
