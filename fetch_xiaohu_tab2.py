import requests
from datetime import datetime, timedelta
import os
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
headers = {'User-Agent': user_agent}

base_url = 'https://www.xiaohu.ai/internal_api/spaces/1510791/posts'
post_api_base = 'https://www.xiaohu.ai/internal_api/spaces/1510791/posts/'

params = {
    'include_top_pinned_post': 'true',
    'used_on': 'cards',
    'per_page': 15,
    'topics[]': 183652,
}

def fetch_new_posts():
    now = datetime.utcnow()
    results = []
    page = 1
    while True:
        params['page'] = page
        response = requests.get(base_url, headers=headers, params=params, verify=False)
        data = response.json()
        records = data.get('records', [])
        if not records:
            break
        for record in records:
            updatetime = record['published_at']
            post_time = datetime.strptime(updatetime, '%Y-%m-%dT%H:%M:%S.%fZ')
            if post_time > now - timedelta(days=1):
                slug = record['slug']
                url = f"https://www.xiaohu.ai/c/xiaohu-ai/{slug}"
                title = record.get('title', '')
                # 标签处理（如有标签字段可补充）
                tags = record.get('topics', [])
                tag_str = ' '.join([f"#{t['name']}" for t in tags[:2]]) if tags else "#AI资讯 #产品动态"
                results.append({'url': url, 'slug': slug, 'published_at': updatetime, 'title': title, 'tags': tag_str})
        if all(datetime.strptime(r['published_at'], '%Y-%m-%dT%H:%M:%S.%fZ') <= now - timedelta(days=1) for r in records):
            break
        page += 1
    print(f"共获取到{len(results)}条24小时内的新内容。")
    return results

def fetch_post_content_by_api(slug):
    api_url = post_api_base + slug
    try:
        resp = requests.get(api_url, headers=headers, verify=False, timeout=10)
        data = resp.json()
    except Exception as e:
        print(f"抓取 {slug} 正文失败，原因：{e}")
        return ""
    # tiptap_body.body.content 是正文富文本块
    content_blocks = data.get('tiptap_body', {}).get('body', {}).get('content', [])
    lines = []
    for block in content_blocks:
        if block['type'] == 'paragraph':
            texts = []
            for item in block.get('content', []):
                txt = item.get('text', '')
                if 'marks' in item and any(m.get('type') == 'bold' for m in item['marks']):
                    txt = f"**{txt}**"
                texts.append(txt)
            lines.append(''.join(texts))
        elif block['type'] == 'bulletList':
            for item in block.get('content', []):
                if item['type'] == 'listItem':
                    for sub in item.get('content', []):
                        if sub['type'] == 'paragraph':
                            txts = []
                            for t in sub.get('content', []):
                                txt = t.get('text', '')
                                if 'marks' in t and any(m.get('type') == 'bold' for m in t['marks']):
                                    txt = f"**{txt}**"
                                txts.append(txt)
                            lines.append('· ' + ''.join(txts))
    return '\n'.join(lines)

def clean_with_gpt_azure(raw_title, raw_content, url, tags):
    api_url = 'https://api.openai.com/v1/chat/completions'
    api_key = os.getenv("OPENAI_KEY")
    Authorization = 'Bearer {0}'.format(api_key)
    headers = {'content-type': 'application/json','Authorization': Authorization}
    # 新清洗规则prompt
    prompt = f"""请将以下 AI 资讯内容清洗为标准格式，仅做结构整理，不删减内容。\n\n清洗规则如下：\n- 标题：保留原文标题，不改写\n- 提要：提炼 3 条关键要点，每条以 "·" 开头，控制在 25～40 字之间，句式简洁\n- 链接格式：[详情链接]({url})\n- 标签：保留 2 个，用 #号标注，空格分隔\n\n输出格式如下：\n## {raw_title}\n\n· {{要点1}}  \n· {{要点2}}  \n· {{要点3}}  \n[详情链接]({url})  \n{tags}\n\n原始内容如下：\n{raw_content}"""
    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    postdata = {
        'model': 'gpt-4o',
        'messages': payload['messages'],
        'temperature': 0,
        'max_tokens': 1500,
        'top_p': 1,
        'frequency_penalty': 0.5,
        'presence_penalty': 0.5
    }
    data = json.dumps(postdata)
    response = requests.post(api_url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()

def main():
    posts = fetch_new_posts()
    cleaned_md_list = []
    for post in posts:
        print(f"抓取: {post['title']}")
        raw_content = fetch_post_content_by_api(post['slug'])
        cleaned_md = clean_with_gpt_azure(post['title'], raw_content, post['url'], post['tags'])
        cleaned_md_list.append(cleaned_md)
    # 合并所有清洗后的内容
    final_md = '\n\n---\n\n'.join(cleaned_md_list)
    print(final_md)  # 你可以选择保存为文件
    # 保存为本地markdown文件
    with open('xiaohu_cleaned_posts.md', 'w', encoding='utf-8') as f:
        f.write(final_md)
    print("已保存为 xiaohu_cleaned_posts.md")

if __name__ == "__main__":
    main()

