#!/usr/bin/env python3
# Made by @Ericwasepic127

import httpx, json, asyncio, platformdirs, os, threading as t, uuid, time

CONFIGS = platformdirs.user_config_dir("TermiAI")
DATA = platformdirs.user_data_dir("TermiAI")
JOIN = os.path.join
LIST = os.listdir
CHATS = JOIN(CONFIGS, "chat.json")
CHATJSON = None
URL = None

os.makedirs(CONFIGS, exist_ok=True)
os.makedirs(DATA, exist_ok=True)

def createChatList():
    if CHATJSON is None:
        return []
    give = []
    for idcard, detail in CHATJSON.items():
        give.append()

def createChatName():
    val = str(uuid.uuid4())
    if CHATJSON is None:
        return val
    obj = JOIN(DATA, val + ".json")
    CHATJSON[val] = ["New Chat", time.time()]
    return val, LiveJson(obj)

def loadChat(name):
    return LiveJson(JOIN(DATA, name))

def append_message(role, message, var, raw=False):
    var.append(message) if raw else var.append({"role": role, "content": message})

async def post(data):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(URL or "https://ai-proxy-x.onrender.com/", data=json.dumps(data), headers={"Content-Type": "application/json"}, timeout=120)
            m = r.json()
        except (BaseException, Exception) as e:
            m = {"error": {"message": e.__class__.__name__ + ": " + str(e)}}
    return m

async def search(data):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(URL or "https://search-proxy-x.onrender.com/", data=json.dumps(data), headers={"Content-Type": "application/json"}, timeout=120)
            m = r.json()
        except (BaseException, Exception) as e:
            m = {"error": {"message": e.__class__.__name__ + ": " + str(e)}}
    return m

class LiveJson(dict):
    def __init__(self, file_path="data.json", default_data=None):
        self.file_path = file_path
        self.lock = t.Lock()
        
        initial_data = {}
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    initial_data = json.load(f)
            except Exception:
                initial_data = default_data or {}
        else:
            initial_data = default_data or {}
            self._save_to_disk(initial_data)
            
        super().__init__(initial_data)

    def _save_to_disk(self, data):
        try:
            with open(self.file_path, "w") as f:
                json.dump(data, f, indent=4)
        except IOError:
            pass

    def __getitem__(self, key):
        with self.lock:
            return super().__getitem__(key)

    def __setitem__(self, key, value):
        with self.lock:
            super().__setitem__(key, value)
            current_state = dict(self.items())
            self._save_to_disk(current_state)

    def __delitem__(self, key):
        with self.lock:
            super().__delitem__(key)
            current_state = dict(self.items())
            self._save_to_disk(current_state)

    def update(self, other=None, **kwargs):
        with self.lock:
            if other is not None:
                if isinstance(other, dict):
                    for k, v in other.items():
                        if k in self and isinstance(self[k], dict) and isinstance(v, dict):
                            self[k].update(v)
                        else:
                            super().__setitem__(k, v)
                else:
                    super().update(other)
            if kwargs:
                super().update(kwargs)
                
            current_state = dict(self.items())
            self._save_to_disk(current_state)

    def reload(self):
        with self.lock:
            if os.path.exists(self.file_path):
                try:
                    with open(self.file_path, "r") as f:
                        data = json.load(f)
                        super().clear()
                        super().update(data)
                except Exception:
                    pass

CHATJSON = LiveJson(CHATS)

if __name__ == '__main__':
    print(asyncio.run(post([{"role": "user", "content": "Hi"}])))
