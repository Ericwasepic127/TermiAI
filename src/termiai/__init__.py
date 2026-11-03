#!/usr/bin/env python3
# Made by @Ericwasepic127

import flet as ft, os, sys, copy
sys.path.append("..")
from termilib import tools, ftapi, PROMPT
sysprompt = PROMPT % ("Do Markdown formatting to format your response", "***NO***")

def chatElem(page: ft.Page):
    name, data = tools.createChatName(default=tools.buildict(sysprompt))
    def delete_click(e):
        tools.deleteChat(name)
        page.controls.clear()
        main(page)
        page.update()
    async def onsend(m):
        dclon = data.clone()
        clone = dclon["messages"]
        tools.append_message("user", m, clone)
        returned = await tools.post(dclon)
        c = returned.get("choices")
        if c:
            tools.append_message("", c[0]["message"], clone, raw=True)
        else:
            tools.append_message("assistant", returned.get("error").get("message"), clone)
        data["messages"] = clone
        return c[0]["message"]["content"] if c else returned.get("error").get("message")
    delBtn = ft.IconButton(
        icon=ft.Icons.DELETE_OUTLINE,
        icon_color="red",
        tooltip="Delete Chat",
        on_click=delete_click
    )
    page.add_sidebar_tab(
        "Chat",
        ft.Icons.CHAT_OUTLINED,
        ftapi.shellv2(page, onsend, "Thinking...")[0],
        delBtn
    )

def loadChatFromJson(page, name):
    data = tools.loadChat(name  + ".json")
    async def onsend(m):
        dclon = data.clone()
        clone = dclon["messages"]
        tools.append_message("user", m, clone)
        returned = await tools.post(dclon)
        c = returned.get("choices")
        if c:
            tools.append_message("", c[0]["message"], clone, raw=True)
        else:
            tools.append_message("assistant", returned.get("error").get("message"), clone)
        data["messages"] = clone
        return c[0]["message"]["content"] if c else returned.get("error").get("message")
    item, ap = ftapi.shellv2(page, onsend, "Thinking...")
    def delete_click(e):
        tools.deleteChat(name)
        page.controls.clear()
        main(page)
        page.update()
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
        "label": "Chat",
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
                
            ],
            "label": "Settings",
            "icon": ft.Icons.SETTINGS
        },
    ]
    for conf in tools.CHATJSON.keys():
        sideItems.append(loadChatFromJson(page, conf))
    sideBar = ftapi.createSideBar(page, sideItems)
    page.add(sideBar)

if __name__ == '__main__':
    ft.run(main)
