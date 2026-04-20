# sentiments_function — Code Explanation

An HTTP Azure Function that analyzes sentiment and extracts key phrases from a list of texts using **Azure AI Language**, a managed cognitive service. No model training is required — the service handles everything.

---

## 1. The approach: managed AI vs. your own model

Unlike `iris_function`, this function does not contain or serve its own model. Instead, it calls an external Azure service via its Python SDK. The pattern is:

```
Client → Azure Function → Azure AI Language API → Client
```

This is appropriate when a high-quality, production-ready model already exists for your task. Sentiment analysis is a solved problem — there is no need to train your own model.

---

## 2. Setting up the Azure AI Language resource

Before running the function you need an Azure AI Language resource:

1. In the Azure portal, search for **Language service** and create a resource.
2. Select the **Free F0** tier (5,000 transactions/month).
3. Once created, go to **Keys and Endpoint** and copy the endpoint URL and one of the keys.
4. Add them to `local.settings.json`:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "LANGUAGE_ENDPOINT": "https://<your-resource>.cognitiveservices.azure.com/",
    "LANGUAGE_KEY": "<your-key>"
  }
}
```

When deployed to Azure, these values go in **Environment variables** in the portal, not in `local.settings.json`.

---

## 3. Initializing the client at startup

```python
endpoint = os.environ["LANGUAGE_ENDPOINT"]
key      = os.environ["LANGUAGE_KEY"]
client   = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
```

Like the model in `iris_function`, the client is initialized **outside the handler** so it is reused across requests. Creating a new client on every call would add unnecessary overhead.

`os.environ` reads the values from `local.settings.json` locally and from Azure environment variables when deployed. The code is identical in both environments.

---

## 4. The handler function

```python
@app.route(route="analyze", methods=["POST"])
def analyze_sentiment(req: func.HttpRequest) -> func.HttpResponse:
```

The function accepts a JSON body with a `texts` field containing a list of strings:

```python
texts = body.get("texts")
if not texts or not isinstance(texts, list):
    return func.HttpResponse(...)   # 400 Bad Request
if len(texts) > 10:
    return func.HttpResponse(...)   # 400 Bad Request — service limit
```

The limit of 10 texts per call matches the default batch limit of the Azure AI Language API.

---

## 5. Calling the service — two operations per request

```python
sentiments  = client.analyze_sentiment(documents=texts)
key_phrases = client.extract_key_phrases(documents=texts)
```

Two separate API calls are made for each request:
- `analyze_sentiment`: returns the overall sentiment (positive, negative, neutral, mixed) and confidence scores.
- `extract_key_phrases`: returns the most relevant words and phrases in each text.

**Cost implication:** each call to the function consumes **2 transactions** against the free quota (one per operation), not 1.

---

## 6. Making a request

```bash
curl -X POST http://localhost:7071/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "I love this master, I am learning a lot about cloud",
      "The deployment failed three times and I do not know why"
    ]
  }'
```

Or from Python:

```python
import requests

r = requests.post("http://localhost:7071/api/analyze",
                  json={"texts": ["BigQuery is incredibly fast for millions of rows"]})
print(r.json())
```

---

## 7. Interpreting the response

```json
{
  "results": [
    {
      "text": "I love this master, I am learning a lot about cloud",
      "sentiment": "positive",
      "confidence": {
        "positive": 0.99,
        "neutral": 0.01,
        "negative": 0.0
      },
      "key_phrases": ["master", "cloud"]
    },
    {
      "text": "The deployment failed three times and I do not know why",
      "sentiment": "negative",
      "confidence": {
        "positive": 0.01,
        "neutral": 0.05,
        "negative": 0.94
      },
      "key_phrases": ["deployment"]
    }
  ]
}
```

- **`sentiment`**: one of `positive`, `negative`, `neutral`, or `mixed`. `mixed` appears when a text contains clearly positive and negative parts.
- **`confidence`**: probability scores for each sentiment class. They always sum to 1.0.
- **`key_phrases`**: the most meaningful words or expressions extracted from the text. These are useful for quickly understanding what a text is about without reading it in full.

---

## 8. Error handling per document

The service can fail on individual documents without failing the whole batch. The function handles this:

```python
for i, (sent, phrases) in enumerate(zip(sentiments, key_phrases)):
    if not sent.is_error and not phrases.is_error:
        results.append({...})
    else:
        results.append({"text": texts[i], "error": "Error processing text"})
```

This means a batch of 5 texts can return 4 successful results and 1 error, rather than failing entirely.

---

## 9. Interactive testing script

The `test_calls.py` script first runs predefined examples and then enters an interactive mode where you can type any sentence and get instant analysis:

```
=== Predefined examples ===
POSITIVE
   I love this master, I'm learning a lot about cloud
   Key phrases: master, cloud

NEGATIVE
   The deployment failed three times and I don't know why
   Key phrases: deployment

=== Interactive mode (type 'exit' to quit) ===

Enter a sentence: The weather is nice today
⚪ NEUTRAL
   The weather is nice today
   Key phrases: weather
```

---

## 10. Key concepts illustrated

| Concept | Where |
|---|---|
| Managed AI service | Azure AI Language instead of a custom model |
| Credentials via environment variables | `os.environ["LANGUAGE_ENDPOINT"]` |
| Client initialized at startup | Outside the handler |
| Batch processing | Multiple texts in a single call |
| Per-document error handling | `is_error` check per result |
| Two operations per call | `analyze_sentiment` + `extract_key_phrases` |
