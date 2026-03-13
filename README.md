# Azure Functions Examples

A collection of practical Python examples for learning how to develop serverless functions on Azure. Each folder is an independent project that can be cloned and run on its own.

---

## Repository Structure

```
functions_azure/
├── hello_function_azure/       # Basic HTTP function: hello world
├── binding_example/            # Input and output bindings example
├── blob_function/              # Function triggered by Blob Storage events
├── blob_upload_appservice/     # File upload to Blob Storage via a web interface
├── eventhub_function/          # Function triggered by Azure Event Hubs
└── parkings_function_azure/    # HTTP function that queries parking data
```

---

## Prerequisites

- [Python 3.9+](https://www.python.org/)
- [Azure Functions Core Tools v4](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
- [Visual Studio Code](https://code.visualstudio.com/) with the [Azure Functions extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions)
- An [Azure account](https://azure.microsoft.com/free/) (for deployment)
- [Azurite](https://learn.microsoft.com/azure/storage/common/storage-use-azurite) to emulate Storage locally

---

## Examples

### `hello_function_azure`

A basic HTTP trigger function that returns a greeting on GET or POST requests. A good starting point to verify that the local environment is set up correctly.

**Trigger:** HTTP

```bash
cd hello_function_azure
func start
```

Visit `http://localhost:7071/api/hello_function_azure` in your browser.

---

### `binding_example`

Demonstrates how to use input and output bindings to connect a function to other Azure services (Storage, queues, etc.) without writing explicit connection code.

**Trigger:** HTTP  
**Key concepts:** input bindings, output bindings, `function.json`

---

### `blob_function`

A function that is automatically triggered when a file is uploaded or modified in an Azure Blob Storage container.

**Trigger:** Blob Storage  
**Required configuration in `local.settings.json`:**

```json
{
  "Values": {
    "AzureWebJobsStorage": "<YOUR_STORAGE_CONNECTION_STRING>"
  }
}
```

---

### `blob_upload_appservice`

A small web application (HTML + Python) that allows uploading files to Azure Blob Storage through a browser interface. Combines Azure Functions with a simple HTML frontend.

**Trigger:** HTTP  
**Key concepts:** file upload, Blob Storage integration, CORS

---

### `eventhub_function`

A function triggered by messages arriving at an Azure Event Hub. Useful for real-time event processing, IoT pipelines, and data streaming scenarios.

**Trigger:** Event Hub  
**Required configuration in `local.settings.json`:**

```json
{
  "Values": {
    "AzureWebJobsStorage": "<YOUR_STORAGE_CONNECTION_STRING>",
    "EventHubConnectionString": "<YOUR_EVENTHUB_CONNECTION_STRING>"
  }
}
```

---

### `parkings_function_azure`

An HTTP function that queries and returns real-time parking data from an open data API. A practical example of consuming an external API from an Azure Function.

**Trigger:** HTTP

```bash
cd parkings_function_azure
func start
```

---

## Running an Example Locally

1. Navigate to the example folder:
   ```bash
   cd <example_folder>
   ```

2. Create a `local.settings.json` file with the required configuration (see each example above):
   ```json
   {
     "IsEncrypted": false,
     "Values": {
       "AzureWebJobsStorage": "UseDevelopmentStorage=true",
       "FUNCTIONS_WORKER_RUNTIME": "python"
     }
   }
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the function:
   ```bash
   func start
   ```

> Note: `local.settings.json` is excluded from the repository because it contains sensitive information. Never commit it to version control.

---

## Deploying to Azure

From VSCode with the Azure Functions extension:

1. Press `F1` and select `Azure Functions: Deploy to Function App`
2. Choose or create a Function App in your subscription
3. Set environment variables in **Azure Portal > Function App > Configuration > Application Settings**

Or from the terminal:

```bash
func azure functionapp publish <YOUR_FUNCTION_APP_NAME>
```

---

## Resources

- [Azure Functions documentation](https://learn.microsoft.com/azure/azure-functions/)
- [Azure Functions Python developer guide](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Triggers and bindings overview](https://learn.microsoft.com/azure/azure-functions/functions-triggers-bindings)
- [Blob Storage trigger](https://learn.microsoft.com/azure/azure-functions/functions-bindings-storage-blob-trigger)
- [Event Hubs trigger](https://learn.microsoft.com/azure/azure-functions/functions-bindings-event-hubs-trigger)

---

## Author

**dgarridouma** · [GitHub](https://github.com/dgarridouma)
