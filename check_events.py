import sqlite3


DATABASE_PATH = "outputs/scholarplan.db"


connection = sqlite3.connect(
    DATABASE_PATH
)

cursor = connection.cursor()

cursor.execute(
    """
    SELECT id, event_type, message
    FROM events
    ORDER BY id
    """
)

events = cursor.fetchall()

print("\n=== SCHOLARPLAN EXECUTION TRACE ===\n")

for event in events:

    event_id, event_type, message = event

    print(
        f"[{event_id}] {event_type}"
    )

    print(
        f"    {message}"
    )

    print()


print(
    f"Total events: {len(events)}"
)

connection.close()