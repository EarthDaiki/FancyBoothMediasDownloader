import requests
import time
import random
import os
from urllib.parse import urlparse
from session_manager import SessionManager
import sys
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed

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

        total = len(images_list)
        results = [None] * total

        def download(index_url_pair):
            index, image_url = index_url_pair
            image_name = image_url.split('/')[-1]
            image_path = os.path.join(file_path, image_name)

            for attempt in range(3):  # max 3 retries
                try:
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        with open(image_path, 'wb') as f:
                            f.write(response.content)
                        return index, True
                except Exception as e:
                    if attempt == 2:
                        print(f"\n[{index + 1}] Failed after 3 attempts: {image_url}")
                    sleep(1)  # wait a second to retry
            return index, False

        def print_progress_bar(done, total):
            bar_len = 40
            filled_len = int(bar_len * done / total)
            bar = '=' * filled_len + '-' * (bar_len - filled_len)
            sys.stdout.write(f'\rDownloading: [{bar}] {done}/{total}')
            sys.stdout.flush()

        with ThreadPoolExecutor(max_workers=8) as executor:
            indexed_urls = list(enumerate(images_list))
            future_to_index = {executor.submit(download, pair): pair[0] for pair in indexed_urls}

            done_count = 0
            for future in as_completed(future_to_index):
                index, success = future.result()
                results[index] = success
                done_count += 1
                print_progress_bar(done_count, total)

        # to make the line beautiful
        print()

        # log for failed to downlaod
        for idx, success in enumerate(results):
            if not success:
                print(f"✗ Failed: {images_list[idx]}")

    def __make_dir(self, root_path, url):
        parsed_url = urlparse(url)

        path = parsed_url.path.strip('/')

        file_path = os.path.join(root_path, path)
        os.makedirs(file_path, exist_ok=True)
        return file_path



    def download_medias(self, albums_ids, albums_keys, root_dir, only: list=None):
        total_count = 0
        index = 0
        donwloaded_list_index = []
        for index, (key, id) in enumerate(zip(albums_keys, albums_ids), 1):

            # if only list is not None and if index is not in only list.
            if only is not None and index not in only:
                continue

            print("#" * 60)
            print(f'{index}. Start downloading...')

            # get album data and image urls
            print("Getting images info...")
            json_data = self.__get_json_file(album_id=id, album_key=key)
            medias_list = self.__get_images_urls(json_data)

            # make store dir
            file_path = self.__make_dir(root_dir, json_data['Albums'][0]['URL'])

            print(f'Number of medias expected to be downloaded: {len(medias_list)}')

            # start download
            self.__download_medias(medias_list, file_path)

            total_count += len(medias_list)
            donwloaded_list_index.append(index)

        self.__log(total_count, donwloaded_list_index)

    def __log(self, total_count, donwloaded_list_index):
        if total_count >= 1:
            verb = 'was' if len(donwloaded_list_index) == 1 else 'were'
            verb_total = 'was' if total_count <= 1 else 'were'
            noun = 'album' if len(donwloaded_list_index) == 1 else 'albums'
            noun_media = 'media' if total_count <= 1 else "medias"
            only_str = ", ".join(map(str, donwloaded_list_index))

            print("=" * 60)
            print(f'Number {only_str} {verb} downloaded!')
            print(f'Done! {len(donwloaded_list_index)} {noun} {verb} downloaded!')
            print(f'Total {total_count} {noun_media} {verb_total} downloaded!')
            print("=" * 60)
        
        else:
            print("=" * 60)
            print('Nothing was downloaded...')
            print('The folder you selected may not exist')
            print("=" * 60)


