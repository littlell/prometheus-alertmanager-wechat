# Prometheus Alertmanager Wechat

## 简介

这是一个基于 Flask 的简单 Web 服务，用于接收 Alert Manager 的告警信息，并将其以 Markdown 格式转发到指定的
Webhook URL，实现告警通知与企业微信群的集成。效果如下：

![效果演示](demo.png)

## 使用

### 本地运行

1. 声明环境变量：
    ```sh
    export WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={your-own-key}"
    ```

2. 运行程序：
    ```sh
    flask run --debug
    ```

3. 测试：
    ```sh
    curl -X POST -H "Content-Type: application/json" -d @data.json http://localhost:5000/alertinfo
    ```

### 容器化部署

1. 构建镜像：
    ```sh
    docker build -t prometheus-alertmanager-wechat:v1.0 .
    ```

2. 运行 Docker 容器：
    ```sh
    docker run -e "WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={your-own-key}" prometheus-alertmanager-wechat:v1.0
    ```

3. 在 Kubernetes 上运行：

   创建一个名为 `deployment.yaml` 的文件，内容如下：

    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: monitor-alert-wx-adapter
      namespace: monitor
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: monitor-alert-wx-adapter
      template:
        metadata:
          labels:
            app: monitor-alert-wx-adapter
        spec:
          containers:
            - name: monitor-alert-wx-adapter
              image: prometheus-alertmanager-wechat:v1.0
              imagePullPolicy: Always
              ports:
                - name: http
                  containerPort: 5000
              env:
                - name: WEBHOOK_URL
                  value: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={your-own-key}"
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: monitor-alert-wx-adapter
      namespace: monitor
    spec:
      selector:
        app: monitor-alert-wx-adapter
      ports:
        - name: http
          port: 80
          targetPort: 5000
    ```

   应用配置：
    ```sh
    kubectl apply -f deployment.yaml
    ```

4. 与 Alert Manager 集成：

   在 Alert Manager 配置文件中添加以下配置：

    ```yaml
    route:
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 1m
      routes:
        - receiver: 'wechat'
          group_by: ["project"]

    receivers:
      - name: 'wechat'
        webhook_configs:
          - url: 'http://monitor-alert-wx-adapter/alert'
            send_resolved: true
    ```