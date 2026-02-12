from langchain_core.tools import tool
from gmail_service import send_email


@tool
def send_gmail(to: str, subject: str, body: str) -> dict:
    """Send an email via Gmail API to a customer.

    Use this tool to send order confirmation emails or any communication to customers.

    Args:
        to: Recipient email address (e.g. 'shreyeshk@iconnectsolutions.com')
        subject: Email subject line (e.g. 'Order Confirmation - Order #123')
        body: Plain text email body with order details and confirmation message
    """
    try:
        result = send_email(to=to, subject=subject, body=body)
        if result.get("success"):
            return {
                "success": True,
                "message": f"Email sent successfully to {to}",
                "message_id": result.get("message_id"),
            }
        return {"success": False, "error": result.get("error", "Failed to send email")}
    except FileNotFoundError:
        return {
            "success": False,
            "error": "Gmail not authenticated. Please visit /auth/google to authenticate first.",
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to send email: {str(e)}"}
