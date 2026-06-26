from mcp.server.fastmcp import FastMCP
from mock_data import get_order_status, get_billing_info

# This creates the MCP server itself — think of it as the "concierge desk"
# that will expose our backend functions as standardized tools.
mcp = FastMCP("ecommerce-support-tools")

# The @mcp.tool() decorator is what turns a normal Python function into
# something an MCP client (an agent) can discover and call through the protocol.

@mcp.tool()
def lookup_order_status(order_id: str) -> dict:
    """Look up the current shipping status of a customer's order by order ID."""
    return get_order_status(order_id)

@mcp.tool()
def lookup_billing_info(customer_id: str) -> dict:
    """Look up a customer's billing record, including their last charge and
    whether a duplicate charge was found, by customer ID."""
    return get_billing_info(customer_id)

if __name__ == "__main__":
    mcp.run()