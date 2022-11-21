# Install

pip install:

* tabulate
* pycryptodome
* colorama

Put an alias to `client/main.py` in your `~/.bashrc`:

```
alias tau=~/src/tau2/client/main.py
```

## Configuration

To give yourself a username, add to `~/.bashrc` these lines:

```
export TAU_USERNAME=foo
```

To configure the session shared key:

```
export TAU_SHARED_SECRET="87b9b70e722d20c046c8dba8d0add1f16307fec33debffec9d001fd20dbca3ee"
```

It must be 32 bytes hexadecimal.

# Usage

```
$ tau add read documents later
Created task 0.

$ tau add rank:4 pay bills due:1112 @john +admin +ops project:core desc:xyz
Created task 1.
```

Now view the tasks:

```
$ tau
  ID  Title                 Status    Project    Tags         Assigned    Rank    Due
----  --------------------  --------  ---------  -----------  ----------  ------  --------------
   0  read documents later  open                                                  
   1  pay bills             open      core       +admin +ops  @john       4.0     17:00 11/12/22
```

To view a task, just use its ID:

```
$ tau 1
Attribute     Value
------------  --------------
Title:        pay bills
Description:  xyz
Status:       open
Project:      core
Tags:         +admin +ops
Assigned:     @john
Rank:         4.0
Due:          17:00 11/12/22
Created:      07:53 19/11/22
```

You can also modify attributes:

```
$ tau 1 modify @upgr -admin +othertag rank:12 due:0512
```

This will modify task 1:
* `@upgr`: assigns to *upgr*
* `-admin`: removes the *admin* tag
* `+othertag`: add the *othertag* tag,
* `rank:12`: set the rank to 12
* `due:0512`: set the due date to the 5th Dec

You can also use the keyword `none` for rank and due.

## Filters

You can filter the tasks using the `show` subcommand:

```
$ tau show +dev @john
```

This will show all the tasks tagged by `+dev` assigned to `@john`.
Whereas to show all `ops` projects you could do:

```
$ tau show project:ops
```

## Change Status

Start working on a task:

```
$ tau 0 start
Started task 0 'read documents later'
```

Pause working on a task:

```
$ tau 0 pause
Paused task 0 'read documents later'
```

To resume the task, simply start it again.

Once you are finished, stop the task:

```
$ tau 0 stop
Completed task 0 'read documents later'
```

Lastly to delete a task:

```
$ tau 1 cancel
Cancelled task 1 'pay bills'
```

That's everything!

# Advanced Stuff

Users can ignore the sections below.
This is mainly for tau dev.

## Running a Server

This is only for deploying your own instance or testing.
Otherwise use the server already provided.

Run the server daemon:

```
$ python server/main.py
```

You also need to edit `client/api.py` where it has the server string
and point it to your server.

## Reset and Testing

```
$ rm ~/.config/tau/
```

The server data is stored in `~/.config/tau/data/`.

We have a testing script:

```
$ ./test_tau.sh
```

