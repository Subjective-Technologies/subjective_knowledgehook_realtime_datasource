# brainboost_desktop_package/BBKnowledgeHooksRealTimeDataSource.py

import time
from typing import List, Tuple, Dict, Any
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_desktop_package.Desktop import Desktop
from subjective_abstract_data_source_package import SubjectiveDataSource
from datetime import datetime
import numpy as np


class SubjectiveKnowledgeHookRealTimeDataSource(SubjectiveDataSource):
    def __init__(
        self,
        name: str = None,
        session: str = None,
        dependency_data_sources: List[Any] = [],
        subscribers: List[Any] = None,
        params: Dict[str, Any] = None
    ):
        """
        Initialize the BBKnowledgeHooksRealTimeDataSource.

        Args:
            name (str, optional): Name of the data source.
            session (str, optional): Session identifier.
            dependency_data_sources (list, optional): List of dependency data sources.
            subscribers (list, optional): List of subscribers.
            params (dict, optional): Parameters including 'frequency' in seconds.
        """
        super().__init__(name, session, dependency_data_sources, subscribers, params)
        self.frequency = self.params.get('frequency', 5)  # frequency in seconds, default to 5 seconds

    def fetch(self):
        """
        Fetch data in an infinite loop by taking desktop snapshots at specified frequency.
        Each snapshot includes an image and extracted texts with their bounding rectangles.
        """
        desktop = Desktop.get_desktop_singleton()
        BBLogger.log(f"Starting BBKnowledgeHooksRealTimeDataSource with frequency {self.frequency} seconds.")
        
        if self.status_callback:
            self.status_callback(self.get_name(), 'started')
        
        while True:
            try:
                # Take a snapshot
                screenshot, texts_with_rects = desktop.snapshot()
                
                # Print the image and rects as text
                snapshot_time = datetime.now().isoformat()
                print(f"Snapshot taken at {snapshot_time}")
                print(f"Image shape: {screenshot.shape}")  # (height, width, channels)
                print("Extracted Texts and their Bounding Rectangles:")
                for text, rect in texts_with_rects:
                    print(f"Text: '{text}', Rect: {rect}")
                
                # Notify subscribers with snapshot data
                snapshot_data = {
                    'timestamp': snapshot_time,
                    'image': screenshot,
                    'texts_with_rects': texts_with_rects
                }
                self.update(snapshot_data)
                
                # Optionally, use progress_callback if needed
                if self.progress_callback:
                    # Example: You can implement progress tracking here if applicable
                    pass  # Replace with actual progress tracking logic
                
                # Sleep for the specified frequency time
                time.sleep(self.frequency)
            
            except Exception as e:
                BBLogger.log(f"Exception in fetch: {e}")
                if self.status_callback:
                    self.status_callback(self.get_name(), 'error')
                break  # Exit the loop on error

    def get_icon(self) -> str:
        """Return SVG icon content, preferring a local icon.svg in the plugin folder."""
        import os
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.svg')
        try:
            if os.path.exists(icon_path):
                with open(icon_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception:
            pass
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect x="8" y="8" width="48" height="48" rx="8" fill="#10b981"/><circle cx="24" cy="24" r="4" fill="#fff"/><circle cx="40" cy="24" r="4" fill="#fff"/><rect x="20" y="36" width="24" height="6" fill="#fff"/></svg>'

    def get_connection_data(self) -> Dict[str, Any]:
        """
        Return the connection type and required fields for this data source.

        Returns:
            dict: Connection type and required fields.
        """
        # Since it's a real-time data source from the local machine, connection type is Local
        return {
            "connection_type": "Local",
            "fields": ["frequency"]  # frequency in seconds
        }


