from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from urllib.parse import parse_qs
import os
import psycopg2


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:uwocproto2026@uwoc-db.clmq80wy8lwq.us-west-2.rds.amazonaws.com:5432/uwoc?sslmode=require",
)


def get_conn():
    return psycopg2.connect(DATABASE_URL, connect_timeout=5)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def messages_view(request):
    if request.method == "POST":
        body = request.body.decode("utf-8")
        params = parse_qs(body)
        text = params.get("text", [""])[0].strip()
        if text:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("INSERT INTO messages (text) VALUES (%s)", (text,))
            conn.commit()
            cur.close()
            conn.close()

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT text, created_at FROM messages ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    messages_html = ""
    for text, created_at in rows:
        messages_html += f"<li><strong>{created_at.strftime('%Y-%m-%d %H:%M:%S')}</strong> — {text}</li>\n"

    html = f"""<!DOCTYPE html>
<html>
<head><title>Messages</title></head>
<body>
  <h1>Messages</h1>
  <form method="POST">
    <input type="text" name="text" placeholder="Type a message..." size="40" autofocus>
    <button type="submit">Save</button>
  </form>
  <hr>
  <ul>{messages_html if messages_html else "<li><em>No messages yet.</em></li>"}</ul>
</body>
</html>"""
    return Response(html, content_type="text/html")


if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 8080))
    with Configurator() as config:
        config.add_route('messages', '/')
        config.add_view(messages_view, route_name='messages')
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', port, app)
    server.serve_forever()
