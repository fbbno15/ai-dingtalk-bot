import requests
import json
from fetch_dynamic_aibase import fetch_dynamic_aibase

webhook = "https://oapi.dingtalk.com/robot/send?access_token=你的token"

markdown_text = fetch_dynamic_aibase()

message = {
    "msgtype": "markdown",
    "markdown": {
        "title": "AI日报自动推送",
        "text": markdown_text
    }
}

headers = {"Content-Type": "application/json"}
res = requests.post(webhook, data=json.dumps(message), headers=headers)
print("发送结果:", res.text)
