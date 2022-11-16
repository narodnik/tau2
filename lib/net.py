import json

class Channel:

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    async def receive(self):
        data = await self.reader.readline()
        if not data:
            self.writer.close()
            return None
        message = data.decode()
        response = json.loads(message)
        return response

    async def send(self, obj):
        message = json.dumps(obj) + "\n"
        data = message.encode()
        self.writer.write(data)
        await self.writer.drain()

