import requests
from bs4 import BeautifulSoup
import re
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import pytz
from datetime import datetime 

# 设置时区为中国/上海（北京时间）
timezone = pytz.timezone('Asia/Shanghai')

# 获取当前时间并转换为北京时间
localtime = datetime.now(timezone)  # 直接使用timezone获取当前时间
beijing_time = localtime.strftime("%Y-%m-%d %H:%M:%S")  # 格式化时间

def de(encoded_str):
    replacements = {
        '~': 'A',
        ':': 'B',
        '-': 'C',
        '@': 'D',
        '#': 'F',
        '%': 'G',
        "'": 'H',
        '&': 'J',
        '*': 'K',
        '?': 'L',
        ';': 'N',
        '!': 'S',
        '_': 'V',
        ')': 'X',
        '(': 'Z'
    }
    
    for old, new in replacements.items():
        encoded_str = encoded_str.replace(old, new)
        
    return encoded_str

def get(url, custom_headers=None, use_headers=True):
    if use_headers:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }
        if custom_headers:
            headers.update(custom_headers)
    else:
        headers = {}

    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
        return response.text
    else:
        return None

# 处理每个ID的函数
def process_id(id):
    url = "http://99754106633f94d350db34d548d6091a.everydaytv.top/index.html"
    html = get(url)

    if html is None:
        return f"无法获取页面内容，ID: {id}。"
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html, 'html.parser')
    entries = soup.find_all('a', class_='am-btn am-btn-primary am-btn-block')
    found_url = False  # 用于标记该ID是否找到了对应的URL

    for entry in entries:
        link_text = entry.get_text()
        if id in link_text:
            href = entry.get('href')
            print(f"找到匹配的URL：{href}")
            # 获取新URL的HTML内容
            new_html = get(href)

            if new_html is None:
                return f"无法获取新URL的页面内容，ID: {id}。"
            else:
                # 使用正则表达式获取str变量的值
                pattern = r'http://[a-zA-Z0-9.-]+/player-[a-zA-Z0-9]+\.html'
                matches = re.findall(pattern, new_html)

                if matches:
                    variable_value = matches[0]
                    print(f"找到匹配的变量声明：{variable_value}")

                    new2_html = get(variable_value)

                    # 检索key
                    key_pattern = r'replace\(/([a-f0-9]+)'
                    key_matches = re.findall(key_pattern, new2_html)
                    if key_matches:
                        keystr = key_matches[0]
                    else:
                        return f"未找到匹配的key，ID: {id}。"

                    # 检索解码字符串
                    decode_pattern = r'de\("([^"]+)"'
                    decode_matches = re.findall(decode_pattern, new2_html)

                    if decode_matches:
                        encoded_data = decode_matches[0]
                        encodedStr = de(encoded_data)
                        decodedStr = encodedStr.replace(keystr, 'M')

                        # Base64 解码
                        final_url = base64.b64decode(decodedStr).decode('utf-8')

                        # 提取host
                        buri = variable_value[:variable_value.index('/player-')]
                        # 检查final_url
                        if not (final_url.startswith('http://') or final_url.startswith('https://')):
                            final_url = buri + final_url

                        print(f"解码后的URL: {final_url}")
                        print(f"输出结果: {id},{final_url}")
                        
                        # 写入到txt文件


                        with open('url.txt', 'a') as f:  # 使用'a'模式追加内容
                            f.write(f"{id},{final_url}\n")

                        found_url = True
                        break  # 找到一个ID的URL后退出当前ID的循环

    if not found_url:
        return f"未找到ID \"{id}\" 的匹配URL。"
    
    return f"查询完成，ID: {id}。"

# 定义ID组
ids = ['翡翠台','HOY 78','美亞電影台','RTHK31','東森超視','東森電影','東森戲劇','東森新聞','東森洋片','東森綜合','ELTA體育1台','EYE TV 旅遊','EYE TV 戲劇','HBO HD','年代新聞','天映頻道','緯來電影','緯來日本','緯來體育','緯來戲劇','緯來育樂','緯來綜合','壹新聞','東森電影','東森洋片','中天新聞',
'三立台灣台','三立戲劇台','三立綜合台',

]  # 替换为实际需要的多个ID


with open('url.txt', 'w') as f:
    f.write(f"开始更新 {beijing_time}\n")
    
# 多线程处理
if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=2) as executor:  # 设置并发线程数
        future_to_id = {executor.submit(process_id, id): id for id in ids}
        for future in as_completed(future_to_id):
            id = future_to_id[future]
            try:
                result = future.result()
                print(result)
            except Exception as exc:
                print(f"ID {id} 生成异常: {exc}")
