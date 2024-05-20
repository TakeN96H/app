#pycatchがウザいので生成停止
from sys import dont_write_bytecode;dont_write_bytecode = True

import sys 
sys.path.insert(0, '/var/www/html/app')
from app import app as application