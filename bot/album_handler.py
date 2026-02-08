"""
Handles Telegram media albums (grouped messages)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Awaitable
from telethon.tl.types import Message

logger = logging.getLogger(__name__)


class AlbumHandler:
    """
    Collects grouped messages and processes them as a single album
    """
    
    def __init__(self, process_callback: Callable[[List[Message]], Awaitable[None]]):
        self.process_callback = process_callback
        self.pending_albums: Dict[int, List[Message]] = {}
        self.locks: Dict[int, asyncio.Lock] = {}
        
    async def handle_message(self, message: Message) -> bool:
        """
        Handle incoming message.
        
        Returns:
            True if message was captured as part of an album (don't process yet)
            False if message is standalone (process immediately)
        """
        if not message.grouped_id:
            return False
            
        group_id = message.grouped_id
        
        # Initialize group if new
        if group_id not in self.pending_albums:
            self.pending_albums[group_id] = []
            self.locks[group_id] = asyncio.Lock()
            
            # Schedule processing
            asyncio.create_task(self._schedule_processing(group_id))
        
        async with self.locks[group_id]:
            self.pending_albums[group_id].append(message)
            
        return True
    
    async def _schedule_processing(self, group_id: int):
        """Wait for more messages then process album"""
        # Wait for other parts to arrive
        await asyncio.sleep(2.0)
        
        messages = []
        async with self.locks[group_id]:
            if group_id in self.pending_albums:
                messages = self.pending_albums.pop(group_id)
                # cleanup lock
                self.locks.pop(group_id, None)
        
        if messages:
            # Sort by ID to ensure correct order
            messages.sort(key=lambda m: m.id)
            logger.info(f"📚 Processing album with {len(messages)} messages (Group: {group_id})")
            
            try:
                # Process the album
                # We typically process the first message (with caption) 
                # and attach others as media
                await self.process_callback(messages)
            except Exception as e:
                logger.error(f"Error processing album {group_id}: {e}")
