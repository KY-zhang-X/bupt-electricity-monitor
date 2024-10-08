import os
import traceback
from monitor import ElecMonitor
from push import ServerChan

DEFAULT_ALARM_THRESHOLD = 20

def main():
    eaisess = os.environ.get('EAISESS')
    area_id = os.environ.get('AREA_ID') # 1-西土城校区, 其他-沙河校区
    partment_name = os.environ.get('PARTMENT') # 西土城校区: 学X楼  沙河校区: 沙河校区雁X园X楼
    floor_name = os.environ.get('FLOOR')
    dorm_name = os.environ.get('DORMITORY')
    alarm_threshold = os.environ.get('ALARM_THRESHOLD')
    sct_key = os.environ.get('SERVERCHAN_KEY')

    if not eaisess:
        print('没有提供EAISESS')
        exit(-1)
    
    if not (area_id and partment_name and floor_name and dorm_name):
        print('''
              没有提供具体的宿舍信息, 需要以下信息(以学校电费查询页面为准)
              - AREA_ID: 校区ID, 1-西土城校区, 0-沙河校区
              - PARTMENT: 宿舍楼名
              - FLOOR: 宿舍楼层
              - DORMITORY: 宿舍名
              ''')
        exit(-1)
    
    if not alarm_threshold:
        alarm_threshold = DEFAULT_ALARM_THRESHOLD
    
    monitor = ElecMonitor(eaisess=eaisess)
    if sct_key:
        sct = ServerChan(sct_key=sct_key)
    else:
        sct = None
    
    try:
        surplus = monitor.run(area_id=area_id, partment_name=partment_name, floor_name=floor_name, dorm_name=dorm_name)
        # if surplus < alarm_threshold:
        if sct:
            sct.push(title=f"电量提醒: 剩余电量{surplus}度")
    except Exception as exc:
        if sct:
            sct.push("电量查询失败")
        traceback.print_exc()
        exit(-1)


if __name__ == '__main__':
    main()