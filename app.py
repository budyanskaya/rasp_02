from flask import Flask, request, jsonify
from datetime import datetime
import uuid
import logging
from typing import Dict, List, Optional


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


app = Flask(__name__)


tasks_db: Dict[str, Dict] = {}
VALID_STATUSES = ['pending', 'in_progress', 'completed', 'cancelled']


class ValidationError(Exception):
    pass


def validate_task_data(data: Dict, partial: bool = False) -> Dict:
    validated = {}
    
    if not partial or 'title' in data:
        title = data.get('title', '').strip()
        if not title:
            raise ValidationError('Title is required')
        if len(title) < 3:
            raise ValidationError('Title must be at least 3 characters long')
        if len	title > 200:
            raise ValidationError('Title cannot exceed 200 characters')
        validated['title'] = title
    
    if not partial or 'status' in data:
        status = data.get('status')
        if status is not None:
            if status not in VALID_STATUSES:
                raise ValidationError(f'Status must be one of: {", ".join(VALID_STATUSES)}')
            validated['status'] = status
    
    return validated


def create_task_response(task: Dict) -> Dict:
    return {
        'id': task['id'],
        'title': task['title'],
        'status': task['status'],
        'created_at': task['created_at'],
        'updated_at': task.get('updated_at', task['created_at']),
        '_links': {
            'self': f'/api/tasks/{task["id"]}',
            'collection': '/api/tasks'
        }
    }


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'status': 404
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad Request',
        'message': str(error.description) if hasattr(error, 'description') else 'Invalid request',
        'status': 400
    }), 400


@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Internal server error: {error}')
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'status': 500
    }), 500


@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({
        'error': 'Validation Error',
        'message': str(error),
        'status': 422
    }), 422


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Task Manager API',
        'version': '1.0.0'
    })


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    status_filter = request.args.get('status')
    limit = min(int(request.args.get('limit', 100)), 1000)  # Максимум 1000
    offset = int(request.args.get('offset', 0))
    
    filtered_tasks = []
    for task in tasks_db.values():
        if status_filter and task['status'] != status_filter:
            continue
        filtered_tasks.append(create_task_response(task))

    paginated_tasks = filtered_tasks[offset:offset + limit]
    
    logger.info(f'GET /api/tasks - returned {len(paginated_tasks)} tasks')
    
    return jsonify({
        'data': paginated_tasks,
        'meta': {
            'total': len(filtered_tasks),
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < len(filtered_tasks)
        }
    }), 200


@app.route('/api/tasks', methods=['POST'])
def create_task():
    try:
        # Проверка Content-Type
        if not request.is_json:
            raise ValidationError('Content-Type must be application/json')
        
        data = request.get_json()
        if data is None:
            raise ValidationError('Invalid JSON data')
        
        validated = validate_task_data(data, partial=False)
        
        task_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        task = {
            'id': task_id,
            'title': validated['title'],
            'status': validated.get('status', 'pending'),
            'created_at': now,
            'updated_at': now
        }
        
        tasks_db[task_id] = task
        
        logger.info(f'POST /api/tasks - created task {task_id}')
        
        response = create_task_response(task)
        headers = {
            'Location': f'/api/tasks/{task_id}',
            'X-Task-ID': task_id
        }
        
        return jsonify({'data': response}), 201, headers
        
    except ValidationError as e:
        raise e
    except Exception as e:
        logger.error(f'Error creating task: {e}')
        raise ValidationError('Failed to create task')


@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    task = tasks_db.get(task_id)
    if not task:
        logger.warning(f'GET /api/tasks/{task_id} - task not found')
        return jsonify({
            'error': 'Task not found',
            'message': f'Task with id {task_id} does not exist'
        }), 404
    
    logger.info(f'GET /api/tasks/{task_id} - retrieved task')
    return jsonify({'data': create_task_response(task)}), 200


@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    task = tasks_db.get(task_id)
    if not task:
        logger.warning(f'PUT /api/tasks/{task_id} - task not found')
        return jsonify({
            'error': 'Task not found',
            'message': f'Task with id {task_id} does not exist'
        }), 404
    
    try:
        if not request.is_json:
            raise ValidationError('Content-Type must be application/json')
        
        data = request.get_json()
        if data is None:
            raise ValidationError('Invalid JSON data')
        
        validated = validate_task_data(data, partial=False)
        
        task.update({
            'title': validated['title'],
            'status': validated.get('status', task['status']),
            'updated_at': datetime.now().isoformat()
        })
        
        logger.info(f'PUT /api/tasks/{task_id} - updated task')
        
        return jsonify({'data': create_task_response(task)}), 200
        
    except ValidationError as e:
        raise e
    except Exception as e:
        logger.error(f'Error updating task {task_id}: {e}')
        raise ValidationError('Failed to update task')


@app.route('/api/tasks/<task_id>', methods=['PATCH'])
def partial_update_task(task_id):
    task = tasks_db.get(task_id)
    if not task:
        logger.warning(f'PATCH /api/tasks/{task_id} - task not found')
        return jsonify({
            'error': 'Task not found',
            'message': f'Task with id {task_id} does not exist'
        }), 404
    
    try:
        if not request.is_json:
            raise ValidationError('Content-Type must be application/json')
        
        data = request.get_json()
        if data is None:
            raise ValidationError('Invalid JSON data')
        validated = validate_task_data(data, partial=True)
        if 'title' in validated:
            task['title'] = validated['title']
        if 'status' in validated:
            task['status'] = validated['status']
        
        task['updated_at'] = datetime.now().isoformat()
        
        logger.info(f'PATCH /api/tasks/{task_id} - partially updated task')
        
        return jsonify({'data': create_task_response(task)}), 200
        
    except ValidationError as e:
        raise e
    except Exception as e:
        logger.error(f'Error updating task {task_id}: {e}')
        raise ValidationError('Failed to update task')


@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = tasks_db.get(task_id)
    if not task:
        logger.warning(f'DELETE /api/tasks/{task_id} - task not found')
        return jsonify({
            'error': 'Task not found',
            'message': f'Task with id {task_id} does not exist'
        }), 404
    
    del tasks_db[task_id]
    
    logger.info(f'DELETE /api/tasks/{task_id} - deleted task')
    
    return '', 204


@app.route('/api/tasks/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    task = tasks_db.get(task_id)
    if not task:
        return jsonify({
            'error': 'Task not found',
            'message': f'Task with id {task_id} does not exist'
        }), 404
    
    return jsonify({
        'data': {
            'id': task_id,
            'status': task['status']
        }
    }), 200


if __name__ == '__main__':
    sample_tasks = [
        {
            'id': '1',
            'title': 'Изучить Flask REST API',
            'status': 'completed',
            'created_at': '2024-01-01T10:00:00Z'
        },
        {
            'id': '2',
            'title': 'Написать документацию',
            'status': 'in_progress',
            'created_at': '2024-01-02T14:30:00Z'
        },
        {
            'id': '3',
            'title': 'Протестировать endpoints',
            'status': 'pending',
            'created_at': '2024-01-03T09:15:00Z'
        }
    ]
    
    for task in sample_tasks:
        task['updated_at'] = task['created_at']
        tasks_db[task['id']] = task
    
    logger.info(f'Initialized with {len(tasks_db)} sample tasks')
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )