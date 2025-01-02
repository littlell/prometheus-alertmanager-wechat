import json
import logging
import os
import textwrap

import requests
from dateutil import parser
from flask import Flask, request

app = Flask(__name__)
# 设置日志级别为 INFO
app.logger.setLevel(logging.INFO)

WEBHOOK_URL = os.getenv('WEBHOOK_URL')


@app.route('/alert', methods=['POST'])
def alert_info():
    data = request.get_json()
    app.logger.info("Received alert JSON: %s", data)

    if not validate_alert_data(data):
        app.logger.error("Invalid alert data received: %s", data)
        return "<p>提供的数据中缺少必要的键值</p>", 400

    alert = data['alerts'][0]
    alert_details = extract_alert_details(alert)
    markdown_message = build_markdown_message(**alert_details)

    if not WEBHOOK_URL:
        app.logger.critical("WEBHOOK_URL environment variable is not set.")
        return "<p>WEBHOOK_URL is required but not provided.</p>", 500

    response = send_alert_to_webhook(markdown_message)

    app.logger.info("Response from webhook: %s", response.text)
    return "<p>Hello, World!</p>"


def validate_alert_data(data):
    if 'alerts' in data and len(data['alerts']) > 0 and 'labels' in data['alerts'][0]:
        return True
    return False


def extract_alert_details(alert):
    alert_details = {
        'alert_name': alert['labels'].get('alertname', '未知告警'),
        'status': alert.get('status', '未知状态'),
        'severity': alert['labels'].get('severity', '未知严重性'),
        'instance': alert['labels'].get('instance', '未知实例'),
        'application': alert['labels'].get('app', '未知应用'),
        'starts_at': format_time(alert.get('startsAt', '未知时间'))
    }
    return alert_details


def format_time(time_str):
    try:
        formatted_time = parser.parse(time_str).strftime("%Y年%m月%d日 %H时%M分%S秒")
    except Exception as e:
        app.logger.error("Error parsing time: %s", e)
        formatted_time = '未知时间'
    return formatted_time


def build_markdown_message(alert_name, status, severity, instance, application, starts_at):
    # Markdown格式的告警信息
    markdown_message = textwrap.dedent(f"""
    **告警名称**：{alert_name}
    **告警状态**：{status}
    **告警级别**：{severity}
    **实例名称**：{instance}
    **应用名称**：{application}
    **告警时间**：{starts_at}
    """)
    return markdown_message


def send_alert_to_webhook(message):
    send_data = {
        "msgtype": "markdown",
        "markdown": {
            "content": message
        }
    }
    json_send_data = json.dumps(send_data)
    response = requests.post(WEBHOOK_URL, headers={'Content-Type': 'application/json'},
                             data=json_send_data)
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
