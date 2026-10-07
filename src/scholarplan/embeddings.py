import pickle
import sqlite3
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingStore:
    """Create and store local semantic embeddings for ScholarPlan sources."""

    def __init__(
        self,
        database_path="outputs/scholarplan.db",
        model_name="all-MiniLM-L6-v2",
        run_id=None
    ):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(self.database_path)

        # Each ScholarPlan execution gets its own embedding namespace.
        self.run_id = run_id

        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

        self._create_table()
        self._migrate_table()

    def _create_table(self):
        """Create the embeddings table if it does not already exist."""

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL,
                vector BLOB NOT NULL,
                dimension INTEGER NOT NULL
            )
        """)

        self.connection.commit()

    def _migrate_table(self):
        """Add run_id to existing embedding tables if necessary."""

        cursor = self.connection.cursor()

        cursor.execute(
            "PRAGMA table_info(embeddings)"
        )

        columns = [
            row[1]
            for row in cursor.fetchall()
        ]

        if "run_id" not in columns:
            cursor.execute(
                """
                ALTER TABLE embeddings
                ADD COLUMN run_id TEXT
                """
            )

        self.connection.commit()

    def create_embedding(self, text):
        """Convert text into a 384-dimensional embedding vector."""

        vector = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return vector.astype(np.float32)

    def store_embedding(self, source_id, vector):
        """Store an embedding as a binary SQLite value."""

        vector_blob = pickle.dumps(vector)

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO embeddings
            (source_id, vector, dimension, run_id)
            VALUES (?, ?, ?, ?)
            """,
            (
                source_id,
                vector_blob,
                len(vector),
                self.run_id
            )
        )

        self.connection.commit()

        return cursor.lastrowid

    def embed_source(self, source_id, title, abstract=""):
        """Create and store an embedding for an academic source."""

        text = f"{title}\n\n{abstract}"

        vector = self.create_embedding(text)

        embedding_id = self.store_embedding(
            source_id=source_id,
            vector=vector
        )

        return {
            "id": embedding_id,
            "source_id": source_id,
            "dimension": len(vector)
        }

    def get_embeddings(self):
        """Retrieve embeddings belonging to the current run."""

        cursor = self.connection.cursor()

        if self.run_id is None:
            cursor.execute("""
                SELECT id, source_id, vector, dimension
                FROM embeddings
                WHERE run_id IS NULL
            """)
        else:
            cursor.execute(
                """
                SELECT id, source_id, vector, dimension
                FROM embeddings
                WHERE run_id = ?
                """,
                (self.run_id,)
            )

        rows = cursor.fetchall()

        embeddings = []

        for embedding_id, source_id, vector_blob, dimension in rows:
            vector = pickle.loads(vector_blob)

            embeddings.append(
                {
                    "id": embedding_id,
                    "source_id": source_id,
                    "vector": vector,
                    "dimension": dimension
                }
            )

        return embeddings

    def find_similar(self, vector, threshold=0.85):
        """
        Find embeddings from the current run whose cosine similarity
        is greater than or equal to the threshold.
        """

        existing_embeddings = self.get_embeddings()

        matches = []

        for embedding in existing_embeddings:
            existing_vector = embedding["vector"]

            similarity = float(
                np.dot(vector, existing_vector)
                / (
                    np.linalg.norm(vector)
                    * np.linalg.norm(existing_vector)
                )
            )

            if similarity >= threshold:
                matches.append(
                    {
                        "source_id": embedding["source_id"],
                        "similarity": similarity
                    }
                )

        matches.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

        return matches

    def is_duplicate(self, vector, threshold=0.85):
        """Return True if a sufficiently similar source exists in this run."""

        matches = self.find_similar(
            vector=vector,
            threshold=threshold
        )

        return len(matches) > 0

    def close(self):
        """Close the SQLite connection."""

        self.connection.close()