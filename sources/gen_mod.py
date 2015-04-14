#!/usr/bin/python
import json

from mod.common import *
from mod.linux import *
from mod.meta import *
from mod.windows import *

mod = {}
for i in (common, linux, meta, windows):
	mod.update(i)

with open('./module.json', 'w+') as f:
	f.write(json.dumps(mod, indent=4, sort_keys=True))

