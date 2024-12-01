import os.path
import random

import pandas as pd
from datetime import datetime, timedelta

from sklearn.model_selection import train_test_split


def is_chinese(string):
    for char in string:
        if not ('\u4e00' <= char <= '\u9fff'):
            return False
    return True

data_prefix = './debug'
seed = 66
kg = pd.read_csv('../sz_assist_kg.csv', sep=',', encoding='gbk')
kg.columns = ['head', 'relation', 'tail']
time_fmt = "%Y/%m/%d_%H:%M"
ent2id = pd.read_csv('../entity2id.txt', sep = '\t', header = None)
rel2id = pd.read_csv('../relation2id.txt', sep = '\t', header = None)
start_time = datetime.strptime("2015/1/1_0:00", time_fmt)
delta = timedelta(minutes=15)
# tkg, time_slice_len = [], 2976    # 1 month
# tkg, time_slice_len = [], 96  # 1 day
tkg, time_slice_len = [], 4  # 1 hour
ent, rel = [], ['adj', 'weather', 'transportation facilities', 'accommodations', 'enterprises', 'others',
                'medical services', 'education services', 'living services', 'shopping services', 'catering services']
random.seed(seed)

def toTxt(lst: list, data_path: str) -> None:
    with open(os.path.join(data_prefix, data_path), 'w', encoding='utf-8') as f:
        for _tuple in lst:
            line = ""
            for _val in _tuple:
                line += str(_val) + '\t'
            line = line[:-1] + '\n'
            f.write(line)
def er2id() -> (dict, dict):
    global ent, rel
    for _ent, _id in ent2id.values:
        if (not is_chinese(_ent)):
            if (_ent.isdigit()):
                ent.append("road {}".format(_ent))
            else:
                ent.append(_ent)
    for _rel, _id in rel2id.values:
        if (_rel.startswith('2015')):
            continue
        if (_rel != 'adj'):
            ent.append(_rel)
    ent, rel = sorted(list(set(ent))), sorted(list(set(rel)))
    ent2id_dict, rel2id_dict = {}, {}
    ent2id_lst, rel2id_lst  = [], []
    for _id, _ent in enumerate(ent):
        ent2id_dict[_ent] = _id
        ent2id_lst.append((_ent, _id))
    toTxt(ent2id_lst, 'entity2id.txt')
    for _id, _rel in enumerate(rel):
        rel2id_dict[_rel] = _id
        rel2id_lst.append((_rel, _id))
    toTxt(rel2id_lst, 'relation2id.txt')
    return ent2id_dict, rel2id_dict

def tr2id(ent2id_dict: dict, rel2id_dict: dict) -> list:
    cnt = 0
    quadruple = []
    # with open(os.path.join(data_prefix, 'quadruple2id.txt'), 'w', encoding='utf-8') as f:
    for _h, _r, _t in kg.values:
        if (_r.startswith('2015/1/1_0:')):
            cur_time = datetime.strptime(_r, time_fmt)
            time_slice = int((cur_time - start_time).total_seconds() // (60 * 15))
            assert time_slice < time_slice_len
            quadruple.append((ent2id_dict["road {}".format(_h)], rel2id_dict['weather'], ent2id_dict[_t], time_slice))
        elif (_r == 'adj'):
            cnt += 1
            for _time_slice in range(time_slice_len):
                quadruple.append((ent2id_dict["road {}".format(_h)], rel2id_dict[_r], ent2id_dict["road {}".format(_t)], _time_slice))
    toTxt(quadruple, 'triple2id.txt')
    return quadruple

def split(quadruple: list) -> None:
    # 仅划分特征数据
    quadruple_train, quadruple_valid = train_test_split(quadruple, test_size=0.2, random_state=seed)
    # print(quadruple_train, quadruple_valid)
    toTxt(quadruple_train, 'train.txt')
    toTxt(quadruple_valid, 'valid.txt')
    toTxt(quadruple_valid, 'test.txt')
    toTxt([(len(ent), len(rel), time_slice_len)], 'stat.txt')

if __name__ == '__main__':
    ent2id_dict, rel2id_dict = er2id()
    quadruple = tr2id(ent2id_dict, rel2id_dict)
    split(quadruple)

