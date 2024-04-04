import asyncio
import aiohttp
import hashlib
import sqlite3
import tkinter as tk
from tkinter import scrolledtext, filedialog,simpledialog, ttk
from threading import Thread

class CMSIdentifierApp:
    def __init__(self, master):
        self.master = master
        self.master.title("CMS Identifier")
        self.create_widgets()

        self.urls = []  # 初始化空的URL列表
        self.cms_patterns = {}  # 初始化空的CMS模式字典
        self.load_cms_patterns()  # 加载数据库中的CMS模式

    def create_widgets(self):
        # 使用Frame并设置padding来组织布局
        self.main_frame = ttk.Frame(self.master, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建滚动文本框用于输出结果
        self.text_area = scrolledtext.ScrolledText(self.main_frame, height=20)
        self.text_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)

        # 按钮布局
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        # 按钮让用户添加单个URL
        self.add_button = ttk.Button(self.button_frame, text="Add URL", command=self.add_url)
        self.add_button.pack(side=tk.LEFT, padx=5)

        # 按钮让用户选择包含URLs的文件
        self.file_button = ttk.Button(self.button_frame, text="Select URL File", command=self.select_file)
        self.file_button.pack(side=tk.LEFT, padx=5)

        # 开始按钮触发处理过程
        self.start_button = ttk.Button(self.button_frame, text="Start", command=self.start_process)
        self.start_button.pack(side=tk.LEFT, padx=5)

    def add_url(self):
        url = simpledialog.askstring("Input", "Enter URL:", parent=self.master)
        if url:
            self.urls.append(url)
            self.text_area.insert(tk.END, f"Added URL: {url}\n")

    def select_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            with open(filepath, 'r') as file:
                self.urls.extend([line.strip() for line in file])
            self.text_area.insert(tk.END, f"Loaded URLs from {filepath}\n")

    def start_process(self):
        self.start_button.config(state=tk.DISABLED)
        self.add_button.config(state=tk.DISABLED)
        self.file_button.config(state=tk.DISABLED)
        thread = Thread(target=self.run_async_loop)
        thread.start()

    def run_async_loop(self):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            new_loop.run_until_complete(self.process_all_urls())
        finally:
            self.start_button.config(state=tk.NORMAL)
            self.add_button.config(state=tk.NORMAL)
            self.file_button.config(state=tk.NORMAL)
            new_loop.close()

    async def process_all_urls(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.check_cms_for_url(session, url) for url in self.urls]
            results = await asyncio.gather(*tasks)
            for result in results:
                self.text_area.insert(tk.END, f"{result}\n")

    async def check_cms_for_url(self, session, url):
        for match_pattern, (path, cms_name, options) in self.cms_patterns.items():
            image_url = url + path
            try:
                async with session.get(image_url, timeout=1) as response:
                    if response.status == 200:
                        content = await response.read()
                        if (options == 'keyword' and match_pattern in content.decode()) or \
                           (options == 'md5' and match_pattern == hashlib.md5(content).hexdigest()):
                            return f"在 {url} 发现CMS: {cms_name}"
            except Exception as e:
                return f"{url}: 主机不可达，检查网站是否正常运行 {e}"
        return f"{url}:网站疑似不存在CMS框架 "

    def load_cms_patterns(self):
        conn = sqlite3.connect('../data/cms_finger.db')
        cursor = conn.cursor()
        cursor.execute('SELECT path, match_pattern, cms_name, options FROM cms')
        rows = cursor.fetchall()
        self.cms_patterns = {row[1]: (row[0], row[2], row[3]) for row in rows}
        cursor.close()
        conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = CMSIdentifierApp(root)
    root.mainloop()