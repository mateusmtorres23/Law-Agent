from fasthtml.common import database

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

db = database('db/database.db')
cases = db.create(Case, pk='id')
messages = db.create(Message, pk='id')
documents = db.create(Document, pk='id')
