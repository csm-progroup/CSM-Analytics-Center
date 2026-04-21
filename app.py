from flask import Flask, jsonify
import requests

app = Flask(__name__)

ACCESS_TOKEN = "EAALm8v75zusBRUICJyL51VZBv7tMovNJp3u4tS5DR2eCagpYcsmUANUe1ZCefGfeHlpOrEv4OtL2VNWYyTSad2WS0zsaPz0VWV5even97bm7aMr7GBd82r0GdMgTGZB0CiTOJzZC4LZC2qxvYOUJoR8rLrgZCXtbutTRso1AF8pZBIZBof2XlwrTS0tMXZA85uZCvNDYxcPA14BErSr4Smwz7b9v3MqIikZCcZCmCaQifiZCqNi383Bx0alfQeD5ZBSN1ZAjHnzBFxMZBScwoBRkSJsV5JMdSNel"
AD_ACCOUNT_ID = "act_1292464679501846"

@app.route("/jr-summary")
def jr_summary():
    url = f"https://graph.facebook.com/v23.0/{AD_ACCOUNT_ID}/insights"
    params = {
        "fields": "campaign_name,spend,impressions,reach,clicks,cpc,ctr",
        "level": "campaign",
        "date_preset": "last_7d",
        "access_token": ACCESS_TOKEN
    }

    response = requests.get(url, params=params)
    data = response.json()
    return jsonify(data)

if __name__ == "__main__":
    app.run()
