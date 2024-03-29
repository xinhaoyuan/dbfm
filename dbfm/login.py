# -*- coding: utf-8 -*-
import colorama
from termcolor import colored
import requests
import getpass
import json
import argparse
import pickle
import tempfile
import os
import six

from . import common

colorama.init()

EMAIL_INFO = colored('➔', 'red') + colored(' Email/Phone: ', 'green')
PASS_INFO = colored('➔', 'red') + colored(' Password: ', 'green')
CAPTCHA_INFO = colored('➔', 'red') + colored(' Solution: ', 'green')
ERROR = colored('(╯‵□′)╯︵┻━┻: ', 'red')

def win_login():
    """登陆界面"""
    print("Grabbing captcha ...")
    captcha_id = get_captcha_id()
    path = get_capthca_pic(captcha_id)
    try:
        from subprocess import call
        from os.path import expanduser
        call([expanduser('~') + '/.iterm2/imgcat', path])
    except:
        import webbrowser
        webbrowser.open('file://' + path)
    captcha_solution = six.moves.input(CAPTCHA_INFO)
    email = six.moves.input(EMAIL_INFO)
    password = getpass.getpass(PASS_INFO)
    return email, password, captcha_solution, captcha_id

def request_token():
    """
    通过帐号,密码请求token,返回一个dict
    {
    "user_info": {
        "ck": "-VQY",
        "play_record": {
            "fav_chls_count": 4,
            "liked": 802,
            "banned": 162,
            "played": 28368
        },
        "is_new_user": 0,
        "uid": "taizilongxu",
        "third_party_info": null,
        "url": "http://www.douban.com/people/taizilongxu/",
        "is_dj": false,
        "id": "2053207",
        "is_pro": false,
        "name": "刘小备"
    },
    "r": 0
    }
    """
    while True:
        email, password, captcha_solution, captcha_id = win_login()
        options = {
            'source': 'radio',
            'alias': email,
            'form_password': password,
            'captcha_solution': captcha_solution,
            'captcha_id': captcha_id,
            'task': 'sync_channel_list'
        }
        r = requests.post('https://douban.fm/j/login', data=options, headers=common.HEADERS)
        req_json = json.loads(r.text)
        # req_json = json.loads(r.text)
        if req_json['r'] == 0:
            post_data = {
                # will not save
                'liked': req_json['user_info']['play_record']['liked'],
                'banned': req_json['user_info']['play_record']['banned'],
                'played': req_json['user_info']['play_record']['played'],
                'is_pro': req_json['user_info']['is_pro'],
                'user_name': req_json['user_info']['name'],

                # to save
                'cookies': r.cookies,
                'valume': 50,
                'channel': 0,
                'theme_id': 0
            }
            return post_data

        print(req_json['err_msg'])
        print(ERROR + req_json['err_msg'])

def get_captcha_id():
    try:
        r = requests.get('https://douban.fm/j/new_captcha', headers=common.HEADERS)
        r.raise_for_status()
        return r.text.strip('"')
    except Exception as e:
        raise exception('get captcha id error: ' + str(e))

def get_capthca_pic(captcha_id=None):
    options = {
        'size': 'm',
        'id': captcha_id
    }
    r = requests.get('https://douban.fm/misc/captcha',
                     params=options,
                     headers=common.HEADERS)
    if r.status_code == 200:
        h, path = tempfile.mkstemp(suffix = ".jpg")
        os.close(h)
        print('Download captcha in ' + path)
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        return path
    else:
        print("get captcha pic error with http code:" + str(r.status_code))
        return None
