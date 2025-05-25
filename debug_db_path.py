#!/usr/bin/env python3
"""
Debug script to check database path configuration.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Calculate paths manually
basedir = os.path.abspath(
    os.path.dirname(os.path.join(os.getcwd(), "src", "auto_psycho", "config.py"))
)
project_dir = os.path.dirname(os.path.dirname(basedir))

print(f"basedir: {basedir}")
print(f"project_dir: {project_dir}")

expected_db_path = os.path.join(project_dir, "data", "tat_experiment.db")
print(f"Expected database path: {expected_db_path}")

# Now import and check
from auto_psycho.config import DevelopmentConfig

# Print database URI
config = DevelopmentConfig()
print(f"Database URI: {config.SQLALCHEMY_DATABASE_URI}")

# Check if data directory exists
data_dir = os.path.join(os.getcwd(), "data")
print(f"Data directory path: {data_dir}")
print(f"Data directory exists: {os.path.exists(data_dir)}")

# Extract database file path from URI
if config.SQLALCHEMY_DATABASE_URI.startswith("sqlite:///"):
    db_path = config.SQLALCHEMY_DATABASE_URI.replace("sqlite:///", "")
    print(f"Database file path: {db_path}")
    print(f"Database file directory: {os.path.dirname(db_path)}")
    print(f"Database file directory exists: {os.path.exists(os.path.dirname(db_path))}")

    # Check if we can create the database file
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        print(f"✓ Database directory created/exists")

        # Test creating a file in that directory
        test_file = os.path.join(os.path.dirname(db_path), "test.txt")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print(f"✓ Can write to database directory")

    except Exception as e:
        print(f"❌ Cannot create database directory or file: {e}")

# Test creating the actual database file path
print(f"\nTesting database file creation...")
try:
    import sqlite3

    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER)")
    conn.commit()
    conn.close()
    print("✓ SQLite database connection successful")

    # Clean up
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✓ Test database file cleaned up")

except Exception as e:
    print(f"❌ SQLite connection failed: {e}")
