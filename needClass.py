import requests,re,json,time
from PyQt5.QtWidgets import QLabel,QApplication,QLineEdit,QTableWidgetItem,QFrame,QAbstractItemView,QPushButton
from PyQt5.QtGui import QMovie,QIcon,QColor
from PyQt5.Qt import QThread
from PyQt5.QtCore import pyqtSignal,Qt,QModelIndex,QRect
from PyQt5.QtWidgets import QTableWidget,QAbstractItemView
from multiprocessing import Process
from datetime import datetime,timedelta
from elasticsearch import Elasticsearch

pressFlag = -1
def getsearchindex(index, days=7,connect="-"):
    totalDays = []
    totalIndex = []
    today = datetime.utcnow()
    for i in range(0, days):
        totalDays.append((today - timedelta(i)).__format__('%Y-%m-%d'))

    for i in totalDays:
        totalIndex.append(index + connect + i)
    return totalIndex
def getbody(query,start = 0,size = 500,isFilter = True,filter = None):
    body = {
        "size": size,  # 返回查询条数
        "from": start,  # 返回起始页
        "sort": {"T": {"order": "desc"}},  # 排序
        "_source": ["M", "T", "host.name"] # 返回指定字段
    }
    if isFilter is not True:
        del body["_source"]
    else:
        if filter is not None:
            if isinstance(filter,type(list)):
                body["_source"] = filter
            else:
                print("body filter need list")
    if isinstance(query,dict):
        for a in query.keys():
            body[a] = query[a]
        return body
    else:
        print("getbody method args need dict type")

def addKeyAndValeToDict(target,exitstarget,value):
    if isinstance(target,dict):
        if exitstarget in target.keys():
            if isinstance(target[exitstarget],dict):
                target[exitstarget]=[target[exitstarget]]
                target[exitstarget].append(value)
            elif isinstance(target[exitstarget],list):
                target[exitstarget].append(value)
            else:
                return target
        else:
            target[exitstarget] = []
            target[exitstarget].append(value)
        return target
    else:
        print("无法将目标数据加入非字典")
        return target

class Tablewidget(QTableWidget):
    def __init__(self,parent):
        super().__init__()
        self.setParent(parent)
        self.frontandnextFlag = []
        self.pat = re.compile(r"<font style='background-color:red;'>(.*?)</font>")
        self.searchbox = QFrame(self)
        self.searchbox.setGeometry(10,50,330,30)
        # self.searchbox.setFrameRect(QRect(10,10,10,10))
        self.searchbox.setStyleSheet("border-radius:2px;background-color:rgb(200,200,200)")
        self.searchbox.setHidden(True)

        self.searchtextbox = QLineEdit(self.searchbox)
        self.searchtextbox.setGeometry(0,0,210,30)
        self.searchtextbox.setStyleSheet("border:none")
        # self.searchtextbox.textChanged.connect(self.searchdata)

        self.search = QPushButton("", self.searchbox)
        self.search.setIcon(QIcon("./pic/search.ico"))
        self.search.setGeometry(210, 0, 30, 30)
        self.search.setStyleSheet("border:none")
        self.search.clicked.connect(self.searchdata)


        self.front  =   QPushButton("",self.searchbox)
        self.front.setIcon(QIcon("./pic/front.ico"))
        self.front.setGeometry(240,0,30,30)
        self.front.setStyleSheet("border:none")
        self.front.clicked.connect(lambda: self.frontandnextpress(-1))

        self.next   =   QPushButton("", self.searchbox)
        self.next.setIcon(QIcon("./pic/next.ico"))
        self.next.setGeometry(270,0,30,30)
        self.next.setStyleSheet("border:none")
        self.next.clicked.connect(lambda: self.frontandnextpress(1))

        self.clo = QPushButton("", self.searchbox)
        self.clo.setIcon(QIcon("./pic/close.ico"))
        self.clo.setGeometry(300, 0, 30, 30)
        self.clo.setStyleSheet("border:none")
        self.clo.clicked.connect(self.searchboxclo)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        # 设置垂直方向滑块像素移动
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        # 设置水平方向滑块像素移动
        self.setEditTriggers(QAbstractItemView.NoEditTriggers | QAbstractItemView.DoubleClicked)
        # 设置表格不可编辑
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # 设置启用右键策略

    def showdata(self, data):
        self.setRowCount(len(data[0]) - 1)
        self.setColumnCount(len(data))
        for i in range(0, len(data)):  # 总列数,显示所有数据
            self.setHorizontalHeaderItem(i, QTableWidgetItem(data[i][0]))
            for j in range(1, len(data[0])):  # 总数据行数
                ss = QTableWidgetItem(data[i][j])
                self.setItem(j - 1, i, ss)
                ss.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 设置所有单元格对齐方式

    def keyPressEvent(self, QkeyEvent):
        if QkeyEvent.key() == Qt.Key_F:
            if QApplication.keyboardModifiers() == Qt.ControlModifier:
                self.searchbox.show()
                self.searchbox.setHidden(False)
                self.searchtextbox.setFocus()
        if QkeyEvent.key() == Qt.Key_Escape:
            if self.searchbox.isHidden():
                pass
            else:
                self.searchbox.setHidden(True)
    def searchdata(self):
        self.frontandnextFlag = []
        global  pressFlag
        pressFlag = -1
        findtext = ""
        if self.searchtextbox.text() == "":
            return
        else:
            try:
                findtext = self.searchtextbox.text().split()[0]
            except IndexError:
                return
        for a in range(self.rowCount()):
            for b in range(self.columnCount()):
                if isinstance(type(self.item(a,b)),type(None)) and isinstance(type(self.cellWidget(a,b)),type(None)):
                    pass
                else:

                    if isinstance(type(self.cellWidget(a,b)),type(QLabel)):
                        if "<font style" in self.cellWidget(a,b).text():
                            d = self.cancelCssFormat(self.cellWidget(a,b).text())
                            celltext = self.cellWidget(a,b).text().replace(
                                "<font style='background-color:red;'>{}</font>".format(d),
                                d)
                            if findtext in celltext:
                                self.cellWidget(a,b).setText(self.setStrkeyColor(celltext,findtext))
                                self.frontandnextFlag.append([a,b])
                            else:
                                self.removeCellWidget(a,b)
                                celltext = celltext.replace("<br>", "\n")
                                self.setItem(a,b,QTableWidgetItem(celltext))
                        else:
                            celltext = self.cellWidget(a,b).text()
                            celltext = celltext.replace("<br>", "\n")
                            self.removeCellWidget(a,b)
                            self.setItem(a,b,QTableWidgetItem(celltext))
                    elif isinstance(type(self.item(a, b)), type(QTableWidgetItem)):
                        if findtext in self.item(a,b).text():
                            celltext = self.item(a,b).text().replace("\n","<br>")
                            celltext = self.setStrkeyColor(celltext,findtext)
                            lab = QLabel(celltext,self)
                            self.setCellWidget(a,b,lab)
                            self.setItem(a,b,QTableWidgetItem(""))
                            self.frontandnextFlag.append([a, b])
                            # print(a,b,type(self.cellWidget(a,b)),type(self.item(a,b)),"\n",lab.text())
                        else:
                            pass
                    else:
                        pass

    def setStrkeyColor(self,strdata,key):
        needstr = strdata.replace(key,"<font style='background-color:red;'>{}</font>".format(key))
        return needstr

    def cancelCssFormat(self,strdata):
        return self.pat.search(strdata).group(1)

    def stecellbackcolor(self,a,b,color=QColor(200,200,200)):
        self.item(a,b).setBackground(QColor(color))

    def searchboxclo(self):
        self.searchtextbox.clear()
        self.searchbox.close()

    def frontandnextpress(self,k):
        global pressFlag
        pressFlag += k
        if pressFlag >= 0 and pressFlag < len(self.frontandnextFlag):
            self.setCurrentCell(self.frontandnextFlag[pressFlag][0],self.frontandnextFlag[pressFlag][1])
        else:
            pressFlag = -1


class GetElasticsearchData():
    def __new__(cls, body,index,es="http://elk.vesync.com:9200"):
        cls.body=body
        cls.index=index
        cls.es=es
        return super().__new__(cls)
    @classmethod
    def getalldata(cls):
        es = Elasticsearch(cls.es)
        try:
            responseResult = es.search(body=cls.body, index=cls.index, ignore_unavailable=True)
            return responseResult
        except Exception as elasticsearchErr:
            raise

class GetOpsData():
    def __new__(cls, userid):
        cls.userid=userid
        return super().__new__(cls)
    @classmethod
    def getdata(cls):
        url="http://ops.vesync.com:8000/api/getUserInfo?uid={}&envValue=prd".format(cls.userid)
        cookie={"csrftoken":"6xRludy3Ptn4p2Kxk775JAN8xFqKRS7SSwgsDZ1NX8a95qiYawbbVoj6IgrqjLfx", "sessionid":"gtq9q1iux068y61k20kdx8szre9010an"}
        header={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
        rsp=requests.get(url,cookies=cookie,headers=header).json()
        return rsp
class ShowMovieAndOther():
    def __init__(self,fa,usemethod,achieved,args=()):
        fa.showmovie = ShowMovie(fa.width(), fa.height(), fa)
        fa.showmovie.showMovie()
        fa.start = ThreadMethod(usemethod, args)
        fa.start.start()
        fa.start.acheived.connect(fa.showmovie.cloMovie)
        fa.start.acheived.connect(achieved)

class ShowMovie(QLabel):
    def __init__(self,width,height,parent):
        super(ShowMovie,self).__init__()
        self.setParent(parent)
        self.setGeometry(width/2 - 100, height / 2 - 100, 200, 200)
        self.movie = QMovie("./pic/loading.gif")
        self.movie.setScaledSize(self.size())
        self.setMovie(self.movie)
    def showMovie(self):
        self.show()
        self.movie.start()
    def cloMovie(self):
        self.movie.stop()
        self.close()


class ThreadMethod(QThread):
    acheived=pyqtSignal()
    def __init__(self,method,args):
        super(ThreadMethod,self).__init__()
        self.method=method
        self.args=args
        self.stopFlag=False

    def run(self,flag=0):
        if self.args==():
            self.method()
        else:
            self.method(arg for arg in self.args)
        self.acheived.emit()

'''
将字典键解析成a.b.c格式，或者a.b.c解析成对应字典的值
'''
class UsefulMethod():
    def __init__(self):
        pass
    '''
    提取字典的所有键值为a.b.c格式,返回iterable
    '''
    @classmethod
    def getMainkeyAndSonkey(cls, d, sk="", s=[]):
        for k, v in d.items():
            if type(v) is dict:
                if sk == "":
                    sk = k
                else:
                    sk = sk + "." + k
                ddd = UsefulMethod.getMainkeyAndSonkey(v, sk)
                for a in ddd:
                    yield a
                sk = sk.split(".")
                if len(sk) == 1:
                    sk = ""
                else:
                    sk = ".".join(sk[:-1])
                # 因yield使用中，该层字典遍历完成后保存的sk为当前的值，而不是调用函数进行赋值操作，所以需要对sk的值重新定义，切掉末尾的键值
            else:
                if sk == "":
                    yield k
                else:
                    yield (sk + "." + k)
    '''
    访问dictdata的["a","b","c"]元素
    '''
    @classmethod
    def parseindex(cls,dictdata,a):
        try:
            for s in a:
                if len(a) ==0:
                    pass
                elif len(a) == 1:
                    yield dictdata[a[0]]
                else:
                    dd=UsefulMethod.parseindex(dictdata[a[0]],a[1:])
                    for t in dd:
                        yield t
                        return
        except KeyError:
            # yield  None
            yield ""
        except TypeError:
            # yield None
            yield ""
    @classmethod
    def getsignaldictkey(cls,dictdata,keyvalue):
        value=""
        for x in dictdata[keyvalue]:
            value=x
        return value


if __name__ == "__main__":
    s=GetOpsData("1322503").getdata()
    print(s)