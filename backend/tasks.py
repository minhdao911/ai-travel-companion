from enum import Enum
from collections import defaultdict
import threading
import uuid

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Task:
    def __init__(self, status, data=None, error=None):
        self.status = status
        self.data = data
        self.error = error

class TaskManager:
    def __init__(self):
        # In-memory storage for task results
        self.task_results = defaultdict(dict)
        # Lock for thread-safe operations on task_results
        self.task_lock = threading.Lock()

    def add_task(self, data=None):
        """Add a new task to the task manager"""
        task_id = str(uuid.uuid4())
        with self.task_lock:
            self.task_results[task_id] = {
                'status': TaskStatus.PENDING,
                'data': data,
                'error': None
            }
        return task_id
        
    def update_task_status(self, task_id, status, data=None, error=None):
        """Thread-safe update of task status"""
        with self.task_lock:
            if data is not None:
                self.task_results[task_id].update({
                    'status': status,
                    'data': data
                })
            elif error is not None:
                self.task_results[task_id].update({
                    'status': status,
                    'error': error
                })
            else:
                self.task_results[task_id]['status'] = status
    
    def get_task(self, task_id):
        """Thread-safe retrieval of task object"""
        with self.task_lock:
            task_data = self.task_results.get(task_id)
            if not task_data:
                return None
            return Task(
                status=task_data.get('status', TaskStatus.PENDING),
                data=task_data.get('data'),
                error=task_data.get('error')
            )
                
    def get_task_status(self, task_id):
        """Thread-safe retrieval of task status"""
        with self.task_lock:
            return self.task_results.get(task_id).get('status', TaskStatus.PENDING)
        