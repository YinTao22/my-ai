import tkinter as tk
from tkinter import scrolledtext
import requests
from rich.console import Console
import threading

# 配置信息
API_URL = "api接口"
API_KEY = "你的key"
model = "模型"

console = Console()

class ChatUI:
    def __init__(self, root):
        self.root = root
        self.root.title("lzx,wxhn")
        self.root.geometry("800x600")

        # 创建聊天区域
        self.chat_frame = tk.Frame(root)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建滚动文本框显示聊天内容
        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, state='disabled')
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # 创建输入区域
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(fill=tk.X, padx=10, pady=10)

        # 创建输入框
        self.user_input = tk.Entry(self.input_frame, font=("Arial", 12))
        self.user_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # 创建发送按钮
        self.send_button = tk.Button(self.input_frame, text="发送", font=("Arial", 12), command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

        # 绑定回车键发送消息
        self.user_input.bind("<Return>", lambda event: self.send_message())

        # 初始化消息列表
        self.messages = []

    def send_message(self):
        user_input = self.user_input.get().strip()
        if not user_input:
            return

        # 清空输入框
        self.user_input.delete(0, tk.END)

        # 添加用户消息到消息列表
        self.messages.append({"role": "user", "content": user_input})

        # 显示用户消息
        self.display_message("用户:", user_input)

        # 显示思考中...
        self.display_message("AI:", "思考中...")

        # 构造提示语，要求AI用幽默风趣的方式回答
        prompt = f"请用幽默风趣的方式回答这句话：{user_input}"

        # 使用线程处理 API 请求
        threading.Thread(target=self.handle_api_request, args=(prompt,), daemon=True).start()

    def handle_api_request(self, prompt):
        # 发送消息到API并获取回复
        response = self.chat_completion(prompt)

        if response:
            # 更新AI的消息
            self.messages.append({"role": "assistant", "content": response})

            # 更新显示AI的回复
            self.root.after(0, lambda: self.update_ai_response(response))
        else:
            # 如果 API 请求失败，显示错误信息
            self.root.after(0, lambda: self.update_ai_response("哎呀，我好像有点小故障，稍后再试试吧！"))

    def chat_completion(self, prompt):
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1024,
            "response_format": {"type": "text"}
        }

        try:
            response = requests.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            console.print(f"[bold red]API请求失败: {str(e)}[/]")
            return None

    def display_message(self, sender, message):
        # 启用文本框以进行编辑
        self.chat_display.config(state='normal')

        # 添加消息到聊天历史
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")

        # 禁用文本框以防止用户编辑
        self.chat_display.config(state='disabled')

        # 滚动到底部
        self.chat_display.yview(tk.END)

    def update_ai_response(self, response):
        # 启用文本框以进行编辑
        self.chat_display.config(state='normal')

        # 获取当前文本内容
        current_text = self.chat_display.get("1.0", tk.END)

        # 移除最后一行的"思考中..."
        lines = current_text.split('\n')
        if len(lines) > 2 and "思考中..." in lines[-3]:
            lines = lines[:-3]

        # 添加新的AI回复
        lines.append(f"AI: {response}\n\n")

        # 更新文本框内容
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.insert(tk.END, '\n'.join(lines))

        # 禁用文本框以防止用户编辑
        self.chat_display.config(state='disabled')

        # 滚动到底部
        self.chat_display.yview(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatUI(root)
    root.mainloop()