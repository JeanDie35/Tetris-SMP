import json


def encode(msg) -> bytes:
    if isinstance(msg, str):
        return msg.encode("utf-8")
    else:
        return json.dumps(msg).encode("utf-8")

def decode(msg: bytes):
    msg = msg.decode("utf-8")
    if isinstance(msg, str):
        return msg
    else:
        return json.loads(msg)
