from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

ACCESS_TOKEN = "EAALm8v75zusBRdTlKXjkLS6hDk1fJOR6xTZCVt7Dz6Qp1sZAk6qZCjEHJmoa7lyvXfgVIZBAeO0ckq3pbnqKgZCKkjF1ZChPaUxDlITipIjApUUWeOXxbzMRAsOMbO3H75km5hVQYLka2fmr5lxp0ZC0kkgHNizwTrDcpt3RVpWfoQkmhzk4I8OapEnpxI9yvCNZAV61ZBquvocZBsILKwQSRs8q1vM8mZBwy4B0LXv9hbZAJpPgpmZBc"

CLIENTS = {
    "jr": "act_1292464679501846",
    "cifuentes": "act_1993215707685561",
    "barca": "act_1397120998533984",
    "kenko": "act_2409090709602611",
    "palacio": "act_1197570595876991"
}

@app.route("/client-summary")
def client_summary():
    client = request.args.get("client", "").lower()

    if client not in CLIENTS:
        return jsonify({"error": "client not found"}), 404

    ad_account_id = CLIENTS[client]

    url = f"https://graph.facebook.com/v23.0/{ad_account_id}/insights"
    params = {
        "fields": "campaign_name,spend,impressions,reach,clicks,cpc,ctr",
        "level": "campaign",
        "date_preset": "last_7d",
        "access_token": ACCESS_TOKEN
    }

    response = requests.get(url, params=params)
    data = response.json()

    return jsonify({
        "client": client,
        "data": data
    })

if __name__ == "__main__":
    app.run()
