from flask import Flask, request, jsonify
from binance.client import Client
import os

app = Flask(__name__)

API_KEY = os.environ.get("BINANCE_API_KEY")
API_SECRET = os.environ.get("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    symbol = data['symbol'].replace("BINANCE:", "")
    side = data['action']
    margin_type = data.get('margin_type', 'ISOLATED')
    leverage = int(data.get('leverage', 10))
    trade_size_type = data.get('trade_size_type', 'Percent')
    trade_amount = float(data.get('trade_amount', 0.1))

    client.futures_change_leverage(symbol=symbol, leverage=leverage)

    if trade_size_type == "Percent":
        balance = float(client.futures_account_balance()[0]['balance'])
        qty = balance * trade_amount / 100
    else:
        qty = trade_amount

    if side == "BUY":
        client.futures_create_order(symbol=symbol, side="BUY", type="MARKET", quantity=qty)
    elif side == "SELL":
        client.futures_create_order(symbol=symbol, side="SELL", type="MARKET", quantity=qty)
    elif side == "EXIT_LONG":
        client.futures_create_order(symbol=symbol, side="SELL", type="MARKET", quantity=qty)
    elif side == "EXIT_SHORT":
        client.futures_create_order(symbol=symbol, side="BUY", type="MARKET", quantity=qty)

    return jsonify({"status":"success","data":data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
