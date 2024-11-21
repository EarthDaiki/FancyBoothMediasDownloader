from session_manager import SessionManager
from api import Api
from medias_getter import ImagesGetter
from unlock import UnlockAlbums


class Example:
    """
    This class is an example of downloading private albums, which means password-protected albums.
    """
    def __init__(self, ua: UnlockAlbums, api: Api, ig: ImagesGetter) -> None:
        self.ua = ua
        self.api = api
        self.ig = ig

    def run(self):
        # You need to put the parent folder's url in this url variable.
        url = 'url'
        # has_access = self.ua.unlock_with_cookies(url, r"your cookies file path. (Netscape's text or json)")
        has_access = self.ua.unlock_without_cookies(url, 'password')
        if has_access:
            folder_info = self.api.get_folder_info(url)
            folder_node_id = self.api.get_folder_node_id(folder_info)
            folder_children = self.api.get_folder_children(folder_node_id)
            albums_keys = self.api.get_albums_keys_almighty(folder_children)
            print(f'Albums Keys: {albums_keys}')
            uris_list = self.api.get_albums_uris_almighty(folder_children)
            albums_ids = self.api.get_albums_ids(uris_list)
            print(f'Albums IDs: {albums_ids}')

            # Change to your preferred root directory.
            root_dir = r'D:\fancybooths'

            # if only is None, it means download all medias.
            self.ig.download_medias(albums_ids, albums_keys, root_dir, only=None)
        else:
            print('password is not correct.')

if __name__ == '__main__':
    sm = SessionManager()
    ua = UnlockAlbums(sm)
    api = Api(sm)
    ig = ImagesGetter(sm)
    app = Example(ua, api, ig)
    app.run()
