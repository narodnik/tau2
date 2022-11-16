import json, sys

import lib, plumbing

class Error:

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

async def get_info():
    #return Error(-110, "oopsie")
    return "Hello World"

async def add_task(task):
    plumbing.save_task(task)

    active = plumbing.load_active()
    id = plumbing.next_free_id(active, task["blob_idx"])
    plumbing.save_active(active)
    return id

async def fetch_active_tasks():
    tasks = []
    active = plumbing.load_active()
    for blob_idx in active:
        if blob_idx is None:
            task.append(None)
            continue

        task = plumbing.load_task(blob_idx)
        tasks.append(task)
    return tasks

async def fetch_task(id):
    active = plumbing.load_active()
    assert id < len(active) and active[id] != None
    blob_idx = active[id]
    task = plumbing.load_task(blob_idx)
    return task

async def modify_task(who, id, changes):
    active = plumbing.load_active()
    assert id < len(active) and active[id] != None
    blob_idx = active[id]
    task = plumbing.load_task(blob_idx)

    for cmd, attr, val in changes:
        if cmd == "set":
            assert attr in ["title", "desc", "project", "due", "rank"]
            task[attr] = val
        elif cmd == "append":
            templ = lib.util.task_template
            assert templ[attr] == list
            task[attr].append(val)
        elif cmd == "remove":
            templ = lib.util.task_template
            assert templ[attr] == list
            try:
                task[attr].remove(val)
            except ValueError:
                print(f"warning: command remove {val} not in {attr}",
                      file=sys.stderr)
        else:
            print(f"warning: unhandled command ({cmd}, {attr}, {val})",
                  file=sys.stderr)
            continue

        task["events"].append([cmd, lib.util.now(), who, attr, val])

    print("Modified task:")
    print(json.dumps(task, indent=2))
    plumbing.save_task(task)

async def change_task_status(who, id, status):
    active = plumbing.load_active()
    assert id < len(active) and active[id] != None
    blob_idx = active[id]
    task = plumbing.load_task(blob_idx)

    old_status = task["status"]
    print(f"Changing status for task {id} from {old_status} to {status}")
    # Perform checks first
    if old_status == "open":
        if status not in ["start", "stop"]:
            return Error(110, "invalid status change")
    elif old_status == "start":
        if status not in ["pause", "stop"]:
            return Error(110, "invalid status change")
    elif old_status == "pause":
        if status not in ["start", "stop"]:
            return Error(110, "invalid status change")
    # This should not be possible
    assert old_status != "stop"

    # Change the status
    task["status"] = status
    plumbing.save_task(task)

    # If task is stopped then archive it
    if status == "stop":
        active[id] = None
        plumbing.save_active(active)
        month = util.current_month()
        archive = plumbing.load_archive(month)
        archive.append(blob_idx)
        plumbing.save_archive(month, archive)

async def add_task_comment(who, id, comment):
    active = plumbing.load_active()
    assert id < len(active) and active[id] != None
    blob_idx = active[id]
    task = plumbing.load_task(blob_idx)

    task["events"].append(["comment", lib.util.now(), who, comment])

    plumbing.save_task(task)

api_table = {
    "get_info": get_info,
    "add_task": add_task,
    "fetch_active_tasks": fetch_active_tasks,
    "fetch_task": fetch_task,
    "modify_task": modify_task,
    "change_task_status": change_task_status,
    "add_task_comment": add_task_comment,
}

async def call(request):
    method = request["method"]
    params = request["params"]
    func = api_table[method]
    result = await func(*params)

    if isinstance(result, Error):
        errcode, errmsg = result.code, result.msg
        response = {
            "id": request["id"],
            "result": None,
            "error": {
                "code": errcode,
                "message": errmsg
            }
        }
        return response

    # Normal reply
    response = {
        "id": request["id"],
        "result": result,
    }
    return response

