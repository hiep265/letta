import pg8000.native

conn = pg8000.native.Connection(user="postgres", password="root", host="localhost", database="letta")
conn.run("CREATE EXTENSION IF NOT EXISTS vector")
print("Enabled pgvector extension")
conn.close()
