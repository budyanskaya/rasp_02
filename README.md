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
## 1. Сначала создаем файл app.py и заполняем его
<img width="677" height="438" alt="image" src="https://github.com/user-attachments/assets/ab1735c7-f711-4b36-91de-0d5480dde1d5" />

# В первом терминале
## 1. Очищаем старые процессы
> Мы завершаем все запущенные процессы Flask-сервера, чтобы избежать конфликтов при повторном запуске.
```
sudo pkill -9 python3 2>/dev/null || true
```
## 2. Устанавливаем Flask
> На данном этапе устанавливаем Flask — основной фреймворк для реализации REST API в задании.
```
pip install flask 2>/dev/null || pip3 install flask
```
## 3. Запускаем Flask
> Командой запускаем Flask-сервер, реализующий REST API для управления задачами.
```
python3 app.py
```
<img width="1176" height="761" alt="image" src="https://github.com/user-attachments/assets/21d511cf-ac07-4687-8dd2-9d4dab19d5d8" />

# Во втором терминале
## 1. Удаляем старые конфигурации
> Удаляем все активные конфиги Nginx, чтобы избежать конфликтов перед подключением файла `taskmanager.conf`
```
sudo rm -f /etc/nginx/sites-enabled/*
```
> Затем удаляем старую или тестовую версию конфигурационного файла taskmanager.conf из папки, чтобы при развёртывании использовать актуальную версию
```
sudo rm -f /etc/nginx/sites-available/taskmanager*
```

## 2. Создаем новый конфиг
> Создаём конфигурационный файл taskmanager.conf для Nginx и настраиваем его как обратный прокси, чтобы все запросы к /api/ перенаправлялись на  Flask-сервер (порт 5001), а остальные блокировались с кодом 404. 
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
## 3. Активируем конфигурацию
> Подключаем конфигурационный файл Nginx к активным настройкам сервера.
```
sudo ln -s /etc/nginx/sites-available/taskmanager.conf /etc/nginx/sites-enabled/
```
## 4. Проверьте и перезапустите
> Командой  проверяем синтаксис конфигурационных файлов Nginx.
```
sudo nginx -t
```
> Перезапускаем систему.
```
sudo systemctl restart nginx
```
## 5. Проверьте статус
> На этом этапе команда проверяет, запущен ли Nginx и работает ли он корректно после настройки прокси.
```
sudo systemctl status nginx
```
<img width="1240" height="817" alt="image" src="https://github.com/user-attachments/assets/0f1f2ec9-3ded-4a11-af90-158f3039d5a0" />



# В третьем терминале
## ТЕСТ 1: Flask напрямую
> Команда тестирует  REST API напрямую (минуя Nginx), запрашивая список задач
curl http://localhost:5001/api/tasks
```
<img width="802" height="411" alt="image" src="https://github.com/user-attachments/assets/22788a51-07c0-4310-89ff-70a81669d322" />

## ТЕСТ 2: Через Nginx
> Команда тестирует  REST API **через Nginx**, проверяя, что обратный прокси корректно перенаправляет запросы на Flask-сервер 
```
curl http://localhost/api/tasks
```
<img width="731" height="407" alt="image" src="https://github.com/user-attachments/assets/6e113a57-41b3-4d84-85d8-6c84230aa8c8" />

## ТЕСТ 3: Создание задачи
> Команда отправляет POST-запрос через Nginx к  REST API, создавая новую задачу с заголовком «Проверить работу», это проверка реализации CRUD-операции 
```
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Проверить работу"}'
```
<img width="560" height="152" alt="image" src="https://github.com/user-attachments/assets/726c7846-2eeb-4593-9fea-1f92520b45aa" />

## ТЕСТ 4: Проверка логов
> Команда показывает последние 5 строк из лога доступа Nginx — это помогает убедиться, что запросы к  REST API действительно проходят через Nginx и обрабатываются корректно.
```
sudo tail -5 /var/log/nginx/taskmanager_access.log
```
<img width="815" height="105" alt="image" src="https://github.com/user-attachments/assets/f66e9d72-d0dd-45a2-8e44-dc972c93ee73" />

# Вывод
В ходе работы было разработано RESTful API на Flask для управления задачами с полной поддержкой CRUD-операций, валидацией данных и корректной обработкой ошибок (HTTP-коды 400, 404, 200/201/204). Модель задачи включает id, title, status и created_at. Nginx настроен как обратный прокси, перенаправляет запросы к /api/ на Flask (порт 5001), остальные  блокирует. Тестирование через curl подтвердило работоспособность API как напрямую, так и через Nginx, а анализ логов  корректность проксирования. Все методы соответствуют REST-принципам (идемпотентность PUT/DELETE, безопасность GET). 



# Ответы на вопросы
> ## HTTP коды состояния:
> 1. Успешный GET запрос - возвращает код 200 OK
> 2. Создание задачи (POST) - возвращает код 201 Created
> 3. Запрос несуществующей задачи - возвращает код 404 Not Found
> 4. Успешное удаление (DELETE) - возвращает код 204 No Content
> 5. Некорректный запрос (валидация) - возвращает код 400 Bad Request
>
> ## Идемпотентность методов:
> 1. Идемпотентные методы: GET, PUT, DELETE
> * GET: Многократные запросы возвращают одинаковый результат без изменения состояния
> * PUT: Повторные запросы с одинаковыми данными дают одинаковый результат
> * DELETE: Повторное удаление уже удаленного ресурса возвращает тот же результат (404 или 204)
> 
> 2. Неидемпотентный метод: POST
> * Каждый POST запрос создает новый ресурс, поэтому повторные запросы с теми же данными создадут дублирующие записи
>
> 3. Что произойдет при повторном DELETE?
> * При первом DELETE: вернется 204 No Content (успешное удаление)
> * При повторном DELETE: вернется 404 Not Found (ресурс уже не существует), что соответствует принципу идемпотентности
>
> ## Преимущества использования Nginx:
> 1. Балансировка нагрузки - Nginx может распределять запросы между несколькими экземплярами приложения
> 2. Кэширование - статические файлы и ответы API могут кэшироваться для повышения производительности
> 3. Безопасность - Nginx обеспечивает дополнительный уровень защиты от DDoS-атак и некорректных запросов
> 4. SSL/TLS терминация - обработка HTTPS на уровне Nginx, упрощение конфигурации Flask
> 5. Статические файлы - эффективная отдача статического контента без нагрузки на Flask
> 6. Логирование и мониторинг - централизованное логирование запросов
> 7. Обработка множества соединений - асинхронная архитектура Nginx эффективнее обрабатывает большое количество одновременных соединений
> ## Разница между доступом через Nginx и напрямую:
> 1. Через Nginx:
> * Запросы идут на порт 80 → Nginx → порт 5000 (Flask)
> * URL: http://localhost/api/tasks
> 2. Напрямую к Flask:
> * Запросы идут напрямую на порт 5001
> * URL: http://localhost:5001/api/tasks
> Nginx выступает как reverse proxy, что улучшает производительность, безопасность и масштабируемость приложения.
