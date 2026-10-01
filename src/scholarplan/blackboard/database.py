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
        """Create the tables required by ScholarPlan."""

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

    # -------------------------
    # TASKS
    # -------------------------

    def add_task(self, description, status="pending"):
        """Add a research task."""

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

    def get_tasks(self):
        """Return all stored tasks."""

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, description, status
            FROM tasks
        """)

        return cursor.fetchall()

    # -------------------------
    # SOURCES
    # -------------------------

    def add_source(self, title, authors="", source_url="", identifier=""):
        """Store an academic source."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO sources
            (title, authors, source_url, identifier)
            VALUES (?, ?, ?, ?)
            """,
            (title, authors, source_url, identifier)
        )

        self.connection.commit()

        return cursor.lastrowid

    def get_sources(self):
        """Return all stored academic sources."""

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, title, authors, source_url, identifier
            FROM sources
        """)

        return cursor.fetchall()

    # -------------------------
    # CLAIMS
    # -------------------------

    def add_claim(self, claim, source_id=None, status="pending"):
        """Store a research claim."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO claims
            (claim, source_id, status)
            VALUES (?, ?, ?)
            """,
            (claim, source_id, status)
        )

        self.connection.commit()

        return cursor.lastrowid

    def get_claims(self):
        """Return all stored claims."""

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, claim, source_id, status
            FROM claims
        """)

        return cursor.fetchall()

    # -------------------------
    # FEEDBACK
    # -------------------------

    def add_feedback(self, claim_id, message):
        """Store verification feedback for a claim."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO feedback
            (claim_id, message)
            VALUES (?, ?)
            """,
            (claim_id, message)
        )

        self.connection.commit()

        return cursor.lastrowid

    def get_feedback(self):
        """Return all stored feedback."""

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, claim_id, message
            FROM feedback
        """)

        return cursor.fetchall()

    # -------------------------
    # EVENTS
    # -------------------------

    def add_event(self, event_type, message):
        """Store an execution event."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO events
            (event_type, message)
            VALUES (?, ?)
            """,
            (event_type, message)
        )

        self.connection.commit()

    def get_events(self):
        """Return all execution events."""

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, event_type, message
            FROM events
        """)

        return cursor.fetchall()

    # -------------------------
    # CLOSE
    # -------------------------

    def close(self):
        """Close the database connection."""

        self.connection.close()