#!/usr/local/bin/python3
import json
import requests
from http.cookiejar import Cookie
from decorator import Lock, synchronized, throwaway


# 序列化
def cookies2string(cookies):
    string = ''
    if cookies:
        _cookies = {}
        for domain, paths, in cookies._cookies.items():
            _cookies[domain] = {}
            for path, names, in paths.items():
                _cookies[domain][path] = {}
                for name, cookie, in names.items():
                    _cookies[domain][path][name] = {
                        'version': cookie.version,
                        'name': cookie.name,
                        'value': cookie.value,
                        'port': cookie.port,
                        'port_specified': cookie.port_specified,
                        'domain': cookie.domain,
                        'domain_specified': cookie.domain_specified,
                        'domain_initial_dot': cookie.domain_initial_dot,
                        'path': cookie.path,
                        'path_specified': cookie.path_specified,
                        'secure': cookie.secure,
                        'expires': cookie.expires,
                        'discard': cookie.discard,
                        'comment': cookie.comment,
                        'comment_url': cookie.comment_url,
                        'rest': cookie._rest,
                        'rfc2109': cookie.rfc2109,
                    }
        string = json.dumps(_cookies)
    return string


# 反序列化
def string2cookies(string):
    cookies = requests.cookies.cookiejar_from_dict({})
    if string:
        try:
            _cookies = json.loads(string)
            for domain, paths, in _cookies.items():
                cookies._cookies[domain] = {}
                for path, names, in paths.items():
                    cookies._cookies[domain][path] = {}
                    for name, cookie, in names.items():
                        cookies._cookies[domain][path][name] = Cookie(**cookie)
        except BaseException:
            pass
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
