"""Simple evaluation helper for the rule-based demo baseline.
Run from the project root: python evaluation/evaluate_demo.py
This script evaluates only the demo rules; it does not evaluate the live LLM.
"""
import csv
from pathlib import Path

def classify(text):
    t=text.lower()
    if any(w in t for w in ["refund","return","money back","cancel order"]): category="Refunds"
    elif any(w in t for w in ["login","log in","password","account","locked"]): category="Account access"
    elif any(w in t for w in ["delivery","shipping","arrived","tracking","late","package"]): category="Shipping"
    elif any(w in t for w in ["crash","error","bug","not working","technical","app"]): category="Technical issue"
    elif any(w in t for w in ["bill","billing","invoice","charged","payment"]): category="Billing"
    else: category="General inquiry"
    high_terms=["urgent","asap","immediately","fraud","charged twice","locked out","data breach","cannot access","cannot log in","account locked"]
    priority="High" if any(w in t for w in high_terms) else ("Medium" if any(w in t for w in ["problem","issue","delay","late","crash","crashes","wrong","failed"]) else "Low")
    return category, priority

path=Path(__file__).with_name("test_tickets.csv")
rows=list(csv.DictReader(path.open(encoding="utf-8", newline="")))
cat_ok=prio_ok=0
for r in rows:
    cat, prio=classify(r["customer_message"])
    cat_ok += cat == r["expected_category"]
    prio_ok += prio == r["expected_priority"]
    print(f'{r["ticket_id"]}: category={cat} (expected {r["expected_category"]}); priority={prio} (expected {r["expected_priority"]})')
print(f"\nCategory accuracy: {cat_ok}/{len(rows)} = {cat_ok/len(rows):.1%}")
print(f"Priority accuracy: {prio_ok}/{len(rows)} = {prio_ok/len(rows):.1%}")
print("Small illustrative dataset only; results are not evidence of production performance.")
