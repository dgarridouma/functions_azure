import azure.functions as func
import logging
import random
import uuid
from datetime import datetime

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="binding_trigger")
@app.cosmos_db_output(arg_name="documents", 
                      database_name="mibd",
                      container_name="micontenedorbinding",
                      create_if_not_exists=True,
                      partition_key="/sensor",
                      connection="CONNECTION_SETTING")
def cosmos_binding(req: func.HttpRequest, documents: func.Out[func.Document]) -> func.HttpResponse:
    new_document = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "sensor": f"sensor-{random.randint(1, 5)}",
        "value": round(random.uniform(10.0, 100.0), 2),
        "status": random.choice(["ok", "warning", "error"])
    }

    # Enviar documento a Cosmos DB
    documents.set(func.Document.from_dict(new_document))

    return func.HttpResponse(f"Documento generado y enviado:\n{new_document}", status_code=200)
