import sys
import os

# add absolute path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from private_main import MainPrivateDL

if __name__ == '__main__':
    '''
    Adjust these variables
    '''
    app = MainPrivateDL()
    password = ''
    url = 'https://photos.fancybooths.com/Issaquah-High-School-Prom-2024'
    root_dir = r'D:\fancybooths'
    folder_number_list = [1,3]
    app.download(password, url, root_dir, folder_number_list)