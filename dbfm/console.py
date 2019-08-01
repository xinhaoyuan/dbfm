import sys
import pickle
import json
import re
from .client import DoubanClient
from . import login, common

def get_playable_data(song_data):
    data = {}
    for src in song_data["all_play_sources"]:
        if "url" in src and isinstance(song_data["url"], str):
            data["url"] = src["url"]
            break
        pass
    if "url" not in data and "url" in song_data and isinstance(song_data["url"], str):
        data["url"] = song_data["url"]
        pass

    if "title" in song_data:
        data["title"] = song_data["title"]
        pass

    if "albumtitle" in song_data:
        data["album"] = song_data["albumtitle"]
        pass

    if "singers" in song_data:
        data["singers"] = [ d["name"] for d in song_data["singers"] ]
        pass

    return data

def parse_channel_id(cmd):
    if "channel_pattern" in cmd:
        for c in common.CHANNELS:
            if re.search(cmd["channel_pattern"], c["name"]):
                return c["channel_id"]
            pass
        pass
    elif "channel_id" in cmd:
        for c in common.CHANNELS:
            if cmd["channel_id"] == c["channel_id"]:
                return c["channel_id"]
            pass
        pass
    return None

class Console(object):

    def __init__(self):
        self._client = None
        self._is_error = False
        self._current_sid = None
        pass

    def is_error(self):
        return self._is_error

    def handle_command(self, cmd):
        if self._is_error:
            return { "type" : "reply_error",
                     "message" : "console is in error state" }
        try:
            if cmd["type"] == "cmd_init":
                with open(cmd["token_file"], "rb") as f:
                    data = pickle.load(f)
                    pass
                self._client = DoubanClient(data)
                return { "type" : "reply_ok" }
            elif cmd["type"] == "cmd_next":
                if self._client is None:
                    return { "type" : "reply_error",
                             "message" : "client is not initialized"}
                try:
                    raw_data = self._client.get_next_song()
                    data = get_playable_data(raw_data)
                    if "sid" in raw_data:
                        self._current_sid = raw_data["sid"]
                    else:
                        self._current_sid = None
                    assert("url" in data)
                except e:
                    return { "type" : "reply_error",
                             "message" : "cannot get next song",
                             "details" : str(e) }
                return { "type" : "reply_ok",
                         "data" : data,
                         "raw_data" : raw_data }
            elif cmd["type"] == "cmd_rate":
                if self._client is None:
                    return { "type" : "reply_error",
                             "message" : "client is not initialized"}
                if self._current_sid is not None:
                    self._client.rate(self._current_sid, cmd["rating"])
                    return { "type" : "reply_ok" }
                else:
                    return { "type" : "reply_error",
                             "message" : "current sid not found" }
            elif cmd["type"] == "cmd_get_channel":
                if self._client is None:
                    return { "type" : "reply_error",
                             "message" : "client is not initialized"}
                return { "type" : "reply_ok", "channel_id" : self._client.get_channel_id() }
            elif cmd["type"] == "cmd_set_channel":
                if self._client is None:
                    return { "type" : "reply_error",
                             "message" : "client is not initialized"}
                channel_id = parse_channel_id(cmd)
                if channel_id is not None:
                    self._client.set_channel_id(channel_id)
                    return { "type" : "reply_ok" }
                else:
                    return { "type" : "reply_error",
                             "message" : "invalid channel request" }
                pass
            else:
                return { "type" : "reply_error",
                         "message" : "command not recognized" }
        except Exception as e:
            self._is_error = True
            return { "type" : "reply_error",
                     "message" : "exception while handling command",
                     "details" : str(e) }

if __name__ == "__main__":
    console = Console()
    for line in sys.stdin:
        reply = console.handle_command(json.loads(line.strip()))
        sys.stdout.write(json.dumps(reply))
        sys.stdout.write("\n")
        if console.is_error():
            sys.exit(1)
            pass
        pass
    pass
