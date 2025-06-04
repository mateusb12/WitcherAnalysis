import asyncio
import json
import logging
import webbrowser
from pathlib import Path
from channels.generic.websocket import AsyncWebsocketConsumer
from scripts.runner import Runner
from path_reference.folder_reference import get_book_graphs_path

logger = logging.getLogger(__name__)


class ProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("ProgressConsumer.connect() method called")
        logger.info(f"Scope: {self.scope}")
        logger.info("Attempting to accept WebSocket connection")
        self.client_info = self.scope.get('client')
        logger.info(f"WebSocket connect: client={self.client_info}")
        try:
            await self.accept()
            logger.info("WebSocket connection accepted successfully")
            logger.info(f"WebSocket accepted: client={self.client_info}. Waiting for 'start_processing' message.")
        except Exception as e:
            logger.error(f"Exception during WebSocket connection: {e}", exc_info=True)
            raise

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnect: client={self.client_info}, code={close_code}")
        pass

    async def run_book_processing(self, series_name, book_num, open_html=False):
        try:
            logger.info(f"Runner: Initializing for {series_name}, book {book_num}. Client: {self.client_info}")
            runner = Runner(series=series_name)

            logger.info(f"Runner: Loading book {book_num}. Client: {self.client_info}")
            await self.send(text_data=json.dumps({'increment': 5.0, 'message': f'Loading book {book_num}...'}))
            await asyncio.to_thread(runner.load_book, book_num)
            logger.info(f"Runner: Book '{runner.book_name}' loaded. Client: {self.client_info}")
            await self.send(text_data=json.dumps({'increment': 5.0, 'message': f'Book \'{runner.book_name}\' loaded.'}))
            await asyncio.sleep(0.1)

            logger.info(f"Runner: Extracting entities. Client: {self.client_info}")
            await self.send(text_data=json.dumps({'increment': 5.0, 'message': 'Starting entity extraction...'}))
            entity_df = await asyncio.to_thread(runner.book_analyser.get_book_entities)
            logger.info(f"Runner: Entity extraction complete. Client: {self.client_info}")
            await self.send(text_data=json.dumps({'increment': 20.0, 'message': 'Entity extraction complete.'}))
            await asyncio.sleep(0.1)

            logger.info(f"Runner: Filtering entities. Client: {self.client_info}")
            runner.entity_filter.set_entity_df(entity_df)  # Assuming this is fast
            filtered_df = await asyncio.to_thread(runner.entity_filter.export_filtered_dataframe)
            logger.info(f"Runner: Entity filtering complete. Client: {self.client_info}")
            await self.send(text_data=json.dumps({'increment': 20.0, 'message': 'Entity filtering complete.'}))
            await asyncio.sleep(0.1)

            logger.info(f"Runner: Building relationships. Client: {self.client_info}")
            runner.relationship_builder.set_entity_df(filtered_df)  # Assuming this is fast
            relationship_df = await asyncio.to_thread(runner.relationship_builder.aggregate_network)
            logger.info(f"Runner: Relationship building complete. Client: {self.client_info}")
            await self.send(text_data=json.dumps({'increment': 20.0, 'message': 'Relationship building complete.'}))
            await asyncio.sleep(0.1)

            logger.info(f"Runner: Running network pipeline. Client: {self.client_info}")
            runner.node_plot.set_network_df(relationship_df)  # Assuming this is fast
            await asyncio.to_thread(runner.node_plot.pipeline)
            logger.info(f"Runner: Network pipeline complete. Client: {self.client_info}")
            await self.send(text_data=json.dumps({'increment': 15.0, 'message': 'Network analysis pipeline complete.'}))
            await asyncio.sleep(0.1)

            logger.info(
                f"Runner: Generating and opening plot for book '{runner.book_name}'. Client: {self.client_info}")
            await self.send(text_data=json.dumps({'increment': 5.0, 'message': 'Generating visualization...'}))
            await asyncio.to_thread(runner.plot)

            html_file_path = Path(get_book_graphs_path(), f"{runner.book_name}.html")
            logger.info(f"HTML file path: {html_file_path}")

            logger.info(f"Runner: Analysis complete. Sending final progress. Client: {self.client_info}")
            await self.send(text_data=json.dumps({'progress': 100, 'message': 'Analysis fully complete!'}))

            if html_file_path.exists() and open_html:
                webbrowser.open_new_tab(html_file_path.as_uri())
                logger.info(f"Opened HTML file in browser: {html_file_path}. Client: {self.client_info}")
                await self.send(text_data=json.dumps({
                    'message': 'Character network visualization opened in a new browser tab.'
                }))
            else:
                logger.warning(f"HTML file not found at: {html_file_path}. Client: {self.client_info}")
                await self.send(text_data=json.dumps({
                    'message': 'Note: Could not find the generated visualization file.'
                }))

        except Exception as e:
            logger.error(f"Error during book processing for client={self.client_info}: {e}", exc_info=True)
            try:
                await self.send(text_data=json.dumps({
                    'error': str(e),
                    'message': 'An error occurred during server-side processing.'
                }))
            except Exception as send_e:
                logger.error(f"Failed to send error message to client={self.client_info}: {send_e}", exc_info=True)
        finally:
            logger.info(
                f"Closing WebSocket connection from server side after processing for: client={self.client_info}")
            await self.close()

    async def receive(self, text_data):
        logger.info(f"WebSocket receive from client={self.client_info}: {text_data}")
        try:
            text_data_json = json.loads(text_data)
            action = text_data_json.get('action')

            if action == 'start_processing':
                files = text_data_json.get('files', {})
                logger.info(f"Received 'start_processing' action. Files: {files}. Client: {self.client_info}")

                # For now, hardcode series and book number.
                # Future: derive from files['txt'] or other parameters.
                series_to_process = "witcher"
                book_to_process = 4  # Example book number from runner.py __main__

                await self.send(text_data=json.dumps({
                    'message': f"Backend received 'start_processing' for {series_to_process} book {book_to_process}. Beginning analysis."
                }))

                # Create a new task for the processing so this receive method doesn't block.
                asyncio.create_task(self.run_book_processing(series_to_process, book_to_process))
            else:
                logger.warning(
                    f"Received unknown action or non-JSON message: {text_data} from client={self.client_info}")
                await self.send(text_data=json.dumps({'message': 'Unknown action received by server.'}))
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from client={self.client_info}: {text_data}", exc_info=True)
            await self.send(text_data=json.dumps({'error': 'Invalid JSON format received by server.'}))
        except Exception as e:
            logger.error(f"Error in receive method for client={self.client_info}: {e}", exc_info=True)
            try:
                await self.send(text_data=json.dumps({'error': 'Error processing your request on the server.'}))
            except Exception as send_e:
                logger.error(f"Failed to send error message to client={self.client_info}: {send_e}", exc_info=True)
