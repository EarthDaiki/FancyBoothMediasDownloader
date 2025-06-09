import requests
import json
from bs4 import BeautifulSoup
import re
from session_manager import SessionManager

class Api:
    def __init__(self, session_manager: SessionManager) -> None:
        self.session = session_manager.session

    def get_folder_info(self, url):
        response = self.session.get(f'https://www.smugmug.com/api/v2!weburilookup?APIKey=W0g9oqdOrzuhEpIQ2qaTXimrzsfryKSZ&WebUri={url}')
        return response.json()

    def get_folder_node_id(self, folder_info):
        return folder_info['Response']['Folder']['NodeID']

    def get_url_name(self, folder_info):
        return folder_info['Response']['Folder']['UrlName']

    def get_albums(self, url_name):
        response = self.session.get(f'https://www.smugmug.com/api/v2/folder/user/fancybooth/{url_name}!albums?APIKey=W0g9oqdOrzuhEpIQ2qaTXimrzsfryKSZ')
        return response.json()

    # only for not protected by password
    def get_albums_keys(self, albums):
        album_key_list = []
        for album in albums['Response']['Album']:
            album_key = album['AlbumKey']
            album_key_list.append(album_key)

        return album_key_list

    def get_albums_uris(self, albums):
        uris_list = [album['WebUri'] for album in albums['Response']['Album']]
        return uris_list


    # this is not recommended way
    def get_albums_ids(self, uris_list):
        albums_ids_list = []
        for count in range(len(uris_list)):
            res = self.session.get(uris_list[count])
            soup = BeautifulSoup(res.text, "html.parser")
            script_tag = soup.find_all('script')[-1]
            if script_tag:
                script_content = ''.join(script_tag.contents)
                # print(script_content)
            else:
                script_content = ''
            script_content = script_tag.string if script_tag else ''

            pattern = re.compile(r'"galleryRequestData":\s*({.*?})', re.DOTALL)
            match = pattern.search(script_content)

            if match:
                album_id = match.group(1)
                albums_ids_list.append(json.loads(album_id)["albumId"])
            else:
                print("galleryRequestData not found.")

        return albums_ids_list


    # use 'Accept': 'application/json'
    def get_token_almighty(self):
        response = self.session.post('https://photos.fancybooths.com/api/v2!token?APIKey=W0g9oqdOrzuhEpIQ2qaTXimrzsfryKSZ')
        try:
            token = response.json()['Response']['Token']['Token']
            return token
        except KeyError:
            print('something went wrong')

    # only for protected folders by password
    def get_token(self, url):
        response = self.session.get(url)

        cookie_header = '; '.join([f"{cookie.name}={cookie.value}" for cookie in self.session.cookies])
        headers = {
            'Cookie': cookie_header
        }

        self.session.headers.update(headers)
        response = self.session.get('https://www.smugmug.com/include/js/cookiemonster.mg?returnTo=https://photos.fancybooths.com', allow_redirects=False)
        response_headers = response.headers

        for header, value in response_headers.items():
            if header == 'location':
                token = value.split('=')[-1]
                return token

    # def get_token_bs4(self, url):
    #     res = self.session.get(url)
    #     soup = BeautifulSoup(res.text, "html.parser")
    #     script_tag = soup.find_all('script')[-1]
    #     if script_tag:
    #         script_content = ''.join(script_tag.contents)
    #         # print(script_content)
    #     else:
    #         script_content = ''
    #     script_content = script_tag.string if script_tag else ''

    #     pattern = re.compile(r'"csrfToken":\s*"([^"]+)"', re.DOTALL)
    #     match = pattern.search(script_content)

    #     if match:
    #         data = match.group(1)
    #         return data
    #     else:
    #         print("galleryRequestData not found.")

    # for protected albums by password and normal albums
    def get_folder_children(self, folder_node_id):
        url = f'https://www.smugmug.com/api/v2/node/{folder_node_id}!children?APIKey=W0g9oqdOrzuhEpIQ2qaTXimrzsfryKSZ'
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()

    def get_albums_keys_almighty(self, folder_children):
        album_keys_list = []
        for album in folder_children['Response']['Node']:
            album_key = album['Uris']['Album']['Uri'].split('/')[-1]
            album_keys_list.append(album_key)

        return album_keys_list

    def get_albums_uris_almighty(self, folder_children):
        uris_list = [node['WebUri'] for node in folder_children["Response"]['Node']]
        return uris_list