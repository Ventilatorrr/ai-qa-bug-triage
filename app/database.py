import os

import sqlite3

DATABASE_NAME = os.getenv("DATABASE_NAME", "bugtriage.db")


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def create_tables():
    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS project_members (
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role VARCHAR(50) NOT NULL,
            PRIMARY KEY (project_id, user_id),
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS bugs (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            title VARCHAR(255) NOT NULL,
            affected_version VARCHAR(20),
            description TEXT,
            steps_to_reproduce TEXT,
            expected_result TEXT,
            actual_result TEXT,
            severity VARCHAR(10),
            priority VARCHAR(10),
            assignee_id INTEGER,
            fix_version VARCHAR(20),
            status VARCHAR(20) NOT NULL DEFAULT 'Triage',
            created_by INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (assignee_id) REFERENCES users(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        """
    )

    conn.commit()
    conn.close()
    