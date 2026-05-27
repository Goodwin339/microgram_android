Microgram Android (Kivy)

Что внутри:
- main.py
- buildozer.spec
- SERVER_URL уже установлен: http://192.168.0.36:5000

Как собрать APK:
1) Лучше через Linux / WSL Ubuntu
2) Установить:
   sudo apt update
   sudo apt install -y python3-pip python3-venv git zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo6 cmake libffi-dev libssl-dev
   pip install --upgrade pip
   pip install buildozer cython

3) В папке проекта:
   buildozer android debug

APK появится в папке bin/

Важно:
- телефон и серверный ПК должны быть в одной сети
- server.py должен быть запущен
- в server.py должен быть host="0.0.0.0"
- порт 5000 должен быть открыт в брандмауэре
