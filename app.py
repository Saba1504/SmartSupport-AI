import os, json, re
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="SmartSupport AI", page_icon="🤖", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 1.6rem; max-width: 1400px;}
.hero {padding: 1.25rem 1.5rem; border-radius: 16px; background: linear-gradient(110deg,#14213d,#254b72); color:white; margin-bottom:1rem;}
.hero h1 {color:white; margin:0;}
.hero p {color:#e4edf7; margin:.35rem 0 0 0;}
.small-note {color:#64748b;font-size:.9rem;}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🤖 SmartSupport AI</h1><p>AI-assisted ticket triage, grounded reply drafting, and human-in-the-loop support operations.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("OpenAI API key (optional)", type="password", help="Used only for this session. Do not paste keys into project files.")
    model = st.text_input("Model", value="gpt-4o-mini")
    use_ai = st.checkbox("Use live AI when API key is provided", value=True)
    st.divider()
    st.caption("Demo mode works without an API key. Live AI output requires internet access and an API account.")

FAQ = [
    {"topic":"Refunds","text":"Refund requests must be reviewed against the order's refund policy. Ask for the order ID and purchase date; do not promise approval."},
    {"topic":"Account access","text":"For login issues, suggest checking the registered email, using the password-reset flow, and confirming whether an error message appears. Never ask for passwords or one-time codes."},
    {"topic":"Shipping","text":"For delivery delays, ask for the order number and estimated delivery date. Explain that tracking information should be checked before giving a delivery estimate."},
    {"topic":"Technical issue","text":"For technical issues, ask for the product/app version, device/browser, steps to reproduce, and any error text. Do not claim a fix has been deployed unless verified."},
    {"topic":"Billing","text":"For billing questions, request the invoice/order reference and date. Never request full card numbers, CVV, passwords, or other sensitive credentials."},
]
faq_df = pd.DataFrame(FAQ)

def retrieve_context(text):
    terms = set(re.findall(r"[a-z]{3,}", text.lower()))
    scored=[]
    for row in FAQ:
        words=set(re.findall(r"[a-z]{3,}", (row["topic"]+" "+row["text"]).lower()))
        scored.append((len(terms & words), row))
    scored.sort(key=lambda x:x[0], reverse=True)
    return [r for score,r in scored[:2] if score > 0]

def demo_classify(text):
    t=text.lower()
    if any(w in t for w in ["refund","return","money back","cancel order"]): category="Refunds"
    elif any(w in t for w in ["login","log in","password","account","locked"]): category="Account access"
    elif any(w in t for w in ["delivery","shipping","arrived","tracking","late","package"]): category="Shipping"
    elif any(w in t for w in ["crash","error","bug","not working","technical","app"]): category="Technical issue"
    elif any(w in t for w in ["bill","billing","invoice","charged","payment"]): category="Billing"
    else: category="General inquiry"
    high_terms=["urgent","asap","immediately","fraud","charged twice","locked out","data breach","cannot access","cannot log in","account locked"]
    priority="High" if any(w in t for w in high_terms) else ("Medium" if any(w in t for w in ["problem","issue","delay","late","crash","crashes","wrong","failed"]) else "Low")
    sentiment="Negative" if any(w in t for w in ["angry","terrible","unacceptable","frustrated","complaint","wrong","failed","urgent"]) else ("Positive" if any(w in t for w in ["thanks","thank you","great","love"]) else "Neutral")
    return {"category":category,"priority":priority,"sentiment":sentiment,"summary":text[:180].strip(),"draft_reply":make_demo_reply(category,text),"confidence":"Rule-based demo (not a model confidence score)"}

def make_demo_reply(category, text):
    starts = {
      "Refunds":"Thanks for contacting us about your refund. ",
      "Account access":"Thanks for letting us know about the account access issue. ",
      "Shipping":"Thanks for reaching out about your delivery. ",
      "Technical issue":"Thanks for reporting this technical issue. ",
      "Billing":"Thanks for contacting us about billing. ",
      "General inquiry":"Thanks for contacting support. "
    }
    next_step = {
      "Refunds":"Please share your order reference and purchase date so the team can review the applicable policy. We cannot confirm refund eligibility until it is checked.",
      "Account access":"Please use the official password-reset flow and share the error message you see. Never send your password or verification code.",
      "Shipping":"Please share your order reference and estimated delivery date so the team can check the latest tracking status.",
      "Technical issue":"Please share your device/browser, app version, steps to reproduce, and the exact error message. We will use these details to investigate.",
      "Billing":"Please share the invoice or order reference and transaction date. Do not send full card details or security codes.",
      "General inquiry":"Please share a little more detail about the issue so the team can direct it to the right person."
    }
    return starts[category]+next_step[category]

def live_ai(text, api_key, model, context):
    from openai import OpenAI
    client=OpenAI(api_key=api_key)
    prompt = f"""You are a careful customer-support triage assistant. Analyse the ticket and return ONLY valid JSON with keys:
category (one of Refunds, Account access, Shipping, Technical issue, Billing, General inquiry),
priority (High, Medium, Low), sentiment (Negative, Neutral, Positive), summary (max 35 words),
draft_reply (polite, specific, concise; do not claim actions were taken; ask only for information necessary; never request passwords, OTPs, CVVs, or full payment-card details),
rationale (one short sentence explaining category/priority).
Escalate potential fraud, security incidents, data breaches, account lockouts, and urgent access failures as High priority.
Use the following support reference notes only as guidance, not as proof of an action: {json.dumps(context)}
If information is missing, say so rather than inventing facts. This is a draft for human review, not an automatically sent response.
Ticket: {text}"""
    response=client.chat.completions.create(model=model, temperature=0.2, messages=[
      {"role":"system","content":"Follow the output schema exactly. Return JSON only."},
      {"role":"user","content":prompt}
    ], response_format={"type":"json_object"})
    return json.loads(response.choices[0].message.content)

if "tickets" not in st.session_state:
    st.session_state.tickets = pd.DataFrame([
      {"ticket_id":"DEMO-001","customer_message":"My package is 5 days late and tracking has not changed. Please help.","status":"Pending review","created_at":"2026-10-25"},
      {"ticket_id":"DEMO-002","customer_message":"I was charged twice on my invoice. This is urgent.","status":"Pending review","created_at":"2026-10-25"},
      {"ticket_id":"DEMO-003","customer_message":"I cannot log in after resetting my password.","status":"Pending review","created_at":"2026-10-25"},
      {"ticket_id":"DEMO-004","customer_message":"I want a refund for order A123. I purchased it last week.","status":"Pending review","created_at":"2026-10-25"},
      {"ticket_id":"DEMO-005","customer_message":"The app crashes every time I open settings.","status":"Pending review","created_at":"2026-10-25"},
      {"ticket_id":"DEMO-006","customer_message":"Thank you, the instructions were really helpful!","status":"Pending review","created_at":"2026-10-25"},
    ])
if "results" not in st.session_state:
    st.session_state.results = []

tab1, tab2, tab3 = st.tabs(["🎫 Process tickets", "📊 Operations dashboard", "📚 How it works"])

with tab1:
    st.subheader("Process a support message")
    msg = st.text_area("Customer message", value="I was charged twice and need this fixed urgently.", height=110, key="single_msg")
    if st.button("Analyse ticket", type="primary"):
        if not msg.strip():
            st.warning("Enter a customer message first.")
        else:
            ctx=retrieve_context(msg)
            try:
                if use_ai and api_key:
                    result=live_ai(msg,api_key,model,ctx)
                    result["mode"]="Live AI"
                else:
                    result=demo_classify(msg)
                    result["rationale"]="Demo rules matched keywords; verify the label before using it."
                    result["mode"]="Demo rules"
                st.session_state.latest = {"ticket_id":"NEW-"+datetime.now().strftime("%H%M%S"),"customer_message":msg,**result,"status":"Pending review","created_at":datetime.now().strftime("%Y-%m-%d")}
            except Exception as e:
                st.error(f"Live AI request failed: {e}. You can remove the API key and use demo mode.")
    if "latest" in st.session_state:
        r=st.session_state.latest
        st.divider()
        st.subheader("Analysis — human review required")
        c1,c2,c3=st.columns(3)
        c1.metric("Category",str(r.get("category","Unknown")))
        c2.metric("Priority",str(r.get("priority","Unknown")))
        c3.metric("Sentiment",str(r.get("sentiment","Unknown")))
        st.write("**Summary:**",r.get("summary",""))
        st.write("**Rationale:**",r.get("rationale","Not provided"))
        st.write("**Retrieved support notes:**")
        notes=retrieve_context(r["customer_message"])
        if notes:
            for note in notes: st.caption(f"• {note['topic']}: {note['text']}")
        else: st.caption("No close match found in the sample support notes.")
        edited_reply=st.text_area("Review and edit suggested reply before approval", value=r.get("draft_reply",""), height=120, key="edited_reply")
        a,b=st.columns(2)
        with a:
            if st.button("Approve & add to dashboard"):
                saved={**r,"draft_reply":edited_reply,"status":"Approved by reviewer","reviewed_at":datetime.now().strftime("%Y-%m-%d %H:%M")}
                st.session_state.results.append(saved)
                st.success("Saved to the local session dashboard. No message was sent to a customer.")
        with b:
            if st.button("Mark for escalation"):
                saved={**r,"draft_reply":edited_reply,"status":"Escalate for human follow-up","reviewed_at":datetime.now().strftime("%Y-%m-%d %H:%M")}
                st.session_state.results.append(saved)
                st.warning("Marked for human follow-up. No message was sent.")
    st.divider()
    st.subheader("Batch process CSV")
    st.caption("CSV must contain a column named customer_message. Optional ticket_id is preserved.")
    uploaded=st.file_uploader("Upload tickets CSV", type=["csv"])
    if uploaded is not None:
        try:
            batch=pd.read_csv(uploaded)
            if "customer_message" not in batch.columns:
                st.error("CSV needs a customer_message column.")
            else:
                st.dataframe(batch.head(10), use_container_width=True)
                if st.button("Analyse batch"):
                    out=[]
                    progress=st.progress(0)
                    for i,row in batch.iterrows():
                        textmsg=str(row["customer_message"])
                        try:
                            if use_ai and api_key:
                                result=live_ai(textmsg,api_key,model,retrieve_context(textmsg)); mode="Live AI"
                            else:
                                result=demo_classify(textmsg); mode="Demo rules"
                            out.append({"ticket_id":row.get("ticket_id",f"UPLOAD-{i+1}"),"customer_message":textmsg,**result,"mode":mode,"status":"Pending review"})
                        except Exception as e:
                            out.append({"ticket_id":row.get("ticket_id",f"UPLOAD-{i+1}"),"customer_message":textmsg,"category":"Error","priority":"Unknown","sentiment":"Unknown","summary":str(e),"draft_reply":"","mode":"Error","status":"Pending review"})
                        progress.progress((i+1)/max(len(batch),1))
                    st.session_state.batch_out=pd.DataFrame(out)
                if "batch_out" in st.session_state:
                    st.dataframe(st.session_state.batch_out, use_container_width=True)
                    st.download_button("Download batch analysis CSV", st.session_state.batch_out.to_csv(index=False).encode("utf-8"), "smart_support_batch_results.csv", "text/csv")
        except Exception as e: st.error(f"Could not read CSV: {e}")

with tab2:
    st.subheader("Support operations overview")
    records=st.session_state.results
    if records:
        df=pd.DataFrame(records)
        k1,k2,k3,k4=st.columns(4)
        k1.metric("Reviewed tickets",len(df))
        k2.metric("High priority",int((df["priority"].astype(str)=="High").sum()))
        k3.metric("Approved",int((df["status"]=="Approved by reviewer").sum()))
        k4.metric("Escalated",int((df["status"]=="Escalate for human follow-up").sum()))
        st.write("**Tickets by category**")
        st.bar_chart(df["category"].value_counts())
        st.write("**Tickets by priority**")
        st.bar_chart(df["priority"].value_counts())
        st.dataframe(df[["ticket_id","category","priority","sentiment","status","draft_reply"]],use_container_width=True)
        st.download_button("Export reviewed tickets",df.to_csv(index=False).encode("utf-8"),"smart_support_reviewed_tickets.csv","text/csv")
    else:
        st.info("Approve or escalate an analysed ticket to populate the dashboard. The demo sample is not counted as reviewed work.")
        st.metric("Sample tickets available",len(st.session_state.tickets))
        st.dataframe(st.session_state.tickets,use_container_width=True)

with tab3:
    st.subheader("Workflow")
    st.markdown("""
    1. **Input:** A user enters a support ticket or uploads a CSV.
    2. **Retrieve:** The app searches a small, local set of support notes for relevant context.
    3. **Classify and draft:** Live mode calls an LLM with a structured JSON prompt. Demo mode uses transparent keyword rules and is not represented as AI.
    4. **Human review:** A reviewer can edit the draft, approve it, or escalate the ticket.
    5. **Measure:** The dashboard counts reviewed items and shows category/priority distributions.

    **Safety boundaries:** No messages are sent automatically. Do not upload real customer personal data. API keys are session inputs and should never be committed to GitHub. The reference notes and demo tickets are illustrative, not company policy.
    """)
    st.subheader("Prompt-engineering choices")
    st.markdown("""
    - Fixed output fields to make results easy to validate.
    - Defined allowed category and priority labels.
    - Added explicit escalation conditions.
    - Added anti-hallucination instructions: do not claim actions happened or invent facts.
    - Added privacy instructions prohibiting passwords, one-time codes, CVVs, and full card details.
    - Included relevant retrieved notes to ground reply suggestions.
    """)
