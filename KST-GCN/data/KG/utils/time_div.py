from collections import defaultdict

import pandas as pd
from datetime import datetime, timedelta


sz_assist_kg_path = '../sz_assist_kg.csv'


# 设置起始时间和结束时间
start_time = datetime.strptime("2015/1/1_0:00", "%Y/%m/%d_%H:%M")
end_time = datetime.strptime("2015/1/31_23:45", "%Y/%m/%d_%H:%M")
# 每次增加 15 分钟
delta = timedelta(minutes=15)
time_slot_kg = dict()

# 迭代输出
current_time = start_time
while current_time <= end_time:
    time = "{}/{}/{}_{}:{}".format(current_time.year, current_time.month, current_time.day, current_time.hour, "00" if current_time.minute == 0 else current_time.minute)
    time_slot_kg[time] = []
    current_time += delta
# print(cnt)
print(len(time_slot_kg))

def main():
    df = pd.read_csv(sz_assist_kg_path, sep=',', header=None, encoding='gbk')
    for _h, _r, _t in df.values:
        print(_h, _r, _t)
        exit(0)
        h, r, t = _[0], _[1], _[2]
        print(h, r, t)
        exit(0)



if __name__ == '__main__':
    main()