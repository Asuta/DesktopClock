import customtkinter as ctk
import time
from datetime import datetime, timedelta
import pystray
from PIL import Image, ImageDraw
import threading
import os

class TimerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 设置窗口属性
        self.title("桌面计时器")
        self.geometry("80x30")  # 减小窗口大小
        self.attributes('-topmost', True)  # 窗口置顶
        self.overrideredirect(True)  # 移除标题栏
        
        # 设置主题和颜色
        ctk.set_appearance_mode("dark")  # 可以改为 "light" 或 "dark"
        ctk.set_default_color_theme("blue")  # 可以改为 "blue", "green", "dark-blue"
        
        # 创建主框架 - 设置背景颜色
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="#5c5c5c",  # 深灰色背景
            bg_color="transparent"
        )
        self.main_frame.pack(expand=True, fill="both")
        
        # 创建计时显示标签 - 设置文字颜色
        self.time_label = ctk.CTkLabel(
            self.main_frame,
            text="00:00:00",
            font=("Arial", 16),
            text_color="#cecece"  # 绿色文字
        )
        self.time_label.pack(pady=2)
        
        # 创建按钮框架
        self.button_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.button_frame.pack(fill="x", padx=5)
        self.button_frame.pack_forget()  # 初始隐藏按钮
        
        # 创建开始/暂停按钮 - 设置按钮颜色
        self.toggle_button = ctk.CTkButton(
            self.button_frame,
            text="开始",
            command=self.toggle_timer,
            width=35,
            height=20,
            font=("Arial", 12),
            fg_color="#1E90FF",  # 道奇蓝
            hover_color="#0066CC",  # 深蓝色
            text_color="white"
        )
        self.toggle_button.pack(side="left", padx=2)
        
        # 创建停止按钮
        self.stop_button = ctk.CTkButton(
            self.button_frame,
            text="停止",
            command=self.stop_timer,
            width=35,
            height=20,
            font=("Arial", 12),
            fg_color="#FF4500",  # 橙红色
            hover_color="#CC3700",  # 深橙色
            text_color="white"
        )
        self.stop_button.pack(side="left", padx=2)
        
        # 添加退出按钮
        self.exit_button = ctk.CTkButton(
            self.button_frame,
            text="×",
            width=20,
            height=20,
            font=("Arial", 12),
            fg_color="#DC143C",  # 猩红色
            hover_color="#B22222",  # 深红色
            text_color="white",
            command=self.hide_window
        )
        self.exit_button.pack(side="right", padx=2)
        
        # 初始化变量
        self.is_running = False
        self.is_paused = False
        self.start_time = None
        self.pause_time = None
        self.elapsed_time = timedelta()
        self.after_id = None
        self.is_visible = True
        
        # 绑定拖动事件到整个窗口
        self.bind("<B1-Motion>", self.drag_window)
        self.bind("<Button-1>", self.get_pos)
        
        # 添加鼠标悬停事件
        self.bind("<Enter>", self.show_buttons)
        self.bind("<Leave>", self.hide_buttons)

        # 保存窗口位置
        self.window_pos = None

        # 创建系统托盘
        self.setup_system_tray()
        
        # 绑定窗口关闭事件
        self.protocol('WM_DELETE_WINDOW', self.hide_window)

    def create_tray_icon(self):
        # 创建一个简单的图标
        image = Image.new('RGB', (64, 64), color='#1E90FF')
        dc = ImageDraw.Draw(image)
        dc.text((10, 10), "计时", fill='white')
        return image

    def setup_system_tray(self):
        menu = (
            pystray.MenuItem('显示/隐藏', self.toggle_window),
            pystray.MenuItem('开始/暂停', self.toggle_timer),
            pystray.MenuItem('停止', self.stop_timer),
            pystray.MenuItem('退出', self.quit_app)
        )
        
        self.icon = pystray.Icon(
            "timer",
            self.create_tray_icon(),
            "桌面计时器",
            menu
        )
        
        self.tray_thread = threading.Thread(target=self.icon.run)
        self.tray_thread.daemon = True
        self.tray_thread.start()

    def toggle_window(self, icon=None, item=None):
        if self.is_visible:
            self.hide_window()
        else:
            self.show_window()

    def show_window(self, icon=None, item=None):
        self.is_visible = True
        self.after(0, self._show_window)

    def _show_window(self):
        self.deiconify()
        self.lift()
        if self.window_pos:
            self.geometry(self.window_pos)
        self.update()

    def hide_window(self):
        self.window_pos = self.geometry()
        self.is_visible = False
        self.withdraw()

    def quit_app(self, icon=None, item=None):
        self.icon.stop()
        self.quit()

    def show_buttons(self, event):
        self.button_frame.pack(fill="x", padx=5, pady=2)
        self.geometry("120x65")  # 扩大窗口以显示按钮

    def hide_buttons(self, event):
        # 检查鼠标是否真的离开了窗口区域
        mouse_x = self.winfo_pointerx() - self.winfo_rootx()
        mouse_y = self.winfo_pointery() - self.winfo_rooty()
        if not (0 <= mouse_x <= self.winfo_width() and 0 <= mouse_y <= self.winfo_height()):
            self.button_frame.pack_forget()
            self.geometry("80x30")  # 恢复原始大小

    def get_pos(self, event):
        self.x = event.x
        self.y = event.y

    def drag_window(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def toggle_timer(self):
        if not self.is_running:
            # 开始计时
            if not self.is_paused:
                self.start_time = datetime.now()
                self.elapsed_time = timedelta()
            else:
                # 从暂停中恢复
                self.start_time = datetime.now() - self.elapsed_time
            self.is_running = True
            self.is_paused = False
            self.toggle_button.configure(text="暂停")
            self.update_timer()
        else:
            # 暂停计时
            self.is_running = False
            self.is_paused = True
            self.toggle_button.configure(text="继续")
            if self.after_id:
                self.after_cancel(self.after_id)
            self.elapsed_time = datetime.now() - self.start_time

    def stop_timer(self):
        # 停止计时
        self.is_running = False
        self.is_paused = False
        self.toggle_button.configure(text="开始")
        if self.after_id:
            self.after_cancel(self.after_id)
        self.elapsed_time = timedelta()
        self.time_label.configure(text="00:00:00")

    def update_timer(self):
        if self.is_running:
            self.elapsed_time = datetime.now() - self.start_time
            # 移除微秒
            display_time = timedelta(seconds=int(self.elapsed_time.total_seconds()))
            self.time_label.configure(text=str(display_time))
            self.after_id = self.after(1000, self.update_timer)

if __name__ == "__main__":
    app = TimerApp()
    app.mainloop() 