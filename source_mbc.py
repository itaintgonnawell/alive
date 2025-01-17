import time
from collections import OrderedDict

import requests

# local
from .model import ChannelItem
from .setup import P, default_headers
from .source_base import SourceBase

logger = P.logger
package_name = P.package_name
ModelSetting = P.ModelSetting


class SourceMBC(SourceBase):
    source_id = "mbc"
    code = {
        "MBC": "0",
        "P_everyone": "2",
        "P_drama": "1",
        "P_music": "3",
        "P_on": "6",
        "P_allthekpop": "4",
        "FM": "sfm",
        "FM4U": "mfm",
        "ALLTHAT": "chm",
    }
    headers = {
        "Host": "mediaapi.imbc.com",
        "Origin": "https://onair.imbc.com",
        "Referer": "https://onair.imbc.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    }

    def get_channel_list(self):
        ret = []
        url = "https://control.imbc.com/Schedule/PCONAIR"
        data = requests.get(url, headers=default_headers, timeout=30).json()
        for cate in ["TVList", "RadioList"]:
            for item in data[cate]:
                if item["ScheduleCode"] not in self.code:
                    continue
                c = ChannelItem(
                    self.source_id, self.code[item["ScheduleCode"]], item["TypeTitle"], None, cate == "TVList"
                )
                c.current = item["Title"]
                ret.append([c.channel_id, c])
        self.channel_list = OrderedDict(ret)
        return self.channel_list

    def get_url(self, channel_id, mode, quality=None):
        if len(channel_id) == 3:
            url = f"https://sminiplay.imbc.com/aacplay.ashx?channel={channel_id}&protocol=M3U8&agent=webapp"
            # logger.debug(url)
            data = requests.get(url, timeout=30).text
            data = data.replace("playlist", "chunklist")
            # logger.debug(data)
            return "redirect", data
        if channel_id != "0":
            url = f"https://mediaapi.imbc.com/Player/OnAirPlusURLUtil?ch={channel_id}&type=PC&t={int(time.time())}"
        else:
            url = f"https://mediaapi.imbc.com/Player/OnAirURLUtil?type=PC&t={int(time.time())}"
        data = requests.get(url, headers=self.headers, timeout=30, verify=False).json()
        url = data["MediaInfo"]["MediaURL"].replace("playlist", "chunklist")
        return "return_after_read", url

    def get_return_data(self, url, mode=None):
        data = requests.get(url, headers=default_headers, timeout=30).text
        # data = self.change_redirect_data(data)
        tmp = url.split("chunklist")
        data = data.replace("media", tmp[0] + "media")
        return data
