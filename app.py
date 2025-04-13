import os
import json
from flask import Flask, jsonify, render_template
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime

app = Flask(__name__)

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
if not SPREADSHEET_ID:
    raise ValueError("❌ Ошибка: SPREADSHEET_ID не найдено!")

GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
if not GOOGLE_CREDENTIALS_JSON:
    raise ValueError("❌ Ошибка: GOOGLE_CREDENTIALS_JSON не найдено!")

try:
    creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n").strip()
    creds = Credentials.from_service_account_info(creds_dict)
except Exception as e:
    raise ValueError(f"❌ Ошибка подключения к Google Sheets: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stats')
def get_stats():
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='A1:L').execute()
    values = result.get('values', [])

    if not values or len(values) < 2:
        return jsonify({'total': 0, 'checkin': 0, 'today': 0})

    headers = values[0]
    rows = values[1:]

    try:
        checkin_index = headers.index("CheckIn")
        sent_index = headers.index("sent")
    except ValueError:
        return jsonify({'error': 'Required columns not found'})

    total = len(rows)
    today_str = datetime.now().strftime('%Y-%m-%d')
    checkin_count = sum(1 for row in rows if len(row) > checkin_index and row[checkin_index].strip())
    today_count = sum(1 for row in rows if len(row) > sent_index and row[sent_index].startswith(today_str))

    return jsonify({
        'total': total,
        'checkin': checkin_count,
        'today': today_count
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
