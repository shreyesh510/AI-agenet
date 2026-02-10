from tools.product_tools import (
    find_product,
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
)
from tools.customer_tools import (
    find_customer,
    find_customer_by_email,
    get_all_customers,
    get_customer_by_id,
    create_order,
)

ALL_TOOLS = [
    find_product,
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
    find_customer,
    find_customer_by_email,
    get_all_customers,
    get_customer_by_id,
    create_order,
]
