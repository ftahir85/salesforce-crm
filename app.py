"""
app.py
------
Streamlit UI for the Salesforce CRM Integration.

Run with:
    python -m streamlit run app.py
"""

import streamlit as st
import pandas as pd
import requests as req
from simple_salesforce import Salesforce

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SF CRM",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0d1b2a; }
    [data-testid="stSidebar"] * { color: #e0e8f0 !important; }
    [data-testid="stMetric"] {
        background: #f0f4ff;
        border-left: 4px solid #1a56db;
        padding: 12px 16px;
        border-radius: 8px;
    }
    [data-testid="stMetricLabel"] { font-size: 0.78rem; color: #6b7280 !important; }
    [data-testid="stMetricValue"] { font-size: 1.5rem; font-weight: 700; color: #111827 !important; }
    .section-header {
        font-size: 1.1rem; font-weight: 600; color: #1a56db;
        margin-top: 1.2rem; margin-bottom: 0.4rem;
        border-bottom: 1px solid #e5e7eb; padding-bottom: 4px;
    }
    .stButton > button { border-radius: 6px; font-weight: 500; }
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_sf():
    return st.session_state.get("sf")

def is_connected():
    return st.session_state.get("sf") is not None

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ☁️ Salesforce CRM")
    st.divider()

    if not is_connected():
        st.markdown("### 🔐 Connect")

        access_token = st.text_input(
            "Access Token",
            type="password",
            placeholder="00Dg500000...",
            help="Get this from the OAuth URL after clicking Allow"
        )

        instance_url = st.text_input(
            "Instance URL",
            value="https://orgfarm-7cbeca96d9-dev-ed.develop.my.salesforce.com",
        )

        st.caption("Get your token: open the authorize link in your browser, click Allow, then copy the access_token from the URL.")

        st.markdown(
            "[🔑 Click here to get a token]"
            "(https://orgfarm-7cbeca96d9-dev-ed.develop.my.salesforce.com/services/oauth2/authorize"
            "?response_type=token"
            "&client_id=3MVG97L7PWbPq6UzkyhseLdvNjjgMvSO9KiHs8ZT0bwQb2ceD5sVJCvV7mI6zgLtiplmFItHKOP6SR5RAz7iQ"
            "&redirect_uri=http://localhost:8501)"
        )

        if st.button("Connect", use_container_width=True, type="primary"):
            if not access_token.strip():
                st.error("Please paste your Access Token.")
            else:
                with st.spinner("Connecting..."):
                    try:
                        sf_conn = Salesforce(
                            instance_url=instance_url.strip(),
                            session_id=access_token.strip(),
                        )
                        # test the connection
                        sf_conn.query("SELECT Id FROM Contact LIMIT 1")
                        st.session_state["sf"] = sf_conn
                        st.session_state["sf_user"] = instance_url
                        st.success("Connected!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Connection failed: {e}")
    else:
        st.success("✅ Connected")
        st.caption("Salesforce CRM is live")
        if st.button("Disconnect", use_container_width=True):
            del st.session_state["sf"]
            del st.session_state["sf_user"]
            st.rerun()

    st.divider()

    if is_connected():
        page = st.radio(
            "Navigate",
            ["📊 Dashboard", "👤 Contacts", "🎯 Leads", "💼 Opportunities", "✅ Tasks"],
            label_visibility="collapsed",
        )
    else:
        page = "📊 Dashboard"

# ── Guard ──────────────────────────────────────────────────────────────────────
if not is_connected():
    st.markdown("## ☁️ Salesforce CRM")
    st.info("Connect your Salesforce account using the sidebar to get started.")
    st.markdown(
        "**Step 1:** Click the link in the sidebar → Click **Allow**\n\n"
        "**Step 2:** From the redirect URL, copy everything after `access_token=` and before `&refresh_token`\n\n"
        "**Step 3:** Replace `%21` with `!` in the token\n\n"
        "**Step 4:** Paste into the Access Token field → Click Connect"
    )
    st.stop()

sf = get_sf()

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("## 📊 Dashboard")

    with st.spinner("Loading..."):
        try:
            contact_count = sf.query("SELECT COUNT(Id) total FROM Contact")["records"][0]["total"]
            lead_count    = sf.query("SELECT COUNT(Id) total FROM Lead WHERE IsConverted = false")["records"][0]["total"]
            opp_count     = sf.query("SELECT COUNT(Id) total FROM Opportunity WHERE IsClosed = false")["records"][0]["total"]
            task_count    = sf.query("SELECT COUNT(Id) total FROM Task WHERE Status != 'Completed'")["records"][0]["total"]
            pipeline_res  = sf.query("SELECT SUM(Amount) total FROM Opportunity WHERE IsClosed = false")
            pipeline_val  = pipeline_res["records"][0]["total"] or 0

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Contacts",      f"{contact_count:,}")
            col2.metric("Open Leads",    f"{lead_count:,}")
            col3.metric("Open Deals",    f"{opp_count:,}")
            col4.metric("Pending Tasks", f"{task_count:,}")
            col5.metric("Pipeline",      f"${pipeline_val:,.0f}")
        except Exception as e:
            st.error(f"Could not load summary: {e}")

    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header">Leads by Status</div>', unsafe_allow_html=True)
        try:
            res = sf.query("SELECT Status, COUNT(Id) total FROM Lead GROUP BY Status")
            records = res.get("records", [])
            if records:
                df = pd.DataFrame([{"Status": r["Status"], "Count": r["total"]} for r in records])
                st.bar_chart(df.set_index("Status"))
            else:
                st.caption("No lead data yet.")
        except Exception as e:
            st.error(str(e))

    with col_b:
        st.markdown('<div class="section-header">Pipeline by Stage</div>', unsafe_allow_html=True)
        try:
            res = sf.query("SELECT StageName, SUM(Amount) total FROM Opportunity WHERE IsClosed = false GROUP BY StageName")
            records = res.get("records", [])
            if records:
                df = pd.DataFrame([{"Stage": r["StageName"], "Value ($)": r.get("total") or 0} for r in records])
                st.bar_chart(df.set_index("Stage"))
            else:
                st.caption("No pipeline data yet.")
        except Exception as e:
            st.error(str(e))

    st.divider()
    st.markdown('<div class="section-header">⚠️ Overdue Tasks</div>', unsafe_allow_html=True)
    try:
        res = sf.query("SELECT Id, Subject, Priority, ActivityDate FROM Task WHERE Status != 'Completed' AND ActivityDate < TODAY ORDER BY ActivityDate ASC LIMIT 10")
        records = res.get("records", [])
        if records:
            df = pd.DataFrame([{"Subject": r.get("Subject","—"), "Priority": r.get("Priority","—"), "Due Date": r.get("ActivityDate","—")} for r in records])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.success("No overdue tasks! 🎉")
    except Exception as e:
        st.error(str(e))


# ══════════════════════════════════════════════════════════════════════════════
# CONTACTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👤 Contacts":
    st.markdown("## 👤 Contacts")
    tab_list, tab_create, tab_edit = st.tabs(["📋 List", "➕ Create", "✏️ Edit / Delete"])

    with tab_list:
        col1, col2 = st.columns([3, 1])
        keyword = col1.text_input("Search by name or email", placeholder="e.g. Tahir")
        limit   = col2.number_input("Max results", min_value=5, max_value=100, value=20, step=5)
        if st.button("Search / Refresh", type="primary"):
            with st.spinner("Fetching..."):
                try:
                    if keyword.strip():
                        sosl = f"FIND {{{keyword}}} IN ALL FIELDS RETURNING Contact(Id, FirstName, LastName, Email, Phone, Title)"
                        records = sf.search(sosl).get("searchRecords", [])
                    else:
                        records = sf.query(f"SELECT Id, FirstName, LastName, Email, Phone, Title FROM Contact ORDER BY CreatedDate DESC LIMIT {limit}")["records"]
                    if records:
                        df = pd.DataFrame([{"ID": r["Id"], "Name": f"{r.get('FirstName','')} {r.get('LastName','')}".strip(), "Email": r.get("Email","—"), "Phone": r.get("Phone","—"), "Title": r.get("Title","—")} for r in records])
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        st.caption(f"{len(records)} contact(s) found.")
                    else:
                        st.info("No contacts found.")
                except Exception as e:
                    st.error(str(e))

    with tab_create:
        st.markdown('<div class="section-header">New Contact</div>', unsafe_allow_html=True)
        with st.form("create_contact_form"):
            col1, col2 = st.columns(2)
            first = col1.text_input("First Name *")
            last  = col2.text_input("Last Name *")
            email = col1.text_input("Email")
            phone = col2.text_input("Phone")
            title = st.text_input("Job Title")
            submitted = st.form_submit_button("Create Contact", type="primary")
        if submitted:
            if not first or not last:
                st.error("First Name and Last Name are required.")
            else:
                try:
                    payload = {"FirstName": first, "LastName": last}
                    if email: payload["Email"] = email
                    if phone: payload["Phone"] = phone
                    if title: payload["Title"] = title
                    res = sf.Contact.create(payload)
                    st.success(f"✅ Contact created! ID: `{res['id']}`")
                except Exception as e:
                    st.error(str(e))

    with tab_edit:
        st.markdown('<div class="section-header">Edit or Delete a Contact</div>', unsafe_allow_html=True)
        contact_id = st.text_input("Contact ID", placeholder="0035g00000AbCdEFG")
        if contact_id and st.button("Load Contact"):
            try:
                st.session_state["loaded_contact"] = sf.Contact.get(contact_id)
            except Exception as e:
                st.error(f"Could not load: {e}")
        if "loaded_contact" in st.session_state:
            rec = st.session_state["loaded_contact"]
            st.markdown(f"**Editing:** {rec.get('FirstName','')} {rec.get('LastName','')}")
            with st.form("edit_contact_form"):
                col1, col2 = st.columns(2)
                new_email = col1.text_input("Email", value=rec.get("Email") or "")
                new_phone = col2.text_input("Phone", value=rec.get("Phone") or "")
                new_title = st.text_input("Title", value=rec.get("Title") or "")
                col_save, col_del = st.columns(2)
                save   = col_save.form_submit_button("💾 Save Changes", type="primary")
                delete = col_del.form_submit_button("🗑️ Delete Contact")
            if save:
                try:
                    sf.Contact.update(contact_id, {"Email": new_email, "Phone": new_phone, "Title": new_title})
                    st.success("Contact updated.")
                    del st.session_state["loaded_contact"]
                except Exception as e:
                    st.error(str(e))
            if delete:
                try:
                    sf.Contact.delete(contact_id)
                    st.success("Contact deleted.")
                    del st.session_state["loaded_contact"]
                except Exception as e:
                    st.error(str(e))


# ══════════════════════════════════════════════════════════════════════════════
# LEADS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Leads":
    st.markdown("## 🎯 Leads")
    tab_list, tab_create, tab_edit = st.tabs(["📋 List", "➕ Create", "✏️ Edit / Delete"])

    LEAD_STATUSES = ["Open - Not Contacted", "Working - Contacted", "Closed - Converted", "Closed - Not Converted"]
    LEAD_SOURCES  = ["Web", "Phone Inquiry", "Partner Referral", "Purchased List", "Other", "Advertisement", "Employee Referral", "External Referral"]

    with tab_list:
        col1, col2 = st.columns([2, 1])
        status_filter = col1.selectbox("Filter by status", ["All"] + LEAD_STATUSES)
        limit = col2.number_input("Max results", min_value=5, max_value=100, value=20, step=5)
        if st.button("Refresh Leads", type="primary"):
            with st.spinner("Fetching..."):
                try:
                    where = "" if status_filter == "All" else f"AND Status = '{status_filter}'"
                    records = sf.query(f"SELECT Id, FirstName, LastName, Company, Email, Status, LeadSource FROM Lead WHERE IsConverted = false {where} ORDER BY CreatedDate DESC LIMIT {limit}")["records"]
                    if records:
                        df = pd.DataFrame([{"ID": r["Id"], "Name": f"{r.get('FirstName','')} {r.get('LastName','')}".strip(), "Company": r.get("Company","—"), "Email": r.get("Email","—"), "Status": r.get("Status","—"), "Source": r.get("LeadSource","—")} for r in records])
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        st.caption(f"{len(records)} lead(s) found.")
                    else:
                        st.info("No leads found.")
                except Exception as e:
                    st.error(str(e))

    with tab_create:
        st.markdown('<div class="section-header">New Lead</div>', unsafe_allow_html=True)
        with st.form("create_lead_form"):
            col1, col2 = st.columns(2)
            first   = col1.text_input("First Name *")
            last    = col2.text_input("Last Name *")
            company = st.text_input("Company *")
            email   = col1.text_input("Email")
            phone   = col2.text_input("Phone")
            source  = col1.selectbox("Lead Source", LEAD_SOURCES)
            status  = col2.selectbox("Status", LEAD_STATUSES)
            submitted = st.form_submit_button("Create Lead", type="primary")
        if submitted:
            if not first or not last or not company:
                st.error("First Name, Last Name, and Company are required.")
            else:
                try:
                    payload = {"FirstName": first, "LastName": last, "Company": company, "LeadSource": source, "Status": status}
                    if email: payload["Email"] = email
                    if phone: payload["Phone"] = phone
                    res = sf.Lead.create(payload)
                    st.success(f"✅ Lead created! ID: `{res['id']}`")
                except Exception as e:
                    st.error(str(e))

    with tab_edit:
        st.markdown('<div class="section-header">Edit, Convert or Delete a Lead</div>', unsafe_allow_html=True)
        lead_id = st.text_input("Lead ID", placeholder="00Q5g00000AbCdEFG")
        if lead_id and st.button("Load Lead"):
            try:
                st.session_state["loaded_lead"] = sf.Lead.get(lead_id)
            except Exception as e:
                st.error(f"Could not load: {e}")
        if "loaded_lead" in st.session_state:
            rec = st.session_state["loaded_lead"]
            st.markdown(f"**Editing:** {rec.get('FirstName','')} {rec.get('LastName','')} @ {rec.get('Company','')}")
            with st.form("edit_lead_form"):
                col1, col2 = st.columns(2)
                new_status = col1.selectbox("Status", LEAD_STATUSES, index=LEAD_STATUSES.index(rec.get("Status", LEAD_STATUSES[0])) if rec.get("Status") in LEAD_STATUSES else 0)
                new_email  = col2.text_input("Email", value=rec.get("Email") or "")
                new_phone  = col1.text_input("Phone", value=rec.get("Phone") or "")
                new_source = col2.selectbox("Lead Source", LEAD_SOURCES, index=LEAD_SOURCES.index(rec.get("LeadSource", LEAD_SOURCES[0])) if rec.get("LeadSource") in LEAD_SOURCES else 0)
                col_save, col_convert, col_del = st.columns(3)
                save    = col_save.form_submit_button("💾 Save Changes", type="primary")
                convert = col_convert.form_submit_button("🔄 Convert Lead")
                delete  = col_del.form_submit_button("🗑️ Delete Lead")

            if save:
                try:
                    sf.Lead.update(lead_id, {"Status": new_status, "Email": new_email, "Phone": new_phone, "LeadSource": new_source})
                    st.success("Lead updated.")
                    del st.session_state["loaded_lead"]
                except Exception as e:
                    st.error(str(e))

            if convert:
                with st.spinner("Converting lead..."):
                    try:
                        first   = rec.get("FirstName", "")
                        last    = rec.get("LastName", "")
                        email   = rec.get("Email", "")
                        phone   = rec.get("Phone", "")
                        company = rec.get("Company", "Unknown Company")

                        # Step 1: Create Contact
                        contact_payload = {"FirstName": first, "LastName": last}
                        if phone: contact_payload["Phone"] = phone
                        # use a unique email to avoid duplicate error
                        if email:
                            contact_payload["Email"] = email
                        try:
                            contact_res = sf.Contact.create(contact_payload)
                            contact_id  = contact_res["id"]
                        except Exception:
                            # if duplicate, skip email
                            contact_payload.pop("Email", None)
                            contact_res = sf.Contact.create(contact_payload)
                            contact_id  = contact_res["id"]

                        # Step 2: Create Account
                        account_res = sf.Account.create({"Name": company})
                        account_id  = account_res["id"]

                        # Step 3: Create Opportunity
                        import datetime
                        close_date = (datetime.date.today() + datetime.timedelta(days=90)).strftime("%Y-%m-%d")
                        opp_res = sf.Opportunity.create({
                            "Name":        f"{company} - Opportunity",
                            "StageName":   "Prospecting",
                            "CloseDate":   close_date,
                            "AccountId":   account_id,
                        })
                        opp_id = opp_res["id"]

                        # Step 4: Mark lead as converted
                        sf.Lead.update(lead_id, {"Status": "Closed - Converted"})

                        st.success(f"✅ Lead converted successfully!")
                        st.markdown(f"**Created:**")
                        st.markdown(f"- 👤 Contact ID: `{contact_id}`")
                        st.markdown(f"- 🏢 Account ID: `{account_id}`")
                        st.markdown(f"- 💼 Opportunity ID: `{opp_id}`")
                        st.info("You can now find Ahmed in Contacts and the deal in Opportunities!")
                        del st.session_state["loaded_lead"]
                    except Exception as e:
                        st.error(f"Conversion failed: {e}")

            if delete:
                try:
                    sf.Lead.delete(lead_id)
                    st.success("Lead deleted.")
                    del st.session_state["loaded_lead"]
                except Exception as e:
                    st.error(str(e))


# ══════════════════════════════════════════════════════════════════════════════
# OPPORTUNITIES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💼 Opportunities":
    st.markdown("## 💼 Opportunities")
    tab_list, tab_create, tab_edit = st.tabs(["📋 Pipeline", "➕ Create", "✏️ Edit / Delete"])

    STAGES = ["Prospecting", "Qualification", "Needs Analysis", "Value Proposition", "Id. Decision Makers", "Perception Analysis", "Proposal/Price Quote", "Negotiation/Review", "Closed Won", "Closed Lost"]

    with tab_list:
        col1, col2, col3 = st.columns([2, 2, 1])
        stage_filter = col1.selectbox("Filter by stage", ["All Open"] + STAGES)
        min_amt      = col2.number_input("Min amount ($)", min_value=0, value=0, step=1000)
        limit        = col3.number_input("Max results", min_value=5, max_value=100, value=20, step=5)
        if st.button("Refresh Pipeline", type="primary"):
            with st.spinner("Fetching..."):
                try:
                    filters = ["IsClosed = false"] if stage_filter == "All Open" else [f"StageName = '{stage_filter}'"]
                    if min_amt > 0: filters.append(f"Amount >= {min_amt}")
                    where = "WHERE " + " AND ".join(filters)
                    records = sf.query(f"SELECT Id, Name, Amount, StageName, CloseDate, Probability FROM Opportunity {where} ORDER BY CloseDate ASC LIMIT {limit}")["records"]
                    if records:
                        df = pd.DataFrame([{"ID": r["Id"], "Name": r.get("Name","—"), "Amount": f"${r.get('Amount',0):,.0f}" if r.get("Amount") else "—", "Stage": r.get("StageName","—"), "Close Date": r.get("CloseDate","—"), "Prob.": f"{r.get('Probability',0):.0f}%"} for r in records])
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        total = sum((r.get("Amount") or 0) for r in records)
                        st.metric("Total Value", f"${total:,.0f}")
                    else:
                        st.info("No opportunities found.")
                except Exception as e:
                    st.error(str(e))

    with tab_create:
        st.markdown('<div class="section-header">New Opportunity</div>', unsafe_allow_html=True)
        with st.form("create_opp_form"):
            name       = st.text_input("Opportunity Name *", placeholder="Acme Corp - Enterprise Deal")
            col1, col2 = st.columns(2)
            stage      = col1.selectbox("Stage *", STAGES)
            close_date = col2.date_input("Expected Close Date *")
            amount     = col1.number_input("Amount ($)", min_value=0.0, step=500.0)
            account_id = col2.text_input("Account ID (optional)")
            description = st.text_area("Notes", height=80)
            submitted  = st.form_submit_button("Create Opportunity", type="primary")
        if submitted:
            if not name:
                st.error("Opportunity Name is required.")
            else:
                try:
                    payload = {"Name": name, "StageName": stage, "CloseDate": str(close_date)}
                    if amount:      payload["Amount"] = amount
                    if account_id:  payload["AccountId"] = account_id
                    if description: payload["Description"] = description
                    res = sf.Opportunity.create(payload)
                    st.success(f"✅ Opportunity created! ID: `{res['id']}`")
                except Exception as e:
                    st.error(str(e))

    with tab_edit:
        st.markdown('<div class="section-header">Edit or Delete an Opportunity</div>', unsafe_allow_html=True)
        opp_id = st.text_input("Opportunity ID", placeholder="0065g00000AbCdEFG")
        if opp_id and st.button("Load Opportunity"):
            try:
                st.session_state["loaded_opp"] = sf.Opportunity.get(opp_id)
            except Exception as e:
                st.error(f"Could not load: {e}")
        if "loaded_opp" in st.session_state:
            rec = st.session_state["loaded_opp"]
            st.markdown(f"**Editing:** {rec.get('Name','')}")
            with st.form("edit_opp_form"):
                col1, col2 = st.columns(2)
                new_stage  = col1.selectbox("Stage", STAGES, index=STAGES.index(rec.get("StageName", STAGES[0])) if rec.get("StageName") in STAGES else 0)
                new_amount = col2.number_input("Amount ($)", value=float(rec.get("Amount") or 0), step=500.0)
                new_close  = col1.text_input("Close Date (YYYY-MM-DD)", value=rec.get("CloseDate") or "")
                new_desc   = col2.text_input("Notes", value=rec.get("Description") or "")
                col_save, col_del = st.columns(2)
                save   = col_save.form_submit_button("💾 Save Changes", type="primary")
                delete = col_del.form_submit_button("🗑️ Delete Opportunity")
            if save:
                try:
                    sf.Opportunity.update(opp_id, {"StageName": new_stage, "Amount": new_amount, "CloseDate": new_close, "Description": new_desc})
                    st.success("Opportunity updated.")
                    del st.session_state["loaded_opp"]
                except Exception as e:
                    st.error(str(e))
            if delete:
                try:
                    sf.Opportunity.delete(opp_id)
                    st.success("Opportunity deleted.")
                    del st.session_state["loaded_opp"]
                except Exception as e:
                    st.error(str(e))


# ══════════════════════════════════════════════════════════════════════════════
# TASKS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "✅ Tasks":
    st.markdown("## ✅ Tasks & Follow-ups")
    tab_list, tab_create, tab_edit = st.tabs(["📋 List", "➕ Create", "✏️ Edit / Delete"])

    TASK_STATUSES   = ["Not Started", "In Progress", "Completed", "Waiting on someone else", "Deferred"]
    TASK_PRIORITIES = ["High", "Normal", "Low"]

    with tab_list:
        col1, col2, col3 = st.columns([2, 2, 1])
        status_filter = col1.selectbox("Filter by status", ["All"] + TASK_STATUSES)
        overdue_only  = col2.checkbox("Show overdue only")
        limit         = col3.number_input("Max results", min_value=5, max_value=100, value=20, step=5)
        if st.button("Refresh Tasks", type="primary"):
            with st.spinner("Fetching..."):
                try:
                    filters = []
                    if status_filter != "All": filters.append(f"Status = '{status_filter}'")
                    if overdue_only:
                        filters.append("ActivityDate < TODAY")
                        filters.append("Status != 'Completed'")
                    where = ("WHERE " + " AND ".join(filters)) if filters else ""
                    records = sf.query(f"SELECT Id, Subject, Status, Priority, ActivityDate FROM Task {where} ORDER BY ActivityDate ASC NULLS LAST LIMIT {limit}")["records"]
                    if records:
                        df = pd.DataFrame([{"ID": r["Id"], "Subject": r.get("Subject","—"), "Priority": r.get("Priority","—"), "Status": r.get("Status","—"), "Due Date": r.get("ActivityDate","—")} for r in records])
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        st.caption(f"{len(records)} task(s) found.")
                    else:
                        st.info("No tasks found.")
                except Exception as e:
                    st.error(str(e))

    with tab_create:
        st.markdown('<div class="section-header">New Task</div>', unsafe_allow_html=True)
        with st.form("create_task_form"):
            subject     = st.text_input("Subject *", placeholder="Follow up with Ahmed Khan")
            col1, col2  = st.columns(2)
            priority    = col1.selectbox("Priority", TASK_PRIORITIES, index=1)
            status      = col2.selectbox("Status", TASK_STATUSES)
            due_date    = col1.date_input("Due Date (optional)", value=None)
            who_id      = col2.text_input("Linked Contact/Lead ID (optional)")
            what_id     = col1.text_input("Linked Opportunity/Account ID (optional)")
            description = st.text_area("Notes", height=80)
            submitted   = st.form_submit_button("Create Task", type="primary")
        if submitted:
            if not subject:
                st.error("Subject is required.")
            else:
                try:
                    payload = {"Subject": subject, "Priority": priority, "Status": status}
                    if due_date:    payload["ActivityDate"] = str(due_date)
                    if who_id:      payload["WhoId"] = who_id
                    if what_id:     payload["WhatId"] = what_id
                    if description: payload["Description"] = description
                    res = sf.Task.create(payload)
                    st.success(f"✅ Task created! ID: `{res['id']}`")
                except Exception as e:
                    st.error(str(e))

    with tab_edit:
        st.markdown('<div class="section-header">Edit or Complete a Task</div>', unsafe_allow_html=True)
        task_id = st.text_input("Task ID", placeholder="00T5g00000AbCdEFG")
        if task_id and st.button("Load Task"):
            try:
                st.session_state["loaded_task"] = sf.Task.get(task_id)
            except Exception as e:
                st.error(f"Could not load: {e}")
        if "loaded_task" in st.session_state:
            rec = st.session_state["loaded_task"]
            st.markdown(f"**Editing:** {rec.get('Subject','')}")
            with st.form("edit_task_form"):
                col1, col2   = st.columns(2)
                new_status   = col1.selectbox("Status", TASK_STATUSES, index=TASK_STATUSES.index(rec.get("Status", TASK_STATUSES[0])) if rec.get("Status") in TASK_STATUSES else 0)
                new_priority = col2.selectbox("Priority", TASK_PRIORITIES, index=TASK_PRIORITIES.index(rec.get("Priority","Normal")) if rec.get("Priority") in TASK_PRIORITIES else 1)
                new_due  = col1.text_input("Due Date (YYYY-MM-DD)", value=rec.get("ActivityDate") or "")
                new_desc = col2.text_input("Notes", value=rec.get("Description") or "")
                col_save, col_done, col_del = st.columns(3)
                save     = col_save.form_submit_button("💾 Save", type="primary")
                complete = col_done.form_submit_button("✅ Mark Complete")
                delete   = col_del.form_submit_button("🗑️ Delete")
            if save:
                try:
                    sf.Task.update(task_id, {"Status": new_status, "Priority": new_priority, "ActivityDate": new_due or None, "Description": new_desc})
                    st.success("Task updated.")
                    del st.session_state["loaded_task"]
                except Exception as e:
                    st.error(str(e))
            if complete:
                try:
                    sf.Task.update(task_id, {"Status": "Completed"})
                    st.success("Task marked as Completed.")
                    del st.session_state["loaded_task"]
                except Exception as e:
                    st.error(str(e))
            if delete:
                try:
                    sf.Task.delete(task_id)
                    st.success("Task deleted.")
                    del st.session_state["loaded_task"]
                except Exception as e:
                    st.error(str(e))
