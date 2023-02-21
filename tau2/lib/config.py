import os, sys, toml

def load_config():
    try:
        cfg_filename = os.environ["TAU_CONFIG"]
    except KeyError:
        cfg_filename = "~/.config/tau/tau.toml"

    cfg_filename = os.path.expanduser(cfg_filename)

    try:
        with open(cfg_filename) as f:
            cfg = toml.load(f)
    except toml.TomlDecodeError:
        print("error: decoding toml failed", file=sys.stderr)
        return None
    except FileNotFoundError:
        return None

    return cfg

def get(attr, default_value):
    if (cfg := load_config()) is None:
        return default_value
    try:
        return cfg[attr]
    except KeyError:
        return default_value

