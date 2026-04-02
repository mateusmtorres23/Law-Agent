from fasthtml.common import fast_app, serve, Div, Form, Input, Button, Textarea, Span, H2, Script, Img
from starlette.staticfiles import StaticFiles
from datetime import datetime
from database import cases, messages

app, rt = fast_app(hdrs=[Script(src="https://cdn.tailwindcss.com")])

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

def IconScale(): return Img(src="/assets/scale.svg", cls="w-5 h-5")
def IconPlus(): return Img(src="/assets/plus.svg", cls="w-4 h-4")
def IconSearch(): return Img(src="/assets/search.svg", cls="w-4 h-4")
def IconMessage(): return Img(src="/assets/message-square.svg", cls="w-4 h-4 shrink-0")
def IconMore(): return Img(src="/assets/more-vertical.svg", cls="w-5 h-5")
def IconSend(): return Img(src="/assets/send.svg", cls="w-4 h-4")

def Sidebar(active_id=None):
    cases_list = cases()
    
    case_buttons = [
        Button(
            IconMessage(),
            Span(case.title, cls="truncate text-left ml-3"),
            hx_get=f"/chat/{case.id}",
            hx_target="#chat-container",
            hx_swap="outerHTML",
            cls=f"w-full flex items-center px-3 py-2 rounded-md text-sm transition-colors {'bg-slate-800 text-amber-400' if active_id == case.id else 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}"
        ) for case in cases_list
    ]

    return Div(
        Div(
            Div(IconScale(), Span("LexAssist AI", cls="ml-2"), cls="flex items-center text-white font-semibold text-lg"),
            cls="p-4 border-b border-slate-800 flex items-center justify-between"
        ),
        Form(
            Button(IconPlus(), Span("New Matter", cls="ml-2"), type="submit", cls="w-full flex items-center justify-center bg-amber-600 hover:bg-amber-700 text-white px-4 py-2 rounded-md transition-colors font-medium shadow-sm"),
            hx_post="/cases",
            cls="p-3"
        ),
        Div(
            Div(
                Span(IconSearch(), cls="absolute left-3 top-2.5 text-slate-500"),
                Input(type="text", placeholder="Search matters...", cls="w-full bg-slate-800 text-slate-200 placeholder-slate-500 rounded-md py-2 pl-9 pr-3 focus:outline-none focus:ring-1 focus:ring-amber-500 text-sm"),
                cls="relative"
            ),
            cls="px-3 py-2"
        ),
        Div(
            Div("Active Matters", cls="px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2"),
            Div(*case_buttons, cls="space-y-1 px-2", id="sidebar-case-list"),
            cls="flex-1 overflow-y-auto mt-2 custom-scrollbar"
        ),
        cls="w-72 bg-slate-900 flex flex-col border-r border-slate-800 h-screen shrink-0"
    )

def ChatMessage(text, sender):
    is_user = sender == 'user'
    return Div(
        Div(
            text,
            cls=f"max-w-[75%] rounded-lg px-5 py-4 text-sm leading-relaxed shadow-sm {'bg-slate-900 text-white rounded-br-none' if is_user else 'bg-white text-slate-800 border border-slate-200 rounded-bl-none'}"
        ),
        cls=f"flex {'justify-end' if is_user else 'justify-start'} mb-6"
    )

def ChatWindow(case_id):
    active_case = cases.get(case_id)
    if not active_case:
        return Div("Case not found.", id="chat-container", cls="flex-1 flex items-center justify-center h-screen")
        
    case_messages = messages(where=f"case_id = {case_id}")
    
    rendered_messages = [ChatMessage(msg.content, msg.role) for msg in case_messages]

    return Div(
        Div(
            Div(
                H2(active_case.title, cls="text-lg font-semibold text-slate-800"),
                Span("AI Agent actively assisting", cls="text-xs text-slate-500")
            ),
            Button(IconMore(), cls="text-slate-400 hover:text-slate-600 transition-colors"),
            cls="bg-white px-6 py-4 border-b border-slate-200 flex justify-between items-center shadow-sm z-10"
        ),
        Div(
            *rendered_messages,
            id="message-list",
            cls="flex-1 overflow-y-auto p-6 bg-slate-50"
        ),
        Div(
            Form(
                Textarea(name="content", placeholder="Ask a legal question...", rows=1, cls="w-full resize-none border border-slate-300 rounded-lg py-3 pl-4 pr-12 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent min-h-[56px] max-h-32 text-sm text-slate-800 shadow-sm"),
                Button(IconSend(), type="submit", cls="absolute right-2 bottom-2 p-2 bg-slate-900 text-white rounded-md hover:bg-slate-800 transition-colors flex items-center justify-center"),
                hx_post=f"/chat/{case_id}/message",
                hx_target="#message-list",
                hx_swap="beforeend",
                hx_on__after_request="this.reset()",
                cls="max-w-4xl mx-auto relative flex items-end"
            ),
            Div(Span("AI may produce inaccurate information regarding case law. Always verify statutes.", cls="text-xs text-slate-400 font-medium tracking-wide"), cls="text-center mt-3"),
            cls="p-6 bg-white border-t border-slate-200"
        ),
        id="chat-container",
        cls="flex-1 flex flex-col min-w-0 h-screen"
    )

@rt("/")
def get():
    all_cases = cases()
    initial_case_id = all_cases[-1].id if all_cases else None
    
    return Div(
        Sidebar(active_id=initial_case_id),
        ChatWindow(initial_case_id) if initial_case_id else Div("Create a new matter to begin.", id="chat-container", cls="flex-1 flex items-center justify-center h-screen bg-slate-50"),
        cls="flex h-screen bg-slate-50 font-sans w-full"
    )

@rt("/chat/{case_id}")
def get(case_id: int):
    return ChatWindow(case_id)

@rt("/cases")
def post():
    timestamp = datetime.now().isoformat()
    new_title = f"New Matter {len(cases()) + 1}"
    cases.insert(title=new_title, creation_date=timestamp)
    return "", {"HX-Refresh": "true"}

@rt("/chat/{case_id}/message")
def post(case_id: int, content: str):
    user_msg = messages.insert(case_id=case_id, role="user", content=content)
    
    ai_response_text = "This is a placeholder for the local Qwen 2.5 2B inference."
    ai_msg = messages.insert(case_id=case_id, role="ai", content=ai_response_text)
    
    return ChatMessage(user_msg.content, user_msg.role), ChatMessage(ai_msg.content, ai_msg.role)

if __name__ == '__main__':
    serve()