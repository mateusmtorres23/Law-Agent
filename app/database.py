from fasthtml.common import database
from pathlib import Path

db_path = Path(__file__).resolve().parent / 'db/database.db'

class Case:
    id: int
    title: str
    creation_date: str

class Message:
    id: int
    case_id: int
    role: str
    content: str

class Document:
    id: int
    case_id: int
    filename: str
    text_content: str

db = database(db_path)
cases = db.create(Case, pk='id')
messages = db.create(Message, pk='id')
documents = db.create(Document, pk='id')
