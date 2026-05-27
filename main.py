from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from datetime import datetime, timedelta
import threading
import requests

APP_TITLE = "Microgram"
SERVER_URL = "http://192.168.0.36:5000"
REQUEST_TIMEOUT = 8
POLL_CONTACTS_SEC = 1.5
POLL_MESSAGES_SEC = 1.2

Window.softinput_mode = "below_target"

KV = r"""
#:import dp kivy.metrics.dp

<PrimaryButton@Button>:
    background_normal: ""
    background_down: ""
    background_color: (0.17, 0.50, 1.0, 1)
    color: (1, 1, 1, 1)
    bold: True
    font_size: "16sp"
    size_hint_y: None
    height: dp(48)

<SecondaryButton@Button>:
    background_normal: ""
    background_down: ""
    background_color: (0.20, 0.26, 0.32, 1)
    color: (1, 1, 1, 1)
    font_size: "15sp"
    size_hint_y: None
    height: dp(44)

<HintLabel@Label>:
    color: (0.62, 0.70, 0.78, 1)
    font_size: "13sp"

<AuthScreen>:
    name: "auth"
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: (0.09, 0.13, 0.17, 1)
            Rectangle:
                pos: self.pos
                size: self.size

        Widget:
            size_hint_y: 0.08

        Label:
            text: "Microgram"
            size_hint_y: None
            height: dp(46)
            font_size: "28sp"
            bold: True
            color: (0.95, 0.96, 0.98, 1)

        HintLabel:
            text: "Вход или создание аккаунта"
            size_hint_y: None
            height: dp(22)

        BoxLayout:
            size_hint_y: None
            height: dp(44)
            spacing: dp(8)
            SecondaryButton:
                text: "Вход"
                background_color: (0.17, 0.50, 1.0, 1) if root.mode == "login" else (0.20, 0.26, 0.32, 1)
                on_release: root.set_mode("login")
            SecondaryButton:
                text: "Регистрация"
                background_color: (0.17, 0.50, 1.0, 1) if root.mode == "register" else (0.20, 0.26, 0.32, 1)
                on_release: root.set_mode("register")

        ScrollView:
            do_scroll_x: False
            bar_width: dp(4)
            GridLayout:
                id: auth_form
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(10)
                padding: 0, dp(8)

                Label:
                    text: "Вход" if root.mode == "login" else "Создание аккаунта"
                    size_hint_y: None
                    height: dp(34)
                    text_size: self.width, None
                    halign: "left"
                    valign: "middle"
                    font_size: "22sp"
                    bold: True
                    color: (0.95, 0.96, 0.98, 1)

                Label:
                    text: "Имя"
                    size_hint_y: None
                    height: dp(20)
                    opacity: 0 if root.mode == "login" else 1
                    disabled: root.mode == "login"
                    text_size: self.width, None
                    halign: "left"
                    color: (0.78, 0.82, 0.86, 1)
                TextInput:
                    id: reg_name
                    multiline: False
                    size_hint_y: None
                    height: dp(48)
                    padding: dp(14), dp(14)
                    background_normal: ""
                    background_active: ""
                    background_color: (0.13, 0.19, 0.25, 1)
                    foreground_color: (0.95, 0.96, 0.98, 1)
                    cursor_color: (0.95, 0.96, 0.98, 1)
                    opacity: 0 if root.mode == "login" else 1
                    disabled: root.mode == "login"

                Label:
                    text: "Ник (@nick)"
                    size_hint_y: None
                    height: dp(20)
                    text_size: self.width, None
                    halign: "left"
                    color: (0.78, 0.82, 0.86, 1)
                TextInput:
                    id: nick
                    multiline: False
                    size_hint_y: None
                    height: dp(48)
                    padding: dp(14), dp(14)
                    background_normal: ""
                    background_active: ""
                    background_color: (0.13, 0.19, 0.25, 1)
                    foreground_color: (0.95, 0.96, 0.98, 1)
                    cursor_color: (0.95, 0.96, 0.98, 1)

                Label:
                    text: "Пароль"
                    size_hint_y: None
                    height: dp(20)
                    text_size: self.width, None
                    halign: "left"
                    color: (0.78, 0.82, 0.86, 1)
                TextInput:
                    id: password
                    multiline: False
                    password: True
                    size_hint_y: None
                    height: dp(48)
                    padding: dp(14), dp(14)
                    background_normal: ""
                    background_active: ""
                    background_color: (0.13, 0.19, 0.25, 1)
                    foreground_color: (0.95, 0.96, 0.98, 1)
                    cursor_color: (0.95, 0.96, 0.98, 1)

                Label:
                    text: "Повтор пароля"
                    size_hint_y: None
                    height: dp(20)
                    opacity: 0 if root.mode == "login" else 1
                    disabled: root.mode == "login"
                    text_size: self.width, None
                    halign: "left"
                    color: (0.78, 0.82, 0.86, 1)
                TextInput:
                    id: password2
                    multiline: False
                    password: True
                    size_hint_y: None
                    height: dp(48)
                    padding: dp(14), dp(14)
                    background_normal: ""
                    background_active: ""
                    background_color: (0.13, 0.19, 0.25, 1)
                    foreground_color: (0.95, 0.96, 0.98, 1)
                    cursor_color: (0.95, 0.96, 0.98, 1)
                    opacity: 0 if root.mode == "login" else 1
                    disabled: root.mode == "login"

                PrimaryButton:
                    text: "Войти" if root.mode == "login" else "Создать аккаунт"
                    on_release: root.submit()

        HintLabel:
            text: root.status_text
            size_hint_y: None
            height: dp(24)

        Widget:
            size_hint_y: 0.08

<ContactsItem>:
    size_hint_y: None
    height: dp(70)
    orientation: "horizontal"
    spacing: dp(12)
    padding: dp(12), dp(10)
    canvas.before:
        Color:
            rgba: (0.16, 0.24, 0.31, 1) if self.selected else (0.12, 0.17, 0.22, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]
    Label:
        text: root.avatar_text
        size_hint_x: None
        width: dp(44)
        color: (1, 1, 1, 1)
        bold: True
        font_size: "20sp"
        canvas.before:
            Color:
                rgba: (0.26, 0.32, 0.38, 1)
            Ellipse:
                pos: self.x, self.center_y - self.width / 2
                size: self.width, self.width
    BoxLayout:
        orientation: "vertical"
        Label:
            text: root.display_name
            text_size: self.width, None
            halign: "left"
            valign: "middle"
            color: (0.95, 0.96, 0.98, 1)
            bold: True
        Label:
            text: root.nick
            text_size: self.width, None
            halign: "left"
            valign: "middle"
            color: (0.62, 0.70, 0.78, 1)

<ChatsScreen>:
    name: "chats"
    BoxLayout:
        orientation: "vertical"
        canvas.before:
            Color:
                rgba: (0.09, 0.13, 0.17, 1)
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: dp(64)
            padding: dp(12), dp(10)
            spacing: dp(8)
            canvas.before:
                Color:
                    rgba: (0.11, 0.15, 0.20, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: "Контакты"
                color: (0.95, 0.96, 0.98, 1)
                font_size: "22sp"
                bold: True
                text_size: self.width, None
                halign: "left"
                valign: "middle"
            SecondaryButton:
                text: "Выйти"
                size_hint_x: None
                width: dp(88)
                on_release: root.logout()

        BoxLayout:
            orientation: "vertical"
            padding: dp(12)
            spacing: dp(10)

            Label:
                text: root.user_line
                size_hint_y: None
                height: dp(22)
                text_size: self.width, None
                halign: "left"
                color: (0.62, 0.70, 0.78, 1)

            BoxLayout:
                size_hint_y: None
                height: dp(46)
                spacing: dp(8)
                TextInput:
                    id: add_contact_input
                    multiline: False
                    hint_text: "@nickname"
                    padding: dp(14), dp(14)
                    background_normal: ""
                    background_active: ""
                    background_color: (0.13, 0.19, 0.25, 1)
                    foreground_color: (0.95, 0.96, 0.98, 1)
                    cursor_color: (0.95, 0.96, 0.98, 1)
                    on_text_validate: root.add_contact()
                PrimaryButton:
                    text: "+"
                    size_hint_x: None
                    width: dp(54)
                    on_release: root.add_contact()

            HintLabel:
                text: root.status_text
                size_hint_y: None
                height: dp(20)

            ScrollView:
                do_scroll_x: False
                bar_width: dp(4)
                GridLayout:
                    id: contacts_box
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(8)
                    padding: 0, dp(4)

<ChatMessageBubble>:
    size_hint_y: None
    height: self.minimum_height
    orientation: "vertical"
    padding: dp(12), dp(8)
    spacing: dp(4)
    canvas.before:
        Color:
            rgba: (0.17, 0.50, 1.0, 1) if self.is_mine else (0.13, 0.19, 0.25, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(16)]
    Label:
        text: root.text
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        halign: "left"
        valign: "top"
        color: (1, 1, 1, 1)
        font_size: "15sp"
    Label:
        text: root.time_text
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        halign: "right"
        valign: "middle"
        color: (0.86, 0.92, 1, 1) if root.is_mine else (0.67, 0.72, 0.78, 1)
        font_size: "11sp"

<DaySeparator>:
    size_hint_y: None
    height: dp(36)
    Label:
        text: root.text
        size_hint: None, None
        size: self.texture_size[0] + dp(22), dp(28)
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        color: (0.58, 0.66, 0.74, 1)
        canvas.before:
            Color:
                rgba: (0.12, 0.17, 0.22, 1)
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(14)]

<ChatScreen>:
    name: "chat"
    BoxLayout:
        orientation: "vertical"
        canvas.before:
            Color:
                rgba: (0.09, 0.13, 0.17, 1)
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: dp(64)
            padding: dp(10), dp(10)
            spacing: dp(8)
            canvas.before:
                Color:
                    rgba: (0.11, 0.15, 0.20, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size
            SecondaryButton:
                text: "←"
                size_hint_x: None
                width: dp(54)
                on_release: root.go_back()
            BoxLayout:
                orientation: "vertical"
                Label:
                    text: root.chat_title
                    text_size: self.width, None
                    halign: "left"
                    valign: "middle"
                    color: (0.95, 0.96, 0.98, 1)
                    bold: True
                    font_size: "20sp"
                Label:
                    text: root.chat_subtitle
                    text_size: self.width, None
                    halign: "left"
                    valign: "middle"
                    color: (0.62, 0.70, 0.78, 1)

        ScrollView:
            id: messages_scroll
            do_scroll_x: False
            bar_width: dp(4)
            GridLayout:
                id: messages_box
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(6)
                padding: dp(10), dp(10)

        BoxLayout:
            size_hint_y: None
            height: dp(64)
            padding: dp(10), dp(10)
            spacing: dp(8)
            canvas.before:
                Color:
                    rgba: (0.11, 0.15, 0.20, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size
            TextInput:
                id: message_input
                multiline: False
                hint_text: "Сообщение..."
                padding: dp(14), dp(14)
                background_normal: ""
                background_active: ""
                background_color: (0.13, 0.19, 0.25, 1)
                foreground_color: (0.95, 0.96, 0.98, 1)
                cursor_color: (0.95, 0.96, 0.98, 1)
                on_text_validate: root.send_message()
            PrimaryButton:
                text: "→"
                size_hint_x: None
                width: dp(60)
                on_release: root.send_message()
"""

def safe_strip(value):
    return str(value).strip() if value is not None else ""

def normalize_nick(nick: str) -> str:
    nick = safe_strip(nick)
    if not nick:
        return ""
    return nick if nick.startswith("@") else "@" + nick

def first_not_none(*values):
    for v in values:
        if v is not None:
            return v
    return None

def short_avatar_text(name: str, nick: str = ""):
    base = safe_strip(name) or safe_strip(nick).replace("@", "")
    return base[:1].upper() if base else "?"

def parse_server_datetime(value: str):
    value = safe_strip(value)
    if not value:
        return None
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            pass
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None

def format_time_only(value: str) -> str:
    dt = parse_server_datetime(value)
    return dt.strftime("%H:%M") if dt else ""

def format_day_label(value: str) -> str:
    dt = parse_server_datetime(value)
    if not dt:
        return "Сообщения"
    today = datetime.now().date()
    d = dt.date()
    if d == today:
        return "Сегодня"
    if d == today - timedelta(days=1):
        return "Вчера"
    return dt.strftime("%d.%m.%Y")

def message_day_key(value: str) -> str:
    dt = parse_server_datetime(value)
    return dt.strftime("%Y-%m-%d") if dt else "unknown"

class APIError(Exception):
    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _url(self, endpoint: str) -> str:
        return f"{self.base_url}{endpoint}"

    def _extract_payload(self, data):
        if isinstance(data, dict):
            for key in ("data", "result", "contacts", "messages", "user"):
                if key in data:
                    return data[key]
        return data

    def _parse_response(self, response):
        try:
            data = response.json()
        except Exception:
            data = {"success": response.ok, "message": response.text.strip() if response.text else f"HTTP {response.status_code}"}
        if response.ok:
            return data
        message = None
        if isinstance(data, dict):
            message = first_not_none(data.get("message"), data.get("error"), data.get("detail"))
        raise APIError(message or f"HTTP {response.status_code}", status_code=response.status_code, payload=data)

    def _post_try(self, endpoints, json_data):
        last_error = None
        for endpoint in endpoints:
            try:
                response = self.session.post(self._url(endpoint), json=json_data, timeout=REQUEST_TIMEOUT)
            except requests.RequestException as e:
                last_error = e
                continue
            if response.status_code == 404:
                last_error = APIError("Endpoint not found", status_code=404)
                continue
            return self._parse_response(response)
        if isinstance(last_error, APIError):
            raise last_error
        raise APIError(f"Ошибка сети: {last_error}" if last_error else "Не удалось выполнить запрос")

    def _get_try(self, endpoints, params=None):
        last_error = None
        for endpoint in endpoints:
            try:
                response = self.session.get(self._url(endpoint), params=params, timeout=REQUEST_TIMEOUT)
            except requests.RequestException as e:
                last_error = e
                continue
            if response.status_code == 404:
                last_error = APIError("Endpoint not found", status_code=404)
                continue
            return self._parse_response(response)
        if isinstance(last_error, APIError):
            raise last_error
        raise APIError(f"Ошибка сети: {last_error}" if last_error else "Не удалось выполнить запрос")

    def ping(self):
        return self._get_try(["/ping", "/", "/health", "/status"])

    def register(self, name, nickname, password):
        nick = normalize_nick(nickname)
        payload = {"name": safe_strip(name), "username": nick, "nickname": nick, "nick": nick, "tag": nick, "password": password}
        return self._post_try(["/register", "/signup", "/create_account", "/auth/register"], payload)

    def login(self, nickname, password):
        nick = normalize_nick(nickname)
        payload = {"username": nick, "nickname": nick, "nick": nick, "tag": nick, "password": password}
        return self._post_try(["/login", "/signin", "/auth/login"], payload)

    def get_contacts(self, current_user_id=None, current_nick=None):
        params = {
            "user_id": current_user_id, "current_user_id": current_user_id,
            "username": current_nick, "nickname": current_nick, "nick": current_nick
        }
        data = self._get_try(["/contacts", "/get_contacts", "/user/contacts"], params=params)
        payload = self._extract_payload(data)
        if isinstance(payload, dict) and "contacts" in payload:
            payload = payload["contacts"]
        return payload if isinstance(payload, list) else []

    def add_contact(self, my_user_id, my_nick, target_nick):
        target_nick = normalize_nick(target_nick)
        payload = {
            "user_id": my_user_id, "current_user_id": my_user_id,
            "username": my_nick, "nickname": my_nick, "nick": my_nick,
            "contact_nick": target_nick, "contact_username": target_nick,
            "target_nick": target_nick, "target_username": target_nick,
            "target": target_nick, "nickname_to_add": target_nick,
        }
        return self._post_try(["/add_contact", "/contacts/add", "/add_user_by_nick"], payload)

    def get_messages(self, my_user_id=None, my_nick=None, other_user_id=None, other_nick=None):
        params = {
            "user_id": my_user_id, "current_user_id": my_user_id, "my_id": my_user_id,
            "username": my_nick, "nickname": my_nick, "nick": my_nick,
            "contact_id": other_user_id, "other_user_id": other_user_id, "target_user_id": other_user_id,
            "contact_nick": other_nick, "other_nick": other_nick, "target_nick": other_nick,
        }
        data = self._get_try(["/messages", "/get_messages", "/chat/messages"], params=params)
        payload = self._extract_payload(data)
        if isinstance(payload, dict) and "messages" in payload:
            payload = payload["messages"]
        return payload if isinstance(payload, list) else []

    def send_message(self, my_user_id=None, my_nick=None, other_user_id=None, other_nick=None, text=""):
        payload = {
            "user_id": my_user_id, "current_user_id": my_user_id, "from_user_id": my_user_id, "sender_id": my_user_id,
            "username": my_nick, "nickname": my_nick, "nick": my_nick,
            "contact_id": other_user_id, "to_user_id": other_user_id, "receiver_id": other_user_id,
            "contact_nick": other_nick, "to_nick": other_nick, "target_nick": other_nick,
            "message": text, "text": text, "content": text,
        }
        return self._post_try(["/send_message", "/messages/send", "/chat/send"], payload)

class ContactsItem(BoxLayout):
    display_name = StringProperty("")
    nick = StringProperty("")
    avatar_text = StringProperty("?")
    selected = BooleanProperty(False)
    contact_data = ObjectProperty(allownone=True)

class ChatMessageBubble(BoxLayout):
    text = StringProperty("")
    time_text = StringProperty("")
    is_mine = BooleanProperty(False)

class DaySeparator(BoxLayout):
    text = StringProperty("")

class AuthScreen(Screen):
    mode = StringProperty("login")
    status_text = StringProperty("Подключение к серверу...")

    def on_pre_enter(self, *args):
        self.status_text = "Подключение к серверу..."
        self.try_ping()

    def set_mode(self, mode):
        self.mode = mode

    def try_ping(self):
        app = App.get_running_app()
        def worker():
            try:
                app.api.ping()
                Clock.schedule_once(lambda dt: setattr(self, "status_text", "Сервер доступен"), 0)
            except Exception:
                Clock.schedule_once(lambda dt: setattr(self, "status_text", "Сервер недоступен или ещё не запущен"), 0)
        threading.Thread(target=worker, daemon=True).start()

    def submit(self):
        self.do_login() if self.mode == "login" else self.do_register()

    def do_login(self):
        app = App.get_running_app()
        nickname = normalize_nick(self.ids.nick.text)
        password = self.ids.password.text
        if not nickname or nickname == "@":
            app.show_alert("Введи ник в формате @nick")
            return
        if not password:
            app.show_alert("Введи пароль")
            return
        self.status_text = "Вход..."
        def worker():
            try:
                data = app.api.login(nickname, password)
                success = first_not_none(data.get("success") if isinstance(data, dict) else None, data.get("ok") if isinstance(data, dict) else None, True)
                if not success:
                    msg = first_not_none(data.get("message") if isinstance(data, dict) else None, data.get("error") if isinstance(data, dict) else None, "Не удалось войти")
                    Clock.schedule_once(lambda dt: app.show_alert(msg), 0)
                    Clock.schedule_once(lambda dt: setattr(self, "status_text", "Ошибка входа"), 0)
                    return
                user_data = first_not_none(data.get("user"), data.get("data"), data) if isinstance(data, dict) else {}
                if not isinstance(user_data, dict):
                    user_data = {}
                user_id = first_not_none(user_data.get("id"), user_data.get("user_id"), user_data.get("uid"))
                name = first_not_none(user_data.get("name"), user_data.get("full_name"), nickname)
                nick = normalize_nick(first_not_none(user_data.get("username"), user_data.get("nickname"), user_data.get("nick"), nickname))
                def ok(_dt):
                    app.current_user = {"id": user_id, "name": name, "nick": nick}
                    self.status_text = "Успешный вход"
                    app.open_chats()
                Clock.schedule_once(ok, 0)
            except APIError as e:
                Clock.schedule_once(lambda dt: setattr(self, "status_text", "Ошибка входа"), 0)
                Clock.schedule_once(lambda dt: app.show_alert(e.message), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: setattr(self, "status_text", "Ошибка подключения"), 0)
                Clock.schedule_once(lambda dt: app.show_alert(f"Ошибка подключения:\n{e}"), 0)
        threading.Thread(target=worker, daemon=True).start()

    def do_register(self):
        app = App.get_running_app()
        name = safe_strip(self.ids.reg_name.text)
        nickname = normalize_nick(self.ids.nick.text)
        password = self.ids.password.text
        password2 = self.ids.password2.text
        if not name:
            app.show_alert("Введи имя")
            return
        if not nickname or nickname == "@":
            app.show_alert("Введи ник в формате @nick")
            return
        if not password:
            app.show_alert("Введи пароль")
            return
        if password != password2:
            app.show_alert("Пароли не совпадают")
            return
        self.status_text = "Создание аккаунта..."
        def worker():
            try:
                data = app.api.register(name, nickname, password)
                success = first_not_none(data.get("success") if isinstance(data, dict) else None, data.get("ok") if isinstance(data, dict) else None, True)
                if not success:
                    msg = first_not_none(data.get("message") if isinstance(data, dict) else None, data.get("error") if isinstance(data, dict) else None, "Не удалось создать аккаунт")
                    Clock.schedule_once(lambda dt: app.show_alert(msg), 0)
                    Clock.schedule_once(lambda dt: setattr(self, "status_text", "Ошибка регистрации"), 0)
                    return
                def ok(_dt):
                    self.status_text = "Аккаунт создан"
                    self.mode = "login"
                    self.ids.nick.text = nickname
                    self.ids.password.text = password
                    self.ids.password2.text = ""
                    app.show_alert("Аккаунт создан. Теперь войди в него.")
                Clock.schedule_once(ok, 0)
            except APIError as e:
                Clock.schedule_once(lambda dt: setattr(self, "status_text", "Ошибка регистрации"), 0)
                Clock.schedule_once(lambda dt: app.show_alert(e.message), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: setattr(self, "status_text", "Ошибка подключения"), 0)
                Clock.schedule_once(lambda dt: app.show_alert(f"Ошибка подключения:\n{e}"), 0)
        threading.Thread(target=worker, daemon=True).start()

class ChatsScreen(Screen):
    user_line = StringProperty("")
    status_text = StringProperty("")
    _poll_contacts_event = None

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        user = app.current_user or {}
        self.user_line = f"{user.get('name', 'Пользователь')}  •  {user.get('nick', '@user')}"
        self.fetch_contacts()
        self.start_polling()

    def on_leave(self, *args):
        self.stop_polling()

    def logout(self):
        app = App.get_running_app()
        app.current_user = None
        app.current_contact = None
        app.contacts_cache = []
        app.messages_cache = []
        self.ids.add_contact_input.text = ""
        self.status_text = "Выйдено из аккаунта"
        app.root.transition = SlideTransition(direction="right")
        app.root.current = "auth"

    def start_polling(self):
        if self._poll_contacts_event is None:
            self._poll_contacts_event = Clock.schedule_interval(lambda dt: self.fetch_contacts(), POLL_CONTACTS_SEC)

    def stop_polling(self):
        if self._poll_contacts_event is not None:
            self._poll_contacts_event.cancel()
            self._poll_contacts_event = None

    def normalize_contact(self, item):
        if not isinstance(item, dict):
            return None
        user_id = first_not_none(item.get("id"), item.get("user_id"), item.get("contact_id"), item.get("uid"))
        name = first_not_none(item.get("name"), item.get("full_name"), item.get("display_name"), item.get("username"), item.get("nickname"), item.get("nick"), "Без имени")
        nick = normalize_nick(first_not_none(item.get("username"), item.get("nickname"), item.get("nick"), item.get("tag"), ""))
        if not nick:
            return None
        return {"id": user_id, "name": str(name), "nick": nick}

    def render_contacts(self, contacts):
        box = self.ids.contacts_box
        box.clear_widgets()
        app = App.get_running_app()
        selected_key = app.current_contact.get("nick") if app.current_contact else None
        for contact in contacts:
            row = ContactsItem(
                display_name=contact["name"],
                nick=contact["nick"],
                avatar_text=short_avatar_text(contact["name"], contact["nick"]),
                selected=(selected_key == contact["nick"]),
                contact_data=contact,
            )
            row.bind(on_touch_down=lambda widget, touch, c=contact: self._row_touch(widget, touch, c))
            box.add_widget(row)

    def _row_touch(self, widget, touch, contact):
        if widget.collide_point(*touch.pos):
            self.open_chat(contact)
            return True
        return False

    def open_chat(self, contact):
        app = App.get_running_app()
        app.current_contact = contact
        app.root.get_screen("chat").set_contact(contact)
        app.root.transition = SlideTransition(direction="left")
        app.root.current = "chat"

    def add_contact(self):
        app = App.get_running_app()
        target_nick = normalize_nick(self.ids.add_contact_input.text)
        if not target_nick or target_nick == "@":
            return
        self.status_text = "Добавление..."
        def worker():
            try:
                app.api.add_contact(app.current_user.get("id"), app.current_user.get("nick"), target_nick)
                def ok(_dt):
                    self.ids.add_contact_input.text = ""
                    self.status_text = "Добавлено"
                    self.fetch_contacts()
                Clock.schedule_once(ok, 0)
            except APIError as e:
                Clock.schedule_once(lambda dt: setattr(self, "status_text", "Ошибка"), 0)
                Clock.schedule_once(lambda dt: app.show_alert(e.message), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: setattr(self, "status_text", "Ошибка"), 0)
                Clock.schedule_once(lambda dt: app.show_alert(f"Не удалось добавить контакт:\n{e}"), 0)
        threading.Thread(target=worker, daemon=True).start()

    def fetch_contacts(self):
        app = App.get_running_app()
        if not app.current_user:
            return
        def worker():
            try:
                raw_contacts = app.api.get_contacts(app.current_user.get("id"), app.current_user.get("nick"))
                contacts = []
                for item in raw_contacts:
                    c = self.normalize_contact(item)
                    if c:
                        contacts.append(c)
                contacts.sort(key=lambda x: (x["name"].lower(), x["nick"].lower()))
                def ok(_dt):
                    app.contacts_cache = contacts
                    self.status_text = f"Контактов: {len(contacts)}"
                    self.render_contacts(contacts)
                Clock.schedule_once(ok, 0)
            except Exception:
                Clock.schedule_once(lambda dt: setattr(self, "status_text", "Ошибка загрузки"), 0)
        threading.Thread(target=worker, daemon=True).start()

class ChatScreen(Screen):
    chat_title = StringProperty("Чат")
    chat_subtitle = StringProperty("")
    _poll_messages_event = None

    def set_contact(self, contact):
        self.chat_title = contact["name"]
        self.chat_subtitle = contact["nick"]
        App.get_running_app().messages_cache = []
        self.render_messages([])
        self.fetch_messages()
        self.start_polling()

    def on_leave(self, *args):
        self.stop_polling()

    def start_polling(self):
        if self._poll_messages_event is None:
            self._poll_messages_event = Clock.schedule_interval(lambda dt: self.fetch_messages(), POLL_MESSAGES_SEC)

    def stop_polling(self):
        if self._poll_messages_event is not None:
            self._poll_messages_event.cancel()
            self._poll_messages_event = None

    def go_back(self):
        self.stop_polling()
        app = App.get_running_app()
        app.root.get_screen("chats").fetch_contacts()
        app.root.transition = SlideTransition(direction="right")
        app.root.current = "chats"

    def normalize_message(self, item):
        app = App.get_running_app()
        if not isinstance(item, dict):
            return None
        msg_id = first_not_none(item.get("id"), item.get("message_id"), item.get("mid"))
        text = str(first_not_none(item.get("message"), item.get("text"), item.get("content"), ""))
        sender_id = first_not_none(item.get("sender_id"), item.get("from_user_id"), item.get("user_id"), item.get("author_id"))
        sender_nick = normalize_nick(first_not_none(item.get("sender_nick"), item.get("from_nick"), item.get("username"), item.get("nickname"), item.get("nick"), ""))
        receiver_id = first_not_none(item.get("receiver_id"), item.get("to_user_id"), item.get("contact_id"))
        created_at = first_not_none(item.get("created_at"), item.get("time"), item.get("timestamp"), item.get("date"), "")
        me_id = app.current_user.get("id") if app.current_user else None
        me_nick = app.current_user.get("nick") if app.current_user else None
        is_mine = str(sender_id) == str(me_id) if me_id is not None and sender_id is not None else (sender_nick == me_nick if sender_nick and me_nick else False)
        return {"id": msg_id, "text": text, "sender_id": sender_id, "sender_nick": sender_nick, "receiver_id": receiver_id, "created_at": str(created_at), "is_mine": is_mine}

    def render_messages(self, messages):
        box = self.ids.messages_box
        box.clear_widgets()
        if not messages:
            box.add_widget(Label(text="Здесь пока нет сообщений", size_hint_y=None, height=dp(60), color=(0.62, 0.70, 0.78, 1)))
            return
        prev_day = None
        for msg in messages:
            day_key = message_day_key(msg["created_at"])
            if day_key != prev_day:
                box.add_widget(DaySeparator(text=format_day_label(msg["created_at"])))
                prev_day = day_key
            bubble = ChatMessageBubble(text=msg["text"], time_text=format_time_only(msg["created_at"]), is_mine=msg["is_mine"])
            bubble.size_hint_x = None
            bubble.width = min(Window.width * 0.78, dp(340))
            outer = BoxLayout(size_hint_y=None, height=dp(10))
            bubble.bind(height=lambda instance, value, container=outer: setattr(container, "height", value + dp(2)))
            if msg["is_mine"]:
                outer.add_widget(Label())
                outer.add_widget(bubble)
            else:
                outer.add_widget(bubble)
                outer.add_widget(Label())
            box.add_widget(outer)
        Clock.schedule_once(lambda dt: self.scroll_to_bottom(), 0.05)

    def scroll_to_bottom(self):
        self.ids.messages_scroll.scroll_y = 0

    def fetch_messages(self):
        app = App.get_running_app()
        if not app.current_user or not app.current_contact:
            return
        contact = app.current_contact.copy()
        def worker():
            try:
                raw_messages = app.api.get_messages(app.current_user.get("id"), app.current_user.get("nick"), contact.get("id"), contact.get("nick"))
                messages = []
                for item in raw_messages:
                    msg = self.normalize_message(item)
                    if msg:
                        messages.append(msg)
                def ok(_dt):
                    if not app.current_contact or app.current_contact.get("nick") != contact.get("nick"):
                        return
                    app.messages_cache = messages
                    self.render_messages(messages)
                Clock.schedule_once(ok, 0)
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()

    def send_message(self):
        app = App.get_running_app()
        text = safe_strip(self.ids.message_input.text)
        if not text:
            return
        if not app.current_user or not app.current_contact:
            app.show_alert("Сначала выбери контакт")
            return
        self.ids.message_input.text = ""
        contact = app.current_contact.copy()
        def worker():
            try:
                app.api.send_message(app.current_user.get("id"), app.current_user.get("nick"), contact.get("id"), contact.get("nick"), text)
                Clock.schedule_once(lambda dt: self.fetch_messages(), 0)
            except APIError as e:
                Clock.schedule_once(lambda dt: app.show_alert(e.message), 0)
                Clock.schedule_once(lambda dt: self._restore_text(text), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: app.show_alert(f"Не удалось отправить сообщение:\n{e}"), 0)
                Clock.schedule_once(lambda dt: self._restore_text(text), 0)
        threading.Thread(target=worker, daemon=True).start()

    def _restore_text(self, text):
        self.ids.message_input.text = text

class MicrogramMobileApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = APIClient(SERVER_URL)
        self.current_user = None
        self.current_contact = None
        self.contacts_cache = []
        self.messages_cache = []

    def build(self):
        self.title = APP_TITLE
        Builder.load_string(KV)
        sm = ScreenManager()
        sm.add_widget(AuthScreen())
        sm.add_widget(ChatsScreen())
        sm.add_widget(ChatScreen())
        return sm

    def open_chats(self):
        self.root.transition = SlideTransition(direction="left")
        self.root.current = "chats"

    def show_alert(self, text):
        view = ModalView(size_hint=(0.86, None), height=dp(180), auto_dismiss=True)
        card = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
        with card.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.11, 0.15, 0.20, 1)
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(16)])
        def _update_bg(*_args):
            card._bg.pos = card.pos
            card._bg.size = card.size
        card.bind(pos=_update_bg, size=_update_bg)
        title = Label(text=APP_TITLE, size_hint_y=None, height=dp(28), bold=True, color=(1,1,1,1), font_size="18sp")
        msg = Label(text=text, color=(0.95, 0.96, 0.98, 1))
        btn = Button(text="OK", size_hint_y=None, height=dp(44), background_normal="", background_down="", background_color=(0.17, 0.50, 1.0, 1), color=(1, 1, 1, 1))
        btn.bind(on_release=lambda *_: view.dismiss())
        card.add_widget(title)
        card.add_widget(msg)
        card.add_widget(btn)
        view.add_widget(card)
        view.open()

if __name__ == "__main__":
    MicrogramMobileApp().run()
