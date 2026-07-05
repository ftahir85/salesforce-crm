"""
main.py
-------
Salesforce CRM Integration — Demo & Entrypoint

Shows how to use all four modules: Contacts, Leads, Opportunities, Tasks.
Run this file directly to see a full walkthrough.

Usage:
    python main.py
"""

from sf_connection import get_connection
import contacts as c
import leads as l
import opportunities as o
import tasks as t


def divider(title: str) -> None:
    print("\n" + "─" * 55)
    print(f"  {title}")
    print("─" * 55)


def demo(sf) -> None:
    """
    End-to-end demo: creates records, reads them, updates them,
    and cleans up afterward.
    """

    # ── CONTACTS ──────────────────────────────────────────────
    divider("👤 CONTACTS")

    contact_id = c.create_contact(
        sf,
        first_name="Faisal",
        last_name="Tahir",
        email="ftahir85@example.com",
        phone="+92-555-0100",
        title="Software Engineer",
    )

    c.get_contact(sf, contact_id)

    c.update_contact(sf, contact_id, Title="Senior Software Engineer", Phone="+92-555-9999")

    c.list_contacts(sf, limit=5)

    c.search_contacts(sf, "Tahir")


    # ── LEADS ─────────────────────────────────────────────────
    divider("🎯 LEADS")

    lead_id = l.create_lead(
        sf,
        first_name="Ahmed",
        last_name="Khan",
        company="TechVentures PK",
        email="ahmed@techventures.pk",
        phone="+92-333-7777",
        source="Web",
    )

    l.list_leads(sf, limit=5)
    l.lead_summary(sf)

    l.update_lead_status(sf, lead_id, "Working - Contacted")


    # ── OPPORTUNITIES ─────────────────────────────────────────
    divider("💼 OPPORTUNITIES (DEALS)")

    opp_id = o.create_opportunity(
        sf,
        name="TechVentures PK - Enterprise License",
        stage="Prospecting",
        close_date="2025-12-31",
        amount=45000.00,
        description="Potential enterprise deal from inbound lead.",
    )

    o.get_opportunity(sf, opp_id)
    o.move_stage(sf, opp_id, "Qualification")
    o.pipeline_summary(sf)


    # ── TASKS ─────────────────────────────────────────────────
    divider("✅ TASKS / FOLLOW-UPS")

    task_id = t.create_task(
        sf,
        subject=f"Follow up with Ahmed Khan",
        due_date="2025-07-15",
        priority="High",
        who_id=lead_id,       # link to the Lead we created
        what_id=opp_id,       # link to the Opportunity
        description="Call to discuss proposal and timeline.",
    )

    t.list_tasks(sf, status="Not Started", limit=5)
    t.overdue_tasks(sf)
    t.complete_task(sf, task_id)


    # ── CLEANUP ───────────────────────────────────────────────
    divider("🧹 CLEANUP (deleting demo records)")

    t.delete_task(sf, task_id)
    o.delete_opportunity(sf, opp_id)
    l.delete_lead(sf, lead_id)
    c.delete_contact(sf, contact_id)

    print("All demo records removed.\n")


if __name__ == "__main__":
    print("\n🚀 Salesforce CRM Integration")
    print("=" * 55)

    try:
        sf = get_connection()
        demo(sf)

    except (ValueError, ConnectionError) as e:
        print(f"\n{e}")
        print("\nSetup steps:")
        print("  1. Copy .env.example → .env")
        print("  2. Fill in SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN")
        print("  3. pip install -r requirements.txt")
        print("  4. python main.py\n")
