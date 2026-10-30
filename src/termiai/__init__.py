#!/usr/bin/env python3
# Made by @Ericwasepic127

import flet as ft, os, sys
sys.path.append("..")
from termilib import tools, ftapi, PROMPT
sysprompt = PROMPT % "Do Markdown formatting to format your response"

def chatElem(page: ft.Page):
    name, data = tools.createChatName()
    data["messages"] = []
    async def onsend(m):
        clone = data["messages"].copy()
        tools.append_message("user", m, clone)
        returned = await tools.post(clone)
        c = returned.get("choices")
        if c:
            tools.append_message("", c[0]["message"], clone, raw=True)
        else:
            tools.append_message("assistant", returned.get("error").get("message"), clone)
        data["messages"] = clone
        return c[0]["message"]["content"] if c else returned.get("error").get("message")
    page.add_sidebar_tab(
        "Chat",
        ft.Icons.CHAT_OUTLINED,
        ftapi.shellv2(page, onsend, "Thinking...")[0],
    )

def loadChatFromJson(page, name):
    data = tools.loadChat(name)
    async def onsend(m):
        clone = data["messages"].copy()
        tools.append_message("user", m, clone)
        returned = await tools.post(clone)
        c = returned.get("choices")
        if c:
            tools.append_message("", c[0]["message"], clone, raw=True)
        else:
            tools.append_message("assistant", returned.get("error").get("message"), clone)
        data["messages"] = clone
        return c[0]["message"]["content"] if c else returned.get("error").get("message")
    item, ap = ftapi.shellv2(page, onsend, "Thinking...")
    for js in data["messages"]:
        ap(js["content"], int(js["role"] == "assistant"))
    return {
        "label": "Chat",
        "icon": ft.Icons.CHAT_OUTLINED,
        "items": item,
    }

def main(page: ft.Page):
    page.title = "TermiAI - Your personal helper to run commands for you"
    ftapi.setSize(page, (960, 540), False)

    def darkMode(event):
        page.theme_mode = ft.ThemeMode.DARK if darkTog.value else ft.ThemeMode.LIGHT
    
    darkTog = ft.Switch(label="Dark mode", on_change=darkMode, value=False)
    
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
                
            ],
            "label": "Settings",
            "icon": ft.Icons.SETTINGS
        },
    ]
    for conf in tools.CHATJSON.:
        sideItems.append(loadChatFromJson(page, conf))
    sideBar = ftapi.createSideBar(page, sideItems)
    page.add(sideBar)

if __name__ == '__main__':
    ft.run(main)
