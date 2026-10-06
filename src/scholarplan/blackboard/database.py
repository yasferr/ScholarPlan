import sqlite3
import uuid
from pathlib import Path


class Blackboard:
    """Shared SQLite state used by ScholarPlan agents."""

    def __init__(self, database_path="outputs/scholarplan.db"):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(self.database_path)

        # Unique identifier for this ScholarPlan execution.
        self.run_id = str(uuid.uuid4())

        self._create_tables()
        self._migrate_tables()

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

    def _migrate_tables(self):
        """
        Add run_id to existing tables.

        This preserves previous ScholarPlan data while allowing
        each new execution to be isolated from earlier runs.
        """

        cursor = self.connection.cursor()

        tables = [
            "tasks",
            "sources",
            "claims",
            "feedback",
            "events"
        ]

        for table in tables:
            cursor.execute(
                f"PRAGMA table_info({table})"
            )

            columns = [
                row[1]
                for row in cursor.fetchall()
            ]

            if "run_id" not in columns:
                cursor.execute(
                    f"ALTER TABLE {table} ADD COLUMN run_id TEXT"
                )

        self.connection.commit()

    # -------------------------
    # TASKS
    # -------------------------

    def add_task(self, description, status="pending"):
        """Add a research task to the current run."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO tasks
            (description, status, run_id)
            VALUES (?, ?, ?)
            """,
            (
                description,
                status,
                self.run_id
            )
        )

        self.connection.commit()

        return cursor.lastrowid

    def get_tasks(self):
        """Return tasks belonging only to the current run."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT id, description, status
            FROM tasks
            WHERE run_id = ?
            """,
            (self.run_id,)
        )

        return cursor.fetchall()

    # -------------------------
    # SOURCES
    # -------------------------

    def add_source(
        self,
        title,
        authors="",
        source_url="",
        identifier=""
    ):
        """Store an academic source for the current run."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO sources
            (title, authors, source_url, identifier, run_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                title,
                authors,
                source_url,
                identifier,
                self.run_id
            )
        )

        self.connection.commit()

        return cursor.lastrowid

    def get_sources(self):
        """Return academic sources belonging only to the current run."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT id, title, authors, source_url, identifier
            FROM sources
            WHERE run_id = ?
            """,
            (self.run_id,)
        )

        return cursor.fetchall()

    # -------------------------
    # CLAIMS
    # -------------------------

    def add_claim(
        self,
        claim,
        source_id=None,
        status="pending"
    ):
        """Store a research claim for the current run."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO claims
            (claim, source_id, status, run_id)
            VALUES (?, ?, ?, ?)
            """,
            (
                claim,
                source_id,
                status,
                self.run_id
            )
        )

        self.connection.commit()

        return cursor.lastrowid

    def update_claim_status(self, claim_id, status):
        """Update the verification status of a research claim."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            UPDATE claims
            SET status = ?
            WHERE id = ?
            AND run_id = ?
            """,
            (
                status,
                claim_id,
                self.run_id
            )
        )

        self.connection.commit()

    def get_claims(self):
        """Return claims belonging only to the current run."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT id, claim, source_id, status
            FROM claims
            WHERE run_id = ?
            """,
            (self.run_id,)
        )

        return cursor.fetchall()

    # -------------------------
    # FEEDBACK
    # -------------------------

    def add_feedback(self, claim_id, message):
        """Store verification feedback for the current run."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO feedback
            (claim_id, message, run_id)
            VALUES (?, ?, ?)
            """,
            (
                claim_id,
                message,
                self.run_id
            )
        )

        self.connection.commit()

        return cursor.lastrowid

    def get_feedback(self):
        """Return feedback belonging only to the current run."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT id, claim_id, message
            FROM feedback
            WHERE run_id = ?
            """,
            (self.run_id,)
        )

        return cursor.fetchall()

    # -------------------------
    # EVENTS
    # -------------------------

    def add_event(self, event_type, message):
        """Store an execution event for the current run."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO events
            (event_type, message, run_id)
            VALUES (?, ?, ?)
            """,
            (
                event_type,
                message,
                self.run_id
            )
        )

        self.connection.commit()

    def get_events(self):
        """Return execution events belonging only to the current run."""

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT id, event_type, message
            FROM events
            WHERE run_id = ?
            """,
            (self.run_id,)
        )

        return cursor.fetchall()

    # -------------------------
    # CLOSE
    # -------------------------

    def close(self):
        """Close the database connection."""

        self.connection.close()