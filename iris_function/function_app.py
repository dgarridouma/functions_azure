import azure.functions as func
import joblib, json, os

app = func.FunctionApp()

# Load model (out of handler)
model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
data         = joblib.load(model_path)
model        = data["model"]
target_names = data["target_names"]

@app.route(route="predict", methods=["POST"])
def predict(req: func.HttpRequest) -> func.HttpResponse:
    """
    Body:     {"features": [5.1, 3.5, 1.4, 0.2]}
    Response: {"class": 0, "species": "setosa", "probabilities": {...}}
    """
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(json.dumps({"error": "invalid JSON"}),
                                 status_code=400, mimetype="application/json")

    features = body.get("features")
    if features is None:
        return func.HttpResponse(json.dumps({"error": "Missing field 'features'"}),
                                 status_code=400, mimetype="application/json")
    if len(features) != 4:
        return func.HttpResponse(
            json.dumps({"error": "4 values are needed: [sepal_length, sepal_width, petal_length, petal_width]"}),
            status_code=400, mimetype="application/json")

    prediction = model.predict([features])[0]
    probs      = model.predict_proba([features])[0]

    response = {
        "class":   int(prediction),
        "species": target_names[prediction],
        "probabilities": {n: round(float(p), 4) for n, p in zip(target_names, probs)},
        "input": {"sepal_length": features[0], "sepal_width": features[1],
                  "petal_length": features[2], "petal_width": features[3]}
    }
    return func.HttpResponse(json.dumps(response), status_code=200, mimetype="application/json")
