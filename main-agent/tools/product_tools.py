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
