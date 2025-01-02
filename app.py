import json
import logging
import os

import requests
from dateutil import parser
from flask import Flask, request

app = Flask(__name__)
# 设置日志级别为 INFO
app.logger.setLevel(logging.INFO)


@app.route('/alertinfo', methods=['POST'])
def hello_world():
    data = request.get_json()
    app.logger.info(data)

    # 从环境变量获取目标WEBHOOK URL
    url = os.getenv('WEBHOOK_URL')

    if 'alerts' in data and len(data['alerts']) > 0 and 'labels' in data['alerts'][0]:
        alert_name = data['alerts'][0]['labels'].get('alertname', '未知告警')
        status = data['alerts'][0].get('status', '未知状态')
        severity = data['alerts'][0]['labels'].get('severity', '未知严重性')
        instance = data['alerts'][0]['labels'].get('instance', '未知实例')
        application = data['alerts'][0]['labels'].get('app', '未知应用')
        starts_at = data['alerts'][0].get('startsAt', '未知时间')
        formatted_time = parser.parse(starts_at).strftime("%Y年%m月%d日 %H时%M分%S秒")

        markdown_message = build_markdown_message(alert_name, status, severity, instance,
                                                  application,
                                                  formatted_time)
        # POST请求的数据
        send_data = {
            "msgtype": "markdown",
            "markdown": {
                "content": markdown_message
            }
        }

        # 将字典转换为JSON格式的字符串
        json_send_data = json.dumps(send_data)

        # 发送POST请求
        response = requests.post(url, headers={'Content-Type': 'application/json'},
                                 data=json_send_data)

        # 打印响应内容
        app.logger.info(response.text)

        return "<p>Hello, World!</p>"
    else:
        print("提供的数据中缺少必要的键值")
        return "<p>提供的数据中缺少必要的键值</p>", 400


def build_markdown_message(alert_name, status, severity, instance, application,
                           starts_at):
    # Markdown格式的告警信息
    markdown_message = f"""
    **告警名称**：{alert_name}
    **告警状态**：{status}
    **告警级别**：{severity}
    **实例名称**：{instance}
    **应用名称**：{application}
    **告警时间**：{starts_at}
    """
    return markdown_message
