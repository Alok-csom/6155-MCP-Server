import os
import sqlite3
import json
import uvicorn
from fastmcp import FastMCP
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from seed_db import init_database

# Initialize database schema and records
init_database()

mcp = FastMCP("Student Gradebook MCP Server")
DB_PATH = "student_records.db"

@mcp.tool()
def get_database_schema() -> str:
    """Returns SQL schema for all tables in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall() if row[0] is not None]
    conn.close()
    return "\n\n".join(tables) if tables else "No tables found."

@mcp.tool()
def execute_sql_query(query: str) -> str:
    """Executes a read-only SELECT SQL query against the database."""
    clean_query = query.strip()
    if not clean_query.upper().startswith("SELECT"):
        return "Security Restriction: Only SELECT queries are allowed."
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(clean_query)
        rows = [dict(r) for r in cursor.fetchall()]
        return json.dumps(rows, default=str)
    except Exception as e:
        return f"Database Error: {str(e)}"
    finally:
        conn.close()

@mcp.tool()
def get_student_transcript(student_name: str) -> str:
    """Fetches course scores and letter grades for a named student."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    sql = """
        SELECT 
            s.full_name, c.course_code, c.course_name,
            g.numeric_score, gs.letter_grade, gs.gpa_points
        FROM students s
        JOIN grades g ON s.student_id = g.student_id
        JOIN courses c ON g.course_id = c.course_id
        JOIN grade_scale gs ON g.numeric_score >= gs.min_score AND g.numeric_score <= gs.max_score
        WHERE s.full_name LIKE ?;
    """
    cursor.execute(sql, (f"%{student_name}%",))
    results = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return json.dumps(results) if results else f"No records found for '{student_name}'."

# 1. Generate FastMCP application with stateless HTTP enabled
mcp_app = mcp.http_app(stateless_http=True)

# 2. Wrap in FastAPI parent container to add explicit CORS headers required by Copilot Studio
app = FastAPI(title="Student Gradebook MCP Wrapper")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Mount FastMCP at both /mcp and root / to accept all incoming path variations
app.mount("/mcp", mcp_app)
app.mount("/", mcp_app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)