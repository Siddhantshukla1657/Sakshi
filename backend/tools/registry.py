from typing import Dict, Any, List
from .services import services

TOOL_DEFINITIONS = [
    {
        "name": "get_order",
        "description": "Look up order details, amount, merchant, delivery status, and refund eligibility facts.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The unique Order ID, e.g. ORD-901"}
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "get_payment",
        "description": "Look up payment or UPI transaction details, debited status, elapsed time, and bank status.",
        "parameters": {
            "type": "object",
            "properties": {
                "upi_ref": {"type": "string", "description": "The UPI Reference ID or transaction number, e.g. UPI-849102"}
            },
            "required": ["upi_ref"]
        }
    },
    {
        "name": "get_customer_history",
        "description": "Retrieve customer profile, language preference, recent transactions, and daily refund velocity.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "Customer identifier, e.g. CUST-101"}
            },
            "required": ["customer_id"]
        }
    },
    {
        "name": "issue_refund",
        "description": "Issue an instant refund for an eligible order directly to customer's source account. (Money-moving tool strictly governed by Policy Engine).",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The Order ID to refund"},
                "amount": {"type": "integer", "description": "Refund amount in INR"},
                "reason": {"type": "string", "description": "Verified business reason for the refund"}
            },
            "required": ["order_id", "amount", "reason"]
        }
    },
    {
        "name": "request_upi_reversal",
        "description": "Request a bank-level UPI transaction reversal or claim ticket for a failed debited payment.",
        "parameters": {
            "type": "object",
            "properties": {
                "upi_ref": {"type": "string", "description": "The UPI transaction reference ID"},
                "amount": {"type": "integer", "description": "Transaction amount in INR"},
                "reason": {"type": "string", "description": "Reason for reversal"}
            },
            "required": ["upi_ref", "amount"]
        }
    },
    {
        "name": "update_crm",
        "description": "Update customer support ticket in CRM with conversation notes and resolution status.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "Customer ID"},
                "issue_summary": {"type": "string", "description": "Short summary of issue"},
                "resolution_notes": {"type": "string", "description": "Outcome and actions taken"}
            },
            "required": ["customer_id", "issue_summary", "resolution_notes"]
        }
    },
    {
        "name": "notify_customer",
        "description": "Send notification (SMS or Push) to customer regarding resolution or handoff.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "Customer ID"},
                "message": {"type": "string", "description": "Notification body"}
            },
            "required": ["customer_id", "message"]
        }
    },
    {
        "name": "get_settlement",
        "description": "Retrieve merchant settlement ledger and dispute details for merchant persona.",
        "parameters": {
            "type": "object",
            "properties": {
                "merchant_id": {"type": "string", "description": "Merchant ID, e.g. MERCH-501"}
            },
            "required": ["merchant_id"]
        }
    },
    {
        "name": "escalate",
        "description": "Escalate case to human supervisor or specialist when outside authority or when confidence is low.",
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {"type": "string", "description": "Specific reason for escalation"},
                "priority": {"type": "string", "enum": ["normal", "high", "urgent"]}
            },
            "required": ["reason"]
        }
    }
]

def execute_tool(tool_name: str, arguments: Dict[str, Any], rule_ids: str = "") -> Dict[str, Any]:
    if tool_name == "get_order":
        return services.get_order(arguments.get("order_id", ""))
    elif tool_name == "get_payment":
        return services.get_payment(arguments.get("upi_ref", ""))
    elif tool_name == "get_customer_history":
        return services.get_customer_history(arguments.get("customer_id", ""))
    elif tool_name == "issue_refund":
        return services.issue_refund(
            order_id=arguments.get("order_id", ""),
            amount=int(arguments.get("amount", 0)),
            reason=arguments.get("reason", "Customer requested resolution"),
            rule_ids=rule_ids
        )
    elif tool_name == "request_upi_reversal":
        return services.request_upi_reversal(
            upi_ref=arguments.get("upi_ref", ""),
            amount=int(arguments.get("amount", 0)),
            reason=arguments.get("reason", "")
        )
    elif tool_name == "update_crm":
        return services.update_crm(
            customer_id=arguments.get("customer_id", ""),
            issue_summary=arguments.get("issue_summary", ""),
            resolution_notes=arguments.get("resolution_notes", "")
        )
    elif tool_name == "notify_customer":
        return services.notify_customer(
            customer_id=arguments.get("customer_id", ""),
            message=arguments.get("message", "")
        )
    elif tool_name == "get_settlement":
        return services.get_settlement(
            merchant_id=arguments.get("merchant_id", "")
        )
    elif tool_name == "reconcile_merchant_settlement":
        return services.reconcile_merchant_settlement(
            merchant_id=arguments.get("merchant_id", "MERCH-501"),
            amount=int(arguments.get("amount", 2000))
        )
    elif tool_name == "escalate":
        return {
            "status": "ESCALATED",
            "reason": arguments.get("reason", ""),
            "priority": arguments.get("priority", "normal")
        }
    else:
        raise ValueError(f"Unknown tool: {tool_name}")
