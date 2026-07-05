"""
opportunities.py
----------------
CRUD operations for Salesforce Opportunities (Deals).
"""

from datetime import date
from tabulate import tabulate
from simple_salesforce import Salesforce


STAGES = [
    "Prospecting",
    "Qualification",
    "Needs Analysis",
    "Value Proposition",
    "Id. Decision Makers",
    "Perception Analysis",
    "Proposal/Price Quote",
    "Negotiation/Review",
    "Closed Won",
    "Closed Lost",
]


def list_opportunities(sf: Salesforce, stage: str = None,
                       min_amount: float = None, limit: int = 10) -> None:
    """List open opportunities with optional filters."""
    filters = ["IsClosed = false"]
    if stage:       filters.append(f"StageName = '{stage}'")
    if min_amount:  filters.append(f"Amount >= {min_amount}")

    where = "WHERE " + " AND ".join(filters)
    query = f"""
        SELECT Id, Name, AccountId, Amount, StageName, CloseDate, Probability
        FROM Opportunity
        {where}
        ORDER BY CloseDate ASC
        LIMIT {limit}
    """
    result = sf.query(query)
    records = result.get("records", [])

    if not records:
        print("No opportunities found.")
        return

    rows = [
        [
            r["Id"],
            r.get("Name", "—"),
            f"${r.get('Amount', 0):,.0f}" if r.get("Amount") else "—",
            r.get("StageName", "—"),
            r.get("CloseDate", "—"),
            f"{r.get('Probability', 0):.0f}%",
        ]
        for r in records
    ]
    print(tabulate(rows, headers=["ID", "Name", "Amount", "Stage", "Close Date", "Prob."], tablefmt="rounded_outline"))
    print(f"\n{len(rows)} opportunity(s) shown.\n")


def get_opportunity(sf: Salesforce, opp_id: str) -> None:
    """Print full details for an Opportunity."""
    try:
        o = sf.Opportunity.get(opp_id)
        print("\n💼 Opportunity Details:")
        print(f"  Name       : {o.get('Name')}")
        print(f"  Amount     : ${o.get('Amount', 0):,.2f}")
        print(f"  Stage      : {o.get('StageName')}")
        print(f"  Close Date : {o.get('CloseDate')}")
        print(f"  Probability: {o.get('Probability')}%")
        print(f"  Account ID : {o.get('AccountId', '—')}")
        print(f"  Description: {o.get('Description', '—')}")
        print(f"  ID         : {o.get('Id')}\n")
    except Exception as e:
        print(f"❌ Could not fetch opportunity: {e}")


def create_opportunity(sf: Salesforce, name: str, stage: str,
                       close_date: str, amount: float = None,
                       account_id: str = None, description: str = None) -> str:
    """
    Create a new Opportunity.

    Args:
        name        : Opportunity name, e.g. 'Acme Corp - Enterprise Deal'
        stage       : Must be a valid Salesforce stage name
        close_date  : Expected close date, format 'YYYY-MM-DD'
        amount      : Deal value in USD
        account_id  : Link to an Account record (optional)
        description : Notes about the deal (optional)

    Returns:
        The new record Id.
    """
    if stage not in STAGES:
        print(f"⚠️  Unknown stage. Valid stages:\n  {STAGES}")

    payload = {
        "Name": name,
        "StageName": stage,
        "CloseDate": close_date,
    }
    if amount:      payload["Amount"] = amount
    if account_id:  payload["AccountId"] = account_id
    if description: payload["Description"] = description

    result = sf.Opportunity.create(payload)
    new_id = result["id"]
    print(f"✅ Opportunity created: '{name}' → ID: {new_id}\n")
    return new_id


def move_stage(sf: Salesforce, opp_id: str, new_stage: str) -> None:
    """Advance or change the stage of an Opportunity."""
    if new_stage not in STAGES:
        print(f"⚠️  Invalid stage. Choose from:\n  {STAGES}")
        return
    sf.Opportunity.update(opp_id, {"StageName": new_stage})
    print(f"✅ Opportunity {opp_id} moved to '{new_stage}'\n")


def update_opportunity(sf: Salesforce, opp_id: str, **fields) -> None:
    """Update any fields on an Opportunity."""
    if not fields:
        print("⚠️  No fields provided.")
        return
    sf.Opportunity.update(opp_id, fields)
    print(f"✅ Opportunity {opp_id} updated: {fields}\n")


def delete_opportunity(sf: Salesforce, opp_id: str) -> None:
    """Delete an Opportunity by Id."""
    sf.Opportunity.delete(opp_id)
    print(f"🗑️  Opportunity {opp_id} deleted.\n")


def pipeline_summary(sf: Salesforce) -> None:
    """Print total pipeline value grouped by stage."""
    query = """
        SELECT StageName, COUNT(Id) count, SUM(Amount) total
        FROM Opportunity
        WHERE IsClosed = false
        GROUP BY StageName
        ORDER BY SUM(Amount) DESC
    """
    result = sf.query(query)
    records = result.get("records", [])

    if not records:
        print("No open pipeline data.")
        return

    rows = [
        [r["StageName"], r["count"], f"${r.get('total') or 0:,.0f}"]
        for r in records
    ]
    total = sum(r.get("total") or 0 for r in records)
    print("\n📊 Open Pipeline by Stage:")
    print(tabulate(rows, headers=["Stage", "Deals", "Total Value"], tablefmt="rounded_outline"))
    print(f"\n  💰 Total Pipeline: ${total:,.0f}\n")
