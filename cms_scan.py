import argparse
import asyncio
import aiohttp
import hashlib
import sqlite3
import time

# 解析命令行参数
parser = argparse.ArgumentParser(description="CMS Identifier Tool")
parser.add_argument('-u', type=str, help='Specify a single URL')
parser.add_argument('-r', type=str, help='Specify a file containing a list of URLs')
parser.add_argument('-ua', action='store_true', help='Enable User-Agent spoofing')
args = parser.parse_args()

# 根据命令行参数设置URLs
if args.u:
    urls = [args.u]
elif args.r:
    with open(args.r, 'r') as file:
        urls = [line.strip() for line in file]
else:
    print("No URL(s) provided. Use -u to specify a single URL or -r to specify a file containing URLs.")
    parser.print_help()
    exit()

# User-Agent伪装
user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/58.0.3029.110 Safari/537.3")

# 连接到SQLite数据库
conn = sqlite3.connect('data/cms_finger.db')
cursor = conn.cursor()

# 查询数据库，获取所需字段
try:
    cursor.execute('SELECT path, match_pattern, cms_name, options FROM cms')
    rows = cursor.fetchall()
finally:
    conn.close()

# 将数据库查询结果转换为字典
cms_patterns = {row[1]: (row[0], row[2], row[3]) for row in rows}

async def check_host_accessible(url, session):
    try:
        async with session.get(url, timeout=1) as response:
            if response.status == 200:
                return True
    except (asyncio.TimeoutError, aiohttp.ClientError):
        return False
    return False

async def process_url_async(url, session, cms_patterns, spoof_ua):
    headers = {'User-Agent': user_agent} if spoof_ua else {}
    status = {"identified": False, "duration": 0.0, "accessible": True}
    start_time = time.time()

    host_accessible = await check_host_accessible(url, session)
    if not host_accessible:
        print(f"{url} 主机不可访问。")
        status["accessible"] = False
        status["duration"] = time.time() - start_time
        return status

    for match_pattern, (path, cms_name, options) in cms_patterns.items():
        image_url = url + path

        try:
            async with session.get(image_url, headers=headers, timeout=1) as response:
                if response.status == 200:
                    content = await response.read()
                    if (options == 'keyword' and match_pattern in content.decode()) or \
                       (options == 'md5' and match_pattern == hashlib.md5(content).hexdigest()):
                        status["identified"] = True
                        status["cms_name"] = cms_name
                        break
        except (asyncio.TimeoutError, aiohttp.ClientError):
            continue
        except Exception as e:
            print(f"处理 {image_url} 时出现异常: {str(e)}")

    status["duration"] = time.time() - start_time
    if status["identified"]:
        print(f"在 {url} 发现CMS: {status['cms_name']}。用时: {status['duration']:.2f}秒")
    else:
        print(f"{url} 未识别到CMS。用时: {status['duration']:.2f}秒")
    return status

async def process_all_urls(urls, cms_patterns, spoof_ua):
    async with aiohttp.ClientSession() as session:
        tasks = [process_url_async(url, session, cms_patterns, spoof_ua) for url in urls]
        return await asyncio.gather(*tasks)

# 执行异步事件循环
loop = asyncio.get_event_loop()
loop.run_until_complete(process_all_urls(urls, cms_patterns, args.ua))
