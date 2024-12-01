import os.path
import random
from collections import defaultdict
from dict import poi_type2en, word2descr
import pandas as pd
from datetime import datetime, timedelta


sz_assist_kg_path = '../sz_assist_kg.csv'
# 设置起始时间和结束时间
start_time = datetime.strptime("2015/1/1_0:00", "%Y/%m/%d_%H:%M")
end_time = datetime.strptime("2015/1/31_23:45", "%Y/%m/%d_%H:%M")
kg_path = "../time_slot_kg/"
delta = timedelta(minutes=15)
time_slot_kg = dict()       # 按照时间片划分知识图谱
voca = ['90217', '95968', '95969', '90218', '90219', '90220', '92899', '92900', '92856', '93851', '93852', '90221',
     '95068', '95069', '95070', '90222', '90223', '90224', '116097', '90225', '90226', '95501', '95502', '95503',
     '116220', '92231', '117189', '92237', '102138', '111380', '92241', '103763', '103764', '112746', '92688', '92689',
     '92690', '92691', '103765', '92694', '92697', '92692', '92693', '111369', '92695', '92696', '99907', '99909',
     '99910', '99881', '99902', '92858', '92878', '93220', '92876', '92877', '92881', '92883', '102121', '102124',
     '101301', '116219', '101298', '101300', '96475', '96484', '94159', '94160', '94161', '94162', '98668', '98669',
     '95970', '94163', '94164', '98670', '102120', '95071', '95072', '95073', '95075', '99880', '99882', '112727',
     '95504', '95505', '95506', '95507', '95598', '95933', '95508', '95934', '95935', '95936', '95570', '95571',
     '95599', '116221', '95915', '99905', '116098', '98671', '95975', '97349', '103351', '96478', '96485', '96486',
     '112141', '96758', '96760', '96761', '102128', '102129', '98662', '99630', '99631', '99632', '98666', '99629',
     '99628', '98672', '99627', '111973', '111974', '99903', '99906', '99904', '112728', '99953', '116100', '101297',
     '101299', '101303', '102122', '101305', '102123', '101302', '101304', '101306', '101307', '111969', '112671',
     '116157', '102134', '102137', '112101', '112102', '112103', '104638', '116099', '111370', '112138', '112139',
     '112140', '112142']
     # '[head_b1]', '[head_b2]', '[head_a1]', '[head_a2]', '[rel_b1]', '[rel_b2]', '[rel_a1]', '[rel_a2]', '[tail_b1]', '[tail_b2]', '[tail_a1]', '[tail_a2]']


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def save_entity2text(entities, path):
    with open(path, "w") as file:
        for _ent in entities:
            if _ent in word2descr.keys():
                file.writelines(_ent + '\t' + word2descr[_ent] + '\n')
            else:
                file.writelines(_ent + '\t' + _ent.replace('_', ' ') + '\n')

def save_relation2text(relations, path):
    with open(path, "w") as file:
        for _rel in relations:
            if _rel in word2descr.keys():
                file.writelines(_rel + '\t' + word2descr[_rel] + '\n')
            else:
                file.writelines(_rel + '\t' + _rel.replace('_', ' ') + '\n')

def time_slot_div():
    current_time = start_time
    while current_time <= end_time:
        time = "{}/{}/{}_{}:{}".format(current_time.year, current_time.month, current_time.day, current_time.hour,
                                       "00" if current_time.minute == 0 else current_time.minute)
        time_slot_kg[time] = []
        current_time += delta
    sz_assist_kg = pd.read_csv(sz_assist_kg_path, sep=',', header=None, encoding='gbk')
    entities_set, relations_set = defaultdict(set), defaultdict(set)
    ind = defaultdict(int)
    for _triple in sz_assist_kg.values:
        _h, _r, _t = _triple
        if (_r == "adj" or _t in poi_type2en.keys()):
            if (_r == "adj"):
                h, r, t = "road_" + str(_h), "adjacent", "road_" + str(_t)
            else:
                h, r, t = "road_" + str(_h), "has_" + str(_r), poi_type2en[_t]
            ind[h] += 1; ind[t] += 1
            for _time in time_slot_kg.keys():
                if _r == "adj":
                    time_slot_kg[_time].append((h, r, t))
                else:
                    time_slot_kg[_time].append((h, r, t))
                entities_set[_time].add(h); entities_set[_time].add(t); relations_set[_time].add(r)
        else:
            h, r, t = "road_" + str(_h), "weather", _t.replace('.', '').lower()
            entities_set[_r].add(h); entities_set[_r].add(t); relations_set[_r].add(r)
            time_slot_kg[_r].append((h, r, t))
    # for _k, _v in ind.items():
    #     print(_k, _v)
    print(len(ind))
    return time_slot_kg, entities_set, relations_set

def save_tsv(triplets, path, ent, rel):
    with open(path, "w") as file:
        for _triple in triplets:
            file.writelines('\t'.join(_triple) + '\n')
    with open(path[:-3] + 'txt', 'w') as file:
        for _triple in triplets:
            _h, _r, _t = ent.index(_triple[0]), rel.index(_triple[1]), ent.index(_triple[2])
            file.writelines('\t'.join((str(_h), str(_r), str(_t))) + '\n')
cnt = 0
# 存储对应时间片的知识图谱、实体集、关系集
def kg_store(kg, entities, relations, time):
    kg = kg[time]
    entities = list(sorted(entities[time]))
    relations = list(sorted(relations[time]))
    random.seed(7092)
    random.shuffle(kg)
    train_len = int(len(kg) * 0.8)
    time_slot_path = os.path.join(kg_path, time.replace('/', '_').replace(':', '_'))
    mkdir(time_slot_path)
    save_tsv(kg[:train_len], os.path.join(time_slot_path, "train.tsv"), entities, relations) # 保存训练集
    save_tsv(kg[train_len:], os.path.join(time_slot_path, "dev.tsv"), entities, relations) # 保存测试集
    save_entity2text(entities, os.path.join(time_slot_path, "entity2text.txt"))   # 保存实体集
    save_relation2text(relations, os.path.join(time_slot_path, "relation2text.txt"))  # 保存关系集
    global cnt
    cnt += 1
    if (cnt == 2):
        exit(0)

def main():
    time_slot_kg, entities_set, relations_set = time_slot_div()
    for _time in time_slot_kg.keys():
        kg_store(time_slot_kg, entities_set, relations_set, _time)

if __name__ == '__main__':
    main()