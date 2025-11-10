from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input
from textual.containers import Container
from rich.panel import Panel
from rich.console import Console
import socket
import threading
import time
import requests
import sys
import os

console = Console()
messages = []
username = "Неизвестный пользователь"
PORT = 11746
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(("", PORT))
VERSION = "2.3 BETA"
VERSION_URL = "https://raw.githubusercontent.com/Davidka4444/DavidX/main/version.py"
SCRIPT_URL = "https://raw.githubusercontent.com/Davidka4444/DavidX/main/main.py"

class DavidX(App):
	def compose(self) -> ComposeResult:
		self.header = Header()
		self.logo = Static(Panel("""
 _______                        __        __      __                      
/       \\                      /  |      /  |    /  |                    
$$$$$$$  |  ______   __     __ $$/   ____$$ |    $$/  _______    _______ 
$$ |  $$ | /      \\ /  \\   /  |/  | /    $$ |    /  |/       \\  /       |
$$ |  $$ | $$$$$$  |$$  \\ /$$/ $$ |/$$$$$$$ |    $$ |$$$$$$$  |/$$$$$$$/ 
$$ |  $$ | /    $$ | $$  /$$/  $$ |$$ |  $$ |    $$ |$$ |  $$ |$$ |      
$$ |__$$ |/$$$$$$$ |  $$ $$/   $$ |$$ \\__$$ | __ $$ |$$ |  $$ |$$ \\_____ 
$$    $$/ $$    $$ |   $$$/    $$ |$$    $$ |/  |$$ |$$ |  $$ |$$       |
$$$$$$$/   $$$$$$$/     $/     $$/  $$$$$$$/ $$/ $$/ $$/   $$/  $$$$$$$/
"""))
		self.usernameInput = Input(placeholder="Ваш ник", type="text", max_length=16)
		self.messagesWidget = Static(Panel(""))
		self.msgInput = Input(placeholder="Введите сообщение...", type="text", max_length=256, classes="comment-important")
		self.versionWidget = Static(Panel(f"Версия: {VERSION}"))
		self.footer = Footer()

		yield self.header
		yield self.logo
		yield self.usernameInput
		yield self.messagesWidget
		yield self.msgInput
		yield self.versionWidget
		yield self.footer

	def on_mount(self) -> None:
		threading.Thread(target=self.listener_thread, daemon=True).start()

	def listener_thread(self):
		while True:
			try:
				data, addr = s.recvfrom(1024)
				received = data.decode()
				if not received.startswith("[" + username + "]"):
					messages.append(received)
					self.refresh_messages()
			except Exception as e:
				console.print(f"Ошибка получения данных: {e}")

	def refresh_messages(self):
		last_messages = "\n".join(messages[-10:])
		self.messagesWidget.update(Panel(last_messages))

	async def on_input_submitted(self, event: Input.Submitted) -> None:
		global username

		if event.input is self.msgInput:
			message_text = f"[{username}]: {event.value}"
			messages.append(message_text)
			self.refresh_messages()
			self.msgInput.value = ""
			s.sendto(message_text.encode(), ('255.255.255.255', PORT))
		elif event.input is self.usernameInput:
			username = event.value
			self.usernameInput.remove()
			joinMsg = f"[SERVER] {username} заходит"
			s.sendto(joinMsg.encode(), ('255.255.255.255', PORT))

def check_update():
    try:
        latest = requests.get(VERSION_URL, timeout=5).text.strip()
        if latest != VERSION:
            print(f"[orange bold]Доступна новая версия ({latest})! Обновляюсь... [orange bold]")
            new_code = requests.get(SCRIPT_URL, timeout=10).text
			new_code = new_code.replace('\r', '')
            with open(sys.argv[0], "w", encoding="utf-8") as f:
                f.write(new_code)
            print("[green bold]Обновление установлено. Перезапуск...[/green bold]")
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            console.print("[green bold]Это актуальная версия[/green bold]")
    except Exception as e:
        console.print("[red bold]Ошибка проверки обновлений:", e)
    time.sleep(5)

if __name__ == "__main__":
	check_update()
	DavidX().run()


