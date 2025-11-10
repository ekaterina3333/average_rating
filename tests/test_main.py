from unittest.mock import patch, mock_open

from main import average_rating

REPORT = 'average-rating'


class TestingAverageRating:
    """Тесты для функции average_rating"""

    def test_wrong_type(self, capsys):
        """Тест что TypeError перехватывается и обрабатывается"""
        with patch('builtins.open', side_effect=TypeError):
            # Функция НЕ должна бросать исключение
            average_rating(['nonexistent.txt'], REPORT)
            # Проверяем вывод предупреждения в консоль
            captured = capsys.readouterr()
            assert "Предупреждение: Файл nonexistent.txt не является csv, пропускаем..." in captured.out

    def test_one_exist_one_missing(self, capsys):
        """Тест обработки когда одни файлы есть, а другие отсутствуют"""
        csv_data = """name,brand,price,rating
iphone 15 pro,apple,999,4.9
galaxy s23 ultra,samsung,1199,4.8
redmi note 12,xiaomi,199,4.6
iphone 14,apple,799,4.7
galaxy a54,samsung,349,4.2"""

        # Мокаем open чтобы первый файл существовал, второй - нет
        with patch('builtins.open', side_effect=[
            mock_open(read_data=csv_data).return_value,  # file1.csv
            FileNotFoundError()  # file2.csv
        ]):
            with patch('main.tabulate') as mock_tabulate:
                average_rating(['file1.csv', 'file2.csv'], REPORT)

                # Проверяем вывод предупреждения в консоль
                captured = capsys.readouterr()
                assert "Предупреждение: Файл file2.csv не найден, пропускаем..." in captured.out

                # Проверяем что tabulate вызван с правильными данными
                assert mock_tabulate.called
                call_args = mock_tabulate.call_args[0]
                table_data = call_args[0]

                # Проверяем расчеты только из существующего файла
                # apple: (4.9 + 4.7) / 2 = 4.8
                # samsung: (4.8 + 4.2) / 2 = 4.5
                # xiaomi: 4.6 / 1 = 4.6
                apple_data = next(item for item in table_data if item[0] == 'apple')
                assert apple_data[1] == 4.8

    def test_filenotfounderror_caught_and_handled(self):
        """Тест что FileNotFoundError перехватывается и обрабатывается"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            with patch('builtins.print'):
                # Функция НЕ должна бросать исключение
                average_rating(['nonexistent.csv'], REPORT)
                assert True

    def test_one_file(self):
        '''Функция работает с одним файлом'''
        csv_data = """name,brand,price,rating
iphone 15 pro,apple,999,4.9
galaxy s23 ultra,samsung,1199,4.8
redmi note 12,xiaomi,199,4.6"""

        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('main.tabulate') as mock_tabulate:

                average_rating(['tests.csv'], REPORT)

                # Проверяем что tabulate был вызван (значит функция работает)
                assert mock_tabulate.called

    def test_two_files(self):
        """Тест обработки нескольких файлов"""

        csv_data1 = """name,brand,price,rating
iphone,apple,999,4.9"""

        csv_data2 = """name,brand,price,rating
galaxy,samsung,1199,4.8"""

        file_contents = {
            'file1.csv': csv_data1,
            'file2.csv': csv_data2
        }

        # Функция которая возвращает правильные данные для каждого файла
        def mock_file_open(filename, *args, **kwargs):
            return mock_open(
                read_data=file_contents[filename])(filename, *args, **kwargs)

        with patch('builtins.open', mock_file_open):
            with patch('main.tabulate') as mock_tabulate:
                average_rating(['file1.csv', 'file2.csv'], REPORT)

                # Проверяем что tabulate вызван
                assert mock_tabulate.called
                # Проверяем что tabulate вызван ровно 1 раз
                assert mock_tabulate.call_count == 1

    def test_average_rating(self):
        '''Функция правильно вычисляет средние значения'''
        csv_data = """name,brand,price,rating
iphone 15 pro,apple,999,4.9
galaxy s23 ultra,samsung,1199,4.8
redmi note 12,xiaomi,199,4.6
iphone 14,apple,799,4.7
galaxy a54,samsung,349,4.2"""

        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('main.tabulate') as mock_tabulate:
                average_rating(['tests.csv'], REPORT)

                # Получаем данные которые передали в tabulate
                call_args = mock_tabulate.call_args[0]  # аргументы функции
                table_data = call_args[0]  # первый аргумент - данные таблицы

                # Проверяем что рейтинг правильно сортируется
                assert table_data[0][0] == 'apple'
                assert table_data[1][0] == 'xiaomi'
                assert table_data[2][0] == 'samsung'
                # Проверяем что рейтинг верно формируется 4.9 + 4.7 / 2 = 4.8
                assert table_data[0][1] == 4.8
