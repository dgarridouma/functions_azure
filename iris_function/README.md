# iris_function — Code Explanation

An HTTP Azure Function that serves a machine learning classification model trained on the Iris dataset. The function receives flower measurements and returns the predicted species.

---

## 1. Training the model

Before deploying the function, run `train_model.py` once locally to generate `model.pkl`:

```python
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

joblib.dump({"model": model, "target_names": list(iris.target_names)}, "model.pkl")
```

- `joblib.dump` serializes the model to a binary file. This is the standard way to persist scikit-learn models.
- Both the model and the class names (`setosa`, `versicolor`, `virginica`) are saved together so the function can return human-readable labels.
- The resulting `model.pkl` file is only a few hundred kilobytes — lightweight enough to include directly in the deployment package.

---

## 2. Loading the model at startup

```python
model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
data         = joblib.load(model_path)
model        = data["model"]
target_names = data["target_names"]
```

This code runs **outside the handler function**, at module load time. This is important: Azure Functions reuses the same Python process across multiple requests, so loading the model once at startup avoids reloading it on every call. If the model were loaded inside the handler, each request would pay the deserialization cost.

---

## 3. The handler function

```python
@app.route(route="predecir", methods=["POST"])
def predecir(req: func.HttpRequest) -> func.HttpResponse:
```

The decorator registers this function as an HTTP trigger responding to POST requests at the route `/api/predecir`.

**Input validation:**
```python
features = body.get("features")
if features is None:
    return func.HttpResponse(...)   # 400 Bad Request
if len(features) != 4:
    return func.HttpResponse(...)   # 400 Bad Request
```

The function expects exactly 4 numeric values corresponding to the Iris measurements:
- `sepal_length`
- `sepal_width`
- `petal_length`
- `petal_width`

**Prediction:**
```python
prediction = model.predict([features])[0]
probs      = model.predict_proba([features])[0]
```

- `model.predict` returns the class index (0, 1, or 2).
- `model.predict_proba` returns the probability for each class. This is more informative than the predicted class alone — it tells you how confident the model is.

---

## 4. Making a request

```bash
curl -X POST http://localhost:7071/api/predecir \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

Or from Python:

```python
import requests

r = requests.post("http://localhost:7071/api/predecir",
                  json={"features": [5.1, 3.5, 1.4, 0.2]})
print(r.json())
```

---

## 5. Interpreting the response

```json
{
  "class": 0,
  "species": "setosa",
  "probabilities": {
    "setosa": 0.97,
    "versicolor": 0.02,
    "virginica": 0.01
  },
  "input": {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }
}
```

- **`class`**: numeric index of the predicted class (0 = setosa, 1 = versicolor, 2 = virginica).
- **`species`**: human-readable class name.
- **`probabilities`**: confidence scores for each class. They always sum to 1.0. A high score for the predicted class means the model is confident. Setosa is usually predicted with very high confidence because it is linearly separable from the other two species.
- **`input`**: the original measurements echoed back, useful for debugging.

---

## 6. What happens when the input is wrong

If you send fewer or more than 4 features:

```bash
curl -X POST http://localhost:7071/api/predecir \
  -d '{"features": [5.1, 3.5]}'
```

Response:
```json
{"error": "Exactly 4 values required: [sepal_length, sepal_width, petal_length, petal_width]"}
```

The function returns HTTP 400 with a descriptive message. Always validate inputs in production functions.

---

## 7. scikit-learn input shapes

Understanding the expected shape of inputs is essential for using scikit-learn correctly.

### Training — `model.fit(X, y)`

`X` must be **2D**: rows are samples, columns are features. `y` must be **1D**: one label per sample.

```python
print(X_train.shape)  # (120, 4) — 120 samples, 4 features
print(y_train.shape)  # (120,)   — 120 labels

# Concrete example: first 3 rows of X_train
# [[5.1, 3.5, 1.4, 0.2],   ← sample 1: setosa
#  [4.9, 3.0, 1.4, 0.2],   ← sample 2: setosa
#  [6.3, 3.3, 4.7, 1.6]]   ← sample 3: versicolor

# Corresponding labels in y_train
# [0, 0, 1]
```

### Prediction — `model.predict(X)`

`X` must also be **2D**, even for a single sample. This is why `features` is wrapped in an extra list:

```python
# features coming from the HTTP request: a plain Python list
features = [5.1, 3.5, 1.4, 0.2]

# Wrong — 1D input, scikit-learn raises an error
model.predict(features)       # shape (4,) — ValueError

# Correct — wrap in a list to make it 2D with shape (1, 4)
model.predict([features])     # shape (1, 4) — OK
```

`predict` returns a 1D array with one prediction per sample:
```python
model.predict([[5.1, 3.5, 1.4, 0.2]])  # array([0])
```

`predict_proba` returns a 2D array — one row per sample, one column per class:
```python
model.predict_proba([[5.1, 3.5, 1.4, 0.2]])
# array([[0.97, 0.02, 0.01]])
#          ↑      ↑      ↑
#        setosa  versicolor  virginica
```

Since we only pass one sample, we access `[0]` to get the flat array of probabilities:
```python
probs = model.predict_proba([features])[0]
# array([0.97, 0.02, 0.01])
```

Then we zip it with the class names to build the response dictionary:
```python
{name: round(float(prob), 4) for name, prob in zip(target_names, probs)}
# {"setosa": 0.97, "versicolor": 0.02, "virginica": 0.01}
```

---

## 8. Key concepts illustrated

| Concept | Where |
|---|---|
| Model serialization | `train_model.py` → `joblib.dump` |
| Load once at startup | Model loaded outside the handler |
| Input validation | Checks before calling `model.predict` |
| 2D input shape required | `model.predict([features])` not `model.predict(features)` |
| Probability scores | `model.predict_proba` returns shape `(1, 3)` |
| HTTP 400 on bad input | Explicit error responses |
