import random, time
from datetime import datetime

def random_blob_idx():
    return "%030x" % random.randrange(16**30)

def datetime_to_unix(dt):
    return int(time.mktime(dt.timetuple()))
def now():
    return datetime_to_unix(datetime.now())

def unix_to_datetime(timestamp):
    return datetime.utcfromtimestamp(timestamp)

task_template = {
    "blob_idx": str,
    "assigned": list,
    "title": str,
    "desc": str,
    "tags": list,
    "project": str,
    "status": str,
    "rank": float,
    "due": int,
    "created": int,
    "events": list,
}

def _enforce_task_format(task):
    for attr, val in task.items():
        val_type = task_template[attr]
        if val is None:
            assert val_type == list or attr not in ["blob_idx", "created"]
            continue
        assert isinstance(val, val_type)

