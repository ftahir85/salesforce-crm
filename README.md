# ☁️ Salesforce CRM App

A full-featured CRM application built with **Python** and **Streamlit** that connects to any Salesforce account. Manage Contacts, Leads, Opportunities, and Tasks from a clean web interface — without needing to log into Salesforce directly.

## 📸 Features

- 📊 **Dashboard** — Live metrics, bar charts, and overdue task tracker
- 👤 **Contacts** — Create, search, edit, and delete customers
- 🎯 **Leads** — Manage potential customers with status tracking + Convert Lead button
- 💼 **Opportunities** — Track deals through all pipeline stages
- ✅ **Tasks** — Follow-up reminders with priority and due dates
- 🔄 **Convert Lead** — One click converts a Lead into Contact + Account + Opportunity

---

## 🏗️ Project Structure

```
sf_crm/
├── app.py              # ⭐ Streamlit UI — all pages and forms
├── sf_connection.py    # Salesforce authentication
├── contacts.py         # Contact CRUD operations
├── leads.py            # Lead CRUD + status management
├── opportunities.py    # Deal CRUD + pipeline summary
├── tasks.py            # Task CRUD + overdue tracker
├── main.py             # CLI demo (no UI)
├── requirements.txt    # Python dependencies
└── .env.example        # Credentials template
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/salesforce-crm.git
cd salesforce-crm
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get a free Salesforce Developer account
Sign up at → **developer.salesforce.com/signup** (free, no credit card needed)

### 4. Set up a Connected App in Salesforce
1. Go to **Setup → External Client App Manager → New External Client App**
2. Enable OAuth Settings
3. Set Callback URL to `http://localhost:8501`
4. Add scope: **Full access (full)**
5. Save and copy your **Consumer Key**

### 5. Run the app
```bash
python -m streamlit run app.py
```

Opens at **http://localhost:8501**

---

## 🔐 How to Connect

This app uses **OAuth 2.0** to connect to Salesforce securely.

**Every time you open the app:**

1. Open this URL in your browser (replace `YOUR_DOMAIN` and `YOUR_CONSUMER_KEY`):
```
https://YOUR_DOMAIN.my.salesforce.com/services/oauth2/authorize?response_type=token&client_id=YOUR_CONSUMER_KEY&redirect_uri=http://localhost:8501
```
2. Click **Allow** on the Salesforce authorization page
3. From the redirect URL, copy everything after `access_token=` and before `&refresh_token`
4. Replace `%21` with `!` in the token
5. Paste the token into the **Access Token** field in the sidebar
6. Enter your **Instance URL** (e.g. `https://yourorg.my.salesforce.com`)
7. Click **Connect**

> 💡 Tip: Bookmark the authorization URL so you can get a token in one click every time!

> ⚠️ Tokens expire after ~2 hours. Simply repeat the steps above to get a new one.

---

## 📖 How It Works

```
Your Browser (localhost:8501)
        ↕
    app.py  ← Streamlit UI
        ↕
contacts.py / leads.py / opportunities.py / tasks.py
        ↕
  sf_connection.py
        ↕
  Salesforce Cloud (via simple-salesforce)
        ↕
   Your Salesforce Org
```

---

## 🔄 Full Sales Cycle Example

```
1. A potential customer contacts you
        ↓
2. Create a LEAD with their details
        ↓
3. Call them → update Lead status to "Working - Contacted"
        ↓
4. Create a TASK as a follow-up reminder
        ↓
5. They say YES → click "Convert Lead"
        ↓
   ✅ Contact created (the person)
   ✅ Account created (their company)
   ✅ Opportunity created (the deal)
        ↓
6. Move deal through stages → Closed Won 🎉
        ↓
7. Mark Task as Complete ✅
```

---

## 🎯 Lead Statuses

| Status | Meaning |
|---|---|
| Open - Not Contacted | New lead, not yet reached out |
| Working - Contacted | You called or emailed them |
| Closed - Converted | They became a customer |
| Closed - Not Converted | They were not interested |

---

## 📊 Opportunity Stages

| Stage | Meaning |
|---|---|
| Prospecting | Found a potential customer, nothing confirmed |
| Qualification | Confirmed they have budget and real interest |
| Needs Analysis | Understanding exactly what they need |
| Value Proposition | Explaining why your product is the best fit |
| Id. Decision Makers | Finding out who makes the final decision |
| Perception Analysis | Understanding their concerns and objections |
| Proposal / Price Quote | Sent a formal proposal with pricing |
| Negotiation / Review | They are reviewing and negotiating the deal |
| Closed Won 🎉 | They signed and paid — deal is done! |
| Closed Lost ❌ | They said no or went with a competitor |

---


## 👨‍💻 Author

Built with Python, Streamlit, and the Salesforce REST API.
