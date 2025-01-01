import json
import requests

from flask import Flask, request

app = Flask(__name__)


@app.route('/alertinfo', methods=['POST'])
def hello_world():
    data = request.get_json()
    print(data)

    # 目标URL
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=5d14483e-7ba4-473f-b75e-0831e0464018'

    if 'alerts' in data and len(data['alerts']) > 0 and 'labels' in data['alerts'][0]:
        alertname = data['alerts'][0]['labels'].get('alertname', '未知告警')
        status = data['alerts'][0].get('status', '未知状态')
        severity = data['alerts'][0]['labels'].get('severity', '未知严重性')
        instance = data['alerts'][0]['labels'].get('instance', '未知实例')
        job = data['alerts'][0]['labels'].get('job', '未知作业')

        markdown_message = build_markdown_message(alertname, data, instance, job, severity, status)

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
        print(response.text)

        return "<p>Hello, World!</p>"
    else:
        print("提供的数据中缺少必要的键值")
        return "<p>提供的数据中缺少必要的键值</p>", 400


def build_markdown_message(alertname, data, instance, job, severity, status):
    # Markdown格式的告警信息
    markdown_message = f"""
        
        **告警名称**：{alertname}
        **告警状态**：{status}
        **告警级别**：{severity}
        **作业名称**：{job}
        **故障实例**：{instance}
        **告警时间**：{data['alerts'][0].get('startsAt', '未知时间')}
        """
    return markdown_message
