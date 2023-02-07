import errno, os, posix, stat, sys

def lazy_init_pipe(filename):
    try:
        if not stat.S_ISFIFO(os.lstat(filename).st_mode):
            print(f"warning: there is an existing file {filename}!",
                  file=sys.stderr)
            return False
    except FileNotFoundError:
        # Create the named pipe
        os.mkfifo(filename)
        print(f"Created named pipe for events: {filename}")
    return True

def write_pipe(filename, data):
    if not lazy_init_pipe(filename):
        return

    try:
        f = posix.open(filename, posix.O_WRONLY | posix.O_NONBLOCK)
    except OSError as ex:
        if ex.errno == errno.ENXIO:
            print("warning: dropping event since no subscribers to pipe")
    else:
        with open(f, "w") as f:
            f.write(data)

if __name__ == "__main__":
    # Run this program once to initialize the pipe.
    # Then in another terminal run:
    #
    #     $ cat /tmp/tau2
    #
    # and rerun this program.
    # 
    # You can also explicitly create the named pipe without relying
    # on lazy_init:
    #
    #     $ mkfifo /tmp/tau2
    #
    write_pipe("/tmp/tau2", "hello")

