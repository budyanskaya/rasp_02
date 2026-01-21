from flask import Flask, jsonify, request, abort
from datetime import datetime
app = Flask(__name__)
# База данных в памяти
tasks = [
    {"id": 1, "title": "Разработать REST API", "status": "pending", 
     "created_at": "2026-01-15T14:30:00"},
    {"id": 2, "title": "Протестировать эндпоинты", "status": "done", 
     "created_at": "2026-01-16T11:20:00"}
]
next_id = 3


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Вернуть список всех задач"""
    return jsonify(tasks), 200


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Вернуть задачу по ID или 404"""
    task = next((task for task in tasks if task['id'] == task_id), None)
    if task is None:
        abort(404, description=f"Task with ID {task_id} not found")
    return jsonify(task), 200


@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Создать задачу"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        abort(400, description="Field 'title' is required")
    
    title = data.get('title', '').strip()
    if not title:
        abort(400, description="Field 'title' cannot be empty")
    
    global next_id
    new_task = {
        "id": next_id,
        "title": title,
        "status": data.get('status', 'pending'),
        "created_at": datetime.now().isoformat()
    }
    
    tasks.append(new_task)
    next_id += 1
    
    return jsonify(new_task), 201


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Обновить статус задачи"""
    data = request.get_json()
    
    if not data or 'status' not in data:
        abort(400, description="Field 'status' is required")
    
    new_status = data.get('status')
    if new_status not in ['pending', 'done']:
        abort(400, description="Status must be 'pending' or 'done'")
    
    task = next((task for task in tasks if task['id'] == task_id), None)
    if task is None:
        abort(404, description=f"Task with ID {task_id} not found")
    
    task['status'] = new_status
    return jsonify(task), 200


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Удалить задачу"""
    global tasks
    initial_length = len(tasks)
    
    tasks = [task for task in tasks if task['id'] != task_id]
    
    if len(tasks) == initial_length:
        abort(404, description=f"Task with ID {task_id} not found")
    
    return '', 204


@app.errorhandler(400)
@app.errorhandler(404)
def handle_error(error):
    return jsonify({"error": error.description}), error.code


if __name__ == '__main__':
    print("=" * 60)
    print("Flask Task Manager API")
    print("Доступен на: http://localhost:5001")
    print("Эндпоинты:")
    print("  GET    /api/tasks")
    print("  GET    /api/tasks/<id>")
    print("  POST   /api/tasks")
    print("  PUT    /api/tasks/<id>")
    print("  DELETE /api/tasks/<id>")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True)
