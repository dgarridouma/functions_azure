import logging
import azure.functions as func
import datetime
from azure.cosmos import CosmosClient, PartitionKey, exceptions
import csv
import requests
import uuid

app = func.FunctionApp()

URL='https://datosabiertos.malaga.eu/recursos/aparcamientos/ocupappublicosmun/ocupappublicosmun.csv'

# Crear el cliente de Cosmos DB con la cadena de conexión
connection_string = "AccountEndpoint=https://YOUR_COSMOS_DB_ACCOUNT.documents.azure.com:443/;AccountKey=YOUR_COSMOS_DB_ACCOUNT_KEY;"
client = CosmosClient.from_connection_string(connection_string)

# Crear la base de datos y el contenedor si no existen
# con clave de partición: id_parking para separar datos por parking
database_name = "mibd"
container_name = "parkings_function"
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

# Store parking occupation for a specific parking
def store_parking_cosmos(id, name, free_places):
 
    response_dict={
        'id': str(uuid.uuid1()), # Id generado por marca tiempo y MAC
        'id_parking': id,   # partition key
        'name': name,
        'free_places': free_places,
        'time': str(datetime.datetime.utcnow().replace(microsecond=0))   # We remove milliseconds (microseconds)
                # _ts (timestamp) is automatially generated when using create_item
    }
    rows_to_insert = [ response_dict ]
    
    for document in rows_to_insert:
        try:
            # Insertar el documento en el contenedor
            container.create_item(body=document)
        except exceptions.CosmosResourceExistsError:
            # Si el documento ya existe, actualizarlo
            container.upsert_item(body=document)





@app.timer_trigger(schedule="0 */5 * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    url='https://datosabiertos.malaga.eu/recursos/aparcamientos/ocupappublicosmun/catalogo.csv'
    catalogo=dict()
    headers = {'User-Agent': 'myagent'}
    response=requests.get(url,headers=headers)
    response.encoding='utf-8'
    reader = csv.reader(response.text.splitlines(),delimiter=',')
    header_row = next(reader)
    for row in reader:
        #print(row[0])
        #print(row[1])
        catalogo[row[0]]=row[1]

    url = URL
    headers = {'User-Agent': 'myagent'}
    response=requests.get(url,headers=headers)
    response.encoding='utf-8'   # accents are ok
    reader = csv.reader(response.text.splitlines(),delimiter=',')
    header_row = next(reader)

    try:
       for row in reader:
            try:
                logging.info(row[1]+" "+catalogo[row[1]]+" "+row[2])
                store_parking_cosmos(row[1],catalogo[row[1]],int(row[2])) 
            except:
                pass
    except:
        pass       

    logging.info('Python timer trigger function executed.')