"""
leads.py
--------
CRUD operations for Salesforce Leads.
"""

from tabulate import tabulate
from simple_salesforce import Salesforce


# Standard Salesforce lead statuses
LEAD_STATUSES = ["Open - Not Contacted", "Working - Contacted", "Closed - Converted", "Closed - Not Converted"]


def list_leads(sf: Salesforce, status: str = None, limit: int = 10) -> None:
    """List leads, optionally filtered by status."""
    where = f"WHERE Status = '{status}'" if status else "WHERE IsConverted = false"
    query = f"""
        SELECT Id, FirstName, LastName, Company, Email, Status, LeadSource
        FROM Lead
        {where}
        ORDER BY CreatedDate DESC
        LIMIT {limit}
    """
    result = sf.query(query)
    records = result.get("records", [])

    if not records:
        print("No leads found.")
        return

    rows = [
        [
            r["Id"],
            f"{r.get('FirstName', '')} {r.get('LastName', '')}".strip(),
            r.get("Company", "—"),
            r.get("Email", "—"),
            r.get("Status", "—"),
            r.get("LeadSource", "—"),
        ]
        for r in records
    ]
    print(tabulate(rows, headers=["ID", "Name", "Company", "Email", "Status", "Source"], tablefmt="rounded_outline"))
    print(f"\n{len(rows)} lead(s) shown.\n")


def create_lead(sf: Salesforce, first_name: str, last_name: str, company: str,
                email: str = None, phone: str = None,
                source: str = "Web", status: str = "Open - Not Contacted") -> str:
    """Create a new Lead. Returns the new record Id."""
    payload = {
        "FirstName": first_name,
        "LastName": last_name,
        "Company": company,
        "LeadSource": source,
        "Status": status,
    }
    if email: payload["Email"] = email
    if phone: payload["Phone"] = phone

    result = sf.Lead.create(payload)
    new_id = result["id"]
    print(f"✅ Lead created: {first_name} {last_name} @ {company} → ID: {new_id}\n")
    return new_id


def update_lead_status(sf: Salesforce, lead_id: str, new_status: str) -> None:
    """Update the status of a Lead."""
    if new_status not in LEAD_STATUSES:
        print(f"⚠️  Invalid status. Choose from: {LEAD_STATUSES}")
        return
    sf.Lead.update(lead_id, {"Status": new_status})
    print(f"✅ Lead {lead_id} status → '{new_status}'\n")


def update_lead(sf: Salesforce, lead_id: str, **fields) -> None:
    """Update any fields on a Lead."""
    if not fields:
        print("⚠️  No fields provided.")
        return
    sf.Lead.update(lead_id, fields)
    print(f"✅ Lead {lead_id} updated: {fields}\n")


def convert_lead(sf: Salesforce, lead_id: str) -> None:
    """
    Mark a lead as converted (creates Account + Contact + Opportunity in Salesforce).
    Note: Full conversion requires Apex or UI — this marks it as converted via API.
    """
    sf.Lead.update(lead_id, {"IsConverted": True, "Status": "Closed - Converted"})
    print(f"✅ Lead {lead_id} marked as Converted.\n")


def delete_lead(sf: Salesforce, lead_id: str) -> None:
    """Delete a Lead by Id."""
    sf.Lead.delete(lead_id)
    print(f"🗑️  Lead {lead_id} deleted.\n")


def lead_summary(sf: Salesforce) -> None:
    """Print a count breakdown of leads by status."""
    query = "SELECT Status, COUNT(Id) total FROM Lead GROUP BY Status"
    result = sf.query(query)
    records = result.get("records", [])

    if not records:
        print("No leads data.")
        return

    rows = [[r["Status"], r["total"]] for r in records]
    print("\n📊 Lead Summary by Status:")
    print(tabulate(rows, headers=["Status", "Count"], tablefmt="rounded_outline"))
    print()
