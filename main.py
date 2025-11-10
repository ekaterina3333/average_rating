import argparse
import csv

from tabulate import tabulate


def average_rating(files, report):
    """
    Подсчитывает средний рейтинг бренда
    """
    brands = {}

    for file in files:
        try:
            if file[-3:] != 'csv':  # Проверяем подходит ли файл по формату
                raise TypeError

            with open(f"{file}", newline='', encoding='utf-8') as f:
                file_reader = csv.reader(f)
                next(file_reader)  # Пропускаем заголовки

                for row in file_reader:
                    # Если бренда нет в словаре, создаем для него ключ
                    if row[1] not in brands:
                        brands[row[1]] = {'sum': 0, 'count': 0}
                    # Подсчитываем сумму и количества вхождений
                    if report == 'average-rating':
                        brands[row[1]]['sum'] += float(row[3])

                    brands[row[1]]['count'] += 1

        except FileNotFoundError:
            print(f"Предупреждение: Файл {file} не найден, пропускаем...")
            continue

        except TypeError:
            print(
                f"Предупреждение: Файл {file} не является csv, пропускаем...")
            continue

    result = []
    if brands:
        for brand in brands:
            # Делим сумму на количество вхождений, получая рейтинг
            result.append([brand,
                           round(brands[brand]['sum'] /
                                 brands[brand]['count'], 2)])
        # Сортируем от большего к меньшему по рейтингу
        result.sort(key=lambda x: x[1], reverse=True)
        headers = ['brand', report]

        print(tabulate(
            result,
            headers,
            tablefmt='psql',
            showindex=range(1, len(result)+1)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--files', required=True, nargs='+', help='file path')
    parser.add_argument('--report',
                        choices=['average-rating'],
                        required=True, help='view of report')

    args = parser.parse_args()
    files = args.files
    report = args.report
    average_rating(files, report)
