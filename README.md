# Install

pip install:

* tabulate
* pycryptodome
* colorama

# Basic Usage

Run the server daemon:

```
$ python server/main.py
```

```
$ tau add read documents later
Created task 1.

$ tau add rank:4 pay bills due:1112 @john +admin +ops project:core desc:xyz
Created task 1.
```

Now view the tasks:

```
$ ./tau
  ID  Title                 Project    Tags         Assigned    Rank    Due
----  --------------------  ---------  -----------  ----------  ------  --------------
   0  read documents later
   1  pay bills             core       +admin +ops  @john       4.0     17:00 11/12/22
```

To view a task, just use its ID:

```
$ ./tau 1
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
Created:      12:17 16/11/22
```

You can also modify attributes:

```
$ tau modify @upgr -admin +othertag rank:12 due:0512
```

# Configuration

To give yourself a username, add to `~/.bashrc` these lines:

```
export TAU_USERNAME=foo
```

To configure the session shared key:

```
export TAU_SHARED_SECRET="87b9b70e722d20c046c8dba8d0add1f16307fec33debffec9d001fd20dbca3ee"
```

It must be 32 bytes hexadecimal.

# Reset and Testing

```
$ rm ~/.config/tau
```

```
$ ./test_tau.sh
```

# TODO

* ~~add changing status: start, pause, stop commands~~
* ~~add comments to discuss tasks~~
* IRC notifications
    * ~~push API for server~~
    * create a bot which listens for events
* general testing and error handling before final deployment

