#!/usr/bin/python
import asyncio, json, os, sys, tempfile
from datetime import datetime
from tabulate import tabulate
from colorama import Fore, Back, Style

import api, lib

USERNAME = "Anonymous"

async def add_task(task_args):
    task = {
        "blob_idx": lib.util.random_blob_idx(),
        "assigned": [],
        "title": None,
        "desc": None,
        "tags": [],
        "project": None,
        # Default status
        "status": "open",
        "rank": None,
        "due": None,
        "created": lib.util.now(),
        "events": [],
    }
    # Everything that isn't an attribute is part of the title
    # Open text editor is desc isn't set to write desc text
    title_words = []
    for arg in task_args:
        if arg[0] == "+":
            tag = arg[1:]
            task["tags"].append(tag)
        elif arg[0] == "@":
            assign = arg[1:]
            task["assigned"].append(assign)
        elif ":" in arg:
            attr, val = arg.split(":", 1)
            set_task_attr(task, attr, val)
        else:
            title_words.append(arg)

    title = " ".join(title_words)
    task["title"] = title
    if task["desc"] is None:
        task["desc"] = prompt_description_text()

    print(json.dumps(task, indent=2))

    id = await api.add_task(task)
    print(f"Created task {id}.")

def prompt_text(comment_lines):
    temp = tempfile.NamedTemporaryFile()
    temp.write(b"\n")
    for line in comment_lines:
        temp.write(line.encode() + b"\n")
    temp.flush()
    editor = os.environ.get('EDITOR', 'nvim')
    os.system(f"{editor} {temp.name}")
    desc = open(temp.name, "r").read()
    # Remove comments and empty lines from desc
    # TODO: this will also strip blank lines.
    desc = "\n".join(line for line in desc.split("\n")
                     if line and line[0] != "#")
    return desc

def prompt_description_text():
    return prompt_for_text([
        "# Write task description above this line",
        "# These lines will be removed"
    ])

def prompt_comment_text():
    return prompt_for_text([
        "# Write comments above this line",
        "# These lines will be removed"
    ])

def set_task_attr(task, attr, val):
    templ = lib.util.task_template
    assert attr != "blob_idx"
    assert attr in ["desc", "rank", "due", "project"]
    assert templ[attr] != list

    if val.lower() == "none":
        task[attr] = None
    else:
        val = convert_attr_val(attr, val)
        task[attr] = val

    lib.util._enforce_task_format(task)

def convert_attr_val(attr, val):
    templ = lib.util.task_template

    if attr in ["desc", "project"]:
        assert templ[attr] == str
        return val
    elif attr == "rank":
        try:
            return float(val)
        except ValueError:
            print("error: rank value isn't convertable to float",
                  file=sys.stderr)
            print()
            raise
    elif attr == "due":
        # Other date formats not yet supported... ez to add
        assert len(val) == 4
        # next year we need to change 22 to 23 lol
        dt = datetime.strptime(f"18:00 {val}22", "%H:%M %d%m%y")
        due = lib.util.datetime_to_unix(dt)
        return due
    else:
        print(f"error: unhandled attr '{attr}' = {val}")
        sys.exit(-1)

async def show_active_tasks():
    tasks = await api.fetch_active_tasks()
    headers = ["ID", "Title", "Status", "Project",
               "Tags", "Assigned", "Rank", "Due"]
    table = []
    for id, task in enumerate(tasks):
        if task is None:
            continue
        title = task["title"]
        status = task["status"]
        project = task["project"]
        tags = " ".join(f"+{tag}" for tag in task["tags"])
        assigned = " ".join(f"@{assign}" for assign in task["assigned"])
        if task["due"] is None:
            due = ""
        else:
            dt = lib.util.unix_to_datetime(task["due"])
            due = dt.strftime("%H:%M %d/%m/%y")
        rank = task["rank"] if task["rank"] is not None else ""

        if status == "start":
            id =        Fore.GREEN + str(id)        + Style.RESET_ALL
            title =     Fore.GREEN + str(title)     + Style.RESET_ALL
            status =    Fore.GREEN + str(status)    + Style.RESET_ALL
            project =   Fore.GREEN + str(project)   + Style.RESET_ALL
            tags =      Fore.GREEN + str(tags)      + Style.RESET_ALL
            assigned =  Fore.GREEN + str(assigned)  + Style.RESET_ALL
            rank =      Fore.GREEN + str(rank)      + Style.RESET_ALL
            due =       Fore.GREEN + str(due)       + Style.RESET_ALL
        else:
            #id =        Style.DIM  + str(id)        + Style.RESET_ALL
            #title =     Style.DIM  + str(title)     + Style.RESET_ALL
            #status =    Style.DIM  + str(status)    + Style.RESET_ALL
            #project =   Style.DIM  + str(project)   + Style.RESET_ALL
            tags =      Style.DIM  + str(tags)      + Style.RESET_ALL
            #assigned =  Style.DIM  + str(assigned)  + Style.RESET_ALL
            rank =      Style.DIM  + str(rank)      + Style.RESET_ALL
            due =       Style.DIM  + str(due)       + Style.RESET_ALL

        table.append([
            id,
            title,
            status,
            project,
            tags,
            assigned,
            rank,
            due,
        ])
    print(tabulate(table, headers=headers))

async def show_task(id):
    task = await api.fetch_task(id)
    tags = " ".join(f"+{tag}" for tag in task["tags"])
    assigned = " ".join(f"@{assign}" for assign in task["assigned"])
    rank = task["rank"] if task["rank"] is not None else ""
    if task["due"] is None:
        due = ""
    else:
        dt = lib.util.unix_to_datetime(task["due"])
        due = dt.strftime("%H:%M %d/%m/%y")

    assert task["created"] is not None
    dt = lib.util.unix_to_datetime(task["created"])
    created = dt.strftime("%H:%M %d/%m/%y")

    table = [
        ["Title:", task["title"]],
        ["Description:", task["desc"]],
        ["Status:", task["status"]],
        ["Project:", task["project"]],
        ["Tags:", tags],
        ["Assigned:", assigned],
        ["Rank:", rank],
        ["Due:", due],
        ["Created:", created],
    ]
    print(tabulate(table, headers=["Attribute", "Value"]))
    #print(json.dumps(task, indent=2))

    table = []
    for event in task["events"]:
        cmd, when, args = event[0], event[1], event[2:]
        when = lib.util.unix_to_datetime(when)
        when = dt.strftime("%H:%M %d/%m/%y")
        if cmd == "set":
            who, attr, val = args
            if attr == "due" and val is not None:
                val = lib.util.unix_to_datetime(val)
                val = dt.strftime("%H:%M %d/%m/%y")
            table.append([
                Style.DIM + f"{who} changed {attr} to {val}" + Style.RESET_ALL,
                Style.DIM + when + Style.RESET_ALL
            ])
        elif cmd == "append":
            who, attr, val = args
            table.append([
                Style.DIM + f"{who} added {val} to {attr}" + Style.RESET_ALL,
                Style.DIM + when + Style.RESET_ALL
            ])
        elif cmd == "removed":
            who, attr, val = args
            table.append([
                Style.DIM + f"{who} removed {val} to {attr}" + Style.RESET_ALL,
                Style.DIM + when + Style.RESET_ALL
            ])
        elif cmd == "comment":
            who, comment = args
            table.append([
                f"{who} said:",
                when
            ])
            table.append([
                "",
                ""
            ])
            table.append([
                comment,
                ""
            ])
    print(tabulate(table))

async def modify_task(id, args):
    changes = []
    for arg in args:
        if arg[0] == "+":
            tag = arg[1:]
            changes.append(("append", "tags", tag))
        elif arg[0] == "-":
            tag = arg[1:]
            changes.append(("remove", "tags", tag))
        elif arg[0] == "@":
            assign = arg[1:]
            changes.append(("append", "assigned", assign))
        elif ":" in arg:
            attr, val = arg.split(":", 1)
            if val.lower() == "none":
                if attr not in ["project", "rank", "due"]:
                    print(f"error: invalid you cannot set {attr} to none",
                          file=sys.stderr)
                    return -1
                val = None
            else:
                val = convert_attr_val(attr, val)
            changes.append(("set", attr, val))
        else:
            print(f"warning: unknown arg '{arg}'. Skipping...", file=sys.stderr)
    await api.modify_task(USERNAME, id, changes)
    return 0

async def change_task_status(id, status):
    if not await api.change_task_status(USERNAME, id, status):
        return -1

    task = await api.fetch_task(id)
    assert task is not None
    title = task["title"]
    if status == "start":
        print(f"Started task {id} '{title}'")
    elif status == "pause":
        print(f"Paused task {id} '{title}'")
    elif status == "stop":
        print(f"Completed task {id} '{title}'")
    return 0

async def comment(id, args):
    if not args:
        comment = prompt_comment_text()
    else:
        comment = " ".join(args)

    if not await api.add_task_comment(USERNAME, id, comment):
        return -1

    task = await api.fetch_task(id)
    assert task is not None
    title = task["title"]
    print(f"Commented on task {id} '{title}'")
    return 0

async def main():
    if len(sys.argv) == 1:
        await show_active_tasks()
        return 0

    if sys.argv[1] == "add":
        task_args = sys.argv[2:]
        await add_task(task_args)
        return 0

    try:
        id = int(sys.argv[1])
    except ValueError:
        print("error: invalid ID", file=sys.stderr)
        return -1

    args = sys.argv[2:]

    if not args:
        return await show_task(id)

    subcmd, args = args[0], args[1:]

    if subcmd == "modify":
        if (errc := await modify_task(id, args)) < 0:
            return errc
        return await show_task(id)
    elif subcmd in ["start", "pause", "stop"]:
        status = subcmd
        if (errc := await change_task_status(id, status)) < 0:
            return errc
    elif subcmd == "comment":
        if (errc := await comment(id, args)) < 0:
            return errc

    return 0

asyncio.run(main())

