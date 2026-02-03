# AI Email Order Agent - Implementation Guide

## Overview

An AI agent that reads order request emails, parses them using OpenAI, and automatically creates orders via API.

---

## Architecture

```
┌────────────┐     ┌─────────┐     ┌─────────────┐     ┌─────────┐     ┌──────────────┐
│  Email     │ --> │ Zapier  │ --> │ FastAPI     │ --> │ OpenAI  │ --> │ Express API  │
│  Inbox     │     │         │     │ (main-agent)│     │ (parse) │     │(parcel-backend)│
└────────────┘     └─────────┘     └─────────────┘     └─────────┘     └──────────────┘
                                          │                                   │
                                          └───────── Confirmation Email ──────┘
```

---

## Components

### 1. main-agent (FastAPI) - Port 8000

AI agent that processes emails and orchestrates order creation.

**Endpoints:**

| Method | Endpoint    | Description                    |
|--------|-------------|--------------------------------|
| POST   | `/webhook`  | Receives email from Zapier     |
| POST   | `/process`  | Local testing with email.txt   |

**Dependencies:**
- fastapi
- uvicorn
- openai
- httpx
- python-dotenv

---

### 2. parcel-backend (Express) - Port 3000

REST API for customers, products, and orders.

**Endpoints:**

| Method | Endpoint              | Description           |
|--------|-----------------------|-----------------------|
| GET    | `/api/customers`      | Get all customers     |
| POST   | `/api/customers`      | Create customer       |
| GET    | `/api/products`       | Get all products      |
| POST   | `/api/products`       | Create product        |
| GET    | `/api/orders`         | Get all orders        |
| POST   | `/api/orders`         | Create order          |

---

## Flow

### Step 1: Email Received
Zapier detects new email and triggers webhook.

### Step 2: Parse Email
FastAPI sends email content to OpenAI to extract:
- Customer name
- Customer email
- Customer address
- Product name
- Quantity

### Step 3: API Calls
Agent calls Express APIs:
1. Check/Create customer (`POST /api/customers`)
2. Find product (`GET /api/products`)
3. Create order (`POST /api/orders`)

### Step 4: Confirmation
Send confirmation email with order ID.

---

## File Structure

```
AI-agenet/
├── main-agent/              # FastAPI - AI Agent
│   ├── main.py              # Entry point
│   ├── agent.py             # Agent logic
│   ├── email.txt            # Test email file
│   ├── requirements.txt
│   └── venv/
│
├── parcel-backend/          # Express - REST API
│   ├── index.js
│   ├── config/
│   ├── models/
│   ├── routes/
│   ├── controllers/
│   ├── test/
│   └── package.json
│
└── docs/
    └── implementation-guide.md
```

---

## Implementation Steps

### Phase 1: Setup
- [x] Create FastAPI project (main-agent)
- [x] Create Express project (parcel-backend)
- [ ] Install OpenAI SDK in main-agent

### Phase 2: Agent Core
- [ ] Create email parser using OpenAI
- [ ] Create API client for parcel-backend
- [ ] Implement `/process` endpoint (local testing)

### Phase 3: Integration
- [ ] Implement `/webhook` endpoint
- [ ] Setup Zapier trigger
- [ ] Add email confirmation (SMTP)

### Phase 4: Testing
- [ ] Test with sample email.txt
- [ ] Test Zapier integration
- [ ] End-to-end testing

---

## Environment Variables

### main-agent (.env)
```
OPENAI_API_KEY=your_openai_key
EXPRESS_API_URL=http://localhost:3000/api
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASSWORD=your_password
```

### parcel-backend (.env)
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=parcel_db
DB_USER=postgres
DB_PASSWORD=your_password
PORT=3000
```

---

## Sample Email Format

```
From: john@example.com

Hi,

I would like to order 2 Laptops.
Please deliver to: 123 Main Street, New York, NY 10001

Thanks,
John Doe
```

---

## Expected OpenAI Response

```json
{
  "customer": {
    "name": "John Doe",
    "email": "john@example.com",
    "address": "123 Main Street, New York, NY 10001"
  },
  "order": {
    "product": "Laptop",
    "quantity": 2
  }
}
```

---

## API Call Sequence

```
1. POST /api/customers
   Body: { name, email, address }
   Response: { id: 1, ... }

2. GET /api/products?name=Laptop
   Response: [{ id: 1, name: "Laptop", price: 999.99 }]

3. POST /api/orders
   Body: { customerId: 1, items: [{ productId: 1, quantity: 2 }] }
   Response: { id: 1, totalAmount: 1999.98, ... }

4. Send confirmation email with order ID
```

---

## Reference: aichat Project (D:\aichat)

We are reusing patterns and components from our existing `aichat` project.

### What We're Using

| Component | From aichat | Purpose |
|-----------|-------------|---------|
| **LangChain** | Core framework | Tool-calling agent pattern |
| **langchain-openai** | LLM integration | ChatOpenAI for processing |
| **Tool pattern** | `@tool` decorator | Define API tools |
| **Agent loop** | `main.py` | LLM decides which tool to call |
| **Logging setup** | `setup_logging()` | Rotating file logs |
| **Config loader** | `load_client_config()` | Environment handling |
| **Project structure** | File organization | Clean separation |

### LangChain Tool Pattern (from aichat)

```python
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

@tool
def my_tool(param: str) -> str:
    """Tool description for LLM"""
    return result

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools([my_tool])
```

### Updated Dependencies (with LangChain)

```
fastapi
uvicorn
langchain
langchain-openai
langchain-core
httpx
python-dotenv
```

### Why LangChain?

| Without LangChain | With LangChain |
|-------------------|----------------|
| Fixed sequence of API calls | LLM decides dynamically |
| Manual parsing logic | Tools auto-executed |
| Hardcoded flow | Flexible for edge cases |

### aichat Files to Reference

| File | What to Copy |
|------|--------------|
| `main.py:51-80` | Logging configuration |
| `main.py:83-125` | Config loader pattern |
| `main.py:419-501` | Agent tool-calling loop |
| `.env.example` | Environment template |
