# Практическое задание №2. Проектирование RESTful API
## Разработайте REST API на Flask для управления задачами (Task Manager).
### Требуется реализовать:
* Базовые CRUD операции для задач (GET, POST, PUT, DELETE)
* Модель Task: id, title, status, created_at
* Валидацию входных данных и обработку ошибок
* Конфигурацию Nginx в качестве обратного прокси
### Проанализировать:
* HTTP коды состояния для различных сценариев
* Идемпотентность методов
* Преимущества использования Nginx
### Формат сдачи: app.py, curl_commands.txt, taskmanager.conf
## Ход работы
### Создаем файл app.py

### Установка зависимостей
Создаем виртуальное окружение следующими командами
```
python3 -m venv venv
source venv/bin/activate
```
Далее переходим к установке Flask и зависимостей
```
pip install flask
pip install gunicorn
pip install python-dotenv
```
