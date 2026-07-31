<img width="2160" height="1221" alt="Screenshot 2026-07-31 124540" src="https://github.com/user-attachments/assets/43d094cd-40c6-423f-b207-2ec6ad40e8cf" />

<img width="1080" height="626" alt="image" src="https://github.com/user-attachments/assets/b353ee27-53a5-4bbb-b774-04239ad8dca3" />

<img width="1080" height="625" alt="image" src="https://github.com/user-attachments/assets/5bfbf97c-47ac-452f-b246-633966172da6" />

<img width="1080" height="628" alt="image" src="https://github.com/user-attachments/assets/2480559a-9748-47a4-9258-72b7e96b4051" />



# AI Agent Platform

**AI Agent Platform** is a Django-based conversational assistant designed to interact with an ecommerce database using natural language and tool-enabled AI. It uses Anthropic Claude models to interpret user requests, execute backend order/customer queries, and render clean UI feedback in a chat interface.

## Why this project stands out

- **AI-first ecommerce assistant**: The app turns natural language prompts into structured database operations like listing orders, finding order details, and cancelling orders.
- **Tool-enabled LLM orchestration**: It uses a modular tool registry so the AI can call backend functions safely and transparently.
- **Practical resume value**: Demonstrates full-stack experience with Django, database modeling, AI agent integration, frontend chat UX, and production-grade prompt/tool handling.
- **Readable, real-world UX**: The frontend renders results in a conversational assistant screen and transforms raw JSON outputs into human-friendly cards.

## Key features

- Conversational AI chat UI with agent history and active tool context
- Anthropic Claude integration with tool call support
- Ecommerce domain modeling for customers, products, orders, and order items
- Structured order rendering inside chat results (order ID, customer, total, status)
- Default ordering API excludes cancelled/deleted orders for accurate results
- Admin-ready backend with Django admin for ecommerce data management

## Project structure

- `ai_assistant/` — main Django project settings and URL configuration
- `agents/` — AI agent models, chat session handling, and agent service layer
- `ecommerce/` — ecommerce models for customers, products, orders, and items
- `chat/` — message/session persistence for the conversational interface
- `core_ai/` — AI orchestration, prompt construction, and Claude tool bridge
- `tools/` — tool registry and ecommerce tool implementations
- `templates/` — single-page UI for the AI assistant experience

## Tech stack

- Python 3.x
- Django 6.0.6
- SQLite database
- Anthropic Claude client (`anthropic` package)
- Django REST and modern JavaScript-driven chat UI

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/25punam/ai-agent-platform.git
   cd "D:\Claude API\ai_assistant"
   ```

2. Install dependencies:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r ..\requirements.txt
   ```

3. Create the `.env` file or set environment variables:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

4. Run database migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

6. Open the assistant:
   ```text
   http://127.0.0.1:8000/
   ```

## How it works

1. The frontend sends user prompts through the Django chat view.
2. The `ChatService` saves user messages and invokes `run_agent()`.
3. `run_agent()` builds context from previous session messages and calls Claude.
4. Claude may return a normal text response or trigger a tool call.
5. If a tool is used, the backend executes a registered function and returns structured JSON.
6. The UI renders the response as a chat bubble or as structured order cards.

## Useful use cases

- Natural language order search: `Show me all orders`
- Order detail queries: `Find order ORD005`
- Cancellation flows: `Cancel order ORD007`
- Ecommerce admin QA: `List pending orders` or `Which customers are active?`

## Dependencies

- `annotated-types==0.7.0`
- `anthropic==0.105.2`
- `anyio==4.13.0`
- `asgiref==3.11.1`
- `certifi==2026.5.20`
- `distro==1.9.0`
- `Django==6.0.6`
- `djangorestframework==3.17.1`
- `docstring_parser==0.18.0`
- `h11==0.16.0`
- `httpcore==1.0.9`
- `httpx==0.28.1`
- `idna==3.18`
- `jiter==0.15.0`
- `pydantic==2.13.4`
- `pydantic_core==2.46.4`
- `python-dotenv==1.2.2`
- `sniffio==1.3.1`
- `sqlparse==0.5.5`
- `typing-inspection==0.4.2`
- `typing_extensions==4.15.0`
- `tzdata==2026.2`

## Notes

- The current implementation uses SQLite for ease of setup.
- For production, replace the secret key, enable `DEBUG=False`, and configure a secure host/database.
- The AI integration is modular: adding more tools is possible through `tools/registry.py`.
