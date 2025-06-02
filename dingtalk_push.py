import requests
import json
from fetch_aibase import fetch_latest_aibase_fulltext

# ✅ 你的钉钉机器人 webhook
webhook = "https://oapi.dingtalk.com/robot/send?access_token=5cb3503b308034b54bcbf5cb6d3bff7b58cd7e95a533407d89949ad3636a50a8"

# ✅ 抓取最新日报正文内容
markdown_text = fetch_latest_aibase_fulltext()

# ✅ 组装钉钉 markdown 消息
message = {
    "msgtype": "markdown",
    "markdown": {
        "title": "AI日报自动推送",
        "text": markdown_text
    }
}

# ✅ 发送消息
headers = {"Content-Type": "application/json"}
res = requests.post(webhook, data=json.dumps(message), headers=headers)
print("发送结果:", res.text)
