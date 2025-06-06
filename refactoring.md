# Refactoring Guide for Your Django Backend
This document provides a step-by-step guide to refactor your Django backend, focusing on improving architectural clarity, clean architecture and maintainability.
---

## Ⅱ. Backend Refactoring Guide
The goal here is to improve the structure for better separation of concerns, maintainability, and scalability

### Current Structure Observations:
* Django project: `character_net`
* Main app: `api` within `django_layer`
* Core logic (book processing, NLP) seems to be in `scripts.runner` and `nlp_processing.entity_network_from_filedata`, which are invoked by `api/consumers.py` and `api/views.py`.
* Uses Django Channels for async tasks and WebSockets.
* `api/models.py` is currently empty
* 
### Step 1: Define a Clearer Project and App Structure
The current `django_layer` folder contains both the Django project (`character_net`) and the `api` app. While functional, you might consider a more standard Django layout:
```
your_project_root/
├── source/
│   ├── manage.py
│   ├── character_net/      # Django Project directory
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py         # Modified to import routings correctly
│   │   └── project_config.py # Or move this into settings
│   ├── apps/                 # A new directory to house all your apps
│   │   ├── __init__.py
│   │   ├── api/              # Your existing api app
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── consumers.py
│   │   │   ├── models.py
│   │   │   ├── routing.py
│   │   │   ├── serializers.py
│   │   │   ├── services.py   # New: For business logic
│   │   │   ├── tests.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   └── book_processor/   # New: Optional app for book processing logic
│   │       ├── __init__.py
│   │       ├── apps.py
│   │       ├── services.py   # Contains logic like Runner, EntityNetworkPipeline
│   │       ├── tasks.py      # For Celery tasks if you move away from Channels for some bg tasks
│   │       └── ...
│   ├── static/               # Project-level static files
│   ├── templates/            # Project-level templates (if any)
│   └── ... (other files like .gitignore, requirements.txt)
├── requirements.txt
└── start.bat
```
**Actions:**

1.  **Create `apps` directory:** `mkdir source/apps`
2.  **Move `api` app:** `mv source/django_layer/api source/apps/`
3.  **Update `INSTALLED_APPS`:** In `source/character_net/settings.py`, change `'django_layer.api'` to `'apps.api'`. Update `apps.api.apps.ApiConfig` name attribute if necessary (it currently is `django_layer.api`).
4.  **Update Imports:** Globally search and replace `django_layer.api` with `apps.api`.
5.  **Relocate Project Directory:** Move `character_net` contents (settings.py, urls.py etc from `source/django_layer/character_net`) into `source/character_net`.
* Update `os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'character_net.settings')` in `manage.py` and `wsgi.py`/`asgi.py`.
* Update `ROOT_URLCONF = 'character_net.urls'` in `settings.py`.
* Update `ASGI_APPLICATION = 'character_net.asgi.application'` in `settings.py`.
* Adjust `BASE_DIR` in `settings.py` if necessary. Currently: `Path(__file__).resolve().parent.parent`. If `settings.py` is in `source/character_net/`, then `BASE_DIR` should be `Path(__file__).resolve().parent.parent` to point to `source/`. This seems correct.


### Step 2: Introduce a Service Layer for Business Logic
Your views and consumers currently call directly into what seems like utility/scripting modules (`scripts.runner`, `nlp_processing`). Encapsulating this logic in a dedicated service layer within your Django apps will make it more organized, testable, and reusable.
**Actions:**
1.  **Create `services.py`:**
* In `source/apps/api/`, create `services.py`.
* If you decide to create a `book_processor` app, create `services.py` there too.
2.  **Relocate and Refactor Business Logic:**
* Move the core logic from `scripts.runner.Runner` and `nlp_processing.entity_network_from_filedata.EntityNetworkPipeline` into classes/functions within these new `services.py` files.
* For example, `EntityNetworkPipeline` could become `BookAnalysisService` in `apps.book_processor.services.py` or `apps.api.services.py`.
* The `Runner` class seems to orchestrate this; it could be part of this service or a higher-level service.
* These service classes should not directly handle HTTP requests/responses or WebSocket messages. They should take plain Python data types as input and return results or raise specific exceptions.
**Example `apps.api.services.py` (conceptual):**
```python
# source/apps/api/services.py
import asyncio
import pandas as pd
from pathlib import Path
import webbrowser # Consider if this should be here or handled by consumer/view
# Assume these are refactored or imported from a more structured location
# from some_core_nlp_module import CoreNLPEngine
# from some_core_graphing_module import CoreGraphPlotter
# from path_reference.folder_reference import get_book_graphs_path # Ensure this path is robust
class BookProcessingService:
def __init__(self, series_name, progress_callback=None):
self.series_name = series_name
self.book_name = None
self.progress_callback = progress_callback
# self.nlp_engine = CoreNLPEngine()
# self.graph_plotter = CoreGraphPlotter()
# self.entity_filter = SomeEntityFilter() # etc.
async def _send_progress(self, increment=None, message=None, progress_value=None):
if self.progress_callback:
payload = {}
if increment:
payload['increment'] = increment
if message:
payload['message'] = message
if progress_value:
payload['progress'] = progress_value
await self.progress_callback(payload)
def _blocking_load_book(self, book_num):
# ... existing logic from Runner.load_book ...
# self.book_name = f"Book {book_num} of {self.series_name}" # Example
# print(f"Book '{self.book_name}' loaded.")
pass
def _blocking_extract_entities(self):
# ... existing logic from Runner.book_analyser.get_book_entities ...
# print("Entity extraction complete.")
# return pd.DataFrame() # Example
pass
def _blocking_filter_entities(self, entity_df):
# ... existing logic from Runner.entity_filter.export_filtered_dataframe ...
# print("Entity filtering complete.")
# return pd.DataFrame() # Example
pass
def _blocking_build_relationships(self, filtered_df):
# ... existing logic from Runner.relationship_builder.aggregate_network ...
# print("Relationship building complete.")
# return pd.DataFrame() # Example
pass
def _blocking_network_pipeline(self, relationship_df):
# ... existing logic from Runner.node_plot.pipeline ...
# print("Network pipeline complete.")
pass
def _blocking_plot(self):
# ... existing logic from Runner.plot ...
# self.html_file_path = Path(get_book_graphs_path(), f"{self.book_name}.html")
# print(f"Plot generated: {self.html_file_path}")
pass
async def process_book(self, book_num):
# This orchestrates the calls, using asyncio.to_thread for blocking parts
await self._send_progress(message=f"Backend received 'start_processing' for {self.series_name} book {book_num}. Beginning analysis.")
await self._send_progress(increment=5.0, message=f'Loading book {book_num}...')
await asyncio.to_thread(self._blocking_load_book, book_num)
await self._send_progress(increment=5.0, message=f'Book \'{self.book_name}\' loaded.')
await asyncio.sleep(0.1) # Keep UI responsive
await self._send_progress(increment=5.0, message='Starting entity extraction...')
entity_df = await asyncio.to_thread(self._blocking_extract_entities)
await self._send_progress(increment=20.0, message='Entity extraction complete.')
await asyncio.sleep(0.1)
await self._send_progress(increment=20.0, message='Entity filtering complete.')
# ... (continue for other steps: filter_entities, build_relationships, etc.) ...
# Each step would call await self._send_progress(...) and await asyncio.to_thread(self._blocking_method, args)
await self._send_progress(increment=5.0, message='Generating visualization...')
await asyncio.to_thread(self._blocking_plot)
# html_file_path = self.html_file_path # Get from instance
# logger.info(f"HTML file path: {html_file_path}")
await self._send_progress(progress_value=100, message='Analysis fully complete!')
# The decision to open webbrowser should ideally be signaled to the consumer,
# and consumer should inform the client, client-side JS handles opening.
# For now, returning the path or a success flag.
# if html_file_path.exists():
#     return {"success": True, "path": html_file_path.as_uri(), "message": "Visualization opened."}
# else:
#     return {"success": False, "path": None, "message": "Could not find visualization."}
return {"success": True, "message": "Processing finished (simulated path)."} # Placeholder
```
3.  **Update Consumers and Views:**
* Modify `ProgressConsumer` in `apps.api.consumers.py` to instantiate and call methods from `BookProcessingService`. The consumer's role becomes primarily managing WebSocket communication and delegating to the service.
* The `progress_callback` for the service can be a method within the consumer that sends data over the WebSocket.
**Refactored `ProgressConsumer` (conceptual):**
```python
# source/apps/api/consumers.py
import asyncio
import json
import logging
# Remove direct imports of Runner, etc.
from .services import BookProcessingService # Assuming service is in api/services.py
logger = logging.getLogger(__name__)
class ProgressConsumer(AsyncWebsocketConsumer):
async def connect(self):
# ... (existing connect logic) ...
await self.accept()
async def disconnect(self, close_code):
# ... (existing disconnect logic) ...
pass
async def _send_progress_update(self, payload):
"""Callback for the service to send progress."""
await self.send(text_data=json.dumps(payload))
async def run_book_processing_task(self, series_name, book_num):
service = BookProcessingService(series_name=series_name, progress_callback=self._send_progress_update)
try:
result = await service.process_book(book_num)
# Handle result, e.g., send a final message if needed, or if webbrowser opening is server-side.
# if result.get("path") and result.get("success"):
#    webbrowser.open_new_tab(result["path"]) # If still server-side
#    await self.send(text_data=json.dumps({'message': result["message"]}))
# elif not result.get("success"):
#    await self.send(text_data=json.dumps({'message': result["message"], 'error': True})) # Example error
pass # Final success message already sent by service via callback
except Exception as e:
logger.error(f"Error during book processing: {e}", exc_info=True)
await self.send(text_data=json.dumps({
'error': str(e),
'message': 'An error occurred during server-side processing.'
}))
finally:
logger.info("Closing WebSocket connection from server side after processing.")
await self.close()
async def receive(self, text_data):
# ... (existing receive logic to parse action) ...
if action == 'start_processing':
# ...
series_to_process = "witcher" # Example
book_to_process = 4         # Example
# Create a new task for the processing
asyncio.create_task(self.run_book_processing_task(series_to_process, book_to_process))
# ...
```
* Similarly, refactor `upload_books` view in `apps.api.views.py` if it directly uses `EntityNetworkPipeline`. It should call a service method instead.
* The `progress_callback` for synchronous views calling services that do background work is tricky if not using Channels. If `upload_books` is meant to be synchronous and *also* report progress, this is architecturally challenging. The current setup with `cache` and `channel_layer.group_send` in `upload_books` suggests it might be trying to do this, but `EntityNetworkPipeline`'s `progress_callback` isn't clearly shown how it links back to a WebSocket for *that specific view's request*.
* **Recommendation:** For long-running tasks initiated by HTTP requests that need progress, the standard pattern is:
1.  HTTP request initiates the task (e.g., creates a task ID, starts it via Celery or `asyncio.create_task` if the webserver setup supports it like Daphne).
2.  Client then connects to a WebSocket (using the task ID) to get progress updates.
* Your `ProgressConsumer` already does this WebSocket part. The `upload_books` view might be redundant or for a different flow. Clarify its purpose. If it's an alternative to the WebSocket flow, it should be simplified or removed if the WebSocket flow is preferred.
### Step 3: Refine Models (If Applicable)
Your `api/models.py` is currently empty. As your application evolves, you might need to store:
* Information about uploaded books (metadata, processing status).
* User accounts (if you add authentication).
* Results of analyses.
**Actions:**
1.  Identify entities that need to be persisted.
2.  Define Django models for these entities.
3.  Create and run migrations: `python manage.py makemigrations api` and `python manage.py migrate`.
### Step 4: Configuration and Settings
* **Environment Variables:** You're using `python-dotenv` (`load_dotenv()` in `manage.py`), which is good for managing sensitive settings like `SECRET_KEY`, database credentials, etc. Ensure all configurable parts are managed this way and not hardcoded.
* **Logging:** `ProgressConsumer` uses `logging`. Ensure logging is configured comprehensively in `settings.py` to capture relevant information for debugging and monitoring.
### Step 5: URL Structure
Your main `character_net/urls.py` includes `api.urls`. This is standard.
* Review URL naming and structure for clarity.
* Ensure you're using `reverse()` or `{% url %}` with URL names instead of hardcoding paths.
### Step 6: Static Files and Templates
* Static files are configured in `settings.py` (`STATIC_URL`, `STATICFILES_DIRS`).
* Templates are in `source/django_layer/static` and configured in `TEMPLATES` setting. This is fine, though typically Django templates are in a `templates` directory, and `static` is for CSS/JS/images. Your current `static` dir seems to serve both. Renaming `source/django_layer/static` to `source/templates` and adjusting `TEMPLATES['DIRS']` might be slightly more conventional if these HTML files are Django templates. If `entry_page.html`, `progress_bar.html`, `upload_component.html` are purely frontend templates rendered by Django views, their location is acceptable.
### Step 7: Iterative Refactoring and Testing
1.  **Small Steps:** Refactor one part of the application at a time (e.g., move `Runner` logic to a service, then update the consumer, then test).
2.  **Test Continuously:** After each small refactoring step, run your tests (unit, integration, consumer) to ensure nothing is broken.
3.  **Version Control:** Use Git and commit frequently. Create branches for significant refactoring efforts.
4.  **Code Review:** If possible, have someone else review your refactored code.
### Long-Term Considerations:
* **Task Queues (Celery):** For very long-running, CPU-bound, or I/O-bound tasks that are not directly tied to a persistent WebSocket connection's lifetime, or if you need more robust task management (retries, distributed workers), consider using Celery with a message broker (RabbitMQ, Redis). Django Channels is excellent for WebSocket handling and tasks tied to the connection, but Celery excels at detached background jobs.
* **Caching:** You're using `django.core.cache` in `views.py` for progress updates. Review caching strategies for other parts of the application if performance becomes an issue.
* **Database Optimization:** If you add models and experience database performance issues, look into query optimization, indexing, etc.
* **Scalability:** Consider how your application will scale. Using services and potentially Celery can help in distributing load.
---
This guide provides a roadmap. The specifics will depend on the full details of your codebase, especially the parts currently in `.repomixignore`. Remember to prioritize writing tests before and during the refactoring. Good luck!

