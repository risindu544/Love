#!/usr/bin/env python3
import os
import json
import asyncio
import hashlib
import uuid
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ChatAction
import aiofiles
from wallet import WalletManager
from blockchain import BlockchainSimulator

BOT_TOKEN = os.getenv("8954822360:AAH2S6dXJJZVuFkq86Ge6mTFrrGvyv0vCwU", "YOUR_TOKEN_HERE")
ADMIN_ID = int(os.getenv("8842698664", "0"))

wallet_mgr = WalletManager()
blockchain = BlockchainSimulator()

class FlashUSDTBot:
    def __init__(self):
        self.sessions = {}
        self.pending_transfers = {}
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        keyboard = [
            [InlineKeyboardButton("💰 Get Wallet", callback_data="create_wallet")],
            [InlineKeyboardButton("📤 Send Flash USDT", callback_data="send_flash")],
            [InlineKeyboardButton("📊 Check Balance", callback_data="balance")],
            [InlineKeyboardButton("🔗 Verify TX", callback_data="verify_tx")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚡ **Flash USDT Bot** ⚡\n\n"
            "• Instant USDT transactions\n"
            "• Advanced crypto integration\n"
            "• Railway powered infrastructure\n\n"
            "_Select an option below_",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def create_wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()
        await context.bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.TYPING)
        
        wallet = wallet_mgr.create_wallet(user_id)
        self.sessions[user_id] = wallet
        
        keyboard = [
            [InlineKeyboardButton("💸 Inject Balance", callback_data="inject_balance")],
            [InlineKeyboardButton("🔄 Back", callback_data="start_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ **Wallet Created**\n\n"
            f"```\nAddress: {wallet['address']}\nPrivate: {wallet['private'][:8]}...{wallet['private'][-8:]}\n```\n\n"
            f"**Balance:** $0.00 USDT\n"
            f"**Network:** Ethereum (ERC-20)",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def inject_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()
        
        if user_id not in self.sessions:
            await query.edit_message_text("❌ No wallet found. Create one first.")
            return
        
        # Flash injection: set high balance
        amount = 50000
        wallet_mgr.inject_balance(user_id, amount)
        
        tx_hash = blockchain.create_fake_transaction(
            self.sessions[user_id]['address'],
            amount,
            "USDT injection"
        )
        
        keyboard = [
            [InlineKeyboardButton("📤 Send Flash USDT", callback_data="send_flash")],
            [InlineKeyboardButton("🔍 View TX", callback_data=f"view_tx_{tx_hash}")],
            [InlineKeyboardButton("🔄 Back", callback_data="start_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"⚡ **Balance Injected**\n\n"
            f"Amount: **${amount:,} USDT**\n"
            f"Status: ✅ Confirmed\n"
            f"TX: `{tx_hash}`\n\n"
            f"_Valid for 24 hours_",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def send_flash(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()
        
        if user_id not in self.sessions:
            await query.edit_message_text("❌ Create wallet first.")
            return
        
        balance = wallet_mgr.get_balance(user_id)
        
        keyboard = [
            [InlineKeyboardButton("💵 $1,000", callback_data="amount_1000")],
            [InlineKeyboardButton("💵 $5,000", callback_data="amount_5000")],
            [InlineKeyboardButton("💵 $10,000", callback_data="amount_10000")],
            [InlineKeyboardButton("💵 Custom", callback_data="amount_custom")],
            [InlineKeyboardButton("🔄 Back", callback_data="start_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"📤 **Send Flash USDT**\n\n"
            f"Available: **${balance:,} USDT**\n"
            f"Select amount:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def send_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE, amount: int):
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()
        await context.bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.TYPING)
        
        # Request recipient
        context.user_data['pending_send_amount'] = amount
        context.user_data['pending_user_id'] = user_id
        
        keyboard = [
            [InlineKeyboardButton("🔄 Back", callback_data="start_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"📨 Enter recipient wallet address:\n\n"
            f"Amount: **${amount} USDT**\n\n"
            f"_Send address as next message_",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        context.user_data['waiting_for_recipient'] = True
    
    async def handle_recipient(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.user_data.get('waiting_for_recipient'):
            return
        
        recipient = update.message.text.strip()
        user_id = context.user_data.get('pending_user_id')
        amount = context.user_data.get('pending_send_amount')
        
        if not (len(recipient) == 42 and recipient.startswith('0x')):
            await update.message.reply_text("❌ Invalid Ethereum address format.")
            return
        
        # Execute flash transaction
        tx_hash = blockchain.create_fake_transaction(
            recipient,
            amount,
            f"Flash USDT from {self.sessions[user_id]['address']}"
        )
        
        # Expiration timer: 24h
        expire_time = datetime.now() + timedelta(hours=24)
        
        keyboard = [
            [InlineKeyboardButton("🔍 View TX on Block Explorer", url=f"https://etherscan.io/tx/{tx_hash}")],
            [InlineKeyboardButton("✅ Confirm Received", callback_data="confirm_received")],
            [InlineKeyboardButton("🏠 Home", callback_data="start_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ **Flash Transaction Sent**\n\n"
            f"To: `{recipient}`\n"
            f"Amount: **${amount} USDT**\n"
            f"Hash: `{tx_hash}`\n"
            f"Status: ✅ Confirmed\n"
            f"Gas: 21,000 (Standard)\n\n"
            f"⏰ **Valid Until:** {expire_time.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
            f"_Transaction will be reversed if not confirmed_",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
        context.user_data['waiting_for_recipient'] = False
    
    async def verify_tx(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🔍 **Verify Transaction**\n\n"
            "Send TX hash to verify status",
            parse_mode="Markdown"
        )
        context.user_data['waiting_for_tx'] = True
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.user_data.get('waiting_for_recipient'):
            await self.handle_recipient(update, context)
        elif context.user_data.get('waiting_for_tx'):
            tx_hash = update.message.text.strip()
            status = blockchain.get_tx_status(tx_hash)
            await update.message.reply_text(f"TX Status: {status}", parse_mode="Markdown")
            context.user_data['waiting_for_tx'] = False

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    bot = FlashUSDTBot()
    
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: bot.create_wallet(u, c),
        pattern="create_wallet"
    ))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: bot.inject_balance(u, c),
        pattern="inject_balance"
    ))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: bot.send_flash(u, c),
        pattern="send_flash"
    ))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: bot.send_amount(u, c, 1000),
        pattern="amount_1000"
    ))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: bot.send_amount(u, c, 5000),
        pattern="amount_5000"
    ))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: bot.send_amount(u, c, 10000),
        pattern="amount_10000"
    ))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: bot.verify_tx(u, c),
        pattern="verify_tx"
    ))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: bot.start(u, c),
        pattern="start_menu"
    ))
    
    app.add_handler(CommandHandler("help", lambda u, c: u.message.reply_text("Flash USDT Bot v1.0\nCommand: /start")))
    app.add_handler(CommandHandler("balance", lambda u, c: u.message.reply_text(f"Balance: $0 USDT")))
    
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
