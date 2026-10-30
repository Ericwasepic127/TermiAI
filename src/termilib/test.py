import flet as ft
from . import ftapi
from .tools import post, append_message as am
from . import tools
#tools.URL = "http://localhost:5000"

data1 = []
async def data1f(x):
    am("user", x, data1)
    msg = await post(data1)
    am("assistant", msg, data1)
    return msg

data2 = []
async def data2f(x):
    am("user", x, data2)
    msg = await post(data2)
    am("assistant", msg, data2)
    return "**AI:** " + msg

am("system", "Do not try to format your response, use 2+ sentences", data1)
am("system", "Use markdown to format your response, use 2+ sentences", data2)

async def s(x):
    import asyncio
    await asyncio.sleep(1)
    return x

def main(page: ft.Page):
    page.title = "TEST"
    page.padding = 20
    ftapi.setSize(page, (600, 400), False)
    content = [
        {
            "items": [ft.Text("test")],
            "label": "Test",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("teest")],
            "label": "Test",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("tessst")],
            "label": "Test",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("test3ed")],
            "label": "Test",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("tesct")],
            "label": "Test",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Button("test")],
            "label": "Test",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("test"), ft.Text("TET")],
            "label": "Test",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("test"), ft.Slider()],
            "label": "Test",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("test"), ft.Checkbox(label="mod")],
            "label": "Test",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("test")],
            "label": "Test",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("test")],
            "label": "Test",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("test")],
            "label": "Test",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("test")],
            "label": "Test",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("test")],
            "label": "Test",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("test")],
            "label": "Test",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("test")],
            "label": "Test",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("test")],
            "label": "Tewst",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("test")],
            "label": "Testc",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("test")],
            "label": "Test6",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": [ft.Text("test")],
            "label": "Test4",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": ftapi.shell(page, data1f, "Thinking..."),
            "label": "Test2",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
        {
            "items": ftapi.shellv2(page, data2f, "Thinking..."),
            "label": "Test3",
            "icon": [ft.Icons.HOME_OUTLINED, ft.Icons.HOME]
        },
    ]
    page.add(ftapi.createSideBar(page, content))

ft.run(main)
