import json
from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP("Notes")

NOTES_FILE = Path("notes_data.json")

def _load() -> dict[str, str]:
    if NOTES_FILE.exists():
        return json.loads(NOTES_FILE.read_text())
    return {}

def _save(notes: dict[str, str]):
    NOTES_FILE.write_text(json.dumps(notes, indent=2))

@mcp.tool()
def add_note(title: str, content: str) -> str:
    """Add a note with a title and content."""
    notes = _load()
    notes[title] = content
    _save(notes)
    return f"Note '{title}' saved."

@mcp.tool()
def search_notes(query: str) -> str:
    """Search notes by keyword. Returns matching notes."""
    notes = _load()
    results = [
        f"{title}: {content}"
        for title, content in notes.items()
        if query.lower() in title.lower() or query.lower() in content.lower()
    ]
    return "\n".join(results) if results else "No notes found."

@mcp.tool()
def list_notes() -> str:
    """List all saved note titles."""
    notes = _load()
    if not notes:
        return "No notes yet."
    return ", ".join(notes.keys())

if __name__ == "__main__":
    mcp.run(transport="stdio")
