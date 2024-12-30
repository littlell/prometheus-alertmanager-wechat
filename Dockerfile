# 使用官方的Python 3.10镜像，基于Alpine Linux
FROM python:3.10-alpine

# 设置工作目录
WORKDIR /app

# 将当前目录下的所有文件复制到工作目录中
COPY . /app

# 安装必要的Python包
RUN pip install --no-cache-dir flask requests

# 使端口5000可供外部访问
EXPOSE 5000

# 定义环境变量
ENV FLASK_APP=prometheus-alertmanager-wechat/main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# 运行Flask应用
CMD ["flask", "run"]