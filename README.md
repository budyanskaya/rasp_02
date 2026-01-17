ПОШАГОВАЯ ИНСТРУКЦИЯ ЗАПУСКА
Терминал 1: 
# Перейдите в папку с проектом
```
cd ~/Downloads/lab/vop2
```
# Очистите старые процессы
```
sudo pkill -9 python3 2>/dev/null || true
```
# Установите Flask
```
pip install flask 2>/dev/null || pip3 install flask
```
# Запустите Flask
```
python3 app.py
```

Терминал 2:
# 1. Удалите старые конфиги (на всякий, у меня без этого не работало)
```
sudo rm -f /etc/nginx/sites-enabled/*
```
```
sudo rm -f /etc/nginx/sites-available/taskmanager*
```

# 2. Создайте новый конфиг
```
sudo tee /etc/nginx/sites-available/taskmanager.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name localhost;
    
    access_log /var/log/nginx/taskmanager_access.log;
    error_log /var/log/nginx/taskmanager_error.log;
    
    location /api/ {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    
    location / {
        return 404;
    }
}
EOF
```
# 3. Активируйте конфиг
```
sudo ln -s /etc/nginx/sites-available/taskmanager.conf /etc/nginx/sites-enabled/
```
# 4. Проверьте и перезапустите
```
sudo nginx -t
```
```
sudo systemctl restart nginx
```
# 5. Проверьте статус
```
sudo systemctl status nginx
```


Терминал 3: Тестирование
# Подождите 5 секунд, чтобы всё запустилось
```
sleep 5
```

ТЕСТ 1: Flask напрямую
```
curl http://localhost:5001/api/tasks
```
ТЕСТ 2: Через Nginx
```
curl http://localhost/api/tasks
```
ТЕСТ 3: Создание задачи
```
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Проверить работу"}'
```
ТЕСТ 4: Проверка логов
```
sudo tail -5 /var/log/nginx/taskmanager_access.log
``





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
<img width="617" height="137" alt="image" src="https://github.com/user-attachments/assets/89a68e90-1a93-46ea-be78-2b48cf404a98" />

Все задачи
```
curl -s http://localhost:5000/api/tasks | jq '.data[]'
```
<img width="622" height="340" alt="image" src="https://github.com/user-attachments/assets/d01836d9-234b-44ca-bb7d-134a05c94305" />

Создать задачу
```
curl -s -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Новая задача"}' | jq .
```
<img width="622" height="292" alt="image" src="https://github.com/user-attachments/assets/841fe2a5-9cef-442e-b7fe-7901b02214e4" />

Обновить
```
curl -s -X PUT http://localhost:5000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Новое", "status": "done"}' | jq .
```
<img width="620" height="287" alt="image" src="https://github.com/user-attachments/assets/794da90e-7b39-4192-b5a6-80e9485ce427" />

Удалить
```
curl -s -X DELETE http://localhost:5000/api/tasks/1 -w "Статус: %{http_code}\n"
```
<img width="618" height="53" alt="image" src="https://github.com/user-attachments/assets/5587c6df-776b-486c-b27f-d6c7e9018eda" />

## Идемпотентность методов
### Идемпотентные методы:
* GET - всегда идемпотентен (чтение не меняет состояние)
* PUT - идемпотентен (полная замена, многократный вызов дает тот же результат)
* DELETE - идемпотентен (после первого удаления, ресурс удален, последующие вызовы также возвращают успех)
### Неидемпотентные методы:
* POST - создает новый ресурс, каждый вызов создает новый объект
* PATCH - частичное обновление, может быть неидемпотентным если логика обновления зависит от текущего состояния

## Преимущества использования Nginx
### Производительность:
* Статический контент отдается напрямую, без Flask
* Кэширование на уровне Nginx
* Gzip сжатие
* Keep-alive соединения

### Безопасность:
* Защита от DDoS (rate limiting)
* Скрытие внутренней структуры
* SSL/TLS termination
* Заголовки безопасности

### Гибкость:
* Перезапись URL
* A/B тестирование
* Географическая маршрутизация
* Различные стратегии балансировки

### Масштабируемость:
* Легко добавить новые бэкенды
* Поддержка горизонтального масштабирования
* Кэширование ответов API
