import requests

URL = "http://localhost:7071/api/predict"  # replace with function URL

ejemplos = [
    {"name": "Setosa",     "features": [5.1, 3.5, 1.4, 0.2]},
    {"name": "Versicolor", "features": [6.0, 2.9, 4.5, 1.5]},
    {"name": "Virginica",  "features": [7.7, 3.8, 6.7, 2.2]},
]

for e in ejemplos:
    r = requests.post(URL, json={"features": e["features"]})
    res = r.json()
    print(f"{e['name']} -> predicted: {res['species']} "
          f"(confidence: {max(res['probabilities'].values()):.0%})")
