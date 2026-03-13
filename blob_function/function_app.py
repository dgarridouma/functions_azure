from collections import Counter
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import logging
import os


app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="miruta",
                               connection="micuentaaci_STORAGE") 
def blob_trigger(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")

    blob_name = myblob.name.split("/")[-1] # Obtenemos el nombre del fichero

    # Procesar solo archivos .txt
    if not blob_name.lower().endswith(".txt"):
        logging.info(f"Ignorando archivo no .txt: {blob_name}")
        return

    try:
        # Leer contenido del archivo .txt
        text = myblob.read().decode("utf-8")
        words = text.lower().split()
        counts = Counter(words)

        # Crear el índice de palabras
        output_lines = [f"{word}: {count}" for word, count in sorted(counts.items())]
        index_text = "\n".join(output_lines)

        # Nombre del archivo de salida (misma base, extensión .index)
        output_name = f"{blob_name}_indexado.txt"

        # Conectarse al storage para escribir la salida en otro contenedor
        connection_string = os.environ["micuentaaci_STORAGE"]
        blob_service = BlobServiceClient.from_connection_string(connection_string)

        # Contenedor de salida
        output_container = "miruta-output"

        # Crear contenedor si no existe
        container_client = blob_service.get_container_client(output_container)
        try:
            container_client.create_container()
            logging.info(f"Contenedor '{output_container}' creado.")
        except Exception:
            pass  # Ya existe

        output_blob = container_client.get_blob_client(output_name)

        # Subir el resultado
        output_blob.upload_blob(index_text, overwrite=True)

        logging.info(f"Archivo de índice guardado: {output_container}/{output_name}")

    except Exception as e:
        logging.error(f"Error procesando {blob_name}: {e}")
