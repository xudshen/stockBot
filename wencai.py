import copy
import json

import requests
from bs4 import BeautifulSoup


class WencaiApi():
    def __init__(self):
        self.form = {}
        self.loadform()

    def loadform(self):
        with open("./wencai.form") as forms:
            line = forms.readline().strip()
            while line:
                key = line.split(":")[0]
                self.form[key] = line[len(key) + 1:]
                line = forms.readline().strip()

    def parse0(self, infos):
        try:
            content = json.loads(infos[0]["content"])
            subjects = content["data"]["global"]["subjects"]
            subject = subjects[list(subjects.keys())[0]]

            return "{}({}) 今日现价{}, 涨跌幅{}%, {}\n".format(
                subject["name"], subject["hqcode"],
                subject["latest_price"],
                subject["rise_fall_rate"], subject["rise_fall"])
        except:
            return None

    def parse2(self, infos):
        try:
            content = json.loads(infos[2]["content"])
            content2_data = content["data"]
            return "→{}\n→{}\n→短期: {}\n→中期: {}\n→长期: {}\n".format(
                content2_data["_title"],
                BeautifulSoup(content2_data["_content"], "html.parser").get_text(),
                content2_data["_short"], content2_data["_mid"], content2_data["_long"])
        except:
            return None

    def parseTable(self, tables):
        try:
            table = tables[0]
            result = table["title"] + "\n"
            for item in table["tr"]:
                result += "{}({}) 今日现价{}, 涨跌幅{}%\n".format(
                    item[1]["val"], item[0]["val"], item[2]["val"], item[3]["val"])
            return result
        except:
            return None

    def chat(self, input_str):
        form = copy.deepcopy(self.form)
        form["query"] = input_str

        try:
            url = 'https://eq.10jqka.com.cn/wencai/interface.php'
            page = requests.post(url, data=form)
            result = page.json()

            if result["status_code"] != 0:
                return None

            answer = result["answer"][0]
            result_hint = ""

            hint0 = self.parse0(answer["txt"])
            if hint0 is not None:
                result_hint += hint0

            hint2 = self.parse2(answer["txt"])
            if hint2 is not None:
                result_hint += hint2

            table = self.parseTable(answer["table"])
            if table is not None:
                result_hint += table

            if "outside_url" in answer:
                if len(answer["outside_url"]) > 0:
                    result_hint += "查看更多:{}".format(answer["outside_url"])
            return result_hint if result_hint != "" else None
            # hints = content["data"]["result"]["descs"]
        except Exception as e:
            return None
