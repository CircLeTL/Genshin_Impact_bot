
from ..config import SECONDARY_LEVEL_PROBABILITY

import os
import json
import random


FILE_PATH = os.path.dirname(__file__)

ARTIFACT_LIST = {}
ARTIFACT_PROPERTY = []
PROPERTY_LIST = {}



artifact_obtain = {}
flower,feather,hourglass,cup,crown = (0,1,2,3,4)


def init_json():
    # 读取join文件
    # 初始化常量
    global ARTIFACT_LIST
    global ARTIFACT_PROPERTY
    global PROPERTY_LIST
    global artifact_obtain

    with open(os.path.join(FILE_PATH,"artifact_list.json"),"r",encoding="UTF-8") as f:
        ARTIFACT_LIST = json.load(f)

    with open(os.path.join(FILE_PATH,"artifact_property.json"),"r",encoding="UTF-8") as f:
        ARTIFACT_PROPERTY = json.load(f)

    with open(os.path.join(FILE_PATH,"property_list.json"),"r",encoding="UTF-8") as f:
        PROPERTY_LIST = json.load(f)

    for suit_name in ARTIFACT_LIST.keys():
        obtain = ARTIFACT_LIST[suit_name]["obtain"]
        if obtain in artifact_obtain:
            artifact_obtain[obtain].append(suit_name)
        else:
            artifact_obtain[obtain] = []
            artifact_obtain[obtain].append(suit_name)

init_json()



class Artifact(object):
    def __init__(self, property = None):
        # property是一个圣遗物名称字符串或者圣遗物属性字典
        # 使用名称字符串初始化会随机圣遗物的属性
        if property.__class__.__name__ == "str":
            self._name_init(property)
        elif property.__class__.__name__ == "dict":
            self._dict_init(property)
        else:
            raise ValueError("你需要提供圣遗物名称字符串或一个字典对象")

    def _name_init(self,_name):
        # 名称初始化圣遗物
        self.name = _name
        self.suit_name = self.get_suit_name(self.name)
        self.level = 0
        self.artifact_type = self.get_artifact_type(self.suit_name,self.name)
        self.main = self.get_random_main()
        self.initial_secondary = {}
        self.initialize_secondary()
        self.strengthen_secondary_list = []

    def _dict_init(self,property):
        # 字典初始化圣遗物
        for key in property.keys():
            self.__dict__[key] = property[key]

    def __getitem__(self, key):
        return self.__dict__[key]

    @staticmethod
    def get_suit_name(_name):
        # 根据部件的名称获取套装名
        for suit in ARTIFACT_LIST.keys():
            for name in ARTIFACT_LIST[suit]["element"]:
                if name == _name:
                    return suit

    @staticmethod
    def get_artifact_type(suit,name):
        # suit表示套装名称，name表示部件名称
        # 查询圣遗物部件在套装中是哪个位置，返回一个整数
        # 从0到4分别表示 花 羽毛 沙漏 杯 头冠
        for i in range(5):
            if name == ARTIFACT_LIST[suit]["element"][i]:
                return i

    @staticmethod
    def number_to_str(number):
        # 把数字转换成str并添加%符号
        # 小于1的是百分比字符串，属性为数值或元素精通用整数，其他用浮点数
        if number < 1 :
            return ('%.1f'% number*100) + "%"
        else:
            return str(int(number))

    def get_random_main(self):
        # 获取一个随机的主属性
        return random.choice(ARTIFACT_PROPERTY[self.artifact_type]["property_list"])

    def get_random_secondary(self):
        # 获取一个不重复的随机副属性

        temp_set = set(ARTIFACT_PROPERTY[5]["property_list"])
        temp_set.difference({self.main})
        temp_set.difference(set(self.get_all_secondary()))
        return random.choice(list(temp_set))

    def get_secondary_value(self,secondary_name):
        # 获取一个副属性的值
        # 每个副属性都有4个等级的值，表示出现或升级时的提升量，详情看property_list.json
        # 副属性4个等级的概率在config.py的SECONDARY_LEVEL_PROBABILITY里
        r = random.random()

        if r < SECONDARY_LEVEL_PROBABILITY[0]:
            return PROPERTY_LIST["secondary"][secondary_name]["level"][0]

        if r < ( SECONDARY_LEVEL_PROBABILITY[0] + SECONDARY_LEVEL_PROBABILITY[1] ):
            return PROPERTY_LIST["secondary"][secondary_name]["level"][1]

        if r < ( SECONDARY_LEVEL_PROBABILITY[0] + SECONDARY_LEVEL_PROBABILITY[1] + SECONDARY_LEVEL_PROBABILITY[2] ):
            return PROPERTY_LIST["secondary"][secondary_name]["level"][2]

        return PROPERTY_LIST["secondary"][secondary_name]["level"][3]

    def get_all_secondary(self):
        # 获取当前所有的副属性名称
        strengthen_secondary_list = [i["property"] for i in self.strengthen_secondary_list]
        temp_list = list(self.initial_secondary.keys())
        temp_list.extend(strengthen_secondary_list)
        temp_list = list(set(temp_list))
        return temp_list

    def initialize_secondary(self):
        # 初始化副属性
        # 这个方法会直接修改self.initial_secondary

        # 随机初始副属性的个数
        number = random.randint(3,4)

        for _ in range(number):
            secondary = self.get_random_secondary()
            secondary_value = self.get_secondary_value(secondary)
            self.initial_secondary[secondary] = secondary_value

    def strengthen(self):
        # 对圣遗物进行1次强化
        # 这个方法会返回一个字典，记录强化过程信息

        self.level += 1
        secondary = ""
        secondary_value = 0
        strengthen_type = ""

        if self.level % 4 == 0:
            if len(self.initial_secondary) + len(self.strengthen_secondary_list) < 4:

                secondary = self.get_random_secondary()
                secondary_value = self.get_secondary_value(secondary)
                strengthen_type = "add"
                self.strengthen_secondary_list.append({"type": strengthen_type, "property": secondary, "value": secondary_value})

            else:
                # 获取所有副属性
                temp_list = self.get_all_secondary()

                secondary = random.choice(temp_list)
                secondary_value = self.get_secondary_value(secondary)
                strengthen_type = "up"
                self.strengthen_secondary_list.append({"type": strengthen_type, "property": secondary, "value": secondary_value})

        return {"level":self.level,"strengthen_type":strengthen_type,"secondary":secondary,"secondary_value":secondary_value}

    def re_init(self):
        # 圣遗物洗点
        self._name_init(self.name)

    def get_artifact_dict(self):
        # 把圣遗物信息打包成dict返回
        return self.__dict__

    def get_artifact_text(self):
        # 圣遗物详情

        if self.level == 20:
            # 强满后主属性直接获取最大值，否则用初始值加上强化等级乘以成长值
            main_property_value = PROPERTY_LIST["main"][self.main]["max"]
        else:
            main_property_value = PROPERTY_LIST["main"][self.main]["initial_value"] + self.level * PROPERTY_LIST["main"][self.main]["growth_value"]

        # 累加初始和强化副属性的值
        secondary_property_value = {}
        for secondary in self.get_all_secondary():
            secondary_property_value[secondary] = 0
        for key in self.initial_secondary.keys():
            secondary_property_value[key] += self.initial_secondary[key]
        for i in self.strengthen_secondary_list:
            secondary_property_value[i["property"]] += i["value"]

        mes = ""
        mes += f"{self.name}\n"
        mes += f"{ARTIFACT_PROPERTY[self.artifact_type]['name']}\n"
        mes += f"{PROPERTY_LIST['main'][self.main]['txt']}   {self.number_to_str(main_property_value)}\n"
        mes += f"★★★★★\n"
        mes += f"+{self.level}\n"
        for secondary in secondary_property_value.keys():
            mes += f"• {PROPERTY_LIST['secondary'][secondary]['txt']} +{self.number_to_str(secondary_property_value[secondary])}\n"

        return mes











