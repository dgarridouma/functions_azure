import requests

URL = "http://localhost:7071/api/analyze"  # replace after deployment

def analyze(texts):
    r = requests.post(URL, json={"texts": texts})
    for res in r.json()["results"]:
        print(f"{res['sentiment'].upper()}")
        print(f"   {res['text'][:60]}")
        print(f"   Key phrases: {', '.join(res['key_phrases'])}")
        print()

# Predefined examples
print("=== Predefined examples ===\n")
analyze([
    "I love this master, I'm learning a lot about cloud",
    "The deployment failed three times and I don't know why",
    "Azure Container Apps is quite useful for production",
    "BigQuery is incredibly fast for analyzing millions of rows"
])

# Interactive mode
print("=== Interactive mode (type 'exit' to quit) ===\n")
while True:
    text = input("Enter a sentence: ").strip()
    if text.lower() == "exit":
        break
    if text:
        analyze([text])