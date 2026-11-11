#!/usr/bin/env python3
# Made by @Ericwasepic127

import httpx, json, asyncio, platformdirs, os, threading as t, uuid, time, datetime, inspect, traceback

CONFIGS = platformdirs.user_config_dir("TermiAI")
DATA = platformdirs.user_data_dir("TermiAI")
JOIN = os.path.join
LIST = os.listdir
CHATS = JOIN(CONFIGS, "chat.json")
APPCONFIG = None
CHATJSON = None
URL = None
BASEAIURL = "https://ai-proxy-%s.onrender.com/"
VERBOSE = False
THERROR = """<!doctype html>
<html lang=en>
<title>429 Too Many Requests</title>
<h1>Too Many Requests</h1>
<p>{&#34;error&#34;: {&#34;message&#34;: &#34;Too many requests!&#34;}}</p>"""

os.makedirs(CONFIGS, exist_ok=True)
os.makedirs(DATA, exist_ok=True)

class HandleError:
    def __init__(self):
        self.cleanup()
    def cleanup(self):
        self.error_occured = False
        self.error = (None, None, None)
        self.raise_error = False
        self.error_simple = None
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_obj, exc_trace):
        self.error = (exc_type,exc_obj,exc_trace)
        self.error_occured = all((exc_type,exc_obj,exc_trace))
        if not self.error_occured:
            return
        name = getattr(exc_type, "__name__", "Exception")
        has = "".join(getattr(exc_obj, "args", ())).replace("\n", " ").strip().rstrip()
        if has:
            self.error_simple = f"{name}: {has}"
        else:
            self.error_simple = name
        return not self.raise_error

def verbose_err(*a):
    if VERBOSE and all(a):
        traceback.print_exception(*a)

def unerror(is_sync=True, onerror=verbose_err):
    """
     Reccomended wrapper for tool call functions
     Useful, does give error simplified (like Exception: testerror)
     Does not raises error
     Gives error's info to onerror function
    """
    def syncwrap(f):
        def wrapper(*a, **k):
            handle = HandleError()
            with handle:
                r = f(*a, **k)
            if handle.error_occured:
                r = handle.error_simple
                err = handle.error
                handle.cleanup()
                if callable(onerror):
                    with handle:
                        onerror(*err)
            return r
        return wrapper
    def asyncwrap(f):
        async def wrapper(*a, **k):
            handle = HandleError()
            with handle:
                r = await f(*a, **k)
            if handle.error_occured:
                r = handle.error_simple
                err = handle.error
                handle.cleanup()
                if callable(onerror):
                    with handle:
                        onerror(*err)
            return r
        return wrapper
    if callable(is_sync):
        return syncwrap(is_sync)
    return syncwrap if is_sync else asyncwrap

def swrap(f):
    def a(*a, **k):
        res = f(*a, **k)
        if VERBOSE and res:
            try:
                print("---", f.__name__, "---")
                print(a, k)
                print(res, repr(res), dir(res), type(res))
            except:
                ...
        return res
    return a

def awrap(f):
    async def a(*a, **k):
        res = await f(*a, **k)
        if VERBOSE and res:
            try:
                print("---", f.__name__, "---")
                print(a, k)
                print(res, repr(res), dir(res), type(res))
            except:
                ...
        return res
    return a

@awrap
@unerror(False)
async def grab(url=None, method="GET", follow_redirects=True, **kwargs):
    async with httpx.AsyncClient() as client:
        return await getattr(client, method.lower())(url, follow_redirects=follow_redirects, **kwargs)

@awrap
@unerror(False)
async def ping(url=None):
    if url is not None:
        url = "https://%s-proxy-%s.onrender.com/" % url
    else:
        url = URL or BASEAIURL % "x"
    return await grab(url, timeout=75)

@awrap
@unerror(False)
async def loop():
    return await ping(), await ping(("search", "x"))

@awrap
@unerror(False)
async def get_current_time(local=True):
    async with httpx.AsyncClient() as client:
        try:
            (1 / 0) if  local else None
            r = await client.get("https://currentdatetimepy.onrender.com/", timeout=45)
            return {r.text, "user_time_zone": "GMT" + str(datetime.datetime.now().astimezone().tzinfo)}
        except:
            import datetime
            return {"utcdate": datetime.datetime.now(datetime.timezone.utc).ctime(), "user_time_zone": "GMT" + str(datetime.datetime.now().astimezone().tzinfo)}

@awrap
@unerror(False)
async def run_command(command="", at="", cmd=""):
    try:
        process = await asyncio.create_subprocess_shell(
            command or cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.DEVNULL,
            cwd=at or None
        )
        stdout, stderr = await process.communicate()
        return {"stdout": stdout.decode("utf-8", errors="replace"), "stderr": stderr.decode("utf-8", errors="replace"), "returncode": process.returncode}
    except Exception as e:
        return {"stdout": "", "stderr": getattr(type(e), "__name__", "<Unknown error>") + ": " + str(e), "returncode": 1}

@swrap
def createChatList():
    if CHATJSON is None:
        return []
    give = []
    for idcard, detail in CHATJSON.items():
        give.append()

@swrap
def createChatName(default=None):
    val = str(uuid.uuid4())
    if CHATJSON is None:
        return val
    obj = JOIN(DATA, val + ".json")
    CHATJSON[val] = ["New Chat", time.time()]
    return val, LiveJson(obj, default_data=default)

@swrap
def loadChat(name):
    return LiveJson(JOIN(DATA, name))

def append_message(role, message, var, raw=False):
    var.append(message) if raw else var.append({"role": role, "content": message})

@awrap
async def post(data):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(URL or "https://ai-proxy-x.onrender.com/", content=json.dumps(data), headers={"Content-Type": "application/json"}, timeout=120)
            m = r.json()
        except json.JSONDecodeError as e:
            try:
                if ("<!doctype html>" in r.text  and "<html>" in r.text and r.status_code == 429 and "error" in r.text) or THERROR in r.text.strip().rstrip():
                    m = {"error": {"message": "Too many requests per minute. Please wait about 1 minute"}}
                else:
                    m = {"error": {"message": "DecodeError: " + r.text}}
            except:
                m = {"error": {"message": e.__class__.__name__ + ": " + str(e)}}
        except (BaseException, Exception) as e:
            m = {"error": {"message": e.__class__.__name__ + ": " + str(e)}}
    return m

@awrap
@unerror(False)
async def instantSearch(**kwargs):
    data = kwargs.get("q") or kwargs.get("query") or kwargs.get("prompt")
    if not data:
        return {"error": "No search query provided"}
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get("https://api.duckduckgo.com/", headers={"Content-Type": "application/json"}, timeout=120, params={"format": "json", "q": data})
            m = r.json()
        except json.JSONDecodeError:
            m = {"error": {"message": "Decode failure on response JSON: " + r.text}}
        except (BaseException, Exception) as e:
            m = {"error": {"message": e.__class__.__name__ + ": " + str(e)}}
    return m

@awrap
@unerror(False)
async def search(noredirectinsta=False, **kwargs):
    data = kwargs.get("q") or kwargs.get("query") or kwargs.get("prompt")
    count = int(kwargs.get("count", 5))
    if not data:
        return {"error": "No search query provided"}
    if INSTANTSEARCH and not noredirectinsta:
        return await instantSearch(q=data)
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post("https://search-proxy-x.onrender.com/", content=json.dumps({"query": data, "contents": {"text": True},"freshness": "noLimit", "count": count}), headers={"Content-Type": "application/json"}, timeout=120)
            m = r.json()
        except json.JSONDecodeError:
            m = {"error": {"message": "Decode failure on response JSON: " + r.text}}
        except (BaseException, Exception) as e:
            m = {"error": {"message": e.__class__.__name__ + ": " + str(e)}}
    return m

async def deepsearch(**kwargs):
    return await search(**kwargs, noredirectinsta=True)

@swrap
def buildict(p, tools=None):
    m = []
    append_message("system", p, m)
    r = {"messages": m}
    if tools:
        r["tools"] = tools
        print(r)
    return r

def deleteChat(name):
    if name in CHATJSON or CHATJSON.get(name) is not None:
        del CHATJSON[name]
    file_path = JOIN(DATA, name + ".json")
    if os.path.exists(file_path):
        os.remove(file_path)

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
    def clone(self):
        cloned = {}
        for name, item in self.items():
            cloned[name] = item
        return cloned

class MemJson(dict):
    def clone(self):
        return MemJson(self)

class AsyncAI:
    def __init__(self, jsonobj: LiveJson, sysprompt):
        self.data = jsonobj
        self.post = post
        self.sysprompt = sysprompt
        self.maxLimit = APPCONFIG.get("maxToolLoop", 4)
        self.funcs = {}
        self.tools = []

    def removeTool(self, name):
        if name in self.funcs:
            self.tools = [t for t in self.tools if t["function"]["name"] != name]
            del self.funcs[name]

    def assignTool(self, asyncfunc, name, desc, params, needs=[]):
        build = {"type": "function","function": {"parameters": {"type": "object","required": []}}}
        build["function"]["name"] = name
        build["function"]["description"] = desc
        build["function"]["properties"] = params
        build["function"]["required"] = needs
        self.funcs[name] = asyncfunc
        self.tools.append(build)

    @awrap
    @unerror(False)
    async def send(self, m):
        currentLoop = 0
        dclon = {**self.data.clone(), "tools": self.tools} if self.tools else self.data.clone()
        clone = [{"role": "system", "content": self.sysprompt}] + dclon.get("messages", [])
        append_message("user", m, clone)
        dclon["messages"] = clone
        returned = await self.post(dclon)
        c = returned.get("choices")
        if not c:
            append_message("assistant", returned.get("error").get("message"), clone)
            self.data["messages"] = [c for c in clone if c.get("role") != "system"]
            return returned.get("error").get("message")
        airesponse = c[0]["message"]
        append_message("", airesponse, clone, raw=True)
        tool = c[0].get("finish_reason", "stop")
        calls = airesponse.get("tool_calls", [])
        while tool != "stop" and self.maxLimit > currentLoop and calls:
            replica, coros = [], []
            for call in calls:
                fd = call.get("function")
                func = self.funcs.get(fd.get("name"))
                nm = fd.get("name")
                arg = json.loads(fd.get("arguments"))
                print(fd.get("name") + ":", arg) if VERBOSE else None
                coros.append(func(**arg))
                replica.append({"role": "tool", "tool_call_id": call.get("id")})
            for index, res in enumerate(await asyncio.gather(*coros)):
                replica[index]["content"] = res if isinstance(res, str) else (json.dumps(res) if isinstance(res, dict) else str(res))
            for x in replica:
                clone.append(x)
            dclon["messages"] = clone
            returned = await self.post(dclon)
            c = returned.get("choices")
            if not c:
                append_message("assistant", returned.get("error").get("message"), clone)
                self.data["messages"] = [c for c in clone if c.get("role") != "system"]
                return returned.get("error").get("message")
            airesponse = c[0]["message"]
            append_message("", airesponse, clone, raw=True)
            tool = c[0].get("finish_reason", "stop")
            calls = airesponse.get("tool_calls", [])
            currentLoop += 1
        if tool == "tool_calls":
            for call in calls:
                clone.append({"role": "tool", "tool_call_id": call.get("id"), "content": "Too much tool calls: try again in next request - you cannot run any tool calls because you exceeding tool limit per one message"})
            dclon["messages"] = clone
            returned = await post(dclon)
            c = returned.get("choices")
            if not c:
                tools.append_message("assistant", returned.get("error").get("message"), clone)
                self.data["messages"] = [c for c in clone if c.get("role") != "system"]
                return returned.get("error").get("message")
            airesponse = c[0]["message"]
            append_message("", airesponse, clone, raw=True)
        self.data["messages"] = [c for c in clone if c.get("role") != "system"]
        return airesponse.get("content") or "AI empty response"

DEFAULTDATA = {
    "dark": False,
    "api": "x",
    "search": True,
    "custom": False,
    "instantSearch": True,
    "maxToolLoop": 4,
}

CHATJSON = LiveJson(CHATS)
APPCONFIG = LiveJson(JOIN(CONFIGS, "appcfg.json"), default_data=DEFAULTDATA)
URL = APPCONFIG.get("api", BASEAIURL % "x") if APPCONFIG.get("custom") else BASEAIURL % APPCONFIG.get("api", "x")
INSTANTSEARCH = APPCONFIG.get("instantSearch", True)

if __name__ == '__main__':
    VERBOSE = True
    asyncio.run(loop())
    asyncio.run(deepsearch(q="What is capital of france"))
    print(asyncio.run(post({"messages": [{"role": "user", "content": "Hi"}]})))
    aichat = AsyncAI(LiveJson("test.json"), "Helpful AI Assistant called TermiAI")
    aichat.assignTool(instantSearch, "ddgsearch", "Instant search API by duckduckgo, for quick lookups.", {"q": {"type": "string", "description": "Search query (no encode like test+example needed)"}}, ["q"])
    aichat.assignTool(deepsearch, "deepsearch", "Deep search API by LangSearch, for deep and unfindable questions.", {"q": {"type": "string", "description": "Search query (no encode like test+example needed)"}, "count": {"type": "integer", "description": "Total counts"}}, ["q"])
    aichat.assignTool(get_current_time, "currentutctime", "Get latest time", {"local": {"type": "boolean", "description": "Only set to False if you think local time is wrong (mostly no, so use true)"}}, ["local"])
    aichat.assignTool(grab, "fetch", "Fetch things from given URL", {"url": {"type": "string", "description": "URL to fetch"}, "params": {"type": "object", "description": "Parameters"}}, ["url"])
    print(asyncio.run(aichat.send("Hi! Can you get my local time clock in UTC please? And then grab latest Github News by that clock so u can fetch absalute latest!")))
