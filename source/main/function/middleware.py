from flask import request
import os.path
from urllib.parse import urlparse
import random


def make_link(localhost, path):
    url = f"{localhost}{path}"
    return url


def split_join(url):
    url = url.split('/')
    url = '/'.join(url[:3])
    return url


def make_image_local_path(PATH, url):
    parsed_url = urlparse(url)

    path = parsed_url.path

    path_segments = path.split("/")
    new_path = "/".join(path_segments[2:])

    return os.path.join(PATH, new_path)


def make_url_image(id_user, path, image, typeof):
    local_host = split_join(request.base_url)
    random_name = f"{id_user}_{typeof}_{random.randint(100000, 999999)}.jpg"
    image_link = f"/get-image/{id_user}/{random_name}"

    if not os.path.isdir(path):
        os.makedirs(path)
    else:
        user_path = os.path.join(path, str(id_user))
        if not os.path.isdir(user_path):
            os.makedirs(user_path)
            image.save(os.path.join(user_path, random_name))
        else:
            image.save(os.path.join(user_path, random_name))

    return make_link(local_host, image_link)

def make_link_share(id_note):
    local_host = split_join(request.base_url)
    return make_link(local_host, f'/share-note/{id_note}')
