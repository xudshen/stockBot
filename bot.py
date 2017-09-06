# coding=utf8
import re
from datetime import datetime
from time import mktime
from urllib.parse import urlparse, parse_qs

import itchat
import rx
from bs4 import BeautifulSoup
from rx import Observable

import Config
import RssReader
from wencai import WencaiApi
from xiaoice import xiaoiceApi

config = Config.read_from_file()
itchat.auto_login(hotReload=True, enableCmdQR=2)


class WaitingMessage:
    def __init__(self, msg_id, msg_text, from_user, from_user_nick_name):
        self.msg_id = msg_id
        self.msg_text = re.sub("\@(\S+)", "", msg_text)
        self.from_user = from_user
        self.from_user_nick_name = from_user_nick_name
        self.waiting = False

    def encode_msg(self):
        return self.msg_text


guoguoGroup = itchat.search_chatrooms(name=config.target_group)[0]['UserName']


def process_waiting(msg: WaitingMessage):
    if msg is None:
        return

    wencai_result = WencaiApi().chat(msg.encode_msg())
    if wencai_result is not None:
        itchat.send(u'@%s\u2005%s' % (msg.from_user_nick_name, wencai_result),
                    toUserName=msg.from_user)
        return

    xiaoice_result = xiaoiceApi().chat(msg.encode_msg())
    if xiaoice_result["status"] == "succeed":
        itchat.send(u'@%s\u2005%s' % (msg.from_user_nick_name, xiaoice_result["text"]),
                    toUserName=msg.from_user)
    else:
        itchat.send(u'@%s\u2005%s' % (msg.from_user_nick_name, "what?"),
                    toUserName=msg.from_user)


xiaoice_subject = rx.subjects.ReplaySubject(None)
xiaoice_subject.subscribe(process_waiting)


@itchat.msg_register('Text', isGroupChat=True)
def group_reply(msg):
    if msg['isAt']:
        waiting_msg = WaitingMessage(msg['MsgId'], msg['Text'], msg['FromUserName'], msg['ActualNickName'])
        xiaoice_subject.on_next(waiting_msg)


rss_map = {}
if len(config.rss_config) == 0:
    config.first_init()
for rss_url in config.rss_config.keys():
    print(rss_url)
    rss_map[rss_url] = RssReader.RssReader(rss_url)


def query_all_rss(_):
    for rss_url, rss in rss_map.items():
        rss.parse()
        print(
            "fetching:" + rss_url + ", last_time" + config.get_rss_last_time(rss_url).strftime("%Y-%m-%d %H:%M:%S.%f"))
        for entry in rss.get_entries_after_time(config.get_rss_last_time(rss_url)):
            url = rss.get_entry_link(entry)
            query = urlparse(url).query
            oriUrl = parse_qs(query)["url"]
            itchat.send("⚡️又有大新闻了惹⚡️" + "\n" + BeautifulSoup(entry.title, "html.parser").get_text() + "\n" + oriUrl[0],
                        toUserName=guoguoGroup)
        config.update_rss_time(rss_url, datetime.fromtimestamp(mktime(rss.get_entries_latest_time())))
    Config.save_to_file(config)


Observable.interval(5 * 60 * 1000) \
    .subscribe(query_all_rss)

itchat.run()
