from langchain_core.tools import tool
import httpx
import config


@tool
def find_product(product_name: str) -> dict:
    """Find a product by name from the store catalog.

    Args:
        product_name: Name of the product to search for (e.g. 'Laptop', 'Wireless Keyboard')
    """
    with httpx.Client() as client:
        response = client.get(f"{config.EXPRESS_API_URL}/products")
        products = response.json()["data"]

        for product in products:
            if product_name.lower() in product["name"].lower():
                return {"found": True, "product": product}

        return {"found": False, "error": f"Product '{product_name}' not found"}


@tool
def get_all_products() -> dict:
    """Get all products from the store catalog.

    Returns a list of all available products with their details including
    id, name, description, price, and stock.
    """
    with httpx.Client() as client:
        response = client.get(f"{config.EXPRESS_API_URL}/products")
        data = response.json()

        if data.get("success"):
            return {"success": True, "products": data["data"]}
        return {"success": False, "error": "Failed to fetch products"}


@tool
def get_product_by_id(product_id: int) -> dict:
    """Get a single product by its ID.

    Args:
        product_id: The unique ID of the product to retrieve
    """
    with httpx.Client() as client:
        response = client.get(f"{config.EXPRESS_API_URL}/products/{product_id}")

        if response.status_code == 404:
            return {"success": False, "error": f"Product with ID {product_id} not found"}

        data = response.json()
        if data.get("success"):
            return {"success": True, "product": data["data"]}
        return {"success": False, "error": data.get("error", "Failed to fetch product")}


@tool
def create_product(name: str, price: float, stock: int, description: str = "") -> dict:
    """Create a new product in the store catalog.

    Args:
        name: Name of the product (e.g. 'Wireless Mouse')
        price: Price of the product (e.g. 29.99)
        stock: Available stock quantity (e.g. 100)
        description: Optional description of the product
    """
    with httpx.Client() as client:
        payload = {
            "name": name,
            "price": price,
            "stock": stock,
            "description": description,
        }
        response = client.post(f"{config.EXPRESS_API_URL}/products", json=payload)
        data = response.json()

        if data.get("success"):
            return {"success": True, "product": data["data"]}
        return {"success": False, "error": data.get("error", "Failed to create product")}


@tool
def update_product(
    product_id: int,
    name: str = None,
    price: float = None,
    stock: int = None,
    description: str = None,
) -> dict:
    """Update an existing product in the store catalog.

    Only the fields provided will be updated. Omit fields you don't want to change.

    Args:
        product_id: The unique ID of the product to update
        name: New name for the product
        price: New price for the product
        stock: New stock quantity
        description: New description for the product
    """
    with httpx.Client() as client:
        payload = {}
        if name is not None:
            payload["name"] = name
        if price is not None:
            payload["price"] = price
        if stock is not None:
            payload["stock"] = stock
        if description is not None:
            payload["description"] = description

        if not payload:
            return {"success": False, "error": "No fields provided to update"}

        response = client.put(
            f"{config.EXPRESS_API_URL}/products/{product_id}", json=payload
        )

        if response.status_code == 404:
            return {"success": False, "error": f"Product with ID {product_id} not found"}

        data = response.json()
        if data.get("success"):
            return {"success": True, "product": data["data"]}
        return {"success": False, "error": data.get("error", "Failed to update product")}


@tool
def delete_product(product_id: int) -> dict:
    """Delete a product from the store catalog.

    Args:
        product_id: The unique ID of the product to delete
    """
    with httpx.Client() as client:
        response = client.delete(f"{config.EXPRESS_API_URL}/products/{product_id}")

        if response.status_code == 404:
            return {"success": False, "error": f"Product with ID {product_id} not found"}

        data = response.json()
        if data.get("success"):
            return {"success": True, "message": data.get("message", "Product deleted successfully")}
        return {"success": False, "error": data.get("error", "Failed to delete product")}
