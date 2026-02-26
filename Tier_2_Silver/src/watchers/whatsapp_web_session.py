#!/usr/bin/env python3
"""
WhatsApp Web Session Manager - Silver Tier
Manages WhatsApp Web browser session and messaging
Uses Playwright for automation
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class WhatsAppWebSession:
    """Manage WhatsApp Web session and messaging"""

    def __init__(self, vault_path: str = None, phone_number: str = "03002385209"):
        self.vault_path = Path(vault_path or '/mnt/d/Hackaton-0/AI_Employee_Vault')
        self.logs = self.vault_path / 'Logs'
        self.inbox = self.vault_path / 'Inbox'
        self.phone_number = phone_number

        # Setup logging
        self.logger = logging.getLogger('WhatsAppSession')
        handler = logging.FileHandler(self.logs / 'whatsapp_session.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Session state
        self.session_active = False
        self.browser = None
        self.page = None
        self.processed_chats = set()

        self.logger.info(f'WhatsApp Session initialized for {phone_number}')

    async def initialize_browser(self):
        """Initialize Playwright browser for WhatsApp Web"""
        try:
            from playwright.async_api import async_playwright

            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=False)
            self.page = await self.browser.new_page()

            # Navigate to WhatsApp Web
            await self.page.goto('https://web.whatsapp.com')

            self.logger.info('Browser initialized - Please scan QR code on screen')
            print('📱 WhatsApp Web opened - Please scan QR code with your phone')
            print('Phone: ' + self.phone_number)

            # Wait for chat list to load (max 30 seconds)
            try:
                await self.page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                self.session_active = True
                self.logger.info('WhatsApp Web session authenticated')
                print('✅ WhatsApp authenticated successfully!')
                return True
            except:
                self.logger.error('QR scan timeout - session not authenticated')
                return False

        except Exception as e:
            self.logger.error(f'Failed to initialize browser: {e}')
            return False

    async def fetch_recent_messages(self, limit: int = 10) -> List[Dict]:
        """
        Fetch recent messages from all chats

        Args:
            limit: Number of recent messages to fetch

        Returns:
            List of recent messages
        """
        try:
            if not self.session_active:
                return []

            # Get all chat bubbles
            messages = []
            chats = await self.page.query_selector_all('[data-testid="msg"]')

            for i, chat in enumerate(chats[:limit]):
                try:
                    # Extract message text
                    msg_text = await chat.text_content()

                    # Extract sender if available
                    sender_elem = await chat.query_selector('[data-testid="bubble-sender"]')
                    sender = await sender_elem.text_content() if sender_elem else 'Unknown'

                    message = {
                        'sender': sender.strip(),
                        'text': msg_text.strip(),
                        'timestamp': datetime.now().isoformat(),
                        'chat_index': i
                    }

                    messages.append(message)
                    self.logger.info(f'Fetched message from {sender}')

                except Exception as e:
                    self.logger.warning(f'Failed to fetch message {i}: {e}')
                    continue

            return messages

        except Exception as e:
            self.logger.error(f'Failed to fetch messages: {e}')
            return []

    async def send_message(self, recipient: str, message_text: str) -> bool:
        """
        Send a WhatsApp message

        Args:
            recipient: Contact name or number
            message_text: Message to send

        Returns:
            Success status
        """
        try:
            if not self.session_active:
                self.logger.error('Session not active - cannot send message')
                return False

            # Search for recipient
            search_box = await self.page.query_selector('[data-testid="search-input"]')
            if search_box:
                await search_box.fill(recipient)
                await self.page.wait_for_timeout(1000)

            # Click first result
            first_result = await self.page.query_selector('[data-testid="contact-list-item"]')
            if first_result:
                await first_result.click()
                await self.page.wait_for_timeout(1000)

            # Type message
            msg_input = await self.page.query_selector('[data-testid="msg-input"]')
            if msg_input:
                await msg_input.fill(message_text)

            # Send button
            send_btn = await self.page.query_selector('[data-testid="send"]')
            if send_btn:
                await send_btn.click()

                self.logger.info(f'Sent message to {recipient}: {message_text[:50]}...')
                print(f'✅ Message sent to {recipient}')

                # Log to vault
                self._log_sent_message(recipient, message_text)

                return True

            return False

        except Exception as e:
            self.logger.error(f'Failed to send message: {e}')
            return False

    def _log_sent_message(self, recipient: str, message: str):
        """Log sent message to vault"""
        try:
            log_file = self.logs / 'whatsapp_sent_messages.log'

            with open(log_file, 'a') as f:
                f.write(f'[{datetime.now().isoformat()}] MESSAGE SENT\n')
                f.write(f'To: {recipient}\n')
                f.write(f'Message: {message}\n')
                f.write(f'Status: SENT\n\n')

        except Exception as e:
            self.logger.error(f'Failed to log sent message: {e}')

    def create_vault_backup(self, message_data: Dict):
        """
        Back up message data to Obsidian vault

        Args:
            message_data: Message to back up
        """
        try:
            filename = f"WA_BACKUP_{message_data['sender'][:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = self.inbox / filename

            content = f"""---
type: whatsapp_backup
from: {message_data['sender']}
timestamp: {message_data['timestamp']}
---

# WhatsApp Message Backup

**From:** {message_data['sender']}
**Time:** {message_data['timestamp']}

## Message
{message_data['text']}

---
*Backed up from WhatsApp Web Session*
*Phone: {self.phone_number}*
"""

            filepath.write_text(content)
            self.logger.info(f'Created vault backup: {filename}')

        except Exception as e:
            self.logger.error(f'Failed to create vault backup: {e}')

    async def close_session(self):
        """Close WhatsApp Web session"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()

            self.session_active = False
            self.logger.info('WhatsApp session closed')
            print('🛑 WhatsApp session closed')

        except Exception as e:
            self.logger.error(f'Failed to close session: {e}')

if __name__ == '__main__':
    import asyncio

    async def main():
        session = WhatsAppWebSession(phone_number='03002385209')

        # Initialize browser
        success = await session.initialize_browser()

        if success:
            print("\n✅ WhatsApp Session Ready!")
            print("- Phone: 03002385209")
            print("- Status: AUTHENTICATED")
            print("- Awaiting commands...")

            # Keep session alive
            await asyncio.sleep(5)

            # Test: fetch recent messages
            messages = await session.fetch_recent_messages()
            print(f"\nFetched {len(messages)} recent messages")

        await session.close_session()

    # Run async main
    asyncio.run(main())
