from langchain_core.tools import tool
import httpx
import config


@tool
def get_all_customers() -> dict:
    """Get all customers from the store database.

    Returns a list of all customers with their details including
    id, name, email, phone, and address.
    """
    with httpx.Client() as client:
        response = client.get(f"{config.EXPRESS_API_URL}/customers")
        data = response.json()

        if data.get("success"):
            return {"success": True, "customers": data["data"]}
        return {"success": False, "error": "Failed to fetch customers"}


@tool
def find_customer(customer_name: str) -> dict:
    """Find a customer by name from the store database.

    Args:
        customer_name: Name of the customer to search for (e.g. 'John Doe')
    """
    with httpx.Client() as client:
        response = client.get(f"{config.EXPRESS_API_URL}/customers")
        customers = response.json()["data"]

        for customer in customers:
            if customer_name.lower() in customer["name"].lower():
                return {"found": True, "customer": customer}

        return {"found": False, "error": f"Customer '{customer_name}' not found"}


@tool
def find_customer_by_email(customer_email: str) -> dict:
    """Find a customer by email from the store database.

    Args:
        customer_email: Email of the customer to search for (e.g. 'john@example.com')
    """
    with httpx.Client() as client:
        response = client.get(f"{config.EXPRESS_API_URL}/customers")
        customers = response.json()["data"]

        for customer in customers:
            if customer_email.lower() == customer["email"].lower():
                return {"found": True, "customer": customer}

        return {"found": False, "error": f"Customer with email '{customer_email}' not found"}


@tool
def get_customer_by_id(customer_id: int) -> dict:
    """Get a single customer by their ID.

    Args:
        customer_id: The unique ID of the customer to retrieve
    """
    with httpx.Client() as client:
        response = client.get(f"{config.EXPRESS_API_URL}/customers/{customer_id}")

        if response.status_code == 404:
            return {"success": False, "error": f"Customer with ID {customer_id} not found"}

        data = response.json()
        if data.get("success"):
            return {"success": True, "customer": data["data"]}
        return {"success": False, "error": data.get("error", "Failed to fetch customer")}


@tool
def create_order(customer_id: int, product_id: int) -> dict:
    """Create a new order for a customer.

    Args:
        customer_id: The unique ID of the customer placing the order
        product_id: The unique ID of the product to order
    """
    with httpx.Client() as client:
        payload = {"product_id": product_id}
        response = client.post(
            f"{config.EXPRESS_API_URL}/customers/{customer_id}/orders", json=payload
        )

        if response.status_code == 404:
            return {"success": False, "error": "Customer or product not found"}

        data = response.json()
        if data.get("success"):
            return {"success": True, "order": data["data"]}
        return {"success": False, "error": data.get("error", "Failed to create order")}
