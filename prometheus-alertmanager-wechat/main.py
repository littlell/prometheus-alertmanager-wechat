from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/alertinfo', methods=['POST'])
def hello_world():
    data = request.get_json()  # 获取 JSON 数据
    print(data)  # 打印 JSON 数据
    return "<p>Hello, World! alert</p>"