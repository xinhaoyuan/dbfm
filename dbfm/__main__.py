import argparse
import pickle
import sys, os
import requests
import time
import subprocess
import json
import errno
import logging

from . import login, common, console

parser = argparse.ArgumentParser()
parser.add_argument("-l", action = "store_true", dest = "to_login")
parser.add_argument("--token-file", dest = "token_file")
parser.add_argument("-p", action = "store_true", dest = "player_mode")
parser.add_argument("--player-cmd", dest = "player_cmd", default = "mplayer {song_url}")
parser.add_argument("--channel-id", dest = "channel_id", type = int)
parser.add_argument("--channel-name", dest = "channel_name")
parser.add_argument("--list-channels", action = "store_true", dest = "list_channels")
parser.add_argument("--logging")
args = parser.parse_args()

if args.logging is not None:
    logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s', filename = args.logging, filemode = "w")
    h = logging.StreamHandler(sys.stderr)
    h.setLevel(logging.DEBUG)
    logging.root.addHandler(h)

if args.token_file is None:
    if "XDG_CONFIG_DIR" in os.environ:
        cache_dir = os.environ["XDG_CACHE_DIR"]
    elif "HOME" in os.environ:
        cache_dir = os.path.join(os.environ["HOME"], ".cache")
    else:
        print("Do not know where is the cache dir")
        sys.exit(1)

    try:
        os.makedirs(cache_dir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(cache_dir):
            pass
        else:
            raise

    args.token_file = os.path.join(cache_dir, "doubanfm.token")

if args.to_login:
    data = login.request_token()
    with open(args.token_file, "wb") as f:
        pickle.dump(data, f)
    print("login information saved to {}".format(args.token_file))
    sys.exit(0)
    pass

if args.list_channels:
    for c in common.CHANNELS:
        print("  {}: {}".format(c["name"], c["id"]))
    sys.exit(0)
    pass

c = console.Console()
r = c.handle_command({"type" : "cmd_init", "token_file" : args.token_file})
if r["type"] != "reply_ok":
    logging.warning("Got error while initialize console. Maybe login again with -l option")
    sys.exit(1)

if args.channel_id is not None:
    r = c.handle_command({ "type" : "cmd_set_channel", "channel_id" : args.channel_id })
    if r["type"] != "reply_ok":
        logging.warning("Got error while set channel id: {}".format(r))
        sys.exit(1)
elif args.channel_name is not None:
    r = c.handle_command({ "type" : "cmd_set_channel", "channel_pattern" : args.channel_name })
    if r["type"] != "reply_ok":
        logging.warning("Got error while set channel name: {}".format(r))
        sys.exit(1)

if args.player_mode:
    try:
        while True:
            r = c.handle_command({"type" : "cmd_next"})
            if r["type"] == "reply_ok":
                subprocess.check_call(args.player_cmd.format(song_url = r["data"]["url"]), shell = True)
            else:
                logging.warning("Got error while retrieving the next song. Wait for 10s.")
                time.sleep(10)
                pass
            pass
        pass
    except KeyboardInterrupt:
        print("Interrupted. Bye!")
else:
    for line in sys.stdin:
        try:
            r = c.handle_command(json.loads(line))
        except:
            logging.exception("Exception in main loop")
            r = {}
            pass
        sys.stdout.write(json.dumps(r))
        sys.stdout.write("\n")
        sys.stdout.flush()
