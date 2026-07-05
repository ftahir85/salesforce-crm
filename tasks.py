"""
tasks.py
--------
CRUD operations for Salesforce Tasks (follow-ups, to-dos).
"""

from tabulate import tabulate
from simple_salesforce import Salesforce


PRIORITIES = ["High", "Normal", "Low"]
STATUSES   = ["Not Started", "In Progress", "Completed", "Waiting on someone else", "Deferred"]


def list_tasks(sf: Salesforce, who_id: str = None,
               status: str = "Not Started", limit: int = 10) -> None:
    """
    List tasks, optionally filtered by related record (WhoId = Contact/Lead)
    and status.
    """
    filters = [f"Status = '{status}'"]
    if who_id: filters.append(f"WhoId = '{who_id}'")

    where = "WHERE " + " AND ".join(filters)
    query = f"""
        SELECT Id, Subject, Status, Priority, ActivityDate, WhoId, WhatId, Description
        FROM Task
        {where}
        ORDER BY ActivityDate ASC NULLS LAST
        LIMIT {limit}
    """
    result = sf.query(query)
    records = result.get("records", [])

    if not records:
        print(f"No tasks found with status '{status}'.")
        return

    rows = [
        [
            r["Id"],
            r.get("Subject", "—"),
            r.get("Priority", "—"),
            r.get("Status", "—"),
            r.get("ActivityDate", "—"),
        ]
        for r in records
    ]
    print(tabulate(rows, headers=["ID", "Subject", "Priority", "Status", "Due Date"], tablefmt="rounded_outline"))
    print(f"\n{len(rows)} task(s) shown.\n")


def create_task(sf: Salesforce, subject: str, due_date: str = None,
                priority: str = "Normal", status: str = "Not Started",
                who_id: str = None, what_id: str = None,
                description: str = None) -> str:
    """
    Create a new Task.

    Args:
        subject     : Short title, e.g. 'Follow up with Ali'
        due_date    : Format 'YYYY-MM-DD' (optional)
        priority    : 'High', 'Normal', or 'Low'
        status      : One of STATUSES
        who_id      : Link to a Contact or Lead (optional)
        what_id     : Link to an Opportunity or Account (optional)
        description : Notes about the task (optional)

    Returns:
        New record Id.
    """
    if priority not in PRIORITIES:
        print(f"⚠️  Invalid priority. Choose from: {PRIORITIES}")
    if status not in STATUSES:
        print(f"⚠️  Invalid status. Choose from: {STATUSES}")

    payload = {
        "Subject": subject,
        "Priority": priority,
        "Status": status,
    }
    if due_date:    payload["ActivityDate"] = due_date
    if who_id:      payload["WhoId"] = who_id
    if what_id:     payload["WhatId"] = what_id
    if description: payload["Description"] = description

    result = sf.Task.create(payload)
    new_id = result["id"]
    print(f"✅ Task created: '{subject}' → ID: {new_id}\n")
    return new_id


def complete_task(sf: Salesforce, task_id: str) -> None:
    """Mark a Task as Completed."""
    sf.Task.update(task_id, {"Status": "Completed"})
    print(f"✅ Task {task_id} marked as Completed.\n")


def update_task(sf: Salesforce, task_id: str, **fields) -> None:
    """Update any fields on a Task."""
    if not fields:
        print("⚠️  No fields provided.")
        return
    sf.Task.update(task_id, fields)
    print(f"✅ Task {task_id} updated: {fields}\n")


def delete_task(sf: Salesforce, task_id: str) -> None:
    """Delete a Task by Id."""
    sf.Task.delete(task_id)
    print(f"🗑️  Task {task_id} deleted.\n")


def overdue_tasks(sf: Salesforce, limit: int = 20) -> None:
    """List all incomplete tasks whose due date has passed."""
    query = f"""
        SELECT Id, Subject, Priority, ActivityDate, WhoId
        FROM Task
        WHERE Status != 'Completed'
          AND ActivityDate < TODAY
        ORDER BY ActivityDate ASC
        LIMIT {limit}
    """
    result = sf.query(query)
    records = result.get("records", [])

    if not records:
        print("🎉 No overdue tasks!")
        return

    rows = [
        [r["Id"], r.get("Subject", "—"), r.get("Priority", "—"), r.get("ActivityDate", "—")]
        for r in records
    ]
    print("⚠️  Overdue Tasks:")
    print(tabulate(rows, headers=["ID", "Subject", "Priority", "Due Date"], tablefmt="rounded_outline"))
    print(f"\n{len(rows)} overdue task(s).\n")
