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
<img width="482" height="411" alt="image" src="https://github.com/user-attachments/assets/028d7580-fd85-407f-8185-c1b3e683c2c6" />

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
<img width="467" height="88" alt="image" src="https://github.com/user-attachments/assets/52581d95-4e46-44c4-b22b-b4384d47d022" />

Перезапускаем Nginx
```
sudo systemctl restart nginx
```
Проверяем статус
```
sudo systemctl status nginx
```
<img width="632" height="353" alt="image" src="https://github.com/user-attachments/assets/37ddc433-fa7a-4120-afa5-fc7b97abdd8e" />

### Настройка хоста (для локального тестирования)
Для этого выполняем следующую команду
```
sudo nano /etc/hosts
```
И добавляем строку: 127.0.0.1 taskmanager.local

<img width="648" height="217" alt="image" src="https://github.com/user-attachments/assets/29911a47-1f79-43dc-acd8-093e6ba33ce2" />

### Запуск приложения через Gunicorn (production)
Установка Gunicorn
```
pip install gunicorn
```
Запуск приложения через Gunicorn
```
gunicorn -w 4 -b 127.0.0.1:5000 "app:app"
```
###  Настройка systemd службы (для автозапуска)
```
sudo nano /etc/systemd/system/taskmanager.service
```
Добавить содержимое:
```
[Unit]
Description=Task Manager Flask Application
After=network.target


[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/task-manager
Environment="PATH=/path/to/task-manager/venv/bin"
ExecStart=/path/to/task-manager/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 "app:app"


[Install]
WantedBy=multi-user.target
```
Активировать службу
```
sudo systemctl daemon-reload
sudo systemctl start taskmanager
sudo systemctl enable taskmanager
```
### Проверка
Сначала установите jq
```
sudo apt install jq
```
Проверка здоровья
```
curl -s http://localhost:5000/api/health | jq .
```
Все задачи
```
curl -s http://localhost:5000/api/tasks | jq '.data[]'
```
Создать задачу
```
curl -s -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Новая задача"}' | jq .
```
Обновить
```
curl -s -X PUT http://localhost:5000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Новое", "status": "done"}' | jq .
```
Удалить
```
curl -s -X DELETE http://localhost:5000/api/tasks/1 -w "Статус: %{http_code}\n"
```
