#-*- coding:utf-8 –*-

from base import REDIS




# 缓存
def data_cache(timeout):
    # 数据缓存
    def deco(view_func):
        def wrapper(*args, **kwargs):
            key = 'DataCache-%s-%s' % ('test', 'test')
            response = REDIS.get(key)
            print '22222222222222222'
            print key
            print '1111111111111111111111'
            print('get from cache: %s' % response)
            if response is None:
                response = view_func(*args, **kwargs)
                print '&&&&&&&&&&&&&&&&&'
                print response
                print('get from view: %s' % response)
                REDIS.set(key, response, timeout)
                print('set to cache')
            return response
        return wrapper
    return deco