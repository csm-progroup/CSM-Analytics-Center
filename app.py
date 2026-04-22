from flask import Flask, jsonify, request
import requests
import os

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


@app.route("/client-summary")
def client_summary():
    client = request.args.get("client", "").lower()
    period = request.args.get("period")          # today, yesterday, last_7d, last_30d, this_month, last_month, maximum
    since = request.args.get("since")            # YYYY-MM-DD
    until = request.args.get("until")            # YYYY-MM-DD
    campaign_name = request.args.get("campaign_name")  # opcional

    if client not in CLIENTS:
        return jsonify({"error": "client not found"}), 404

    ad_account_id = CLIENTS[client]

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{ad_account_id}/insights"
    params = {
        "fields": "campaign_name,spend,impressions,reach,clicks,cpc,ctr",
        "level": "campaign",
        "access_token": ACCESS_TOKEN
    }

    if since and until:
        params["time_range"] = {"since": since, "until": until}
    else:
        params["date_preset"] = period or "last_7d"

    response = requests.get(url, params=params, timeout=30)
    data = response.json()

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
    client = request.args.get("client", "").lower()

    if client not in CLIENTS:
        return jsonify({"error": "client not found"}), 404

    ad_account_id = CLIENTS[client]

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{ad_account_id}"
    params = {
        "fields": "name,account_status,amount_spent,spend_cap,balance",
        "access_token": ACCESS_TOKEN
    }

    response = requests.get(url, params=params, timeout=30)
    data = response.json()

    if "error" in data:
        return jsonify(data), 400

    amount_spent = data.get("amount_spent")
    spend_cap = data.get("spend_cap")
    balance = data.get("balance")

    remaining_budget = None
    if spend_cap not in (None, "", "0") and amount_spent not in (None, ""):
        try:
            remaining_budget = int(spend_cap) - int(amount_spent)
        except Exception:
            remaining_budget = None

    return jsonify({
        "client": client,
        "billing": {
            "name": data.get("name"),
            "account_status": data.get("account_status"),
            "amount_spent": amount_spent,
            "spend_cap": spend_cap,
            "balance": balance,
            "remaining_budget": remaining_budget
        }
    })


if __name__ == "__main__":
    app.run()
