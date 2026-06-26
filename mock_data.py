ORDERS = {
    "4521": {
        "order_id": "4521",
        "status": "in_transit",
        "estimated_delivery": "2 days",
        "carrier": "FedEx"
    },
    "7788": {
        "order_id": "7788",
        "status": "delivered",
        "estimated_delivery": "already delivered",
        "carrier": "UPS"
    }
}

BILLING_RECORDS = {
    "customer_001": {
        "customer_id": "customer_001",
        "last_charge_amount": 49.99,
        "last_charge_date": "2026-06-20",
        "duplicate_charge_found": False
    },
    "customer_002": {
        "customer_id": "customer_002",
        "last_charge_amount": 89.99,
        "last_charge_date": "2026-06-22",
        "duplicate_charge_found": True
    }
}

def get_order_status(order_id: str) -> dict:
    """Look up the status of an order by its ID."""
    order = ORDERS.get(order_id)
    if order is None:
        return {"error": f"No order found with ID {order_id}"}
    return order

def get_billing_info(customer_id: str) -> dict:
    """Look up billing information for a customer by their ID."""
    record = BILLING_RECORDS.get(customer_id)
    if record is None:
        return {"error": f"No billing record found for customer {customer_id}"}
    return record