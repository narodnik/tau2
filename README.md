# Install

Dependencies installation:
```
$ pip install -r requirements.txt
```

Put an alias to `client/main.py` in your `~/.bashrc`:

```
alias tau=~/src/tau2/client/main.py
```

Or install the package (and the `tau` command):

```
./setup.py install
```

## Configuration

Copy `tau.sample.toml` to `~/.config/tau/tau.toml` and
edit the file accordingly.

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
$ tau 1 modify @upgr -admin +othertag rank:12 due:0512 -@john
```

This will modify task 1:
* `@upgr`: assigns to *upgr*
* `-admin`: removes the *admin* tag
* `+othertag`: add the *othertag* tag
* `rank:12`: set the rank to 12
* `due:0512`: set the due date to the 5th Dec
* `-@john`: removes john from the assigned list

You can also use the keyword `none` for rank and due.

Comment on a task:

```
# Short one line comment
$ tau 0 comment hello world!!!

# For longer comments. This will open your EDITOR
$ tau 0 comment
```

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

This will show all projects starting with `ops` such as `ops.media`
or `ops.foo`. Projects should be organized in a hierarchy.

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

## Multiple Instances

You can modify `TAU_CONFIG` to switch between multiple instances
of tau for different organizations, or even alias the tau command:

```
alias tau_home="TAU_CONFIG=~/.config/tau/tau_home.toml tau"
```

## Running a Server

Generate a shared secret:

```
$ python generate_secret.py
```

This is only for deploying your own instance or testing.

Then add the shared secret to your config file.

Run the server daemon:

```
$ python server/main.py
```

## Reset and Testing

```
$ rm ~/.config/tau/
```

The server data is stored in `~/.config/tau/data/`.

We have a testing script:

```
$ ./test_tau.sh
```

