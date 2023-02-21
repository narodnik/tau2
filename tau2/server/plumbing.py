import json
from util import config_path, safe_open

def save_task(task):
    blob_idx = task["blob_idx"]
    blob_prefix = blob_idx[:2]

    with safe_open(
        f"{config_path()}/data/blob/{blob_prefix}/{blob_idx}", "w"
    ) as f:
        json.dump(task, f, indent=2)

def load_task(blob_idx):
    blob_prefix = blob_idx[:2]
    with safe_open(
        f"{config_path()}/data/blob/{blob_prefix}/{blob_idx}", "r"
    ) as f:
        return json.load(f)

def save_active(active):
    with safe_open(f"{config_path()}/data/active", "w") as f:
        json.dump(active, f, indent=2)

def load_active():
    try:
        with safe_open(f"{config_path()}/data/active", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Gives the task an ID. Either reuse next free slot or append to the end
def next_free_id(active, blob_idx):
    for i, other_idx in enumerate(active):
        if other_idx is None:
            active[i] = blob_idx
            return i
    # No free slot found so just append
    active.append(blob_idx)
    return len(active) - 1

def save_archive(month, archive):
    with safe_open(f"{config_path()}/data/archive/{month}", "w") as f:
        json.dump(archive, f, indent=2)

def load_archive(month):
    try:
        with safe_open(f"{config_path()}/data/archive/{month}", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Finds the blob's index from its active ID
def blob_idx_from_id(id):
    active = load_active()

    try:
        active[id]
    except IndexError:
        return None

    blob_idx = active[id]
    if blob_idx is None:
        return None

    return blob_idx

