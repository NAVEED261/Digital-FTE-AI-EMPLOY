#!/usr/bin/env python3
"""
neon-postgres-setup: Initialize LearnFlow database on Neon PostgreSQL
MCP Code Execution Pattern - Script executes externally (0 tokens in context)
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from pathlib import Path

def read_schema() -> str:
    """Read schema.sql file."""
    schema_path = Path(__file__).parent.parent.parent.parent.parent / "learnflow-app" / "database" / "schema.sql"
    if not schema_path.exists():
        print(f"✗ Schema file not found: {schema_path}", file=sys.stderr)
        sys.exit(1)
    return schema_path.read_text()

def get_connection_string() -> str:
    """Get Neon connection string from environment."""
    conn_str = os.getenv('NEON_CONNECTION_STRING')
    if not conn_str:
        print("✗ NEON_CONNECTION_STRING environment variable not set", file=sys.stderr)
        print("  Set it with: export NEON_CONNECTION_STRING='postgresql://...'", file=sys.stderr)
        sys.exit(1)
    return conn_str

def execute_schema(conn_str: str, action: str = "init") -> bool:
    """Execute database schema."""
    try:
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()

        if action == "verify":
            # Just verify tables exist
            cur.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cur.fetchall()]
            expected_tables = ['users', 'modules', 'topics', 'exercises', 'submissions',
                             'conversations', 'progress_events', 'struggles', 'learning_paths']

            missing = set(expected_tables) - set(tables)
            if missing:
                print(f"✗ Missing tables: {', '.join(missing)}", file=sys.stderr)
                conn.close()
                return False
            else:
                print(f"✓ All {len(tables)} tables exist")
                conn.close()
                return True

        elif action in ["init", "reset"]:
            if action == "reset":
                # Drop all tables first
                cur.execute("""
                    DROP TABLE IF EXISTS learning_paths CASCADE;
                    DROP TABLE IF EXISTS struggles CASCADE;
                    DROP TABLE IF EXISTS progress_events CASCADE;
                    DROP TABLE IF EXISTS conversations CASCADE;
                    DROP TABLE IF EXISTS submissions CASCADE;
                    DROP TABLE IF EXISTS exercises CASCADE;
                    DROP TABLE IF EXISTS topics CASCADE;
                    DROP TABLE IF EXISTS teacher_profiles CASCADE;
                    DROP TABLE IF EXISTS student_profiles CASCADE;
                    DROP TABLE IF EXISTS modules CASCADE;
                    DROP TABLE IF EXISTS users CASCADE;
                """)
                print("✓ Dropped existing tables")

            # Read and execute schema
            schema = read_schema()
            cur.execute(schema)
            conn.commit()

            # Verify tables created
            cur.execute("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            table_count = cur.fetchone()[0]
            print(f"✓ Created {table_count} tables successfully")

            # Verify modules inserted
            cur.execute("SELECT COUNT(*) FROM modules")
            module_count = cur.fetchone()[0]
            print(f"✓ Inserted {module_count} Python modules")

            conn.close()
            return True

        else:
            print(f"✗ Unknown action: {action}", file=sys.stderr)
            return False

    except psycopg2.Error as e:
        print(f"✗ Database error: {str(e)[:200]}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)[:200]}", file=sys.stderr)
        return False

def main():
    """Main entry point."""
    action = sys.argv[1] if len(sys.argv) > 1 else "init"

    if action not in ["init", "verify", "reset"]:
        print(f"✗ Unknown action: {action}", file=sys.stderr)
        print("  Use: init (default), verify, or reset", file=sys.stderr)
        sys.exit(1)

    conn_str = get_connection_string()
    success = execute_schema(conn_str, action)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
