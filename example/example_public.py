import sys
import os

# add absolute path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from public_main import MainPublicDL

if __name__ == '__main__':
    '''
    Adjust these variables
    '''
    app = MainPublicDL()
    url = 'https://photos.fancybooths.com/Shoreline-Prom-2025'
    root_dir = r'D:\fancybooths'
    folder_number_list = [1]
    app.download(url, root_dir, folder_number_list)