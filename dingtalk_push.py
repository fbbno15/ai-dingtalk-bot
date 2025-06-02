from fetch_aibase import fetch_latest_aibase_fulltext
import requests
import json

# 你的 webhook 地址（替换成你钉钉机器人的真实地址）
webhook = "https://oapi.dingtalk.com/robot/send?access_token=5cb3503b308034b54bcbf5cb6d3bff7b58cd7e95a533407d89949ad3636a50a8"

# 消息内容，包含关键词“AI日报”
message = {
    "msgtype": "markdown",
    "markdown": {
        "title": "AI日报自动推送",
        "text": """
## 🤖 AI日报自动推送（关键词触发）

**今天的内容摘要如下：**

- DeepSeek 发布 R1-0528，支持 128K 上下文
- 字节跳动推出图像 Agent“小云雀”

👉 [点击查看详情](https://top.aibase.com)
"""
    }
}

# 发出请求
headers = {"Content-Type": "application/json"}
res = requests.post(webhook, data=json.dumps(message), headers=headers)
print("🧪 抓取的内容如下：\n")
print(fetch_latest_aibase_fulltext())
print("发送结果:", res.text)
