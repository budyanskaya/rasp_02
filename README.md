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
### Установка и настройка Nginx
Переходим к установке Nginx
```
sudo apt update
sudo apt install nginx
```
### Создаем конфигурацию для нашего приложения
```
sudo nano /etc/nginx/sites-available/taskmanager.conf
```
Вставляем туда следующее:
```
server {
    listen 80;
    server_name localhost;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Активируем конфигурацию
```
sudo ln -s /etc/nginx/sites-available/taskmanager.conf /etc/nginx/sites-enabled/
```
Отключаем дефолтную конфигурацию
```
sudo rm /etc/nginx/sites-enabled/default
```
Проверяем конфигурацию
```
sudo nginx -t
```
Перезапускаем Nginx
```
sudo systemctl restart nginx
```
Проверяем статус
```
sudo systemctl status nginx
```

