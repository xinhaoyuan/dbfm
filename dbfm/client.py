import requests

from . import common

class DoubanClient(object):

    def __init__(self, login_data):
        self.login_data = login_data
        self._cookies = self.login_data['cookies']
        self._channel_id = 2
        self._queue = []
        pass

    def _request_url(self, ptype, **data):
        """
        这里包装了一个函数,发送post_data
        :param ptype: n 列表无歌曲,返回新列表
                      e 发送歌曲完毕
                      b 不再播放,返回新列表
                      s 下一首,返回新的列表
                      r 标记喜欢
                      u 取消标记喜欢
        """
        options = {
            'type': ptype,
            'pt': '3.1',
            'channel': self._channel_id,
            'pb': '320',
            'from': 'mainsite',
            'r': '',
            'kbps': '320',
            'app_name': 'radio_website',
            'client': 's:mainsite|y:3.0',
            'version': '100'
        }
        if 'sid' in data:
            options['sid'] = data['sid']
            pass
        url = 'https://douban.fm/j/v2/playlist'
        while True:
            try:
                s = requests.get(url, params=options,
                                 cookies=self._cookies, headers = common.HEADERS)
                req_json = s.json()
                if req_json['r'] == 0:
                    if 'song' not in req_json or not req_json['song']:
                        break
                    return req_json['song']
            except Exception as err:
                raise err
            break
        return None

    def append_songs(self, songs):
        for s in songs:
            self._queue.append(s)
        pass

    def refresh_playlist(self, data = None):
        self._queue = []
        if data is None:
            self.append_songs(self._request_url("n"))
        else:
            self.append_songs(data)
        pass

    def get_next_song(self, channel_id = None):
        if channel_id is not None:
            self.set_channel_id(channel_id)
        retry = 3
        while len(self._queue) == 0 and retry > 0:
            self.refresh_playlist()
            retry -= 1
            pass
        if len(self._queue) == 0:
            raise Exception("Cannot get new song")
        return self._queue.pop(0)

    def set_channel_id(self, id):
        self._channel_id = id
        self._queue = []
        pass

    def get_channel_id(self):
        return self._channel_id

    def rate(self, sid, rating):
        if rating < 0:
            self.refresh_playlist(self._request_url("b", sid = sid))
        elif rating == 0:
            self._request_url("u", sid = sid)
        else:
            self._request_url("r", sid = sid)
