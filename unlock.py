from api import Api
from session_manager import SessionManager
from bs4 import BeautifulSoup
from http.cookiejar import MozillaCookieJar
from requests.cookies import RequestsCookieJar, cookiejar_from_dict
import json
import os

class UnlockAlbums:
    def __init__(self, session_manager: SessionManager) -> None:
        self.api = Api(session_manager=session_manager)
        self.session = session_manager.session

    # this is not reccomended way
    def unlock_with_cookies(self, url, file_path):
        cookies = self.parse_cookie_file(file_path)
        
        self.session.cookies.update(cookies)
        res = self.session.get(url)

        if res.status_code == 200:
            try:
                soup = BeautifulSoup(res.text, "html.parser")
                title = soup.find('title').text
                if 'password' in title:
                    return False
            except:
                return True

    def parse_cookie_file(self, file_path):
        _, ext = os.path.splitext(file_path)
        if ext.lower() == '.json':
            return self._parse_json_cookie_file(file_path)
        elif ext.lower() == '.txt':
            return self._parse_netscape_file(file_path)
        else:
            raise ValueError("Unsupported file format. Please provide a JSON or Netscape format cookie file.")

    def _parse_json_cookie_file(self, file_path):
        with open(file_path, 'r') as f:
            cookies = json.load(f)
        cookie_jar = RequestsCookieJar()
        for cookie in cookies:
            cookie_jar.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])
        return cookie_jar

    def _parse_netscape_file(self, file_path):
        cookie_jar = MozillaCookieJar()
        cookie_jar.load(file_path, ignore_discard=True, ignore_expires=True)
        return cookie_jar

    # now you need password to get into and get album id.
    def unlock_without_cookies(self, url, password):
        # token = self.api.get_token_almighty()
        token = self.api.get_token(url)
        has_access = self.unlock(url, token, password)
        return has_access

    def check_unlock(self, url, token, password=''):
        data = {
            'NodeID': self.api.get_folder_node_id(self.api.get_folder_info(url)),
            'Password': password,
            'Remember': 0,
            'method': 'rpc.node.auth',
            '_token': token
        }
        response = self.session.post('https://photos.fancybooths.com/services/api/json/1.4.0/', data=data)
        if response.status_code == 200:
            return response

    def unlock(self, url, token, password=''):
        response = self.check_unlock(url, token, password)
        if response.json().get('stat') == 'ok':
            node_info = response.json().get('Node', {})
            has_access = node_info.get('HasAccess', False)
            return has_access
        else:
            return False