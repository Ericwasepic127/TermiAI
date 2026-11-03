#!/usr/bin/env python3
# Made by @Ericwasepic127

import flet as ft, os, sys, copy
sys.path.append("..")
from termilib import tools, ftapi, PROMPT
sysprompt = PROMPT % ("Do Markdown formatting to format your response", "***NO***")

def setup_ai(data):
    ai = tools.AsyncAI(data, sysprompt)
    ai.assignTool(tools.instantSearch, "ddg_search", "Instant search API by duckduckgo, for quick lookups.", {"q": {"type": "string", "description": "Search query"}}, ["q"]) if tools.APPCONFIG.get("instantSearch", True) else None
    ai.assignTool(tools.deepsearch, "deepsearch", "Deep search API by LangSearch, for deep and unfindable questions.", {"q": {"type": "string", "description": "Search query"}}, ["q"]) if not tools.APPCONFIG.get("instantSearch", True) else None
    ai.assignTool(tools.get_current_time, "currentutctime", "Get latest time", {"local": {"type": "boolean", "description": "Use true"}}, ["local"])
    ai.assignTool(tools.run_command, "run_command", "Runs a shell command.", {"command": {"type": "string", "description": "The command (not cmd argument!!!!)"}, "at": {"type": "string", "description": "Directory to run on"}}, ["command"])
    return ai

def chatElem(page: ft.Page):
    name, data = tools.createChatName(default=tools.buildict(sysprompt))
    chat = setup_ai(data)
    def delete_click(e):
        def ok(e):
            tools.deleteChat(name)
            page.controls.clear()
            main(page)
            page.update()
        # TODO: make Are you sure? section
        ok(e)
    async def onsend(m):
        tools.CHATJSON[name] = [tools.CHATJSON[name][0], time.time()]
        return await chat.send(m)
    delBtn = ft.IconButton(
        icon=ft.Icons.DELETE_OUTLINE,
        icon_color="red",
        tooltip="Delete Chat",
        on_click=delete_click
    )
    tools.CHATJSON[name] = ["Chat %s" % name[:6], tools.CHATJSON[name][1]]
    page.add_sidebar_tab(
        tools.CHATJSON[name][0],
        ft.Icons.CHAT_OUTLINED,
        ftapi.shellv2(page, onsend, "Thinking...")[0],
        delBtn
    )

def loadChatFromJson(page, name):
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
            page.update()
        # TODO: make Are you sure? section
        ok(e)
    delBtn = ft.IconButton(
        icon=ft.Icons.DELETE_OUTLINE,
        icon_color="red",
        tooltip="Delete Chat",
        on_click=delete_click
    )
    for js in data["messages"]:
        if js["role"] == "system":
            continue
        ap(js["content"], int(js["role"] == "assistant"))
    return {
        "label": tools.CHATJSON[name][0],
        "icon": ft.Icons.CHAT_OUTLINED,
        "items": item,
        "trailing": delBtn,
    }

def main(page: ft.Page):
    page.title = "TermiAI - Your personal helper to run commands for you"
    ftapi.setSize(page, (960, 540), False)

    def darkMode(event):
        page.theme_mode = ft.ThemeMode.DARK if darkTog.value else ft.ThemeMode.LIGHT
        tools.APPCONFIG["dark"] = bool(darkTog.value)

    if tools.APPCONFIG.get("dark", False):
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.theme_mode = ft.ThemeMode.LIGHT
    darkTog = ft.Switch(label="Dark mode", on_change=darkMode, value=tools.APPCONFIG.get("dark", False))
    
    sideItems = [{
            "items": [
                ft.Text("Welcome to TermiAI!", size=30),
                ft.Button("Create new chat", on_click=lambda e: chatElem(page))
            ],
            "label": "New Chat",
            "icon": ft.Icons.ADD_CIRCLE
        },
        {
            "items": [
                ft.Text("Settings", size=30),
                darkTog,
                ft.Text("Coming soon"),
            ],
            "label": "Settings",
            "icon": ft.Icons.SETTINGS
        },
    ]
    for conf in sorted(tools.CHATJSON.keys(), key=lambda k: tools.CHATJSON[k][1], reverse=True):
        sideItems.append(loadChatFromJson(page, conf))
    sideBar = ftapi.createSideBar(page, sideItems)
    page.add(sideBar)

if __name__ == '__main__':
    ft.run(main)
