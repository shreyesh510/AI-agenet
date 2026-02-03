# AI Email Order Agent - Implementation Guide v2

> Based on actual project structure and code

---

## Project Structure

```
D:/AI-agenet/
├── main-agent/                    # FastAPI - AI Agent (Port 8000)
│   ├── main.py                    # Entry point
│   ├── requirements.txt
│   └── venv/
│
├── parcel-backend/                # Express - REST API (Port 3000)
│   ├── index.js                   # Server entry
│   ├── .env                       # DB config
│   ├── config/
│   │   └── database.js            # Sequelize setup
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
│   ├── implementation-guide.md
│   └── implementation-guide2.md
│
└── README.md
```

---

## Database Schema (PostgreSQL)

### Relationships
```
Customer (1) ──────< (M) Order (1) ──────< (M) OrderItem (M) >────── (1) Product
```

### Tables

**customers**
| Field | Type | Constraints |
|-------|------|-------------|
| id | INTEGER | PK, Auto Increment |
| name | STRING(255) | NOT NULL |
| email | STRING(255) | NOT NULL, UNIQUE |
| phone | STRING(50) | - |
| address | TEXT | - |
| createdAt | TIMESTAMP | Auto |
| updatedAt | TIMESTAMP | Auto |

**products**
| Field | Type | Constraints |
|-------|------|-------------|
| id | INTEGER | PK, Auto Increment |
| name | STRING(255) | NOT NULL |
| description | TEXT | - |
| price | DECIMAL(10,2) | NOT NULL |
| stock | INTEGER | NOT NULL, Default: 0 |
| createdAt | TIMESTAMP | Auto |
| updatedAt | TIMESTAMP | Auto |

**orders**
| Field | Type | Constraints |
|-------|------|-------------|
| id | INTEGER | PK, Auto Increment |
| customerId | INTEGER | FK → customers.id |
| totalAmount | DECIMAL(10,2) | Default: 0 |
| status | ENUM | pending/processing/shipped/delivered/cancelled |
| createdAt | TIMESTAMP | Auto |
| updatedAt | TIMESTAMP | Auto |

**order_items**
| Field | Type | Constraints |
|-------|------|-------------|
| id | INTEGER | PK, Auto Increment |
| orderId | INTEGER | FK → orders.id |
| productId | INTEGER | FK → products.id |
| quantity | INTEGER | NOT NULL, Default: 1 |
| price | DECIMAL(10,2) | NOT NULL |
| createdAt | TIMESTAMP | Auto |

---

## Existing Express APIs

### Customer APIs
```
POST   /api/customers         → Create customer
GET    /api/customers         → Get all (with orders)
GET    /api/customers/:id     → Get by ID (with orders)
PUT    /api/customers/:id     → Update
DELETE /api/customers/:id     → Delete
```

### Product APIs
```
POST   /api/products          → Create product
GET    /api/products          → Get all
GET    /api/products/:id      → Get by ID
PUT    /api/products/:id      → Update
DELETE /api/products/:id      → Delete
```

### Order APIs
```
POST   /api/orders                    → Create order
GET    /api/orders                    → Get all (with customer & items)
GET    /api/orders/:id                → Get by ID
GET    /api/orders/customer/:customerId → Get by customer
PUT    /api/orders/:id/status         → Update status
DELETE /api/orders/:id                → Delete (restores stock)
```

---

## API Request/Response Examples

### Create Customer
```http
POST /api/customers
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "1234567890",
  "address": "123 Main St, City"
}
```
Response:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "address": "123 Main St, City",
    "createdAt": "2024-02-03T...",
    "updatedAt": "2024-02-03T..."
  }
}
```

### Create Order
```http
POST /api/orders
Content-Type: application/json

{
  "customerId": 1,
  "items": [
    { "productId": 1, "quantity": 2 },
    { "productId": 2, "quantity": 1 }
  ]
}
```
Response:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "customerId": 1,
    "totalAmount": "1029.97",
    "status": "pending",
    "customer": { ... },
    "items": [
      {
        "productId": 1,
        "quantity": 2,
        "price": "999.99",
        "product": { "name": "Laptop", ... }
      }
    ]
  }
}
```

---

## Implementation Plan for main-agent

### Step 1: Install Dependencies

Update `main-agent/requirements.txt`:
```
fastapi
uvicorn
openai
httpx
python-dotenv
```

Install:
```bash
cd main-agent
venv\Scripts\pip install -r requirements.txt
```

### Step 2: Create Environment File

Create `main-agent/.env`:
```
OPENAI_API_KEY=sk-your-key
EXPRESS_API_URL=http://localhost:3000/api
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASSWORD=your-app-password
```

### Step 3: Project Structure

```
main-agent/
├── main.py              # FastAPI app & endpoints
├── agent.py             # AI agent logic
├── api_client.py        # Express API client
├── email_parser.py      # OpenAI email parsing
├── email_sender.py      # SMTP confirmation
├── email.txt            # Test email file
├── requirements.txt
└── .env
```

### Step 4: Implement Files

#### main.py
```python
from fastapi import FastAPI
from pydantic import BaseModel
from agent import process_email

app = FastAPI()

class WebhookPayload(BaseModel):
    email_body: str
    from_email: str

@app.get("/")
def root():
    return {"message": "fast api app is running"}

@app.post("/webhook")
async def webhook(payload: WebhookPayload):
    result = await process_email(payload.email_body, payload.from_email)
    return result

@app.post("/process")
async def process_local():
    with open("email.txt", "r") as f:
        email_content = f.read()
    result = await process_email(email_content, "test@example.com")
    return result
```

#### email_parser.py
```python
from openai import OpenAI
import json
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def parse_email(email_content: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": """Extract order details from email. Return JSON:
                {
                    "customer": {
                        "name": "",
                        "email": "",
                        "address": ""
                    },
                    "order": {
                        "product": "",
                        "quantity": 1
                    }
                }"""
            },
            {"role": "user", "content": email_content}
        ]
    )
    return json.loads(response.choices[0].message.content)
```

#### api_client.py
```python
import httpx
import os

BASE_URL = os.getenv("EXPRESS_API_URL", "http://localhost:3000/api")

async def create_customer(data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/customers", json=data)
        return response.json()

async def get_products() -> list:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/products")
        return response.json()["data"]

async def create_order(customer_id: int, items: list) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/orders",
            json={"customerId": customer_id, "items": items}
        )
        return response.json()
```

#### agent.py
```python
from email_parser import parse_email
from api_client import create_customer, get_products, create_order
from email_sender import send_confirmation

async def process_email(email_content: str, from_email: str) -> dict:
    # 1. Parse email with OpenAI
    parsed = await parse_email(email_content)

    # 2. Create customer
    customer_data = parsed["customer"]
    customer_data["email"] = from_email
    customer_response = await create_customer(customer_data)
    customer_id = customer_response["data"]["id"]

    # 3. Find product
    products = await get_products()
    product_name = parsed["order"]["product"].lower()
    product = next(
        (p for p in products if product_name in p["name"].lower()),
        None
    )

    if not product:
        return {"success": False, "error": "Product not found"}

    # 4. Create order
    items = [{"productId": product["id"], "quantity": parsed["order"]["quantity"]}]
    order_response = await create_order(customer_id, items)

    # 5. Send confirmation
    order_id = order_response["data"]["id"]
    await send_confirmation(from_email, order_id)

    return {
        "success": True,
        "order_id": order_id,
        "message": f"Order created successfully"
    }
```

#### email_sender.py
```python
import smtplib
from email.mime.text import MIMEText
import os

async def send_confirmation(to_email: str, order_id: int):
    msg = MIMEText(f"Your order #{order_id} has been confirmed!")
    msg["Subject"] = f"Order Confirmation #{order_id}"
    msg["From"] = os.getenv("SMTP_USER")
    msg["To"] = to_email

    with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
        server.starttls()
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
        server.send_message(msg)
```

#### email.txt (Test File)
```
Hi,

I would like to order 2 Laptops.

Please deliver to:
John Doe
123 Main Street
New York, NY 10001

Thanks!
```

---

## Testing Flow

### 1. Start Express Server
```bash
cd parcel-backend
npm start
# Running on http://localhost:3000
```

### 2. Create Test Product
```http
POST http://localhost:3000/api/products
Content-Type: application/json

{
  "name": "Laptop",
  "description": "High performance laptop",
  "price": 999.99,
  "stock": 50
}
```

### 3. Start FastAPI Agent
```bash
cd main-agent
venv\Scripts\activate
uvicorn main:app --reload
# Running on http://localhost:8000
```

### 4. Test Local Processing
```http
POST http://localhost:8000/process
```

### 5. Test Webhook
```http
POST http://localhost:8000/webhook
Content-Type: application/json

{
  "email_body": "I want to order 2 Laptops to 123 Main St, NY",
  "from_email": "customer@example.com"
}
```

---

## Zapier Integration

### Trigger
- App: Gmail / Outlook
- Event: New Email

### Action
- App: Webhooks by Zapier
- Event: POST
- URL: `https://your-domain.com/webhook`
- Payload:
```json
{
  "email_body": "{{body}}",
  "from_email": "{{from_email}}"
}
```

---

## Error Handling

| Error | Response |
|-------|----------|
| Product not found | `{"success": false, "error": "Product not found"}` |
| Customer exists | Express returns existing customer or error |
| Insufficient stock | `{"success": false, "error": "Insufficient stock for..."}` |
| OpenAI parse fail | `{"success": false, "error": "Failed to parse email"}` |

---

## Status Checklist

### parcel-backend (Express) ✅ Complete
- [x] Customer CRUD
- [x] Product CRUD
- [x] Order CRUD with transactions
- [x] Stock management
- [x] Relationships configured
- [x] Test files

### main-agent (FastAPI) ⏳ Pending
- [x] Basic setup
- [ ] OpenAI integration
- [ ] API client for Express
- [ ] /webhook endpoint
- [ ] /process endpoint
- [ ] Email sender
- [ ] Error handling

---

## Reference: D:\aichat Project

> We are using patterns from the existing `aichat` project for LangChain tool-calling approach.

### aichat Tech Stack (Reusable)

| Component | Library | Purpose |
|-----------|---------|---------|
| LLM Framework | LangChain | Tool orchestration |
| OpenAI Integration | langchain-openai | ChatOpenAI model |
| HTTP Client | httpx | API calls |
| Config | python-dotenv | Environment variables |
| Logging | Python logging | Rotating file logs |

### aichat Pattern: Tool-Calling Agent

```
User Query → LLM Agent → Decides Tool → Executes Tool → Returns Result
```

**How aichat does it (main.py):**
```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# Define tools
@tool
def business_info_tool(query: str) -> str:
    """Search business information"""
    # ... implementation
    return result

# Create agent with tools
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools([business_info_tool, other_tool])

# Agent loop
messages = [system_prompt, user_message]
response = llm_with_tools.invoke(messages)

# If tool call requested, execute and continue
if response.tool_calls:
    tool_result = execute_tool(response.tool_calls[0])
    messages.append(tool_result)
    response = llm_with_tools.invoke(messages)
```

---

## LangChain Implementation for Email Agent

### Updated Dependencies

```
fastapi
uvicorn
langchain
langchain-openai
langchain-core
httpx
python-dotenv
```

### Tools to Create

| Tool | Purpose | Calls |
|------|---------|-------|
| `parse_email` | Extract customer/product info | OpenAI |
| `create_customer` | Create new customer | POST /api/customers |
| `find_product` | Search product by name | GET /api/products |
| `create_order` | Place order | POST /api/orders |
| `send_confirmation` | Email confirmation | SMTP |

### Updated Project Structure

```
main-agent/
├── main.py              # FastAPI endpoints
├── agent.py             # LangChain agent orchestrator
├── tools/
│   ├── __init__.py
│   ├── customer_tools.py
│   ├── product_tools.py
│   ├── order_tools.py
│   └── email_tools.py
├── config.py            # Configuration loader
├── logger.py            # Logging setup (from aichat)
├── email.txt            # Test file
├── requirements.txt
└── .env
```

### LangChain Agent Implementation

#### tools/customer_tools.py
```python
from langchain_core.tools import tool
import httpx
import os

BASE_URL = os.getenv("EXPRESS_API_URL", "http://localhost:3000/api")

@tool
def create_customer(name: str, email: str, address: str, phone: str = "") -> dict:
    """Create a new customer in the system.

    Args:
        name: Customer full name
        email: Customer email address
        address: Delivery address
        phone: Phone number (optional)
    """
    with httpx.Client() as client:
        response = client.post(
            f"{BASE_URL}/customers",
            json={"name": name, "email": email, "address": address, "phone": phone}
        )
        return response.json()
```

#### tools/product_tools.py
```python
from langchain_core.tools import tool
import httpx
import os

BASE_URL = os.getenv("EXPRESS_API_URL", "http://localhost:3000/api")

@tool
def find_product(product_name: str) -> dict:
    """Find a product by name.

    Args:
        product_name: Name of the product to search
    """
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/products")
        products = response.json()["data"]

        for product in products:
            if product_name.lower() in product["name"].lower():
                return {"found": True, "product": product}

        return {"found": False, "error": f"Product '{product_name}' not found"}
```

#### tools/order_tools.py
```python
from langchain_core.tools import tool
import httpx
import os

BASE_URL = os.getenv("EXPRESS_API_URL", "http://localhost:3000/api")

@tool
def create_order(customer_id: int, product_id: int, quantity: int) -> dict:
    """Create an order for a customer.

    Args:
        customer_id: ID of the customer
        product_id: ID of the product
        quantity: Number of items to order
    """
    with httpx.Client() as client:
        response = client.post(
            f"{BASE_URL}/orders",
            json={
                "customerId": customer_id,
                "items": [{"productId": product_id, "quantity": quantity}]
            }
        )
        return response.json()
```

#### agent.py (LangChain Orchestrator)
```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from tools.customer_tools import create_customer
from tools.product_tools import find_product
from tools.order_tools import create_order
import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are an order processing agent. When given an email:

1. Extract customer info (name, email, address)
2. Extract product name and quantity
3. Use tools in this order:
   - find_product: Check if product exists
   - create_customer: Create customer record
   - create_order: Place the order

Always use the tools. Never make up data."""

def create_agent():
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    tools = [find_product, create_customer, create_order]
    return llm.bind_tools(tools)

async def process_email(email_content: str, from_email: str) -> dict:
    agent = create_agent()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Process this order email:\n\n{email_content}\n\nCustomer email: {from_email}")
    ]

    # Agent loop
    while True:
        response = agent.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            break

        # Execute tool calls
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            # Get tool function
            tool_fn = {
                "find_product": find_product,
                "create_customer": create_customer,
                "create_order": create_order
            }[tool_name]

            result = tool_fn.invoke(tool_args)
            messages.append({"role": "tool", "content": str(result), "tool_call_id": tool_call["id"]})

    return {"success": True, "result": response.content}
```

---

## Flow Comparison

### Basic Approach (Without LangChain)
```
Email → Parse (OpenAI) → Fixed sequence of API calls → Result
```

### LangChain Approach (From aichat)
```
Email → Agent (LLM decides) → Dynamic tool selection → Result
```

**Benefits of LangChain approach:**
- LLM decides which tools to call
- Handles edge cases better
- Can retry or skip steps
- More flexible for complex emails

---

## Reusable from aichat

| File | Component | Use Case |
|------|-----------|----------|
| `main.py:51-80` | Logging setup | Copy logging config |
| `main.py:83-125` | Config loader | Load client config |
| `main.py:419-501` | Agent pattern | Tool-calling loop |
| `.env.example` | Env template | Environment setup |

---

## Updated Status Checklist

### main-agent (FastAPI) with LangChain
- [x] Basic FastAPI setup
- [ ] Install LangChain dependencies
- [ ] Create tools/customer_tools.py
- [ ] Create tools/product_tools.py
- [ ] Create tools/order_tools.py
- [ ] Create tools/email_tools.py
- [ ] Create agent.py (orchestrator)
- [ ] Create config.py
- [ ] Create logger.py
- [ ] Update main.py with endpoints
- [ ] Add .env configuration
- [ ] Test with email.txt
- [ ] Integrate with Zapier
