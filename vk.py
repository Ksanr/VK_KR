import requests
import json
#from pprint import pprint


class VK:
    def __init__(self, access_token, version='5.199'):
        self.params = {'access_token': access_token, 'v': version}
        self.base_url = 'https://api.vk.com/method/'

    def users_info(self, user_id):
        url = f'{self.base_url}users.get'
        params = {'user_ids': user_id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def get_photos(self, user_id, count = 5):
        url = f'{self.base_url}photos.get'
        params = {'owner_id': user_id,'count': count,'album_id':
            'profile','extended': 1}
        params.update(self.params)
        response = requests.get(url, params=params)
        return response.json()

    def get_status(self, user_id):
        url = f'{self.base_url}status.get'
        params = {'owner_id': user_id}
        params.update(self.params)
        response = requests.get(url, params=params)
        return response.json()


if __name__ == '__main__':
    access_token_vk = input('Введите ваш токен для доступа к ВК: ')
    user_id = input('Введите id пользователя ВК для архивации фотографий: ')
    access_token_yd = input('Введите ваш токен для доступа к Яндекс-Диск: ')


    step = 1

    print(f'Шаг {step}. Подключение к ВК')
    vk = VK(access_token_vk)
    #print(vk.users_info(user_id))

    step += 1
    print(f'Шаг {step}. Получение информации об альбоме пользователя ВК')

    d = vk.get_photos(user_id)
    filenames = []
    files_info = []
    #print(d)
    photo_count = len(d.get('response').get('items'))

    #pprint(d.get('response').get('items'))

    step += 1
    print(f'Шаг {step}. Создание на Яндекс-диске папки для хранения картинок')
    yd_url = 'https://cloud-api.yandex.net/v1/disk/resources'
    params = {'path': user_id}
    headers = {'Authorization': access_token_yd}
    response = requests.put(yd_url, params=params, headers=headers)

    step += 1
    print(f'Шаг {step}. Сохранение фотографий пользователя ВК на локальном компьютере и на Яндекс-диске ({photo_count} шт.)')


    for i, photo in enumerate(d.get('response').get('items'), 1):
        print(f' {i}/{photo_count}')
        print(f'    Получение информации о фотографии')
        filename = str(photo.get('likes').get('count'))
        if filename in filenames:
            filename += '_' + str(photo.get('date'))
        filenames.append(filename)
        #print(filename)
        filename += '.jpg'

        size = str(photo.get('orig_photo').get('height')) + 'x' + str(photo.get('orig_photo').get('width'))
        #print(size)
        files_info.append({
            'file_name': filename,
            'size': size
        })
        print(f'    Сохранение фотографии на локальном компьютере')

        response = requests.get(photo.get('orig_photo').get('url'))
        with open(f'images/{filename}', 'wb') as f:
            f.write(response.content)

        print(f'    Загрузка фотографий на Яндекс-диск')

        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        params = {'path': f'{user_id}/{filename}'}
        response = requests.get(upload_url, params=params, headers=headers)
        url_for_upload = response.json()['href']
        with open(f'images/{filename}', 'rb') as f:
            requests.put(url_for_upload, files={'file': f})


        print()

    step += 1
    print(f'Шаг {step}. Экспорт информации в файл data.json')
    with open('data.json', 'w') as file:
        json.dump(files_info, file)
