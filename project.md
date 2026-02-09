# AI Email Order Agent

## What Is This?

An AI agent that automatically reads customer order emails, extracts order details using OpenAI, creates orders via API, and sends confirmation emails back to the customer.

## Flow

```
Customer Email --> Zapier --> FastAPI Agent --> OpenAI (parse) --> Express API (create order) --> Confirmation Email
```

---

## Architecture

| Component        | Tech                  | Port | Role                                  |
|------------------|-----------------------|------|---------------------------------------|
| **main-agent**   | FastAPI + LangChain   | 8000 | AI agent: parses emails, calls APIs   |
| **parcel-backend** | Express + Sequelize | 3000 | REST API: customers, products, orders |
| **Database**     | PostgreSQL            | 5432 | Stores all data                       |
| **LLM**          | OpenAI (gpt-4o)       | -    | Understands unstructured email content|
| **Email Trigger**| Zapier                | -    | Watches inbox, triggers webhook       |
| **Confirmation** | SMTP (Gmail)          | -    | Sends order confirmation emails       |

---

## Project Structure

```
AI-agenet/
├── main-agent/                    # FastAPI - AI Agent (Port 8000)
│   ├── main.py                    # FastAPI entry point (/chat endpoint)
│   ├── mainAgent.py               # Agent logic (placeholder)
│   ├── model/
│   │   └── schema.py              # Pydantic models (ChatRequest)
│   ├── template/                  # Sample order emails for testing
│   │   ├── email1.txt             # Laptop order (John Doe)
│   │   ├── email2.txt             # Multi-item order (Sarah Miller)
│   │   └── email3.txt             # Corporate PO (Robert Wilson)
│   ├── test/
│   │   └── api-test.http          # HTTP test file
│   ├── requirements.txt
│   └── venv/
│
├── parcel-backend/                # Express - REST API (Port 3000)
│   ├── index.js                   # Server entry
│   ├── config/
│   │   └── database.js            # Sequelize + PostgreSQL setup
│   ├── models/
│   │   ├── index.js               # Relationships
│   │   ├── Customer.js
│   │   ├── Product.js
│   │   ├── Order.js
│   │   └── OrderItem.js
│   ├── controllers/
│   │   ├── customerController.js
│   │   ├── productController.js
│   │   └── orderController.js
│   ├── routes/
│   │   ├── customerRoutes.js
│   │   ├── productRoutes.js
│   │   └── orderRoutes.js
│   └── test/
│       ├── customer.http
│       ├── product.http
│       └── order.http
│
├── docs/
│   ├── how-it-works.md
│   ├── implementation-guide.md
│   └── implementation-guide2.md
│
├── project.md                     # <-- This file
└── README.md
```

---

## Database Schema (PostgreSQL)

```
Customer (1) ──< (M) Order (1) ──< (M) OrderItem (M) >── (1) Product
```

| Table        | Key Fields                                          |
|--------------|-----------------------------------------------------|
| customers    | id, name, email (unique), phone, address            |
| products     | id, name, description, price, stock                 |
| orders       | id, customerId (FK), totalAmount, status (enum)     |
| order_items  | id, orderId (FK), productId (FK), quantity, price   |

Order status values: `pending`, `processing`, `shipped`, `delivered`, `cancelled`

---

## Express API Endpoints (parcel-backend)

### Customers
```
POST   /api/customers         Create customer
GET    /api/customers         Get all (with orders)
GET    /api/customers/:id     Get by ID (with orders)
PUT    /api/customers/:id     Update
DELETE /api/customers/:id     Delete
```

### Products
```
POST   /api/products          Create product
GET    /api/products          Get all
GET    /api/products/:id      Get by ID
PUT    /api/products/:id      Update
DELETE /api/products/:id      Delete
```

### Orders
```
POST   /api/orders                        Create order (auto-calculates total, deducts stock)
GET    /api/orders                        Get all (with customer & items)
GET    /api/orders/:id                    Get by ID
GET    /api/orders/customer/:customerId   Get by customer
PUT    /api/orders/:id/status             Update status
DELETE /api/orders/:id                    Delete (restores stock)
```

---

## Agent Design (LangChain Tool-Calling Pattern)

The agent uses LangChain with OpenAI to dynamically decide which tools to call. Based on patterns from the `D:\aichat` project.

### Tools

| Tool              | Purpose                      | Calls                   |
|-------------------|------------------------------|-------------------------|
| `find_product`    | Search product by name       | GET /api/products       |
| `create_customer` | Create new customer record   | POST /api/customers     |
| `create_order`    | Place order for customer     | POST /api/orders        |
| `send_confirmation` | Email order confirmation   | SMTP                    |

### Agent Loop
```
1. Receive email content
2. LLM reads email + decides which tool to call first
3. Execute tool, return result to LLM
4. LLM decides next tool (or finish)
5. Repeat until all steps complete
```

### Target File Structure (main-agent)
```
main-agent/
├── main.py              # FastAPI endpoints (/webhook, /process)
├── agent.py             # LangChain agent orchestrator
├── tools/
│   ├── __init__.py
│   ├── customer_tools.py
│   ├── product_tools.py
│   ├── order_tools.py
│   └── email_tools.py
├── config.py            # Configuration loader
├── logger.py            # Logging setup
├── template/            # Test emails
├── requirements.txt
└── .env
```

---

## Environment Variables

### main-agent/.env
```
OPENAI_API_KEY=sk-your-key
EXPRESS_API_URL=http://localhost:3000/api
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASSWORD=your-app-password
```

### parcel-backend/.env
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=parcel_db
DB_USER=postgres
DB_PASSWORD=your_password
PORT=3000
```

---

## Dependencies

### main-agent (Python)
```
fastapi
uvicorn
langchain
langchain-openai
langchain-core
httpx
python-dotenv
```

### parcel-backend (Node.js)
```
express, sequelize, pg, pg-hstore, dotenv, uuid, cors
```

---

## How to Run

### 1. Start parcel-backend
```bash
cd parcel-backend
npm start
# http://localhost:3000
```

### 2. Start main-agent
```bash
cd main-agent
venv\Scripts\activate
uvicorn main:app --reload
# http://localhost:8000
```

---

## Progress

### parcel-backend (Express) - DONE
- [x] Customer CRUD
- [x] Product CRUD
- [x] Order CRUD with transactions
- [x] Stock management
- [x] Model relationships
- [x] Test files

### main-agent (FastAPI) - IN PROGRESS
- [x] Basic FastAPI setup
- [x] Sample email templates (3 emails)
- [x] Pydantic model (ChatRequest)
- [ ] Install LangChain dependencies
- [ ] Create tools (customer, product, order, email)
- [ ] Create agent.py (LangChain orchestrator)
- [ ] Create /webhook endpoint (Zapier)
- [ ] Create /process endpoint (local testing)
- [ ] Email confirmation sender (SMTP)
- [ ] Config + logging setup
- [ ] Error handling

### Integration - TODO
- [ ] Zapier trigger setup
- [ ] End-to-end testing
- [ ] Deployment
