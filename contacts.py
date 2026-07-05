"""
contacts.py
-----------
CRUD operations for Salesforce Contacts.
"""

from tabulate import tabulate
from simple_salesforce import Salesforce


def list_contacts(sf: Salesforce, limit: int = 10) -> None:
    """Display a table of recent contacts."""
    query = f"""
        SELECT Id, FirstName, LastName, Email, Phone, AccountId
        FROM Contact
        ORDER BY CreatedDate DESC
        LIMIT {limit}
    """
    result = sf.query(query)
    records = result.get("records", [])

    if not records:
        print("No contacts found.")
        return

    rows = [
        [
            r["Id"],
            f"{r.get('FirstName', '')} {r.get('LastName', '')}".strip(),
            r.get("Email", "—"),
            r.get("Phone", "—"),
        ]
        for r in records
    ]
    print(tabulate(rows, headers=["ID", "Name", "Email", "Phone"], tablefmt="rounded_outline"))
    print(f"\n{len(rows)} contact(s) shown.\n")


def get_contact(sf: Salesforce, contact_id: str) -> None:
    """Print all details for a single contact."""
    try:
        c = sf.Contact.get(contact_id)
        print("\n📋 Contact Details:")
        print(f"  Name   : {c.get('FirstName', '')} {c.get('LastName', '')}")
        print(f"  Email  : {c.get('Email', '—')}")
        print(f"  Phone  : {c.get('Phone', '—')}")
        print(f"  Title  : {c.get('Title', '—')}")
        print(f"  Account: {c.get('AccountId', '—')}")
        print(f"  ID     : {c.get('Id')}\n")
    except Exception as e:
        print(f"❌ Could not fetch contact: {e}")


def create_contact(sf: Salesforce, first_name: str, last_name: str,
                   email: str = None, phone: str = None, title: str = None) -> str:
    """
    Create a new Contact. Returns the new record Id.
    """
    payload = {
        "FirstName": first_name,
        "LastName": last_name,
    }
    if email:  payload["Email"] = email
    if phone:  payload["Phone"] = phone
    if title:  payload["Title"] = title

    result = sf.Contact.create(payload)
    new_id = result["id"]
    print(f"✅ Contact created: {first_name} {last_name} → ID: {new_id}\n")
    return new_id


def update_contact(sf: Salesforce, contact_id: str, **fields) -> None:
    """
    Update any fields on a Contact.
    Example: update_contact(sf, 'abc123', Email='new@email.com', Phone='+1234')
    """
    if not fields:
        print("⚠️  No fields provided to update.")
        return
    sf.Contact.update(contact_id, fields)
    print(f"✅ Contact {contact_id} updated: {fields}\n")


def delete_contact(sf: Salesforce, contact_id: str) -> None:
    """Delete a Contact by Id."""
    sf.Contact.delete(contact_id)
    print(f"🗑️  Contact {contact_id} deleted.\n")


def search_contacts(sf: Salesforce, keyword: str) -> None:
    """Search contacts by name or email using SOSL."""
    sosl = f"FIND {{{keyword}}} IN ALL FIELDS RETURNING Contact(Id, FirstName, LastName, Email, Phone)"
    results = sf.search(sosl)
    records = results.get("searchRecords", [])

    if not records:
        print(f"No contacts found for '{keyword}'.")
        return

    rows = [
        [
            r["Id"],
            f"{r.get('FirstName', '')} {r.get('LastName', '')}".strip(),
            r.get("Email", "—"),
            r.get("Phone", "—"),
        ]
        for r in records
    ]
    print(tabulate(rows, headers=["ID", "Name", "Email", "Phone"], tablefmt="rounded_outline"))
    print(f"\n{len(rows)} result(s) for '{keyword}'\n")
