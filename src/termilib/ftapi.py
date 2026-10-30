#!/usr/bin/env python3
# Made by @Ericwasepic127

import flet as ft

def setSize(page, size, resizable=True):
    w, h = size
    if resizable:
        page.window.resizable = True
        page.window.min_width = None
        page.window.min_height = None
        page.window.max_width = None
        page.window.max_height = None
    else:
        page.window.min_width = w
        page.window.max_width = w
        page.window.min_height = h
        page.window.max_height = h

    page.window.width = w
    page.window.height = h
    page.update()

def createSideBar(page, contents, container_configs={}, minw=100, minEw=220, gpA=-0.9):
    objects = {}
    state = {"active_idx": 0}
    
    sidebar_items_list = ft.ListView(expand=True, spacing=5, padding=10, auto_scroll=True)
    content_area = ft.Container(expand=True)

    def switch_tab(target_index):
        if state["active_idx"] < len(sidebar_items_list.controls):
            sidebar_items_list.controls[state["active_idx"]].selected = False
        
        sidebar_items_list.controls[target_index].selected = True
        state["active_idx"] = target_index
        content_area.content = objects.get(target_index, ft.Container(ft.Text("Empty Workspace")))
        page.update()

    for index, metadatas in enumerate(contents):
        items = metadatas["items"]
        container = ft.Container(ft.Column(items, expand=True), expand=True, **container_configs)
        objects[index] = container
        
        label = metadatas["label"]
        icon = metadatas["icon"]
        
        tile = ft.ListTile(
            key=str(index),
            leading=ft.Icon(icon),
            title=ft.Text(label, weight=ft.FontWeight.W_500),
            selected=(index == 0),
            selected_color=ft.Colors.BLUE_400,
            on_click=lambda e, idx=index: switch_tab(idx),
            shape=ft.RoundedRectangleBorder(radius=8)
        )
        sidebar_items_list.controls.append(tile)

    if not objects:
        raise ValueError("No display elements specified inside contents mapping")
        
    content_area.content = objects[0]

    def add_dynamic_tab(label, icon, layout_items):
        new_index = len(objects)
        
        objects[new_index] = ft.Container(ft.Column(layout_items, expand=True), expand=True, **container_configs)
        
        new_tile = ft.ListTile(
            key=str(new_index),
            leading=ft.Icon(icon),
            title=ft.Text(label, weight=ft.FontWeight.W_500),
            selected=False,
            selected_color=ft.Colors.BLUE_400,
            on_click=lambda e, idx=new_index: switch_tab(idx),
            shape=ft.RoundedRectangleBorder(radius=8)
        )
        sidebar_items_list.controls.append(new_tile)
        switch_tab(new_index)
        page.update()

    page.add_sidebar_tab = add_dynamic_tab

    sidebar_wrapper_container = ft.Container(
        content=sidebar_items_list,
        width=minEw,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        alignment=ft.Alignment.TOP_CENTER
    )

    return ft.Row([sidebar_wrapper_container, ft.VerticalDivider(width=1), content_area], expand=True)

def createSideBar_old(page, contents, container_configs={}, minw=100, minEw=200, gpA=-0.9):
    obj = []
    objects = {}
    metadata = []

    def on_nav_change(e):
        content_area.content = objects.get(e.control.selected_index, objects[0])
        page.update()
    
    for metadatas in contents:
        items = metadatas["items"]
        container = ft.Container(ft.Column(items, auto_scroll=True, scroll=ft.ScrollMode.AUTO), expand=True, **container_configs)
        label = metadatas["label"]
        icon, selIcon = metadatas["icon"]
        metadata.append(ft.NavigationRailDestination(icon=icon, selected_icon=selIcon, label=label))
        obj.append(container)

    if not obj:
        raise ValueError("no items it get")
    
    for index, content in enumerate(obj):
        objects[index] = content
    del obj

    def add_dynamic_tab(label, icon_tuple, layout_items):
        new_index = len(sidebar.destinations)
        icon, selIcon = icon_tuple
        
        sidebar.destinations.append(
            ft.NavigationRailDestination(icon=icon, selected_icon=selIcon, label=label)
        )

        objects[new_index] = ft.Container(ft.Column(layout_items), expand=True, **container_configs)
        page.update()

    page.add_sidebar_tab = add_dynamic_tab
    
    content_area = ft.Container(content=objects[0], expand=True)
    sidebar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL, 
        extended=True,
        min_width=minw,
        min_extended_width=minEw,
        group_alignment=gpA,
        destinations=metadata,
        on_change=on_nav_change,
        height=page.window.height,
    )
    return ft.Row([ft.Column([sidebar], scroll=ft.ScrollMode.AUTO, width=minEw if sidebar.extended else minw, expand=True), ft.VerticalDivider(width=1), content_area], expand=True)

def shell(page, do, waitmsg="Please wait..."):
    log = ft.Column(auto_scroll=True, spacing=6, expand=True)
    inp = ft.TextField(expand=True, autofocus=True)
    send_btn = ft.IconButton(ft.Icons.SEND)

    async def send(e):
        q = inp.value.strip()
        if not q:
            return
        inp.value = ""
        log.controls.append(ft.Text(f"- {q}", color="blue"))
        out = ft.Text(waitmsg, color="red")
        log.controls.append(out)
        send_btn.disabled = True
        page.update()
        out.value = await do(q)
        send_btn.disabled = False
        await inp.focus()
        page.update()

    inp.on_submit = lambda e: page.run_task(send, e)
    send_btn.on_click = lambda e: page.run_task(send, e)

    return [ft.Container(content=log, expand=True), ft.Row([inp, send_btn])]

def shellv2(page, do, waitmsg="Please wait..."):
    url_launcher = ft.UrlLauncher()

    log = ft.Column(auto_scroll=True, spacing=12, expand=True, scroll=ft.ScrollMode.AUTO)
    log.flag = False
    inp = ft.TextField(expand=True, autofocus=True)
    send_btn = ft.IconButton(ft.Icons.SEND)
    def handle_link(e):
        page.run_task(url_launcher.launch_url, e.data)

    def append(msg, role=0):
        assert type(role) == int, "INT"
        if role == 0:
            if len(log.controls) > 0 and log.flag:
                log.controls.append(ft.Divider(thickness=1))
                log.flag = False
            log.controls.append(
                ft.Markdown(
                    value=f"**You:** {msg}",
                    selectable=True,
                    on_tap_link=handle_link
                )
            )
        elif role == 1:
            log.flag = True
            log.controls.append(ft.Markdown(
                value=msg, selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                on_tap_link=handle_link
            ))
            page.update()

    async def send(e):
        q = inp.value.strip()
        if not q:
            return
        inp.value = ""
        if len(log.controls) > 0:
            log.controls.append(ft.Divider(thickness=1))
        log.controls.append(
            ft.Markdown(
                value=f"**You:** {q}",
                selectable=True,
                on_tap_link=handle_link
            )
        )
        out = ft.Markdown(value=f"*{waitmsg}*", selectable=False, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB)
        log.controls.append(out)
        send_btn.disabled = True
        page.update()
        response_text = await do(q)
        out.value = response_text
        out.selectable = True
        send_btn.disabled = False
        await inp.focus()
        page.update()
    inp.on_submit = lambda e: page.run_task(send, e)
    send_btn.on_click = lambda e: page.run_task(send, e)
    return [ft.Container(content=log, expand=True), ft.Row([inp, send_btn])], append

