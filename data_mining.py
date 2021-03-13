import sys
import requests


# из двух файлов (ссылки и имена скопированные прямо с вк пачкой) делаем массив
def lists_of_track_links(links_file='doc/test_link.txt'):

    # first-list of links
    links = []
    # размер файла
    with open(links_file) as file_l:
        len_l = 0
        for i in file_l:
            len_l += 1
    # открываем файл и парсим из него в массив ссылки
    with open(links_file) as file_l:
        for j in range(0, len_l):
            links.append(file_l.readline()[0:-1])

    return links


# из двух файлов (ссылки и имена скопированные прямо с вк пачкой) делаем массив
def lists_of_track_names(names_file='doc/test_name.txt'):

    # list of names
    names = []
    with open(names_file, encoding='utf-8') as file_n:
        data_n = file_n.read().split('\n')
    for i in range(0, len(data_n), 4):
        tmp = f'<b>{data_n[i]}:</b><u><i>"{data_n[i + 1]}"</i></u>'
        names.append(tmp)

    return names


# по ссылке скачивает файл в нужный файл и выдает название этого файла
def download_file(url, file_name):
    r = requests.get(url, allow_redirects=True)
    print(r)
    open(file_name, 'wb').write(r.content)
    return file_name


if __name__ == "__main__":
    pass
