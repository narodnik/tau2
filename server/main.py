import asyncio, json
import api, lib, plumbing, util

# So we can see the goddamn exceptions
async def handle_connect(reader, writer):
    try:
        addr = writer.get_extra_info("peername")
        print(f"Received connection from {addr}")
        channel = lib.net.Channel(reader, writer)
        await process(channel)
    except:
        import traceback
        traceback.print_exc()

async def process(channel):
    while True:
        request = await channel.receive()
        if request is None:
            print("Channel closed")
            return

        print("request:")
        print(json.dumps(request, indent=2))

        response = await api.call(request)
        print("response:")
        print(json.dumps(response, indent=2))

        await channel.send(response)

def stuff():
    task = {
        "blob_idx": lib.util.random_blob_idx(),
        "assigned": [],
        "title": "foo",
        "desc": "do foo",
        "tags": [],
        "project": "zk",
        "status": "open",
        "due": None,
        "created": lib.util.now(),
        "events": [],
    }
    lib.util._enforce_task_format(task)

    # Create task
    plumbing.save_task(task)

    active = plumbing.load_active()
    id = plumbing.next_free_id(active, task["blob_idx"])
    print(id)
    plumbing.save_active(active)

    # Load task 1
    blob_idx = active[1]
    print(plumbing.load_task(blob_idx))

    # Archive task
    active[1] = None
    plumbing.save_active(active)
    month = util.current_month()
    archive = plumbing.load_archive(month)
    archive.append(blob_idx)
    plumbing.save_archive(month, archive)

async def main():
    print("Server started")

    server = await asyncio.start_server(handle_connect, "0.0.0.0", 7643)
    async with server:
        await server.serve_forever()

asyncio.run(main())

