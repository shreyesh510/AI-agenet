# How It Works

## Overview

An AI agent that automatically processes order emails and creates orders in the system.

---

## Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Email   │ --> │  Zapier  │ --> │ AI Agent │ --> │   APIs   │ --> │  Email   │
│  Inbox   │     │          │     │          │     │          │     │ Confirm  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
```

---

## Step by Step

### 1. Customer Sends Email
```
To: orders@company.com

Hi, I want to order 2 Laptops.
Deliver to: 123 Main St, New York

- John Doe
```

### 2. Zapier Detects Email
- Watches inbox for new emails
- Triggers webhook to AI Agent
- Sends email content

### 3. AI Agent Processes
- Reads email content
- Uses OpenAI to understand:
  - Customer name: John Doe
  - Product: Laptop
  - Quantity: 2
  - Address: 123 Main St, New York

### 4. Agent Calls APIs
```
1. Find Product    →  GET /api/products
2. Create Customer →  POST /api/customers
3. Create Order    →  POST /api/orders
```

### 5. Confirmation Email Sent
```
To: john@example.com

Your order #1234 has been confirmed!

- 2x Laptop
- Total: $1999.98
- Status: Pending
```

---

## Components

| Component | Role |
|-----------|------|
| **Gmail/Outlook** | Receives order emails |
| **Zapier** | Triggers agent on new email |
| **FastAPI Agent** | Processes email, calls APIs |
| **OpenAI** | Understands email content |
| **Express API** | Manages customers, products, orders |
| **PostgreSQL** | Stores all data |
| **SMTP** | Sends confirmation emails |

---

## Simple Diagram

```
Customer                    System
   │                          │
   │  1. Sends order email    │
   │ ──────────────────────>  │
   │                          │
   │                    [Zapier detects]
   │                          │
   │                    [AI Agent reads]
   │                          │
   │                    [OpenAI extracts info]
   │                          │
   │                    [Creates order via API]
   │                          │
   │  2. Receives confirmation│
   │ <──────────────────────  │
   │                          │
```

---

## What AI Decides

The AI agent autonomously:

- Extracts customer info from unstructured email
- Identifies which product is requested
- Determines quantity
- Calls correct APIs in right order
- Handles errors (product not found, out of stock)

---

## Example

**Input Email:**
```
Hey, can I get 3 wireless keyboards shipped to
456 Oak Avenue, Los Angeles, CA 90001?

Thanks,
Sarah Miller
sarah@email.com
```

**AI Extracts:**
```json
{
  "customer": {
    "name": "Sarah Miller",
    "email": "sarah@email.com",
    "address": "456 Oak Avenue, Los Angeles, CA 90001"
  },
  "product": "wireless keyboard",
  "quantity": 3
}
```

**Result:**
- Order #1235 created
- Confirmation sent to sarah@email.com
