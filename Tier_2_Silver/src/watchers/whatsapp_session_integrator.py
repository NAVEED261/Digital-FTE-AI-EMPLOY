#!/usr/bin/env python3
"""
WhatsApp Session Integrator - Silver Tier
Bridges WhatsApp Web browser automation with Obsidian vault
Manages message fetching, processing, and sending via Playwright
"""

import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright not installed. Install with: pip install playwright")
    raise


class WhatsAppSessionIntegrator:
    """Integrate WhatsApp Web with Obsidian vault via Playwright"""

    def __init__(self, vault_path: str = None, phone_number: str = "03002385209"):
        self.vault_path = Path(vault_path or '/mnt/d/Hackaton-0/AI_Employee_Vault')
        self.inbox = self.vault_path / 'Inbox'
        self.logs = self.vault_path / 'Logs'
        self.phone_number = phone_number

        # Ensure directories exist
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger('WhatsAppIntegrator')
        handler = logging.FileHandler(self.logs / 'whatsapp_integrator.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Browser state
        self.playwright = None
        self.browser = None
        self.page = None
        self.session_active = False
        self.processed_chats = set()

        self.logger.info(f'WhatsApp Session Integrator initialized for {phone_number}')

    async def initialize_browser(self) -> bool:
        """Initialize Playwright browser for WhatsApp Web"""
        try:
            self.playwright = await async_playwright().start()

            # Launch browser with headless=False to show UI for QR scanning
            self.browser = await self.playwright.chromium.launch(headless=False)
            self.page = await self.browser.new_page()

            # Navigate to WhatsApp Web
            await self.page.goto('https://web.whatsapp.com')

            self.logger.info('Browser initialized - Waiting for QR code scan')
            print('📱 WhatsApp Web opened - Please scan QR code with phone 03002385209')
            print('⏳ Waiting for authentication (max 30 seconds)...')

            # Wait for authentication by checking for chat list
            try:
                await self.page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                self.session_active = True
                self.logger.info('✅ WhatsApp Web session authenticated successfully')
                print('✅ WhatsApp authenticated successfully!')
                return True
            except:
                self.logger.error('QR scan timeout - session not authenticated')
                print('❌ Authentication timeout - please try again')
                return False

        except Exception as e:
            self.logger.error(f'Failed to initialize browser: {e}')
            print(f'❌ Browser initialization failed: {e}')
            return False

    async def fetch_recent_messages(self, limit: int = 10) -> List[Dict]:
        """
        Fetch recent messages from all chats

        Args:
            limit: Number of recent messages to fetch

        Returns:
            List of message dicts with sender, text, timestamp
        """
        try:
            if not self.session_active:
                self.logger.warning('Session not active - cannot fetch messages')
                return []

            messages = []

            # Query all message bubbles
            msg_elements = await self.page.query_selector_all('[data-testid="msg"]')

            self.logger.info(f'Found {len(msg_elements)} message elements')

            for i, msg_elem in enumerate(msg_elements[:limit]):
                try:
                    # Extract message text
                    msg_text = await msg_elem.text_content()

                    # Try to extract sender from parent chat
                    chat_elem = await msg_elem.evaluate('el => el.closest("[data-testid=\"chatlist-item\"]")')
                    sender = "Unknown"

                    if chat_elem:
                        sender_elem = await msg_elem.evaluate(
                            'el => el.closest("[data-testid=\"chat\"]")?.querySelector("[title]")'
                        )
                        if sender_elem:
                            sender = await sender_elem.evaluate('el => el.getAttribute("title")')

                    message = {
                        'sender': sender.strip() if sender else 'Unknown',
                        'text': msg_text.strip() if msg_text else '',
                        'timestamp': datetime.now().isoformat(),
                        'chat_index': i
                    }

                    messages.append(message)
                    self.logger.info(f'Fetched message from {message["sender"]}: {message["text"][:50]}...')

                except Exception as e:
                    self.logger.warning(f'Failed to extract message {i}: {e}')
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

            # Search for recipient in chat list
            search_box = await self.page.query_selector('[data-testid="search-input"]')
            if search_box:
                await search_box.fill(recipient)
                await self.page.wait_for_timeout(1000)

            # Click first search result
            first_result = await self.page.query_selector('[data-testid="contact-list-item"]')
            if first_result:
                await first_result.click()
                await self.page.wait_for_timeout(1000)

            # Type message in input
            msg_input = await self.page.query_selector('[data-testid="msg-input"]')
            if msg_input:
                await msg_input.fill(message_text)

            # Click send button
            send_btn = await self.page.query_selector('[data-testid="send"]')
            if send_btn:
                await send_btn.click()
                await self.page.wait_for_timeout(500)

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
status: backed_up
---

# WhatsApp Message Backup

**From:** {message_data['sender']}
**Time:** {message_data['timestamp']}

## Message
{message_data['text']}

---
*Backed up from WhatsApp Web Session*
*Phone: {self.phone_number}*
*Integrator: Fatima Zehra - Message Specialist*
"""

            filepath.write_text(content)
            self.logger.info(f'Created vault backup: {filename}')

        except Exception as e:
            self.logger.error(f'Failed to create vault backup: {e}')

    async def process_and_backup_messages(self, messages: List[Dict]):
        """Process and backup messages to vault"""
        for msg in messages:
            self.create_vault_backup(msg)
            self.logger.info(f'Backed up message from {msg["sender"]}')

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

    async def run_continuous_sync(self, check_interval: int = 120):
        """
        Run continuous WhatsApp monitoring loop

        Args:
            check_interval: Seconds between checks
        """
        self.logger.info('Starting continuous WhatsApp sync')
        print(f'🔄 Starting WhatsApp continuous sync (check interval: {check_interval}s)')

        try:
            while self.session_active:
                # Fetch recent messages
                messages = await self.fetch_recent_messages()

                if messages:
                    print(f'📩 Found {len(messages)} messages')
                    await self.process_and_backup_messages(messages)

                # Wait for next check
                await asyncio.sleep(check_interval)

        except KeyboardInterrupt:
            print('\n⌨️ Sync interrupted by user')
        except Exception as e:
            self.logger.error(f'Error in sync loop: {e}')
        finally:
            await self.close_session()


async def main():
    """Main entry point for WhatsApp Session Integrator"""
    print('🚀 WhatsApp Session Integrator - Silver Tier')
    print('=' * 60)

    integrator = WhatsAppSessionIntegrator(phone_number='03002385209')

    # Initialize browser and authenticate
    success = await integrator.initialize_browser()

    if success:
        print("\n✅ WhatsApp Session Ready!")
        print("- Phone: 03002385209")
        print("- Status: AUTHENTICATED")
        print("- Vault Integration: ACTIVE")
        print("- Awaiting commands...")

        # Keep session alive for message monitoring
        await asyncio.sleep(5)

        # Test: Fetch messages
        messages = await integrator.fetch_recent_messages()
        print(f"\n📊 Fetched {len(messages)} recent messages")

        if messages:
            for msg in messages[:3]:
                print(f"  - From {msg['sender']}: {msg['text'][:50]}...")
                integrator.create_vault_backup(msg)

    # Close session
    await integrator.close_session()


if __name__ == '__main__':
    asyncio.run(main())
