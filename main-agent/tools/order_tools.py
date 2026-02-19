from langchain_core.tools import tool
import httpx
import config


@tool
def get_all_orders() -> dict:
    """Get all orders from the store database.

    Returns a list of all orders with their details including
    order id, customer, product, and status.
    """
    with httpx.Client() as client:
        response = client.get(f"{config.EXPRESS_API_URL}/orders")
        data = response.json()

        if data.get("success"):
            return {"success": True, "orders": data["data"]}
        return {"success": False, "error": "Failed to fetch orders"}


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
