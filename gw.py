import requests
from bs4 import BeautifulSoup
import re
import base64

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

id = '壹新聞'  # 默认为'壹新聞'
# 获取指定网站的HTML内容
url = "http://99754106633f94d350db34d548d6091a.everydaytv.top/index.html"
html = get(url)

if html is None:
    print("无法获取页面内容，重定向到https://cloud.lxweb.cn/f/eKneUa/shixiaoyuan.mp4")
else:
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html, 'html.parser')
    entries = soup.find_all('a', class_='am-btn am-btn-primary am-btn-block')

    for entry in entries:
        link_text = entry.get_text()
        if id in link_text:
            href = entry.get('href')
            print(f"找到匹配的URL：{href}")
            # 获取新URL的HTML内容
            new_html = get(href)

            if new_html is None:
                print("无法获取新URL的页面内容，重定向到https://cloud.lxweb.cn/f/eKneUa/shixiaoyuan.mp4")
            else:
                # 使用正则表达式获取str变量的值
                pattern = r'http://[a-zA-Z0-9.-]+/player-[a-zA-Z0-9]+\.html'
                matches = re.findall(pattern, new_html)
                
                if matches:
                    variable_value = matches[0]
                    print(f"找到匹配的变量声明：{variable_value}")

                    new2_html = get(variable_value)
                    print(new2_html)

                    # 检索key
                    key_pattern = r'replace\(/([a-f0-9]+)'
                    key_matches = re.findall(key_pattern, new2_html)
                    if key_matches:
                        keystr = key_matches[0]
                        print(f'keystr: {keystr}')
                    else:
                        print("未找到匹配的key。")

                    # 检索解码字符串
                    decode_pattern = r'de\("([^"]+)"'
                    decode_matches = re.findall(decode_pattern, new2_html)
                    
                    if decode_matches:
                        encoded_data = decode_matches[0]
                        print(f"解码字符串:  {encoded_data}")

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
                        print(f"重定向到: {final_url}")
                        #写入到txt文件
                        with open('url.txt', 'w') as f:
                            f.write(final_url)
                        # 这里可以使用`redirect`或`print`输出最终URL
                    exit()
    print("未找到匹配的URL")
