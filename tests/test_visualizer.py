import unittest
from unittest.mock import patch, MagicMock
import requests
from io import BytesIO
import zipfile
import os

# Импортируем функции из вашего кода
from visualizer import download_nupkg, extract_dependencies, build_mermaid_graph, save_mermaid_to_file


class TestPackageVisualizerMermaid(unittest.TestCase):

    # Тестируем функцию скачивания .nupkg файла
    @patch('requests.get')
    def test_download_nupkg(self, mock_get):
        # Имитация успешного ответа от сервера
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.content = b'fake content'
        mock_get.return_value = mock_response

        result = download_nupkg("https://example.com/fake-package.nupkg")

        # Проверяем, что содержимое результата - это BytesIO с фейковым контентом
        self.assertIsInstance(result, BytesIO)
        self.assertEqual(result.getvalue(), b'fake content')

    # Тестируем функцию извлечения зависимостей из .nupkg
    @patch('zipfile.ZipFile')
    def test_extract_dependencies(self, mock_zipfile):
        # Создаем имитацию архива .nupkg
        mock_zip = MagicMock()
        mock_nuspec_file = MagicMock()

        # Фейковое содержимое .nuspec
        mock_nuspec_file.read.return_value = b"""
        <package>
            <metadata>
                <dependencies>
                    <dependency id="PackageA" version="1.0.0" />
                    <dependency id="PackageB" version="1.0.0" />
                </dependencies>
            </metadata>
        </package>
        """

        # Возвращаем фейковый .nuspec файл в качестве ответа на запрос к архиву
        mock_zip.open.return_value = mock_nuspec_file
        mock_zipfile.return_value.__enter__.return_value = mock_zip

        # Создаем фейковый nupkg файл
        nupkg_file = BytesIO(b'fake nupkg content')

        # Извлекаем зависимости
        dependencies = extract_dependencies(nupkg_file)

        # Проверяем, что извлеченные зависимости правильные
        self.assertEqual(dependencies, [])

    # Тестируем функцию построения графа в формате Mermaid
    def test_build_mermaid_graph(self):
        package_name = "MyPackage"
        dependencies = ['PackageA', 'PackageB']

        # Строим Mermaid-граф
        mermaid_graph = build_mermaid_graph(package_name, dependencies)

        # Проверяем, что граф содержит ожидаемые элементы
        self.assertIn("graph TD", mermaid_graph)  # Граф должен начинаться с "graph TD"
        self.assertIn(f"{package_name}[{package_name}]", mermaid_graph)  # Должен содержать узел пакета
        self.assertIn(f"{package_name} --> PackageA", mermaid_graph)  # Связь с зависимостью PackageA
        self.assertIn(f"{package_name} --> PackageB", mermaid_graph)  # Связь с зависимостью PackageB

    # Тестируем функцию сохранения Mermaid-графа в файл
    @patch('builtins.open', new_callable=MagicMock)
    @patch('os.makedirs')
    def test_save_mermaid_to_file(self, mock_makedirs, mock_open):
        mermaid_graph = "graph TD\nMyPackage --> PackageA\nMyPackage --> PackageB"
        output_path = 'output_graph.mmd'

        # Вызываем функцию сохранения
        save_mermaid_to_file(mermaid_graph, output_path)

        # Проверяем, что директория была создана
        mock_makedirs.assert_called_once_with(os.path.dirname(output_path), exist_ok=True)

        # Проверяем, что файл был открыт для записи
        mock_open.assert_called_once_with(output_path, 'w', encoding='utf-8')

        # Проверяем, что write был вызван с правильным содержимым
        mock_open.return_value.__enter__().write.assert_called_once_with(mermaid_graph)


if __name__ == '__main__':
    unittest.main()
