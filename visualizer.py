import sys
import argparse
import requests
import zipfile
import os
from io import BytesIO


# Функция для скачивания .nupkg файла
def download_nupkg(url):
    response = requests.get(url)
    response.raise_for_status()
    return BytesIO(response.content)


# Функция для извлечения зависимостей из .nupkg
def extract_dependencies(nupkg_file):
    with zipfile.ZipFile(nupkg_file) as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith('nuspec'):
                with zip_ref.open(file) as nuspec:
                    dependencies = []
                    for line in nuspec.read().decode('utf-8').splitlines():
                        if '<dependency' in line:
                            dep_name = line.split('id="')[1].split('"')[0]
                            dependencies.append(dep_name)
                    return dependencies
    return []


# Функция для построения графа в формате Mermaid
def build_mermaid_graph(package_name, dependencies):
    mermaid_graph = ["graph TD"]
    mermaid_graph.append(f'{package_name}[{package_name}]')

    # Используем множество для отслеживания уже добавленных зависимостей
    added_dependencies = set()

    for dep in dependencies:
        if dep not in added_dependencies:
            mermaid_graph.append(f'{package_name} --> {dep}')
            added_dependencies.add(dep)

    return "\n".join(mermaid_graph)


# Функция для сохранения Mermaid-графа в файл
def save_mermaid_to_file(mermaid_graph, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(mermaid_graph)
    print(f"Mermaid graph successfully saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Visualize .NET package dependencies with a custom visualizer.")
    parser.add_argument('--visualizer_path', type=str, required=True, help='Path to the visualizer executable.')
    parser.add_argument('--package_name', type=str, required=True, help='Name of the .NET package to analyze.')
    parser.add_argument('--output_png_path', type=str, required=True, help='Path to save the PNG file.')
    parser.add_argument('--url', type=str, required=True, help='URL to download the .nupkg file.')

    args = parser.parse_args()

    try:
        nupkg_file = download_nupkg(args.url)
        dependencies = extract_dependencies(nupkg_file)
        mermaid_graph = build_mermaid_graph(args.package_name, dependencies)

        # Сохраняем Mermaid граф
        mermaid_output_path = args.output_png_path.replace(".png", ".mmd")
        save_mermaid_to_file(mermaid_graph, mermaid_output_path)

        # Вызов Mermaid CLI для создания PNG с настройками разрешения
        os.system(
            f"mmdc -i {mermaid_output_path} -o {args.output_png_path} --width 1440 --height 1000 --scale 3"
        )
        print(f"Graph successfully saved as PNG to {args.output_png_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()


# python visualizer.py --visualizer_path ./visualizer.py --package_name Newtonsoft.Json --output_png_path ./output/output_graph_1.png --url https://www.nuget.org/api/v2/package/Newtonsoft.Json/13.0.3
# python visualizer.py --visualizer_path ./visualizer.py --package_name Microsoft.Extensions.DependencyInjection --output_png_path ./output/output_graph_2.png --url https://www.nuget.org/api/v2/package/Microsoft.Extensions.DependencyInjection/9.0.0
# python visualizer.py --visualizer_path ./visualizer.py --package_name Azure.Core --output_png_path ./output/output_graph_3.png --url https://www.nuget.org/api/v2/package/Azure.Core/1.44.1
