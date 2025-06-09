from http.cookiejar import MozillaCookieJar
from requests.cookies import RequestsCookieJar, cookiejar_from_dict
import requests
import json
import os
from bs4 import BeautifulSoup


class SessionManager:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.set_headers()
        self.set_sstrack()

    def set_headers(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            'Accept': 'application/json'
        }
        self.session.headers.update(headers)

    def set_sstrack(self):
        res = self.session.post('https://stats-new.smugmug.com/com.snowplowanalytics.snowplow/tp2')
        cookies = RequestsCookieJar()
        for cookie in res.headers['Set-Cookie'].split('; '):
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies.set(key, value)

        self.session.cookies.update(cookies)

    

