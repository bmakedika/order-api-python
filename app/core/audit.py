import time
import csv
import os
from datetime import datetime
from functools import wraps
from fastapi import HTTPException

FILE_AUDIT = 'audit_log.csv'

def performance_audit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not os.path.exists(FILE_AUDIT):
            with open(FILE_AUDIT, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'endpoint', 'duration_ms', 'status_code'])
        start_time = time.perf_counter()
        status_code = 200

        try:
            return func(*args, **kwargs)
        except HTTPException as e:
            status_code = e.status_code
            raise e
        except Exception as e:
            status_code = 500 
            raise e 
        finally:
            duration = round((time.perf_counter() - start_time) * 1000, 2)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(FILE_AUDIT, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, func.__name__, duration, status_code])
    return wrapper