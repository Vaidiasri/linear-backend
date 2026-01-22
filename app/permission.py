from fastapi import HTTPException, status
from typing import Optional, Any
from app.model.user import User
from app.policies import POLICIES


def check_permission(
    user: Optional[User],
    resource_type: str,
    action: str,
    resource: Optional[Any] = None,
) -> bool:
    """
    Check if user has permission to perform an action on a resource using generic policies.

    The engine iterates through POLICIES defined in app.policies.
    If ANY policy allows the action (returns True), access is GRANTED.
    If NO policy allows the action, access is DENIED.
    """

    # --- Input Validation ---
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User authentication required"
        )

    if not resource_type or not action:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resource_type or action",
        )

    # Construct the target action key (e.g., "issue:create")
    target_action = f"{resource_type}:{action}"

    # --- Policy Evaluation Engine ---
    allowed = False

    for policy in POLICIES:
        policy_action = policy["action"]

        # Check if policy applies to this action (Exact match or Wildcard)
        if policy_action == "*" or policy_action == target_action:

            # Execute Condition
            # Catch errors in condition to be safe (e.g. AttributeError)
            try:
                if policy["condition"](user, resource):
                    allowed = True
                    break  # Short-circuit: Access Granted
            except Exception:
                continue  # If condition fails logic, ignore this policy

    if allowed:
        return True

    # --- Deny ---
    # We can try to provide context-aware error messages if needed,
    # but for pure PBAC, a generic message is standard.
    # To maintain some backward compatibility with previous error messages:
    detail_msg = "You do not have permission to perform this action"

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail_msg,
    )
