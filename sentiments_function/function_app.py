import azure.functions as func
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import json, os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

endpoint = os.environ["LANGUAGE_ENDPOINT"]
key      = os.environ["LANGUAGE_KEY"]
client   = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))


@app.route(route="analyze", methods=["POST"])
def analyze_sentiment(req: func.HttpRequest) -> func.HttpResponse:
    """
    Body:     {"texts": ["I love this master", "The deployment failed"]}
    Response: list with sentiment + key phrases per text
    """
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(json.dumps({"error": "Invalid JSON"}),
                                 status_code=400, mimetype="application/json")

    texts = body.get("texts")
    if not texts or not isinstance(texts, list):
        return func.HttpResponse(json.dumps({"error": "'texts' must be a list"}),
                                 status_code=400, mimetype="application/json")
    if len(texts) > 10:
        return func.HttpResponse(json.dumps({"error": "Maximum 10 texts per call"}),
                                 status_code=400, mimetype="application/json")

    sentiments  = client.analyze_sentiment(documents=texts)
    key_phrases = client.extract_key_phrases(documents=texts)

    results = []
    for i, (sent, phrases) in enumerate(zip(sentiments, key_phrases)):
        if not sent.is_error and not phrases.is_error:
            results.append({
                "text": texts[i],
                "sentiment": sent.sentiment,
                "confidence": {
                    "positive": round(sent.confidence_scores.positive, 3),
                    "neutral":  round(sent.confidence_scores.neutral,  3),
                    "negative": round(sent.confidence_scores.negative, 3)
                },
                "key_phrases": phrases.key_phrases
            })
        else:
            results.append({"text": texts[i], "error": "Error processing text"})

    return func.HttpResponse(json.dumps({"results": results}, ensure_ascii=False),
                             status_code=200, mimetype="application/json")