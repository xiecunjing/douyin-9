import os
import threading
# import mobile_sliding_v1
def mitm_start_proxy():
    os.system('mitmdump -s user_info_spider_v1.py')
def start_douyin():
    pass
s1 = threading.Thread(target=mitm_start_proxy)
s1.start()
# s2 = threading.Thread(target=mobile_sliding_v1.project_start)
# s2.start()
