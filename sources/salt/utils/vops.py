# VisualOps salt Utils
# @author: Thibault BRONCHAIN
# (c) 2014 - MadeiraCloud

# Imports
import json

# Defines
PRINT_NOT=["stream"]

def string_to_print(s, acc, level):
    if not s:
        return acc
    return acc+("  "*level)+s.encode('ascii','ignore').strip()+"\n"

def list_to_print(l, acc, level):
    for item in l:
        acc = obj_to_print(item,acc,level+1)
    return acc

def dict_to_print(d, acc, level):
    for key in d:
        if key not in PRINT_NOT:
            acc = obj_to_print("%s:\n"%key,acc,level)
        acc = obj_to_print(d[key],acc,level+1)
    return acc

def obj_to_print(o, acc, level=0):
    if type(o) is dict:
        acc = dict_to_print(o,acc,level)
    elif type(o) is list:
        acc = list_to_print(o,acc,level)
    else:
        acc = string_to_print(("%s"%o),acc,level)
    return acc

def stream_to_print(s):
    ls = []
    if s:# and s.startswith('{') and s.endswith('}'):
        delim = 0
        buf = ''
        for char in s:
            buf += char
            if char == '{':
                delim += 1
            if char == '}':
                delim -= 1
            if delim == 0:
                try:
                    buf = json.loads(buf)
                except Exception:
                    pass
                else:
                    ls.append(buf)
                    buf = ''
    return obj_to_print(ls,"")
