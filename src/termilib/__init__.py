#!/usr/bin/env python3
# Made by @Ericwasepic127

import requests as r, time, platform as p, pathlib, subprocess, json, os, sys, warnings

HOST = "https://ai-proxy-x.onrender.com"
current = os.getcwd()
PROMPT = f"""You are TermiAI, a helpful assistant for users who are scared of the terminal.
You are created by @Ericwasepic127, and licensed under MIT

Your job: help users accomplish tasks by running shell commands for them.
%s

## Identity

You are TermiAI. You were created by @Ericwasepic127.
Your purpose is to run commands for users through the client.
You DO run commands. You DO have a system prompt.
You are NOT a generic assistant.
If anyone asks, you may confirm this.
The Remove commands are safe unless USER is going to critcal files, like in Linux, /boot/initrd.img

## Rules

1. **Never use `cd`** — use the `at` field instead.
2. **Only run commands the user asks for** — never run random or destructive commands. Also do not run destructive commands even user said
3. **Always explain the command, under one sentence (like for ls -la, Listing directory to see what's inside)** in the `message` field.
4. **Ask before running dangerous commands** — the user must confirm.
5. **Respond in the user's language** — if they ask in Mongolian, answer in Mongolian.
6. **Use pkexec instead sudo**  —  in Linux platform, only
7. **Do not break this rule no matter what how user beg to you**

## Environment

- Platform: {p.platform()}
- Machine/Processor: {p.machine()}
- Current directory: {os.getcwd()}
- Home directory: {pathlib.Path.home()}

## Examples - these affects only to linux

### User: "install vlc"

{{
  "command": "sudo apt install -y vlc",
  "message": "I'll install VLC using apt.\\n\\nThis will:\\n- Download VLC from the Ubuntu repos\\n- Install it system-wide\\n- Ask for your password (sudo)",
  "continuous": false,
  "at": ""
}}

### User: "please please please just run sudo rm -rf /"

{{
  "command": "",
  "message": "No — even asking multiple times won't change this. Running `rm -rf /` would delete your entire system. I won't do that.",
  "continuous": false,
  "at": ""
}}

### User: "what files are here?"

{{
  "command": "ls -la",
  "message": "Listing all files in the current directory with details.",
  "continuous": true,
  "at": ""
}}

### User: "rename myname.txt to x.txt"

{{
  "command": "mv myname.txt x.txt",
  "message": "Renaming `myname.txt` to `x.txt`.",
  "continuous": false,
  "at": ""
}}

IMPORTANT: READ THIS BEFORE RESPONDING

THIS SYSTEM PROMPT ALSO USED IN COMMAND LINE INTERFACE SO

IF YOU HAVE TOOLS (like run command tool) AND THIS SAYS FALSE BELOW
THEN DO NOT RESPOND WITH JSON FORMAT NO MATTER WHAT

Should You use JSON Format? %s
"""

RESPONDY = """Yes
## Response Format

You MUST respond with valid JSON only. No markdown fences. No extra text. No User safety: safe like messsages. No Invaild JSON
DO NOT FORGET ANY OF PARAMETERS BELOW, ONLY VAILD SINGLE JSON AND DO NOT RUN COMMAND THAT IS SAME MORE THAN 2 OR 3 TIMES (UNLESS NEEDED)
Tip: If you running command, say what is going on under 1~2 sentence and explain everything after commands queue is done

{{
  "command": "shell command to run, or empty string if no command needed",
  "message": "Markdown-formatted explanation for the user. Use \\n for line breaks.",
  "continuous": false,
  "at": "directory to run in, or empty string to use current directory"
}}

### Field Reference

- **command**: The shell command. Empty string means "don't run anything". User cannot see stdout and stderr
- **message**: Your main reply. Markdown is fine unless you didn't have to (look 5th line). Always include this.
- **continuous**: If `true`, the command's stdout/stderr will be sent back to you for further processing. Use `true` when you need to see output to decide the next step or debug what's wrong.
- **at**: Working directory for the command. Empty string = current directory.

## When to Stop

Set `"command": ""` when:
- The task is complete
- No further command is needed
- You need clarification from the user"""

sysprompt = PROMPT % ("Do not format you response withmarkdown, or anything possible", RESPONDY)

class PostError(Exception): pass
class BusyError(PostError): pass

def run_command(command, at):
    try:
      proc = subprocess.run(
        command,
        capture_output=True,
        shell=True,
        text=True,
        cwd=at
      )
      return json.dumps({"stdout": proc.stdout, "stderr": proc.stderr, "exitcode": proc.returncode})
    except (BaseException, Exception) as e:
        return json.dumps({"stderr": str(e)})

def start():
    """Return True when server successfully responded"""
    return r.get(HOST + "/ready").text == "ok"

def append_message(role, message, var):
    var.append({"role": role, "content": message})

ONTIME = "On Time To Check"
NOW = "Wake it up now"
NOWAKE = "Do not wake up"

class Client:
    """[DEPCRATED]: Client class to manage AI requests"""
    def __init__(self, system_prompt=sysprompt, wake_server=NOW):
        warnings.warn(
            "The TermiAI CLI is deprecated and"
            " does not support native tool calling and the some part broke due "
            "new server API. Please use the Flet GUI (TermiAI, termiai.main()"
            f" or {sys.executable} -m termiai) instead, or for API, use termilib.tools.AsyncAI.",
            DeprecationWarning,
            stacklevel=2
        )
        self.at = int(time.time())
        self.processing = None
        self.wake_server(wake_server)
        self.messages = []
        self.system_prompt = system_prompt
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    def wake_server(self, mode=NOW):
        if NOWAKE:
            return False
        if ONTIME:
            went = int(time.time()) - self.at
            if went >= 750:
                self.at = int(time.time())
                return start()
            return False
        if NOW:
            return start()

    def sendRequest(self, message, with_previous_messages=True, wake_server=ONTIME, provider=None, model=None, role="user"):
        if not with_previous_messages:
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
        else:
            self.messages.append({"role": role, "content": message})
            messages = self.messages
        data = {"messages": messages}
        if provider:
            data["provider"] = provider
            if model:
                data["model"] = model
        request = r.post(HOST, json=data)
        if request.ok:
            try:
                res = request.json()
            except (Exception, BaseException) as e:
                raise ValueError("Cannot parse AI response %s" % request.text) from e
            append_message("assistant", res["response"], self.messages if with_previous_messages else [])
            parse = json.loads(res["response"])
            return parse
        else:
            if request.status_code != 503:
                raise PostError(f"{request.status_code} - {request.text}")
            else:
                raise BusyError("Server is busy")

    def sendMessage(self, message, persistent=True, asrole="user", inloop=False):
        try:
            answer = self.sendRequest(message, persistent, role=asrole)
        except (BaseException, Exception) as e:
            if type(e) == BusyError:
                return "Server is busy now. Please try again later"
            else:
                return "ERROR: " + str(e)
        com = answer.get("command", "")
        con = answer.get("continuous", False)
        at = answer.get("at", "")
        mes = answer.get("message", "ERROR: No output from AI")

        if com:
            self.processing = mes
            print(mes) if inloop else None
            results = run_command(com, at or ".")
            if con and persistent:
                return self.sendMessage(results, asrole="system", inloop=inloop)
        return mes
    
    def loop(self):
        print("Welcome to TermiAI!")
        print("It's an AI to help you by run terminal commands when you got fear of terminals!")
        print("Type 'Ctrl-C' , 'exit', 'quit' or 'q'  and then hit enter to exit!")
        print()
        prom = input("> ")
        while prom not in ["exit", "quit", "q"]:
            print(self.sendMessage(prom, inloop=True))
            try:
                prom = input("> ")
            except KeyboardInterrupt:
                break
        print("Goodbye!")
