import requests
import time
import random
import os
from urllib.parse import urlparse
from session_manager import SessionManager

class ImagesGetter:
    def __init__(self, session_manager: SessionManager) -> None:
        self.ALBUMURL = 'https://photos.fancybooths.com/services/api/json/1.4.0/?galleryType=album&albumId={album_id}&albumKey={album_key}&imageId=0&imageKey={image_key}&PageSize={page_size}&PageNumber={page_num}&returnModelList=true&method=rpc.gallery.getalbum'
        self.session = session_manager.session

    # need to use the same session to get correct json files.
    def __get_json_file(self, album_id, album_key, page_size=100):
        delay = True
        page_num = 1
        image_key = ""
        images_list = None
        while(True):
            if delay: 
                random_num = random.uniform(1.0,2.0)
                time.sleep(random_num)
            url = self.ALBUMURL.format(album_id=album_id, album_key=album_key, image_key=image_key, page_size=page_size, page_num=page_num)
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                page_num += 1
                if images_list:
                    images_list['Images'].extend(data['Images'])
                else:
                    images_list = data
                if not data['NextImageUrl']:
                    break
                else:
                    image_key = data['NextImageKey']
            else:
                return None

        return images_list

    def __get_images_urls(self, data):
        images_list = []
        for image in data['Images']:
            best_image = image['Sizes']['D']['url']
            if image['Sizes'].get('1280'):
                mp4 = image['Sizes']['1280']['url']
                images_list.append(mp4)
            images_list.append(best_image)
        return images_list

    # you don't need to use the same session to download images
    def __download_medias(self, images_list, file_path):
        if not os.path.exists(file_path):
            os.makedirs(file_path, exist_ok=True)
        for image_url in images_list:
            image_path = os.path.join(file_path, image_url.split('/')[-1])
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(response.content)

    def __make_dir(self, root_path, url):
        parsed_url = urlparse(url)

        path = parsed_url.path.strip('/')

        file_path = os.path.join(root_path, path)
        os.makedirs(file_path, exist_ok=True)
        return file_path



    def download_medias(self, albums_ids, albums_keys, root_dir, only: list=None):
        num = 0
        total_count = 0
        list_count = 0
        for num, (key, id) in enumerate(zip(albums_keys, albums_ids), 1):
            if only and list_count >= len(only):
                continue
            if only and only[list_count] != num:
                continue
            json_data = self.__get_json_file(album_id=id, album_key=key)
            medias_list = self.__get_images_urls(json_data)
            file_path = self.__make_dir(root_dir, json_data['Albums'][0]['URL'])
            print(f'{num}. Start downloading...')
            print(f'Number of medias expected to be downloaded: {len(medias_list)}')
            self.__download_medias(medias_list, file_path)

            total_count += len(medias_list)
            list_count += 1

        self.__log(only, total_count, num)

    def __log(self, only, total_count, num):
        if total_count >= 1:
            if only is None:
                only = list(range(1, num+1))
            verb = 'was' if len(only) == 1 else 'were'
            verb_total = 'was' if total_count <= 1 else 'were'
            noun = 'album' if len(only) == 1 else 'albums'
            noun_media = 'media' if total_count <= 1 else "medias"
            only_str = ", ".join(map(str, only))

            print(f'Number {only_str} {verb} downloaded!')
            print(f'Done! {len(only)} {noun} {verb} downloaded!')
            print(f'Total {total_count} {noun_media} {verb_total} downloaded!')
        
        else:
            print('Nothing was downloaded...')
            print('The folder you selected may not exist')


