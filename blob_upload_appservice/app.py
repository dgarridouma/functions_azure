from flask import Flask, request, render_template, redirect, url_for, flash
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import time

# Inicializar la aplicación Flask
app = Flask(__name__)
app.secret_key = 'secret' # Esto es para poder mostrar mensajes flash dentro sesion usuario,
                          # se puede poner cualquier cosa como secreto

# Configura tu conexión (claves mejor con variables de entorno)
STORAGE_ACCOUNT_NAME = "YOUR_STORAGE_ACCOUNT_NAME"  # Reemplaza con tu nombre de cuenta de almacenamiento
STORAGE_ACCOUNT_KEY = "YOUR_STORAGE_ACCOUNT_KEY"  # Reemplaza con tu clave de cuenta de almacenamiento
INPUT_CONTAINER = "miruta"
OUTPUT_CONTAINER = "miruta-output"
blob_service_client = BlobServiceClient(
    account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
    credential=STORAGE_ACCOUNT_KEY
)



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename.endswith('.txt'):
            flash("Por favor selecciona un archivo .txt válido.")
            return redirect(request.url)

        try:
            filename = file.filename
            input_blob = blob_service_client.get_blob_client(container=INPUT_CONTAINER, blob=filename)
            input_blob.upload_blob(file.read(), overwrite=True)
            return redirect(url_for('resultado', filename=filename))

        except Exception as e:
            flash(f"Error al subir: {str(e)}")
            return redirect(request.url)

    return render_template('upload.html')


@app.route('/resultado/<filename>')
def resultado(filename):
    result_blob_name = filename.replace('.txt', '.txt_indexado.txt')
    result_blob_client = blob_service_client.get_blob_client(container=OUTPUT_CONTAINER, blob=result_blob_name)

    try:
        # Verifica si el archivo procesado ya existe
        result_blob_client.get_blob_properties()

        # Genera SAS Shared Access Signature (firma de acceso compartido)
        # Es un token de seguridad limitado y temporal
        sas_token = generate_blob_sas(
            account_name=STORAGE_ACCOUNT_NAME,
            container_name=OUTPUT_CONTAINER,
            blob_name=result_blob_name,
            account_key=STORAGE_ACCOUNT_KEY,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(minutes=10)
        )

        download_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{OUTPUT_CONTAINER}/{result_blob_name}?{sas_token}"
        return render_template('resultado.html', download_url=download_url, listo=True)

    except Exception:
        # Si no existe, espera que refresquen más tarde
        return render_template('resultado.html', listo=False)


# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
