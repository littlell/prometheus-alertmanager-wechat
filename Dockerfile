# 使用官方的 Python 3.10 Alpine 基础镜像
FROM python:3.10-alpine

# 设置工作目录
WORKDIR /app

# 使用国内源替换默认的apk源
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

# 复制当前目录中的所有文件到工作目录
COPY . /app

# 安装必要的依赖
RUN apk add --no-cache curl && \
    pip install --no-cache-dir flask requests

# 暴露端口
EXPOSE 5000

# 设置默认命令来运行应用，并绑定到所有网络接口
CMD ["flask", "run", "--host=0.0.0.0"]