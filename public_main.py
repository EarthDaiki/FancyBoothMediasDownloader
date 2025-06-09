from session_manager import SessionManager
from api import Api
from medias_getter import ImagesGetter
from unlock import UnlockAlbums


class MainPublicDL:
    def __init__(self) -> None:
        sm = SessionManager()
        self.ua = UnlockAlbums(sm)
        self.api = Api(sm)
        self.ig = ImagesGetter(sm)

    def download(self, url, root_dir, folder_number_list=None):
        '''
        Entry point for downloading media from an event page.

        This function accesses the main event URL, retrieves all associated albums,
        and downloads the media (e.g., images) into the specified root directory.
        A separate subdirectory is created for each album.

        Args:
            url (str): The main event page URL.
                    Example: "https://photos.fancybooths.com/Shoreline-Prom-2025"

            root_dir (str): The root directory where the media files will be saved.
                            A subfolder will be created for each album automatically.

            folder_number_list (list[int], optional): A list of album indices to download (1-based).
                                        Example: [1, 3] downloads only the 1st and 3rd albums.
                                        If None (default), all albums will be downloaded.

        Returns:
            None
        '''

        folder_info = self.api.get_folder_info(url)
        folder_node_id = self.api.get_folder_node_id(folder_info)
        folder_children = self.api.get_folder_children(folder_node_id)
        albums_keys = self.api.get_albums_keys_almighty(folder_children)
        print(f'Albums Keys: {albums_keys}')
        uris_list = self.api.get_albums_uris_almighty(folder_children)
        albums_ids = self.api.get_albums_ids(uris_list)
        print(f'Albums IDs: {albums_ids}')
        
        self.ig.download_medias(albums_ids, albums_keys, root_dir, folder_number_list)