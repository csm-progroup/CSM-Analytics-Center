from flask import Flask, jsonify, request
import requests
import os
import json

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

CLIENTS = {
    "jr": "act_1292464679501846",
    "cifuentes": "act_1993215707685561",
    "barca": "act_1397120998533984",
    "kenko": "act_2409090709602611",
    "palacio": "act_1197570595876991"
}

GRAPH_VERSION = "v25.0"


def meta_get(url, params):
    response = requests.get(url, params=params, timeout=30)
    return response.json()


@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "service": "CSM Analytics API",
        "endpoints": [
            "/client-summary?client=jr&period=last_7d",
            "/client-summary?client=jr&since=2026-01-01&until=2026-04-21",
            "/client-summary?client=jr&campaign_name=Whatsapp",
            "/client-summary?client=jr&campaign_name=Whatsapp&since=2026-01-01&until=2026-04-21",
            "/client-billing?client=barca"
        ]
    })


@app.route("/client-summary")
def client_summary():
    client = request.args.get("client", "").strip().lower()
    period = request.args.get("period")
    since = request.args.get("since")
    until = request.args.get("until")
    campaign_name = request.args.get("campaign_name")

    if not ACCESS_TOKEN:
        return jsonify({"error": "ACCESS_TOKEN not configured"}), 500

    if client not in CLIENTS:
        return jsonify({"error": "client not found"}), 404

    ad_account_id = CLIENTS[client]

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{ad_account_id}/insights"
    params = {
        "fields": "campaign_name,spend,impressions,reach,clicks,cpc,ctr,date_start,date_stop",
        "level": "campaign",
        "access_token": ACCESS_TOKEN
    }

    if since and until:
        params["time_range"] = json.dumps({
            "since": since,
            "until": until
        })
    else:
        params["date_preset"] = period or "last_7d"

    data = meta_get(url, params)

    if "error" in data:
        return jsonify(data), 400

    rows = data.get("data", [])

    if campaign_name:
        campaign_name_lower = campaign_name.strip().lower()
        rows = [
            row for row in rows
            if row.get("campaign_name", "").strip().lower() == campaign_name_lower
        ]

    return jsonify({
        "client": client,
        "filters": {
            "period": period,
            "since": since,
            "until": until,
            "campaign_name": campaign_name
        },
        "data": rows
    })


@app.route("/client-billing")
def client_billing():
    client = request.args.get("client", "").strip().lower()

    if not ACCESS_TOKEN:
        return jsonify({"error": "ACCESS_TOKEN not configured"}), 500

    if client not in CLIENTS:
        return jsonify({"error": "client not found"}), 404

    ad_account_id = CLIENTS[client]

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{ad_account_id}"
    params = {
        "fields": "name,account_status,amount_spent,spend_cap,balance",
        "access_token": ACCESS_TOKEN
    }

    data = meta_get(url, params)

    if "error" in data:
        return jsonify(data), 400

    amount_spent = int(data.get("amount_spent") or 0)
    spend_cap = int(data.get("spend_cap") or 0)
    balance = int(data.get("balance") or 0)

    remaining_budget = None
    if spend_cap > 0:
        remaining_budget = spend_cap - amount_spent

    account_status_map = {
        1: "ACTIVE",
        2: "DISABLED",
        3: "UNSETTLED",
        7: "PENDING_RISK_REVIEW",
        8: "PENDING_SETTLEMENT",
        9: "IN_GRACE_PERIOD",
        100: "PENDING_CLOSURE",
        101: "CLOSED",
        201: "ANY_ACTIVE",
        202: "ANY_CLOSED"
    }

    return jsonify({
        "client": client,
        "billing": {
            "name": data.get("name"),
            "account_status_code": data.get("account_status"),
            "account_status_label": account_status_map.get(data.get("account_status"), "UNKNOWN"),
            "amount_spent": amount_spent,
            "spend_cap": spend_cap,
            "balance_due": balance,
            "remaining_budget": remaining_budget
        }
    })


if __name__ == "__main__":
    app.run()
