"""
Main Telegram bot client with dependency injection
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from telethon import TelegramClient, events, Button
from telethon.errors import FloodWaitError, SessionPasswordNeededError
from telethon.tl.types import Message

from bot.config import Config
from bot.storage import Storage
from bot.filters import MessageFilter
from bot.ai_service import AIService
from bot.processors import MessageProcessor
from bot.rate_limiter import RateLimiter
from bot.monitoring import Monitoring
from bot.health import HealthCheckServer
from bot.performance import get_performance_monitor, TimedOperation
import bot.exceptions as be
from bot.deduplication import Deduplicator

logger = logging.getLogger(__name__)


class NewsBot:
    """
    Production-ready Telegram news bot with modular architecture
    """
    
    def __init__(
        self,
        config: Config,
        storage: Storage,
        monitoring: Monitoring,
        health_server: HealthCheckServer
    ):
        """
        Initialize news bot with dependencies
        
        Args:
            config: Configuration instance
            storage: Storage instance
            monitoring: Monitoring instance
            health_server: Health check server instance
        """
        self.config = config
        self.storage = storage
        self.monitoring = monitoring
        self.health_server = health_server
        self.perf_monitor = get_performance_monitor()
        
        # Initialize services
        self.message_filter = MessageFilter(
            keywords=config.KEYWORDS,
            spam_keywords=config.SPAM_KEYWORDS
        )
        
        self.ai_service = AIService(api_key=config.GROQ_API_KEY)
        
        self.processor = MessageProcessor(
            message_filter=self.message_filter,
            ai_service=self.ai_service
        )
        
        # New deduplicator (85% similarity threshold)
        self.deduplicator = Deduplicator(threshold=85)
        
        self.rate_limiter = RateLimiter(
            max_per_minute=20,
            max_per_hour=100
        )
        
        # Telegram clients
        from telethon.sessions import StringSession
        import os
        
        session_str = os.getenv('SESSION_STRING')
        if session_str:
            session = StringSession(session_str)
            logger.info("Using StringSession from environment variable")
        else:
            session = 'session'
            logger.info("Using file session")
            
        self.client = TelegramClient(
            session,
            config.API_ID,
            config.API_HASH
        )
        
        self.bot_client: Optional[TelegramClient] = None
        self.review_channel: Optional[int] = None
        
        # State
        self.running = False
        self.valid_sources = []
        
        logger.info("🤖 NewsBot initialized with modular architecture")
        logger.info(f"📊 Source channels: {', '.join(config.SOURCE_CHANNELS)}")
        logger.info(f"🎯 Target channel: {config.TARGET_CHANNEL}")
        logger.info(f"📝 Max posts/day: {config.MAX_POSTS_PER_DAY}")
        logger.info(f"🔑 Keywords: {len(config.KEYWORDS)} configured")
    
    async def start(self) -> None:
        """Start the bot"""
        logger.info("🚀 Starting NewsBot...")
        
        try:
            # Initialize database
            await self.storage.initialize()
            
            # Start health check server
            await self.health_server.start()
            
            # Connect userbot
            await self._connect_userbot()
            
            # Connect bot API if configured
            if self.config.BOT_TOKEN:
                await self._connect_bot_api()
            
            # Validate channels
            await self._validate_channels()
            
            # Forward today's old messages first
            await self._forward_today_messages()
            
            # Setup handlers
            self._setup_handlers()
            
            # Mark as ready
            self.health_server.mark_ready()
            self.running = True
            
            logger.info("✅ NewsBot started successfully!")
            logger.info("👂 Listening for new messages...")
            
            # Run both clients
            await asyncio.gather(
                self.client.run_until_disconnected(),
                self.bot_client.run_until_disconnected() if self.bot_client else asyncio.sleep(0)
            )
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            await self.shutdown()
        except Exception as e:
            logger.error(f"Fatal error in bot: {e}", exc_info=True)
            self.monitoring.record_error("fatal_error", e)
            raise
    
    async def _connect_userbot(self) -> None:
        """Connect userbot for message monitoring"""
        logger.info("Connecting userbot...")
        
        try:
            await self.client.start()
            me = await self.client.get_me()
            logger.info(f"✅ Userbot connected: {me.first_name} (@{me.username})")
            
            self.monitoring.set_user_context(me.id, me.username)
            
        except SessionPasswordNeededError:
            logger.error("❌ 2FA password required! Run bot locally first to authenticate.")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to connect userbot: {e}")
            self.monitoring.record_error("userbot_connection_failed", e)
            raise
    
    async def _connect_bot_api(self) -> None:
        """Connect bot API for review mode"""
        logger.info("Connecting Bot API...")
        
        try:
            self.bot_client = TelegramClient(
                'bot_session',
                self.config.API_ID,
                self.config.API_HASH
            )
            await self.bot_client.start(bot_token=self.config.BOT_TOKEN)
            
            bot_me = await self.bot_client.get_me()
            logger.info(f"✅ Bot API connected: @{bot_me.username}")
            
            # Setup review channel
            if self.config.REVIEW_CHANNEL_ID:
                rc_id = self.config.REVIEW_CHANNEL_ID
                if rc_id.lstrip('-').isdigit():
                    self.review_channel = int(rc_id)
                else:
                    self.review_channel = rc_id
                logger.info(f"👀 Review channel: {self.review_channel}")
            else:
                me = await self.client.get_me()
                self.review_channel = me.id
                logger.info(f"ℹ️ Review channel not set, using PM: {me.id}")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to connect Bot API: {e}")
            self.bot_client = None
    
    async def _validate_channels(self) -> None:
        """Validate source and target channels"""
        logger.info("🔍 Validating channels...")
        
        # Validate target channel
        try:
            target = await self.client.get_entity(self.config.TARGET_CHANNEL)
            logger.info(f"✅ Target channel: {target.title}")
        except Exception as e:
            logger.error(f"❌ Cannot access target channel {self.config.TARGET_CHANNEL}: {e}")
            raise
        
        # Validate source channels
        for source in self.config.SOURCE_CHANNELS:
            try:
                await self.client.get_entity(source)
                self.valid_sources.append(source)
            except Exception as e:
                logger.warning(f"⚠️ Cannot access source channel {source}: {e}")
        
        if not self.valid_sources:
            raise ValueError("No valid source channels available!")
        
        logger.info(f"✅ Valid sources: {len(self.valid_sources)}/{len(self.config.SOURCE_CHANNELS)}")
    
    async def _forward_today_messages(self) -> None:
        """Forward today's old messages (from midnight until now)"""
        logger.info("📅 Checking for today's old messages...")
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        forwarded_count = 0
        total_checked = 0
        
        for source in self.valid_sources:
            logger.info(f"  🔍 Checking {source}...")
            channel_messages = 0
            
            try:
                # Get messages from today
                async for message in self.client.iter_messages(
                    source,
                    offset_date=datetime.now(),
                    reverse=True,
                    limit=100  # Check last 100 messages per channel
                ):
                    total_checked += 1
                    channel_messages += 1
                    
                    # Check if message is from today
                    if message.date < today:
                        continue
                    
                    # Skip if no text
                    if not message.text:
                        continue
                    
                    # Check if already forwarded
                    msg_id = f"{message.chat_id}_{message.id}"
                    if await self.storage.is_message_forwarded(msg_id):
                        continue
                    
                    # Check daily limit
                    today_count = await self.storage.get_today_post_count()
                    if today_count >= self.config.MAX_POSTS_PER_DAY:
                        logger.info(f"⚠️ Daily limit reached ({self.config.MAX_POSTS_PER_DAY})")
                        return
                    
                    # Process message
                    chat = await message.get_chat()
                    source_name = getattr(chat, 'title', getattr(chat, 'username', 'Unknown'))
                    processed = await self.processor.process_message(message, source_name)
                    
                    if not processed:
                        continue
                    
                    # Apply rate limiting
                    await self.rate_limiter.acquire()
                    
                    # Send directly (no review for old messages)
                    try:
                        await self.client.send_message(
                            self.config.TARGET_CHANNEL,
                            processed['final_text']
                        )
                        
                        # Mark as forwarded
                        await self.storage.mark_message_forwarded(msg_id, source_name, processed['original_text'])
                        await self.storage.increment_today_post_count()
                        
                        forwarded_count += 1
                        logger.info(f"  ✅ [{forwarded_count}] Forwarded old message from {source_name}")
                        
                        # Small delay
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        logger.error(f"Failed to forward old message: {e}")
                
                logger.info(f"    📊 Checked {channel_messages} messages from {source}")
                        
            except Exception as e:
                logger.warning(f"Error checking {source} for old messages: {e}")
        
        logger.info(f"📊 Total checked: {total_checked} messages")
        if forwarded_count > 0:
            logger.info(f"✅ Forwarded {forwarded_count} old messages from today")
        else:
            logger.info("ℹ️ No old messages to forward")
    
    
    def _setup_handlers(self) -> None:
        """Setup message handlers"""
        # Bot API callback handler (for review buttons)
        if self.bot_client:
            @self.bot_client.on(events.CallbackQuery)
            async def callback_handler(event):
                await self._handle_callback(event)
        
        # Userbot message handler
        @self.client.on(events.NewMessage(chats=self.valid_sources))
        async def message_handler(event):
            await self._handle_new_message(event.message)
    
    async def _handle_new_message(self, message: Message) -> None:
        """
        Handle new message from source channel
        
        Args:
            message: Telegram message
        """
        source_name = "Unknown"
        start_time = datetime.now()
        
        try:
            # Get source channel info
            chat = await message.get_chat()
            source_name = getattr(chat, 'title', getattr(chat, 'username', 'Unknown'))
            msg_id = f"{message.chat_id}_{message.id}"
            
            # Record reception
            self.health_server.record_message_processed()
            
            # Performance monitoring context
            with TimedOperation(self.perf_monitor, "processing"):
                
                # Check if already forwarded
                with TimedOperation(self.perf_monitor, "db"):
                    if await self.storage.is_message_forwarded(msg_id):
                        logger.debug(f"Message {msg_id} already forwarded, skipping")
                        self.perf_monitor.record_message_processed(0.0, source_name, forwarded=False)
                        return
                
                # Check daily limit
                with TimedOperation(self.perf_monitor, "db"):
                    today_count = await self.storage.get_today_post_count()
                
                if today_count >= self.config.MAX_POSTS_PER_DAY:
                    logger.info(f"Daily limit reached ({self.config.MAX_POSTS_PER_DAY}), skipping")
                    self.perf_monitor.record_message_processed(0.0, source_name, forwarded=False)
                    return
                
                # --- Smart Deduplication ---
                if message.text and len(message.text) > 50:  # Only check meaningful messages
                    with TimedOperation(self.perf_monitor, "db"):
                        recent_msgs = await self.storage.get_recent_messages(limit=20)
                    
                    is_dup, score, match = self.deduplicator.is_duplicate(message.text, recent_msgs)
                    
                    if is_dup:
                        logger.info(f"♻️ Duplicate content detected ({score}% similarity). Skipping.")
                        logger.debug(f"Matches: {match[:50]}...")
                        self.perf_monitor.record_message_processed(
                            (datetime.now() - start_time).total_seconds(),
                            source_name,
                            forwarded=False
                        )
                        return
                # ---------------------------
                
                # Process message
                processed = await self.processor.process_message(message, source_name)
                
                if not processed:
                    self.perf_monitor.record_message_processed(
                        (datetime.now() - start_time).total_seconds(),
                        source_name,
                        forwarded=False
                    )
                    return
                
                logger.info(f"📨 Message from {source_name}: {processed['reason']}")
                
                # Apply rate limiting
                await self.rate_limiter.acquire()
                
                # Forward message
                if self.bot_client and self.review_channel:
                    await self._send_to_review(processed, message)
                else:
                    await self._send_directly(processed)
                
                # Mark as forwarded
                with TimedOperation(self.perf_monitor, "db"):
                    await self.storage.mark_message_forwarded(
                        msg_id,
                        source_name,
                        processed['original_text']
                    )
                    new_count = await self.storage.increment_today_post_count()
                
                # Record success
                self.perf_monitor.record_message_processed(
                    (datetime.now() - start_time).total_seconds(),
                    source_name,
                    forwarded=True
                )
                
                logger.info(f"✅ Forwarded! Today: {new_count}/{self.config.MAX_POSTS_PER_DAY}")
            
        except FloodWaitError as e:
            logger.warning(f"FloodWaitError: {e.seconds}s", extra={"error_code": "FLOOD_WAIT"})
            self.perf_monitor.record_rate_limit_hit()
            self.perf_monitor.record_error("flood_wait")
            await self.rate_limiter.handle_flood_wait(e.seconds)
            
        except be.BotError as e:
            logger.error(be.format_error_message(e))
            self.perf_monitor.record_error(e.error_code)
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            self.perf_monitor.record_error("unexpected_error")
    
    async def _send_to_review(self, processed: dict, original_message: Message) -> None:
        """Send message to review channel"""
        try:
            # Download media if present
            file_path = await self.processor.download_media(original_message)
            
            buttons = [
                [Button.inline("✅ Skelbti", b'approve')],
                [Button.inline("❌ Ištrinti", b'reject')]
            ]
            
            await self.bot_client.send_message(
                self.review_channel,
                processed['final_text'],
                file=file_path,
                buttons=buttons
            )
            
            # Cleanup
            if file_path:
                self.processor.cleanup_media_file(file_path)
            
            logger.info(f"👀 Sent to review: {self.review_channel}")
            
        except Exception as e:
            raise be.TelegramConnectionError(f"Failed to send to review: {e}")
    
    async def _send_directly(self, processed: dict) -> None:
        """Send message directly to target channel"""
        try:
            await self.client.send_message(
                self.config.TARGET_CHANNEL,
                processed['final_text'],
                file=processed['media']
            )
            
            logger.info(f"✅ Sent directly to {self.config.TARGET_CHANNEL}")
            
        except Exception as e:
            raise be.TelegramConnectionError(f"Failed to send directly: {e}")
    
    async def _handle_callback(self, event) -> None:
        """Handle callback from review buttons"""
        try:
            data = event.data.decode('utf-8')
            msg = await event.get_message()
            
            if data == 'approve':
                # Publish message
                await self.bot_client.send_message(
                    self.config.TARGET_CHANNEL,
                    msg.text,
                    file=msg.media
                )
                await event.edit(f"✅ PASKELBTA\n\n{msg.text[:100]}...", buttons=None)
                logger.info("✅ [Admin] Message approved and published")
                
            elif data == 'reject':
                await event.delete()
                logger.info("🗑 [Admin] Message rejected")
                
        except Exception as e:
            logger.error(f"Callback error: {e}")
            await event.answer(f"Klaida: {e}", alert=True)
            self.monitoring.record_error("callback_error", e)
    
    async def shutdown(self) -> None:
        """Graceful shutdown"""
        logger.info("🛑 Shutting down NewsBot...")
        
        self.running = False
        self.health_server.mark_not_ready()
        
        # Close database
        await self.storage.close()
        
        # Disconnect clients
        if self.client.is_connected():
            await self.client.disconnect()
        
        if self.bot_client and self.bot_client.is_connected():
            await self.bot_client.disconnect()
        
        # Stop health server
        await self.health_server.stop()
        
        logger.info("✅ Shutdown complete")
