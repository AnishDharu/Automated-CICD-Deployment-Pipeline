import os, psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def init_db():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS tasks
            (id SERIAL PRIMARY KEY, title TEXT NOT NULL, done BOOLEAN DEFAULT FALSE)""")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def list_tasks():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
        return jsonify([{"id": r[0], "title": r[1], "done": r[2]} for r in cur.fetchall()])

@app.post("/tasks")
def add_task():
    title = (request.get_json(silent=True) or {}).get("title")
    if not title:
        return {"error": "title required"}, 400
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING id", (title,))
        return {"id": cur.fetchone()[0], "title": title}, 201

@app.put("/tasks/<int:task_id>")
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    done = data.get("done")
    if done is None or not isinstance(done, bool):
        return {"error": "boolean 'done' required"}, 400
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE tasks SET done = %s WHERE id = %s RETURNING id, title, done", (done, task_id))
        row = cur.fetchone()
        if not row:
            return {"error": "task not found"}, 404
        return {"id": row[0], "title": row[1], "done": row[2]}, 200

init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)