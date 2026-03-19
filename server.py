from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
import os
import psycopg2


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:UwocProto2026!@uwoc-db.clmq80wy8lwq.us-west-2.rds.amazonaws.com:5432/uwoc",
)


def hello_world(request):
    return Response("Hello, Kevin!\n")


def db_test(request):
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        cur.close()
        conn.close()
        return Response(f"DB connected!\n{version}\n")
    except Exception as e:
        return Response(f"DB error: {e}\n", status=500)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    with Configurator() as config:
        config.add_route('hello', '/')
        config.add_view(hello_world, route_name='hello')
        config.add_route('db', '/db')
        config.add_view(db_test, route_name='db')
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', port, app)
    server.serve_forever()
