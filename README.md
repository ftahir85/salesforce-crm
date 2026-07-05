# Salesforce CRM Integration (Python)

A clean Python integration with Salesforce covering **Contacts, Leads, Opportunities, and Tasks** using `simple-salesforce`.

---

## Project Structure

```
sf_crm/
├── .env.example        # Credentials template
├── requirements.txt    # Dependencies
├── sf_connection.py    # Auth / connection
├── contacts.py         # Contact CRUD + search
├── leads.py            # Lead CRUD + status + summary
├── opportunities.py    # Deal CRUD + pipeline summary
├── tasks.py            # Task CRUD + overdue tracker
└── main.py             # Demo entrypoint
```

---

## Project Structure

```
sf_crm/
├── .env.example        # Credentials template (for CLI use)
├── requirements.txt    # Dependencies
├── sf_connection.py    # Auth / connection
├── contacts.py         # Contact CRUD + search
├── leads.py            # Lead CRUD + status + summary
├── opportunities.py    # Deal CRUD + pipeline summary
├── tasks.py            # Task CRUD + overdue tracker
├── app.py              # ⭐ Streamlit UI
└── main.py             # CLI demo entrypoint
```

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit app
```bash
streamlit run app.py
```

Enter your Salesforce credentials directly in the sidebar login form — no `.env` file needed for the UI.

> **How to get your Security Token:**
> Salesforce → Avatar (top right) → Settings → Reset My Security Token

### (Optional) CLI usage via `.env`
```bash
cp .env.example .env
# Fill in SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN
python main.py
```

---

## Usage Examples

### Contacts
```python
from sf_connection import get_connection
import contacts as c

sf = get_connection()

# Create
id = c.create_contact(sf, "Ali", "Tahir", email="ali@example.com")

# List
c.list_contacts(sf, limit=10)

# Search
c.search_contacts(sf, "Tahir")

# Update
c.update_contact(sf, id, Title="CTO", Phone="+92-555-0000")

# Delete
c.delete_contact(sf, id)
```

### Leads
```python
import leads as l

id = l.create_lead(sf, "Sara", "Ahmad", company="Startup PK", source="Web")
l.update_lead_status(sf, id, "Working - Contacted")
l.lead_summary(sf)          # count by status
```

### Opportunities (Deals)
```python
import opportunities as o

id = o.create_opportunity(sf, "Acme Deal", "Prospecting", "2025-12-31", amount=50000)
o.move_stage(sf, id, "Qualification")
o.pipeline_summary(sf)      # total value by stage
```

### Tasks
```python
import tasks as t

id = t.create_task(sf, "Call client", due_date="2025-07-10", priority="High",
                   who_id=contact_id, what_id=opp_id)
t.overdue_tasks(sf)
t.complete_task(sf, id)
```

---

## Key SOQL Examples

```sql
-- Open deals closing this quarter
SELECT Name, Amount, StageName, CloseDate
FROM Opportunity
WHERE IsClosed = false AND CloseDate = THIS_QUARTER
ORDER BY CloseDate ASC

-- All high-priority tasks due today
SELECT Subject, ActivityDate, WhoId
FROM Task
WHERE Priority = 'High' AND ActivityDate = TODAY AND Status != 'Completed'

-- Leads by source
SELECT LeadSource, COUNT(Id) total
FROM Lead
WHERE IsConverted = false
GROUP BY LeadSource
```

---

## Security Note
- Never commit your `.env` file — add it to `.gitignore`
- Never commit `credentials.json` or tokens if you extend this project
