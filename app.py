import json
import logging
import os

import pytz
import requests
from dateutil import parser
from flask import Flask, request

app = Flask(__name__)
# 设置日志级别为 INFO
app.logger.setLevel(logging.INFO)

WEBHOOK_URL = os.getenv('WEBHOOK_URL')

STATUS_LABELS = {
    'firing': '告警中',
    'resolved': '已恢复',
}

EXTRA_LABEL_KEYS = ('uri', 'method', 'status', 'pod', 'namespace', 'downstream')


@app.route('/healthz')
def healthz():
    return {'status': 'ok'}, 200


@app.route('/alert', methods=['POST'])
def alert_info():
    data = request.get_json()
    app.logger.info("Received alert JSON: %s", data)

    if not validate_alert_data(data):
        app.logger.error("Invalid alert data received: %s", data)
        return "<p>提供的数据中缺少必要的键值</p>", 400

    for alert in data['alerts']:
        send_alert(alert)

    return "所有告警已处理", 200

def send_alert(alert):
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
    labels = alert.get('labels', {})
    annotations = alert.get('annotations', {})
    alert_details = {
        'alert_name': labels.get('alertname', '未知告警'),
        'status': alert.get('status', '未知状态'),
        'severity': labels.get('severity', '未知严重性'),
        'module': labels.get('module', '未知业务'),
        'instance': labels.get('instance', '未知实例'),
        'application': labels.get('app', '未知应用'),
        'starts_at': format_time(alert.get('startsAt', '')),
        'ends_at': format_time(alert.get('endsAt', '')),
        'summary': annotations.get('summary', ''),
        'description': annotations.get('description', ''),
        'extra_labels': format_labels(labels),
    }
    return alert_details


def format_time(time_str):
    if not time_str:
        return ''
    try:
        # 解析时间字符串并将其转换为 UTC 时区
        utc_time = parser.parse(time_str).astimezone(pytz.utc)
        if utc_time.year <= 1:
            return ''
        # 将时间转换为 UTC+8 时区
        local_time = utc_time.astimezone(pytz.timezone('Asia/Shanghai'))
        # 格式化时间字符串
        formatted_time = local_time.strftime("%m月%d日 %H时%M分%S秒")
    except Exception as e:
        app.logger.error("Error parsing time: %s", e)
        formatted_time = '未知时间'
    return formatted_time


def format_status(status):
    return STATUS_LABELS.get(status, status)


def status_color(status, severity):
    if status == 'resolved':
        return 'info'
    return 'warning' if severity == '严重' else 'comment'


def format_labels(labels):
    return ' | '.join(
        f'{key}={labels[key]}'
        for key in EXTRA_LABEL_KEYS
        if labels.get(key)
    )


def build_markdown_message(alert_name, status, severity, module, instance, application,
                           starts_at, ends_at='', summary='', description='', extra_labels=''):
    # Markdown格式的告警信息
    lines = [
        f'## <font color="{status_color(status, severity)}">【{format_status(status)}】{alert_name}</font>',
        '',
        f'**级别**：{severity}　**模块**：{module}',
        f'**应用**：{application}',
        f'**实例**：{instance}',
    ]
    if summary:
        lines.append(f'**摘要**：{summary}')
    if description:
        lines.append(f'**详情**：{description}')
    if starts_at:
        lines.append(f'**触发时间**：{starts_at}')
    if status == 'resolved' and ends_at:
        lines.append(f'**恢复时间**：{ends_at}')
    if extra_labels:
        lines.append(f'**关键标签**：{extra_labels}')
    return '\n'.join(lines) + '\n'


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
