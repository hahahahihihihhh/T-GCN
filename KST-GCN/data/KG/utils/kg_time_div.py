import os.path
import random
from collections import defaultdict
from dict import poi_type2en, ent_word2descr
import pandas as pd
from datetime import datetime, timedelta


sz_assist_kg_path = '../sz_assist_kg.csv'
# 设置起始时间和结束时间
start_time = datetime.strptime("2015/1/1_0:00", "%Y/%m/%d_%H:%M")
end_time = datetime.strptime("2015/1/31_23:45", "%Y/%m/%d_%H:%M")
kg_path = "../time_slot_kg/"
delta = timedelta(minutes=15)
time_slot_kg = dict()


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def save_entity2text(entities, path):
    with open(path, "w") as file:
        for _ent in entities:
            if _ent in ent_word2descr.keys():
                file.writelines(_ent + '\t' + ent_word2descr[_ent] + '\n')
            else:
                file.writelines(_ent + '\t' + _ent.replace('_', ' ') + '\n')

def save_relation2text(relations, path):
    with open(path, "w") as file:
        for _rel in relations:
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

def save_tsv(triplets, path):
    with open(path, "w") as file:
        for _triple in triplets:
            file.writelines('\t'.join(_triple) + '\n')
cnt = 0
# 存储对应时间片的知识图谱、实体集、关系集
def kg_store(kg, entities, relations, time):
    kg = kg[time]
    entities = entities[time]
    relations = relations[time]
    random.seed(7092)
    random.shuffle(kg)
    train_len = int(len(kg) * 0.8)
    time_slot_path = os.path.join(kg_path, time.replace('/', '_').replace(':', '_'))
    mkdir(time_slot_path)
    save_tsv(kg[:train_len], os.path.join(time_slot_path, "train.tsv")) # 保存训练集
    save_tsv(kg[train_len:], os.path.join(time_slot_path, "dev.tsv")) # 保存测试集
    save_entity2text(sorted(list(entities)), os.path.join(time_slot_path, "entity2text.txt"))   # 保存实体集
    save_relation2text(sorted(list(relations)), os.path.join(time_slot_path, "relation2text.txt"))  # 保存关系集
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