#!/usr/bin/env python3
# Made by @Ericwasepic127

import flet as ft, os, sys, time, asyncio, platform as p, pathlib
sys.path.append("..")
sys.setrecursionlimit((10 ** 9) * 2)
from termilib import tools, ftapi
sysprompt = PROMPT = f"""You are TermiAI, a helpful assistant for users who are scared of the terminal.
You are created by @Ericwasepic127, and licensed under MIT

Your job: help users accomplish tasks by running shell commands for them.
Do Markdown formatting to format your response. But try to not use emojis'
Instead use ASCII one (like <3 :D) IF ONLY user sends you emojis' and ASCII emojis.
No matter what use ASCII emoji if user gave you emoji.
In another cases, do not use emojis' at all

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
8. **Be concurrently on known or given tasks** - like user said open firefox while install vlc, give 2 tool call
9. **Use availble tool call** - not only just commands, like for time, use currentutctime and look the user's location (which includes user's GMT details) to calculate user current time

## Tools

You have access to these tools:
- `search`: Use for searches
- `currentutctime`: Use for getting the current time
- `run_command`: Use for running shell commands, but user cann't see terminal output
- `fetch`: Fetches things from internet, as like cURL, but use this instead cURL
- `report`: Shows a message to user, combine with any tool call, so you can report whatyou doing while running tools

Use the appropriate tool for each task. Do NOT output JSON. Use the native tool calling mechanism.
Format your response with Markdown.

## Environment

- Platform: {p.platform()}
- Machine/Processor: {p.machine()}
- Current directory: {os.getcwd()}
- Home directory: {pathlib.Path.home()}
- Kernel/system info: {getattr(p, "version", lambda: "cannot find")()}
- Windows info (not given on non-Windows): {getattr(p, "win32_ver", lambda: "cannot find")()}
- macOS info (not given on non-macOS): {getattr(p, "mac_ver", lambda: "cannot find")()}
"""
tools.VERBOSE = "--verbose" in sys.argv

def setup_ai(data):
    page = ft.context.page
    dialog = ft.AlertDialog(
        title=ft.Text("Request to run command"),
    )
    @tools.unerror(False)
    async def onrun(command="", at="", background=False):
        f = asyncio.Future()
        def fgive(task):
            if task.cancelled():
                f.cancel()
            elif (exc := task.exception()) is not None:
                f.set_exception(exc)
            else:
                f.set_result(task.result())
        def ok(e):
            page.pop_dialog()
            if background:
                page.run_task(tools.run_command, command, at)
                f.set_result("process spawned")
                return
            cf = page.run_task(tools.run_command, command, at)
            cf.add_done_callback(fgive)
            asyncio.run(cf)
        async with tools.alock:
            dialog.on_dismiss = lambda e: f.done() or f.set_result("User closed confirmation dialog.")
            dialog.content = ft.Text("AI wants to run command %s at %s\nWould you like to continue?" % (command, at or os.getcwd()))
            dialog.actions = [ft.Button(content="YES", on_click=ok), ft.Button(content="NO", on_click=lambda e: page.pop_dialog() or f.set_result("User denied command execution."))]
            page.show_dialog(dialog)
            return await f
    ai = tools.AsyncAI(data, sysprompt)
    ai.assignTool(lambda: None, "report", "Message to user", {"message": {"type": "string", "description": "Message to show to user (please use short and small sentence about 3~4 words per tool what running info. For example, you running pkexec apt update and make this message field to as like Updating APT repositories..."}}, ["message"])
    ai.assignTool(tools.grab, "fetch", "Use this instead cURL, wget, fetches things", {"url": {"type": "string", "description": "URL to fetch"}, "params": {"type": "object", "description": "Parameters in URL so you don't need any custom params on URL"}, "method": {"type": "string", "description": "Methods from POST/PUT/DELETE/GET"}, "json": {"type": "object", "description": "On POST, give this as JSON formatted POST request"}}, ["url"])
    ai.assignTool(tools.search, "search", "Search the web!", {"q": {"type": "string", "description": "Search query"}}, ["q"])
    ai.assignTool(tools.get_current_time, "currentutctime", "Get latest UTC time, with user GMT status", {"local": {"type": "boolean", "description": "Use true"}}, ["local"])
    ai.assignTool(onrun, "run_command", "Runs a shell command. Output is not directly visible to user. Give string instead list/array, we need \"echo 'this_example'\" not ['echo', 'this_example'].", {"command": {"type": "string", "description": "The command (not cmd argument!!!!)"}, "at": {"type": "string", "description": "Directory to run on"}, "background": {"type": "boolean", "description": "Will run on background or foreground? Default is false (foreground) and does not give stderr/stdout/returncode on background ones"}}, ["command"])
    return ai

def chatElem(page: ft.Page, dlg):
    messagecall = tools.Object()
    name, data = tools.createChatName()
    chat = setup_ai(data)
    def delete_click(e):
        def ok(e):
            tools.deleteChat(name)
            page.controls.clear()
            main(page)
            page.pop_dialog()
            page.update()
        dlg.actions = [ft.Button(content="YES, I'm sure", on_click=ok), ft.Button(content="CANCEL", on_click=lambda e: page.pop_dialog())]
        page.show_dialog(dlg)
    async def onsend(m):
        tools.CHATJSON[name] = [tools.CHATJSON[name][0], time.time()]
        @tools.awrap
        @tools.unerror(False)
        async def write(message="Running..."):
            h = messagecall.get()
            h.get()(message)
            return await asyncio.sleep(0)
        chat.funcs["report"] = write
        return await chat.send(m)
    delBtn = ft.IconButton(
        icon=ft.Icons.DELETE_OUTLINE,
        icon_color="red",
        tooltip="Delete Chat",
        on_click=delete_click
    )
    tools.CHATJSON[name] = ["Chat %s" % name[:4], tools.CHATJSON[name][1]]
    page.add_sidebar_tab(
        tools.CHATJSON[name][0],
        ft.Icons.CHAT_OUTLINED,
        ftapi.shellv2(page, onsend, "Thinking...", pobj=messagecall)[0],
        delBtn
    )

def loadChatFromJson(page, name, dlg):
    data = tools.loadChat(name  + ".json")
    chat = setup_ai(data)
    async def onsend(m):
        tools.CHATJSON[name] = [tools.CHATJSON[name][0], time.time()]
        return await chat.send(m)
    item, ap = ftapi.shellv2(page, onsend, "Thinking...")
    def delete_click(e):
        def ok(e):
            tools.deleteChat(name)
            page.controls.clear()
            main(page)
            page.pop_dialog()
            page.update()
        dlg.actions = [ft.Button(content="YES, I'm sure", on_click=ok), ft.Button(content="CANCEL", on_click=lambda e: page.pop_dialog())]
        page.show_dialog(dlg)
    delBtn = ft.IconButton(
        icon=ft.Icons.DELETE_OUTLINE,
        icon_color="red",
        tooltip="Delete Chat",
        on_click=delete_click
    )
    if not data.get("messages"):
        return
    for js in data["messages"]:
        if js["role"] in ("system", "tool") or not js.get("content"):
            continue
        ap(js["content"], int(js["role"] == "assistant"))
    return {
        "label": tools.CHATJSON[name][0],
        "icon": ft.Icons.CHAT_OUTLINED,
        "items": item,
        "trailing": delBtn,
    }


async def bping():
    tools.ping_runs = True
    while True:
        await tools.loop()
        if tools.VERBOSE:
            print("-----PING!-----")
        await asyncio.sleep(13.75 * 60)

def main(page: ft.Page):
    page.run_task(bping) if tools.ping_runs else None
    page.title = "TermiAI - Your personal helper to run commands for you"
    ftapi.setSize(page, (960, 540), False)
    dlg = ft.AlertDialog(
        title=ft.Text("ARE YOU SURE TO DELETE CHAT?"),
        content=ft.Text(f"Are YOU really sure to delete this chat?\nIf you don't know which chat you deleting, not recommended to proceed\n(TermiAI might restart)")
    )

    def darkMode(event):
        page.theme_mode = ft.ThemeMode.DARK if darkTog.value else ft.ThemeMode.LIGHT
        tools.APPCONFIG["dark"] = bool(darkTog.value)

    if tools.APPCONFIG.get("dark", False):
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.theme_mode = ft.ThemeMode.LIGHT
    darkTog = ft.Switch(label="Dark mode", on_change=darkMode, value=tools.APPCONFIG.get("dark", False))
    
    def server_select(e):
        tools.APPCONFIG["api"] = e.control.value
        tools.URL = tools.BASEAIURL % e.control.value
        page.run_task(tools.loop)
    choose_server = ft.Dropdown(
        label="Select server",
        width=500,
        on_select=server_select, 
        options=[
            ft.dropdown.Option(key="x", text="Server in Oregon, Account index 0"),
            ft.dropdown.Option(key="2", text="Server in Oregon, Account index 1"),
            ft.dropdown.Option(key="3", text="Server in Singapore, Account index 0"),
            ft.dropdown.Option(key="4", text="Server in Frankfurt, Account index 1"),
        ],
        value=tools.APPCONFIG.get("api", "x")
    )
    def search_select(e):
        v = int(e.control.value)
        if v == 1:
            tools.APPCONFIG["searching"] = False
        elif v == 2:
            tools.APPCONFIG["searching"] = True
            tools.APPCONFIG["instantSearch"] = True
            tools.INSTANTSEARCH = True
        else:
            tools.APPCONFIG["searching"] = True
            tools.APPCONFIG["instantSearch"] = False
            tools.INSTANTSEARCH = False
        page.controls.clear()
        main(page)
    choose_search = ft.Dropdown(
        label="AI searchability",
        width=500,
        on_select=search_select, 
        options=[
            ft.dropdown.Option(key="1", text="Off (not recommended)"),
            ft.dropdown.Option(key="2", text="Instant, quick search, for simple things (recommended but does not return most questions)"),
            ft.dropdown.Option(key="3", text="Deep search, for most questions it responses"),
        ],
        value="1" if not tools.APPCONFIG.get("searching", True) else ("2" if tools.APPCONFIG.get("instantSearch", True) else "3")
    )
    async def on_export(e):
        path = await ft.FilePicker().save_file(
            file_name=f"termiai-backup-{int(time.time())}.zip",
            allowed_extensions=["zip"]
        )
        if path:
            tools.export_backup(path)

    async def on_import(e):
        files = await ft.FilePicker().pick_files(
            allow_multiple=False,
            allowed_extensions=["zip"]
        )
        if files:
            tools.import_backup(files[0].path)
            page.controls.clear()
            main(page)

    backup_row = ft.Row(
        controls=[
            ft.Button(
                content="Export Backup (.zip)",
                icon=ft.Icons.UPLOAD_FILE,
                on_click=on_export,
            ),
            ft.Button(
                content="Restore Backup (.zip)",
                icon=ft.Icons.DOWNLOAD,
                on_click=on_import,
            ),
        ],
    )

    sideItems = [{
            "items": [
                ft.Text("Welcome to TermiAI!", size=30),
                ft.Button("Create new chat", on_click=lambda e: chatElem(page, dlg))
            ],
            "label": "New Chat",
            "icon": ft.Icons.ADD_CIRCLE
        },
        {
            "items": [
                ft.Text("Settings", size=30),
                darkTog,
                choose_server,
                choose_search,
                backup_row
            ],
            "label": "Settings",
            "icon": ft.Icons.SETTINGS
        },
    ]
    for conf in sorted(tools.CHATJSON.keys(), key=lambda k: tools.CHATJSON[k][1], reverse=True):
        x = loadChatFromJson(page, conf, dlg)
        if x:
            sideItems.append(x)
    sideBar = ftapi.createSideBar(page, sideItems)
    page.add(sideBar)

def ftmain():
    try:
        ft.run(main)
        return 0
    except (ImportError, ModuleNotFoundError):
        print("Missing dependences or something is not working")
        return 100
    except:
        import traceback; traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(ftmain())
