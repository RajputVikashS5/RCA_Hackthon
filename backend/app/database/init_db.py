from app.database.connection import initialize_database


if __name__ == "__main__":
    initialize_database()
    print("PostgreSQL schema and pgvector index are ready.")
