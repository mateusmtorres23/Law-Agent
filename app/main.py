from fasthtml.common import fast_app, serve, Form, Input, Button, Div, P
from database import db, cases, messages, documents
from datetime import datetime

app, rt = fast_app()

@rt("/")
def get():
    return Div(
        P("Law Agent Core Initialized"),
        Form(
            Input(name='title', type='text', placeholder='Enter a case title'),
            Button('Initialize case chat', type='submit'),
            hx_post='/cases',
            hx_target='#case-ledger',
            hx_swap='beforeend'
        ),
        Div(id='case-ledger')
    )

@rt("/cases")
def post(title: str):
    timestamp = datetime.now().isoformat()
    new_case = cases.insert(title=title, creation_date=timestamp)
    return P(f"Case '{title}' initialized with ID {new_case.id}")

if __name__ == "__main__":
    serve() 