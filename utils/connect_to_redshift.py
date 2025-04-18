import psycopg2
def connect_to_redshift(host, port, database, user, password):
    try:
        conn = psycopg2.connect(
            host = host,
            port = port,
            database = database,
            user = user,
            password = password 
        )
        return conn
    except Exception as e:
        print(f"Error connect to Redshift: {e}")
        return None