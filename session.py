#!/usr/local/bin/python3
import pickle
import requests
from decorator import Lock, synchronized, throwaway


# 序列化
def cookies2string(cookies):
    string = ''
    if cookies:
        string = pickle.dumps(cookies._cookies).hex()
    return string


# 反序列化
def string2cookies(string):
    cookies = requests.cookies.cookiejar_from_dict({})
    if string:
        cookies._cookies = pickle.loads(bytes.fromhex(string))
    return cookies


class Session(requests.Session):
    # 动态代理
    def _proxies(self):
        pass

    # 读写缓存
    def _cookies(self, string):
        pass

    @synchronized()
    @throwaway()
    def __cookies(self):
        cookies = string2cookies(self._cookies(None))
        if cookies:
            if self.cookies:
                cookies.update(self.cookies)
                self._cookies(cookies2string(cookies))
            self.cookies.update(cookies)

    def request(self, *args, **kwargs):
        self.__cookies()
        if 'proxies' not in kwargs:
            proxies = self._proxies()
            if proxies is not None:
                kwargs['proxies'] = proxies
        response = super().request(*args, **kwargs)
        if response.cookies:
            with Lock(self):
                cookies = string2cookies(self._cookies(None))
                cookies.update(response.cookies)
                self._cookies(cookies2string(cookies))
        return response
