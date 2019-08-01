An overly simple douban.fm client.

Author (also see Credit): Xinhao Yuan <xinhaoyuan@gmail.com>

## Login

`python3 -m dbfm -l`

## Backend

`python3 -m dbfm`

Use `--help` option to see how to set channel.

## Frontend

It comes with a minimal frontend, which keeps getting songs from douban.fm, and plays them one by one with command template.
By default the template is `mplayer {song_url}` with `{song_url}` replaced by the url retrieved from douban.fm.

`python3 -m dbfm -p`

## Misc

By default, the login token is saved at `$HOME/.cache/doubanfm.token`.

## Credit

Most of the douban.fm protocol code in `login.py` and `client.py` is from `https://github.com/taizilongxu/douban.fm` with MIT License.
