from elasticsearch import Elasticsearch
import datetime
import re
import textwrap


class MyClass():
    """docstring for ClassName"""

    def __init__(self, CID, numberday,fromsize=0,size=500):
        self.CID = CID
        self.numberday = numberday
        self.T=[]
        self.fromsize=fromsize
        self.size=size
        self.totallogs = 0

        self.start_data()


    def total_day(self, numberday):  # 获取最近几天天UTC日期
        fif = []
        now = datetime.datetime.utcnow()
        for i in range(1, numberday):
            fif.append((now - datetime.timedelta(days=(i - 1))).__format__('%Y-%m-%d'))
        # allday=datetostr(fif)
        return fif

    def get_main_data(self, find_result):
        T = []
        Host = []
        M = []
        for hit in find_result['hits']['hits']:
            T.append(hit["_source"]["T"])
            Host.append(hit["_source"]["host"]["name"])
            M.append(hit["_source"]["M"])
        self.totallogs = find_result["hits"]["total"]
        return T, Host, M

    def get_index(self, args):  # 获取最近15天所有index索引
        es_index = []
        for i in range(0, len(args)):
            es_index.append('vdmp-online-' + args[i])
        return es_index

    def date_null(self, k):
        s = ''
        try:
            if k :
                s = k.group(1)
            else:
                s = ''
        except Exception as e:
            s=""
        return s
    def countfirmofflinetime(self,a,b):
        a1=datetime.datetime.utcfromtimestamp(a)
        b1=datetime.datetime.utcfromtimestamp(b)
        ss=(b1-a1).seconds
        return ss
    def judeWhthertimeexist(self,a,b):
        if a and b:
            if int(a.group(1)) != 0 and int(b.group(1)) != 0:
                wifiofftime = self.countfirmofflinetime(int(a.group(1)),int(b.group(1)))
                return wifiofftime
            else:
                return 0
        else:
            return 0

    def onoffline_data(self, T, Host, M):  # 获取日志关键字信息
        offlinetime=0
        pat1 = r"client\[(.*?)\] publish"
        pat2 = r"\"initState\":\"(.*?)\""
        pat3 = r"\"routerMac\":\"(.*?)\""
        pat4 = r"\"rssi\":(-\d{2})"
        pat5 = r"\"retry\":\"(.*?)\""
        pat6 = r"\'T\': \'(.*?)\'"
        pat7 = r"\'host\': \{\'name\': \'(.*?)\'\}"
        pat8 = re.compile("\"wifiName\":\"(.*?)\"")
        pat9 = re.compile("\"firmVersion\":\"(.*?)\"")
        wifiDisTs=re.compile("\"wifiDisTs\":(.*?),")
        wifiRecTs=re.compile("\"wifiRecTs\":(.*?),")
        mqttDisTs=re.compile("\"mqttDisTs\":(.*?),")
        mqttRecTs=re.compile("\"mqttRecTs\":(.*?),")
        mucversion=re.compile("\"mcuVersion\":\"(.*?)\"")
        self.cid = ["CID"]
        self.onoffline = ["重连原因"]
        self.routermac = ["routermac"]
        self.RSSI = ["RSSI"]
        self.retry = ["重连情况"]
        self.time = []
        self.host_name = ["重连服务器"]
        self.wifiName=["WIFI名"]
        self.firmVersion=["固件版本"]
        self.fimuploadofftime=["掉线时长"]
        self.mcuversion=["mcuVersion"]

        for i in range(0, len(T)):
            self.cid.append(self.date_null(re.search(pat1, M[i])))
            self.onoffline.append(self.date_null(re.search(pat2, M[i])))
            self.routermac.append(self.date_null(re.search(pat3, M[i])))
            self.RSSI.append(self.date_null(re.search(pat4, M[i])))
            self.retry.append(self.date_null(re.search(pat5, M[i])))
            self.wifiName.append(self.date_null(pat8.search(M[i])))
            self.firmVersion.append(self.date_null(pat9.search(M[i])))
            self.mcuversion.append(self.date_null(mucversion.search(M[i])))
            self.time.append(str(T[i]))
            self.host_name.append(Host[i])
            if self.date_null(re.search(pat2, M[i])) == "Network":
                wifi=self.judeWhthertimeexist(wifiDisTs.search(M[i]),wifiRecTs.search(M[i]))
                mqtt=self.judeWhthertimeexist(mqttDisTs.search(M[i]),mqttRecTs.search(M[i]))
                self.fimuploadofftime.append(str(wifi+mqtt))
            elif self.date_null(re.search(pat2, M[i])) == "Wifi":
                wifi1 = self.judeWhthertimeexist(wifiDisTs.search(M[i]), wifiRecTs.search(M[i]))
                mqtt1 = self.judeWhthertimeexist(mqttDisTs.search(M[i]), mqttRecTs.search(M[i]))
                self.fimuploadofftime.append(str(wifi1+mqtt1))
            else:
                self.fimuploadofftime.append("")


        self.count_Network = 0
        self.count_Wifi = 0
        self.count_PowerOn = 0
        self.count_ConfigNet = 0
        self.count_upgrade = 0
        for i in range(0, len(self.cid)):
            if self.onoffline[i] == "Network":
                self.count_Network = self.count_Network + 1
            elif self.onoffline[i] == "Wifi":
                self.count_Wifi = self.count_Wifi + 1
            elif self.onoffline[i] == "PowerOn":
                self.count_PowerOn = self.count_PowerOn + 1
            elif self.onoffline[i] == "ConfigNet":
                self.count_ConfigNet = self.count_ConfigNet + 1
            else:
                self.count_upgrade = self.count_upgrade + 1

    def gettimedetail(self, time):
        self.date = ["日期"]
        self.second = ["时间"]
        self.accurate = ["秒"]
        pat1 = r"(\d{4}-\d{2}-\d{2})T"
        pat2 = r"T(\d{2}:\d{2}:\d{2})"
        pat3 = r"T\d{2}:\d{2}:\d{2}\.(\d{5})"
        self.date = self.date + re.findall(pat1, str(time))
        self.second = self.second + re.findall(pat2, str(time))
        self.accurate = self.accurate + re.findall(pat3, str(time))
        return self.date, self.second, self.accurate

    def get_source(self):
        # es = Elasticsearch("http://elk.vesync.com:9200/?_source=T,M,host.name")
        # dates=fiftenndaystonow()
        # es_index=get_index(dates)#获取最近15天UTC日期
        # CID="0LbXNVUq42_9wVTfclu1eRfphSRwGk01"
        body = {
            "size":500,  # 返回查询条数
            "from":0,  # 返回起始页
            "sort": {"T": {"order": "desc"}},  # 排序
            "_source": ["M", "T", "host.name"],  # 返回指定字段
            "query": {
                "bool": {
                    "minimum_should_match": 2,
                    "must": {
                        "match": {
                            "M": {
                                "operator": "and",
                                "query": "initstate publish"
                            }
                        }
                    },
                    "should": [
                        {
                            "match": {
                                "M": "received"
                            }
                        },
                        {
                            "match": {
                                "M": "send"
                            }
                        },
                        {"match_phrase": {
                            "M": {
                                "query": "{}".format(self.CID)
                            }
                        }}
                    ]
                }
            }

        }
        body["size"]=self.size
        body["from"]=self.fromsize
        return body

    def start_data(self):
        es = Elasticsearch("http://elk.vesync.com:9200")
        dates = self.total_day(self.numberday)
        es_index = self.get_index(dates)  # 获取最近15天UTC日期
        try:
            find_result = es.search(index=es_index, body=self.get_source(),ignore_unavailable=True)
        except Exception as e:
            self.err=e
            raise
        self.T, self.HOST, self.M = self.get_main_data(find_result)
        self.onoffline_data(self.T, self.HOST, self.M)
        self.gettimedetail(self.T)

    def get_cid(self):
        return self.cid

    def get_onoffline(self):
        return self.onoffline

    def get_routermac(self):
        return self.routermac

    def get_RSSI(self):
        return self.RSSI

    def get_retry(self):
        return self.retry

    def get_time(self):
        return self.time

    def get_host_name(self):
        return self.host_name

    def get_count_Network(self):
        return self.count_Network

    def get_count_Wifi(self):
        return self.count_Wifi

    def get_count_PowerOn(self):
        return self.count_PowerOn

    def get_count_ConfigNet(self):
        return self.count_ConfigNet

    def get_count_upgrade(self):
        return self.count_upgrade

    def get_date(self):
        return self.date

    def get_second(self):
        return self.second

    def get_accurate(self):
        return self.accurate
    def get_T(self):
        sss=["时间"]
        for i in range (1,len(self.get_date())):
            sss.append((self.get_date()[i]+"  "+self.get_second()[i]+":"+self.get_accurate()[i]))
        return sss
    def get_wifiName(self):
        return self.wifiName

    def get_firmVersion(self):
        return self.firmVersion

    def get_total_logs(self):
        return self.totallogs
    def get_fimuploadofftime(self):
        return self.fimuploadofftime
    def get_mcuVersion(self):
        return self.mcuversion

# onofflinedata=MyClass("0Lfwzc2VKXg_9OWRzddqDjfrOfuBDShA",14)
# all_data = []
# all_data.append(onofflinedata.get_date())
# all_data.append(onofflinedata.get_second())
# all_data.append(onofflinedata.get_accurate())
# all_data.append(onofflinedata.get_onoffline())
# all_data.append(onofflinedata.get_routermac())
# all_data.append(onofflinedata.get_RSSI())
# all_data.append(onofflinedata.get_retry())
# all_data.append(onofflinedata.get_host_name())
# for i in range(0, len(all_data)):  # 总列数
#     for j in range(1, len(all_data[0])):  # 总数据行数
#         print(all_data[i][j])


