import requests
import zipfile
import io
import os
import re
import unicodedata

url = "https://datos.gob.cl/api/action/package_show?id=33245"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    resources = data["result"]["resources"]

    for resource in resources:
        url_download = resource["url"]
        print("URL:", url_download)

        response_download = requests.get(url_download)

        if response_download.status_code == 200:
            folder_name = resource["name"]
            folder_name = re.sub(r'[<>:"/\\|?*]', '', folder_name)  # Remover caracteres no permitidos en el nombre de carpeta

            # Remover acentos y caracteres especiales
            folder_name = unicodedata.normalize("NFKD", folder_name).encode("ascii", "ignore").decode("utf-8")

            # Crear ruta absoluta para la carpeta
            folder_path = os.path.abspath(folder_name)

            os.makedirs(folder_path, exist_ok=True)

            content = io.BytesIO(response_download.content)
            with zipfile.ZipFile(content, "r") as zip_ref:
                for file in zip_ref.namelist():
                    if "version" in file:
                        new_file = file.replace("version", "")
                        file_path = os.path.join(folder_path, new_file)
                        zip_ref.extract(file, folder_path)
                        os.rename(os.path.join(folder_path, file), file_path)
                        print(f"Extracción de {file} completa en {file_path}")
                    else:
                        file_path = os.path.join(folder_path, file)
                        zip_ref.extract(file, folder_path)
                        print(f"Extracción de {file} completa en {file_path}")
        else:
            print("Error al descargar el archivo. Código de estado:", response_download.status_code)
else:
    print("Error al obtener los datos. Código de estado:", response.status_code)
