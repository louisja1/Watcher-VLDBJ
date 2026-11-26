import psycopg2

def get_connection():
    conn = psycopg2.connect(
        database="watcherdb", user="ANONYMOUS", host="127.0.0.1", port="5555"
    )
    conn.set_session(autocommit=True)
    cursor = conn.cursor()
    return conn, cursor

def close_connection(conn, cursor):
    cursor.close()
    conn.close()

def configure_single_worker_session(cursor):
    # Disable parallel query execution for deterministic single-worker behavior.
    cursor.execute("set max_parallel_workers_per_gather = 0;")