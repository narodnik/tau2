#!/usr/bin/python3
import asyncio, json, os, sys, tempfile
from datetime import datetime
from tabulate import tabulate
from colorama import Fore, Back, Style

import api, lib

USERNAME = lib.config.get("username", "Anonymous")

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
            if tag in task["tags"]:
                print(f"error: duplicate tag +{tag} in task", file=sys.stderr)
                sys.exit(-1)
            task["tags"].append(tag)
        elif arg[0] == "@":
            assign = arg[1:]
            if assign in task["assigned"]:
                print(f"error: duplicate assigned @{assign} in task", file=sys.stderr)
                sys.exit(-1)
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

    #print(json.dumps(task, indent=2))

    id = await api.add_task(USERNAME, task)
    print(f"Created task {id}.")

def prompt_text(comment_lines):
    temp = tempfile.NamedTemporaryFile()
    temp.write(b"\n")
    for line in comment_lines:
        temp.write(line.encode() + b"\n")
    temp.flush()
    editor = os.environ.get('EDITOR') if os.environ.get('EDITOR') else 'nano'    
    os.system(f"{editor} {temp.name}")
    desc = open(temp.name, "r").read()
    # Remove comments and empty lines from desc
    # TODO: this will also strip blank lines.
    desc = "\n".join(line for line in desc.split("\n")
                     if line and line[0] != "#")
    return desc

def prompt_description_text():
    return prompt_text([
        "# Write task description above this line",
        "# These lines will be removed"
    ])

def prompt_comment_text():
    return prompt_text([
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

    if attr in ["desc", "project", "title"]:
        assert templ[attr] == str
        return val
    elif attr == "rank":
        try:
            return float(val)
        except ValueError:
            print(f"error: rank value {val} isn't convertable to float",
                  file=sys.stderr)
            sys.exit(-1)
    elif attr == "due":
        # Other date formats not yet supported... ez to add
        assert len(val) == 4
        date = datetime.now().date()
        year = int(date.strftime("%Y"))%100
        try:
            dt = datetime.strptime(f"18:00 {val}{year}", "%H:%M %d%m%y")
        except ValueError:
            print(f"error: unknown date format {val}")
            sys.exit(-1)
        due = lib.util.datetime_to_unix(dt)
        return due
    else:
        print(f"error: unhandled attr '{attr}' = {val}")
        sys.exit(-1)

async def show_active_tasks():
    tasks = await api.fetch_active_tasks()
    list_tasks(tasks, [])

async def show_deactive_tasks(month):
    tasks = await api.fetch_deactive_tasks(month)
    list_tasks(tasks, [])

def list_tasks(tasks, filters):
    headers = ["ID", "Title", "Status", "Project",
               "Tags", "Assigned", "Rank", "Due"]
    table_rows = []
    for id, task in enumerate(tasks):
        if task is None:
            continue
        if is_filtered(task, filters):
            continue
        title = task["title"]
        status = task["status"]
        project = task["project"] if task["project"] is not None else ""
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
        elif status == "pause":
            id =        Fore.YELLOW + str(id)        + Style.RESET_ALL
            title =     Fore.YELLOW + str(title)     + Style.RESET_ALL
            status =    Fore.YELLOW + str(status)    + Style.RESET_ALL
            project =   Fore.YELLOW + str(project)   + Style.RESET_ALL
            tags =      Fore.YELLOW + str(tags)      + Style.RESET_ALL
            assigned =  Fore.YELLOW + str(assigned)  + Style.RESET_ALL
            rank =      Fore.YELLOW + str(rank)      + Style.RESET_ALL
            due =       Fore.YELLOW + str(due)       + Style.RESET_ALL
        else:
            #id =        Style.DIM  + str(id)        + Style.RESET_ALL
            #title =     Style.DIM  + str(title)     + Style.RESET_ALL
            #status =    Style.DIM  + str(status)    + Style.RESET_ALL
            #project =   Style.DIM  + str(project)   + Style.RESET_ALL
            tags =      Style.DIM  + str(tags)      + Style.RESET_ALL
            #assigned =  Style.DIM  + str(assigned)  + Style.RESET_ALL
            rank =      Style.DIM  + str(rank)      + Style.RESET_ALL
            due =       Style.DIM  + str(due)       + Style.RESET_ALL

        rank_value = task["rank"] if task["rank"] is not None else 0
        row = [
            id,
            title,
            status,
            project,
            tags,
            assigned,
            rank,
            due,
        ]
        table_rows.append((rank_value, row))

    table = [row for (_, row) in
             sorted(table_rows, key=lambda item: item[0], reverse=True)]
    print(tabulate(table, headers=headers))

async def show_task(id):
    task = await api.fetch_task(id)
    task_table(task)
    return 0

async def show_archive_task(id, month):
    task = await api.fetch_archive_task(id, month)
    task_table(task)
    return 0

def task_table(task):
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
        when = when.strftime("%H:%M %d/%m/%y")
        if cmd == "set":
            who, attr, val = args
            if attr == "due" and val is not None:
                val = lib.util.unix_to_datetime(val)
                val = val.strftime("%H:%M %d/%m/%y")
            table.append([
                Style.DIM + f"{who} changed {attr} to {val}" + Style.RESET_ALL,
                "",
                Style.DIM + when + Style.RESET_ALL
            ])
        elif cmd == "append":
            who, attr, val = args
            if attr == "tags":
                val = f"+{val}"
            elif attr == "assigned":
                val = f"@{val}"
            table.append([
                Style.DIM + f"{who} added {val} to {attr}" + Style.RESET_ALL,
                "",
                Style.DIM + when + Style.RESET_ALL
            ])
        elif cmd == "remove":
            who, attr, val = args
            if attr == "tags":
                val = f"+{val}"
            elif attr == "assigned":
                val = f"@{val}"
            table.append([
                Style.DIM + f"{who} removed {val} from {attr}" + Style.RESET_ALL,
                "",
                Style.DIM + when + Style.RESET_ALL
            ])
        elif cmd == "status":
            who, status = args
            assert status not in ["stop", "cancel"]
            if status == "pause":
                status_verb = "paused"
            elif status == "start":
                status_verb = f"{status}ed"
            else:
                print(f"internal error: unhandled task state {status}",
                      file=sys.stderr)
                sys.exit(-2)

            table.append([
                f"{who} {status_verb} task",
                "",
                Style.DIM + when + Style.RESET_ALL
            ])
        elif cmd == "comment":
            who, comment = args
            table.append([
                f"{who}>",
                comment,
                Style.DIM + when + Style.RESET_ALL
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
    # TODO: fix fetching a task after it's stopped
    task = await api.fetch_task(id)
    assert task is not None
    title = task["title"]

    if not await api.change_task_status(USERNAME, id, status):
        return -1

    if status == "start":
        print(f"Started task {id} '{title}'")
    elif status == "pause":
        print(f"Paused task {id} '{title}'")
    elif status == "stop":
        print(f"Completed task {id} '{title}'")
    elif status == "cancel":
        print(f"Cancelled task {id} '{title}'")

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

def is_filtered(task, filters):
    for fltr in filters:
        if fltr.startswith("+"):
            tag = fltr[1:]
            if tag not in task["tags"]:
                return True
        elif fltr.startswith("@"):
            assign = fltr[1:]
            if assign not in task["assigned"]:
                return True
        elif ":" in fltr:
            attr, val = fltr.split(":", 1)
            if val.lower() == "none":
                if attr not in ["project", "rank", "due"]:
                    print(f"error: invalid you cannot set {attr} to none",
                            file=sys.stderr)
                    sys.exit(-1)
                if task[attr] is not None:
                    return True
            elif attr == "status" :
                if val not in ["open", "start", "pause"]:
                    print(f"error: invalid, filter by {attr} can only be [\"open\", \"start\", \"pause\"]",
                            file=sys.stderr)
                    sys.exit(-1)
                if task["status"] != val:
                    return True
            elif attr == "project":
                if task["project"] is None:
                    return True
                if not task["project"].startswith(val):
                    return True
            else:
                val = convert_attr_val(attr, val)
                if task[attr] != val:
                    return True
        else:
            print(f"error: unknown arg '{fltr}'", file=sys.stderr)
            sys.exit(-1)

    return False

async def main():
    if len(sys.argv) == 1:
        await show_active_tasks()
        return 0

    if sys.argv[1] in ["-h", "--help", "help"]:
        print('''USAGE:
    tau [OPTIONS] [SUBCOMMAND]

OPTIONS:
    -h, --help                   Print help information

SUBCOMMANDS:
    add        Add a new task.
    archive    Show completed tasks.
    comment    Write comment for task by id.
    modify     Modify an existing task by id.
    pause      Pause task(s).
    start      Start task(s).
    stop       Stop task(s).
    help       Show this help text.

Example:
    tau add task one due:0312 rank:1.022 project:zk +lol @sk desc:desc +abc +def
    tau add task two  rank:1.044 project:cr +mol @up desc:desc2
    tau add task three due:0512 project:zy +trol @kk desc:desc3 +who
    tau 1 modify @upgr due:1112 rank:none
    tau 1 modify -mol -xx
    tau 2 start
    tau 1 comment "this is an awesome comment"
    tau 2 pause
    tau archive         # current month's completed tasks
    tau archive 1122    # completed tasks in Nov. 2022
    tau 0 archive 1122  # show info of task completed in Nov. 2022
''')
        return 0
    elif sys.argv[1] == "add":
        task_args = sys.argv[2:]
        await add_task(task_args)
        return 0
    elif sys.argv[1] == "archive":
        if len(sys.argv) > 2:
            if len(sys.argv[2]) == 4:
                month = sys.argv[2]
            else:
                print("error: month must be of format MMYY")
                return -1
        else:
            month = lib.util.current_month()

        await show_deactive_tasks(month)
        return 0
    elif sys.argv[1] == "show":
        if len(sys.argv) > 2:
            filters = sys.argv[2:]
            tasks = await api.fetch_active_tasks()
            #filtered_tasks = apply_filters(tasks, filters)
            list_tasks(tasks, filters)
        else:
            await show_active_tasks()
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
    elif subcmd in ["start", "pause", "stop", "cancel"]:
        status = subcmd
        if (errc := await change_task_status(id, status)) < 0:
            return errc
    elif subcmd == "comment":
        if (errc := await comment(id, args)) < 0:
            return errc
    elif subcmd == "archive":
        if len(args) == 1:
            if len(args[0]) == 4:
                month = args[0]
            else:
                print("Error: month must be of format MMYY")
                return -1
        else:
            month = lib.util.current_month()

        if (errc := await show_archive_task(id, month)) < 0:
            return errc
    else:
        print(f"error: unknown subcommand '{subcmd}'")
        return -1

    return 0

asyncio.run(main())

