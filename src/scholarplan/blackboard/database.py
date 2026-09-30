import sqlite3
from pathlib import Path


class Blackboard:
    """Shared SQLite state used by ScholarPlan agents."""

    def __init__(self, database_path="outputs/scholarplan.db"):
        self.database_path = Path(database_path)

        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(self.database_path)

        self._create_tables()

    def _create_tables(self):
        """Create the tables required by the blackboard."""

        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                authors TEXT,
                source_url TEXT,
                identifier TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim TEXT NOT NULL,
                source_id INTEGER,
                status TEXT,
                FOREIGN KEY (source_id) REFERENCES sources(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id INTEGER,
                message TEXT NOT NULL,
                FOREIGN KEY (claim_id) REFERENCES claims(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)

        self.connection.commit()

    def add_task(self, description, status="pending"):
        """Add a research task to the blackboard."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO tasks (description, status)
            VALUES (?, ?)
            """,
            (description, status)
        )

        self.connection.commit()

        return cursor.lastrowid

    def add_event(self, event_type, message):
        """Store an execution event on the blackboard."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO events (event_type, message)
            VALUES (?, ?)
            """,
            (event_type, message)
        )

        self.connection.commit()

    def get_tasks(self):
        """Return all tasks stored on the blackboard."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT id, description, status
            FROM tasks
            """
        )

        return cursor.fetchall()

    def close(self):
        """Close the database connection."""

        self.connection.close()