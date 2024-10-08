import requests

class ElecMonitor(object):
    ELEC_PART_URL = "https://app.bupt.edu.cn/buptdf/wap/default/part"
    ELEC_FLOOR_URL = "https://app.bupt.edu.cn/buptdf/wap/default/floor"
    ELEC_DORM_URL = "https://app.bupt.edu.cn/buptdf/wap/default/drom"
    ELEC_SEARCH_URL = "https://app.bupt.edu.cn/buptdf/wap/default/search"

    ELEC_PART_TIMEOUT = 1
    ELEC_FLOOR_TIMEOUT = 1
    ELEC_DORM_TIMEOUT = 1
    ELEC_SEARCH_TIMEOUT = 10

    def __init__(self, eaisess: str = None):
        self.eaisess = eaisess
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        self.session.cookies.update({'eai-sess': eaisess})

    def run(self, area_id: int, partment_name: str, floor_name: str, dorm_name: str) -> float:
        '''
        脚本入口, 进行一次电量查询
        '''
        partment_id = self.query_part_id(area_id=area_id, partment_name=partment_name)
        floor_id = self.query_floor_id(area_id=area_id, partment_id=partment_id, floor_name=floor_name)
        dorm_id = self.query_dorm_id(area_id=area_id, partment_id=partment_id, floor_id=floor_id, dorm_name=dorm_name)
        surplus = self.query_elec_surplus(area_id=area_id, partment_id=partment_id, floor_id=floor_id, dorm_id=dorm_id)
        return surplus
    
    def query_part_id(self, area_id: int, partment_name: str) -> str:
        '''
        查询宿舍楼id
        '''
        res = self.session.post(url=self.ELEC_PART_URL, data={'areaid': area_id}, timeout=self.ELEC_PART_TIMEOUT)
        res_json = res.json()
        if res_json['e'] != 0:
            raise RuntimeError(f'查询宿舍楼id失败, msg={res_json}')
        d = res_json['d']
        data = d['data']
        partments = list(filter(lambda p: p['partmentName']==partment_name, data))
        if len(partments) == 0:
            raise RuntimeError(f'未查询到宿舍楼, name={partment_name}, data={data}')
        return partments[0]['partmentId']

    def query_floor_id(self, area_id: int, partment_id: str, floor_name: str) -> str:
        '''
        查询楼层id
        '''
        res = self.session.post(url=self.ELEC_FLOOR_URL, data={'areaid': area_id, 'partmentId': partment_id}, timeout=self.ELEC_FLOOR_TIMEOUT)
        res_json = res.json()
        if res_json['e'] != 0:
            raise RuntimeError(f'查询楼层id失败, msg={res_json}')
        d = res_json['d']
        data = d['data']
        floors = list(filter(lambda p: p['floorName']==floor_name, data))
        if len(floors) == 0:
            raise RuntimeError(f'未查询到对应楼层, name={floor_name}, data={data}')
        return floors[0]['floorId']
    
    def query_dorm_id(self, area_id: int, partment_id: str, floor_id: str, dorm_name: str) -> str:
        '''
        查询宿舍id
        '''
        res = self.session.post(url=self.ELEC_DORM_URL, data={
            'areaid': area_id, 
            'partmentId': partment_id, 
            'floorId': floor_id
        }, timeout=self.ELEC_DORM_TIMEOUT)
        res_json = res.json()
        if res_json['e'] != 0:
            raise RuntimeError(f'查询宿舍id失败, msg={res_json}')
        d = res_json['d']
        data = d['data']
        dormitory = list(filter(lambda p: p['dromName']==dorm_name, data))
        if len(dormitory) == 0:
            raise RuntimeError(f'未查询到对应宿舍, name={dorm_name}, data={data}')
        return dormitory[0]['dromNum']
        

    def query_elec_surplus(self, area_id: int, partment_id: str, floor_id: str, dorm_id: str) -> float:
        '''
        查询剩余电量
        '''
        res = self.session.post(url=self.ELEC_SEARCH_URL, data={
            'areaid': area_id, 
            'partmentId': partment_id, 
            'floorId': floor_id, 
            'dromNumber': dorm_id
        }, timeout=self.ELEC_SEARCH_TIMEOUT)
        res_json = res.json()
        if res_json['e'] != 0:
            raise RuntimeError(f'查询剩余电费失败, msg={res_json}')
        d = res_json['d']
        data = d['data']
        surplus = float(data['surplus'])
        free_end = float(data['freeEnd'])
        return surplus + free_end
    
    