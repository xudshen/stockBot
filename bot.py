# coding=utf8
import re
from datetime import datetime
from time import mktime
from urllib.parse import urlparse, parse_qs

import itchat
from bs4 import BeautifulSoup
from rx import Observable

import Config
import RssReader

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


class MessageQueue:
    def __init__(self):
        self.stack = list()

    def request_answer(self):
        if len(self.stack) == 0:
            return
        msg = self.stack[0]
        if not msg.waiting:
            itchat.send(msg.encode_msg(), toUserName=xiaoice)
            msg.waiting = True

    def en_queue(self, msg: WaitingMessage):
        self.stack.append(msg)
        self.request_answer()

    def clear_all(self):
        self.stack.clear()


xiaoice = itchat.search_mps(name='小冰')[0]['UserName']
guoguoGroup = itchat.search_chatrooms(name=config.target_group)[0]['UserName']
messageQueue = MessageQueue()


@itchat.msg_register(itchat.content.TEXT, isMpChat=True)
def from_xiaoice(msg):
    if xiaoice != msg["FromUserName"]:
        return
    ice_msg = msg['Text']
    try:
        msg = messageQueue.stack.pop(0)
        while msg.waiting:
            try:
                itchat.send(u'@%s\u2005%s' % (msg.from_user_nick_name, ice_msg), toUserName=msg.from_user)
            except:
                itchat.send(u'@%s\u2005%s' % (msg.from_user_nick_name, "不懂诶"), toUserName=msg.from_user)
            msg = messageQueue.stack.pop(0)
    except:
        pass

    messageQueue.request_answer()


@itchat.msg_register('Text', isGroupChat=True)
def group_reply(msg):
    if msg['isAt']:
        waiting_msg = WaitingMessage(msg['MsgId'], msg['Text'], msg['FromUserName'], msg['ActualNickName'])
        if waiting_msg.encode_msg() == " 重启":
            messageQueue.clear_all()
        else:
            messageQueue.en_queue(waiting_msg)


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
