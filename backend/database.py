from models import Base, engine
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Base and models


def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def check_table_exists(table_name):
    """Check if a table exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def check_column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    inspector = inspect(engine)
    if not check_table_exists(table_name):
        return False

    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def migrate_database():
    """Apply any necessary database migrations."""
    # First create tables that don't exist yet
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    if "pipelines" not in existing_tables:
        print("Creating pipelines table...")
        Base.metadata.tables["pipelines"].create(bind=engine)

    if "build_logs" not in existing_tables:
        print("Creating build_logs table...")
        Base.metadata.tables["build_logs"].create(bind=engine)

    # Check and add missing columns to pipelines table
    if "pipelines" in existing_tables:
        # List of columns to check and add if missing
        pipeline_columns = [
            {"name": "url", "type": "VARCHAR"},
            {"name": "last_build_number", "type": "INTEGER"},
            {"name": "description", "type": "VARCHAR"}
        ]

        for col in pipeline_columns:
            if not check_column_exists("pipelines", col["name"]):
                print(f"Adding column {col['name']} to pipelines table...")
                conn = engine.connect()
                conn.execute(
                    f"ALTER TABLE pipelines ADD COLUMN {col['name']} {col['type']}")
                conn.close()

    # Check and add missing columns to build_logs table
    if "build_logs" in existing_tables:
        # List of columns to check and add if missing
        build_log_columns = [
            {"name": "build_number", "type": "INTEGER"},
            {"name": "duration", "type": "VARCHAR"},
            {"name": "commit_hash", "type": "VARCHAR"},
            {"name": "commit_message", "type": "VARCHAR"}
        ]

        for col in build_log_columns:
            if not check_column_exists("build_logs", col["name"]):
                print(f"Adding column {col['name']} to build_logs table...")
                conn = engine.connect()
                conn.execute(
                    f"ALTER TABLE build_logs ADD COLUMN {col['name']} {col['type']}")
                conn.close()

    print("Database migration completed successfully!")


if __name__ == "__main__":
    print("Checking database tables...")
    if not check_table_exists("pipelines") or not check_table_exists("build_logs"):
        print("Initializing database...")
        init_db()
    else:
        print("Tables already exist. Running migrations...")
        migrate_database()
