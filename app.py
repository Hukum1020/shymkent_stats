from flask import Flask, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

app = Flask(__name__)

SERVICE_ACCOUNT_FILE = 'credentials.json'  # замените на свой файл
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

SPREADSHEET_ID = 'ВСТАВЬ_СЮДА_ID_ТВОЕЙ_ТАБЛИЦЫ'
RANGE = 'A1:L'

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

@app.route('/stats')
def get_stats():
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE).execute()
    values = result.get('values', [])

    if not values or len(values) < 2:
        return jsonify({'total': 0, 'checkin': 0, 'today': 0})

    headers = values[0]
    rows = values[1:]

    total = len(rows)
    checkin_index = headers.index("CheckIn")
    sent_index = headers.index("sent")

    checkin_count = sum(1 for row in rows if len(row) > checkin_index and row[checkin_index].strip())
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_count = sum(1 for row in rows if len(row) > sent_index and row[sent_index].startswith(today_str))

    return jsonify({
        'total': total,
        'checkin': checkin_count,
        'today': today_count
    })

if __name__ == '__main__':
    app.run(debug=True)
