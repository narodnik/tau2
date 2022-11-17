import asyncio, json, random
import sys
from lib.net import Channel

async def create_channel():
    reader, writer = await asyncio.open_connection("dasman.xyz", 7643)
    channel = Channel(reader, writer)
    return channel

def random_id():
    return random.randint(0, 2**32)

async def get_info():
    channel = await create_channel()
    request = {
        "id": random_id(),
        "method": "get_info",
        "params": [],
    }
    await channel.send(request)

    response = await channel.receive()
    # Closed connect returns None
    assert response is not None

    print("response:")
    print(json.dumps(response, indent=2))
    result = response["result"]
    return result

async def add_task(who, task):
    channel = await create_channel()
    request = {
        "id": random_id(),
        "method": "add_task",
        "params": [who, task],
    }
    await channel.send(request)

    response = await channel.receive()
    # Closed connect returns None
    assert response is not None

    assert "error" not in response
    id = response["result"]
    return id

async def fetch_active_tasks():
    channel = await create_channel()
    request = {
        "id": random_id(),
        "method": "fetch_active_tasks",
        "params": [],
    }
    await channel.send(request)

    response = await channel.receive()
    assert response is not None
    assert "error" not in response
    tasks = response["result"]
    return tasks

async def fetch_task(task_id):
    channel = await create_channel()
    request = {
        "id": random_id(),
        "method": "fetch_task",
        "params": [task_id],
    }
    await channel.send(request)

    response = await channel.receive()
    assert response is not None
    assert "error" not in response
    task = response["result"]
    return task

async def modify_task(who, id, changes):
    channel = await create_channel()
    request = {
        "id": random_id(),
        "method": "modify_task",
        "params": [who, id, changes],
    }
    await channel.send(request)

    response = await channel.receive()
    assert response is not None
    assert "error" not in response
    assert not response["result"]

async def change_task_status(who, id, status):
    channel = await create_channel()
    request = {
        "id": random_id(),
        "method": "change_task_status",
        "params": [who, id, status],
    }
    await channel.send(request)

    response = await channel.receive()
    assert response is not None
    if "error" in response:
        error = response["error"]
        errcode, errmsg = error["code"], error["message"]
        print(f"error: {errcode} - {errmsg}", file=sys.stderr)
        return False

    assert not response["result"]
    return True

async def add_task_comment(who, id, comment):
    channel = await create_channel()
    request = {
        "id": random_id(),
        "method": "add_task_comment",
        "params": [who, id, comment],
    }
    await channel.send(request)

    response = await channel.receive()
    assert response is not None
    if "error" in response:
        error = response["error"]
        errcode, errmsg = error["code"], error["message"]
        print(f"error: {errcode} - {errmsg}", file=sys.stderr)
        return False

    assert not response["result"]
    return True

