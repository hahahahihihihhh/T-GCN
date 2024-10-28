from collections import defaultdict

import pandas as pd
import os

sz_assist_kg_path = 'sz_assist_kg.csv'

sz_assist_kg = pd.read_csv(os.path.join('../', sz_assist_kg_path), encoding='GBK', header=None)
rel_dict = defaultdict(int)
def is_english(string):
    for char in string:
        if not ('a' <= char <= 'z' or 'A' <= char <= 'Z' or char == '.' or char == '_'):
            return False
    return True

def main():
    for _head, _rel, _tail in sz_assist_kg.values:
        if (_rel == 'adj'):
            rel_dict['adj'] += 1
        else:
            if (is_english(_tail)):
                rel_dict['weather'] += 1
            else:
                rel_dict['poi'] += 1
    for _type, _num in rel_dict.items():
        print("{}: {}".format(_type, _num))

if __name__ == '__main__':
    main()


