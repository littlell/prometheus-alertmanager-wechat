# 使用官方的 Python 3.10 Alpine 基础镜像
FROM python:3.10-alpine

# 设置工作目录
WORKDIR /app

# 使用国内源替换默认的apk源
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

# 复制当前目录中的所有文件到工作目录
COPY . /app

# 使用国内源替换默认的pip源
ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/

# 安装必要的依赖
RUN apk add --no-cache curl && \
    pip install --no-cache-dir flask requests python-dateutil pytz gunicorn

# 暴露端口
EXPOSE 5000

# 设置默认命令来运行应用
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]