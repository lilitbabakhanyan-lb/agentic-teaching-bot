import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from agents.orchestrator import build_package, research, prepare_email
from tools.email import send_email
from tools.slides import save_uploaded_file
from tools.logger import log

load_dotenv()
SESSIONS = {}


def get_state(user_id: int) -> dict:
    return SESSIONS.setdefault(user_id, {"approved": False, "logs": []})


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I am your Agentic Teaching Assistant Bot.\n\n"
        "Here is how you can use me:\n\n"
        "1. Upload a lecture PDF.\n"
        "2. Send a command like:\n\n"
        "/plan 60 minutes | undergraduate students | English | your_email@gmail.com\n\n"
        "3. I will generate a lesson plan and teaching package.\n"
        "4. Use /research to get supporting web resources.\n"
        "5. Use /send after approval to email the result.\n\n"
        "Use /help to see all commands."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - introduce the bot\n"
        "/help - show commands and limitations\n"
        "/plan duration | audience | language | recipient@email - generate package\n"
        "/research - find 3 supporting web resources\n"
        "/status - show uploaded files, current state, and errors\n"
        "/approve - approve latest preview for email sending\n"
        "/send - send latest approved report by email\n\n"
        "Email is never sent without /approve."
    )


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(update.effective_user.id)
    doc = update.message.document
    if not doc.file_name.lower().endswith(".pdf"):
        await update.message.reply_text("Please upload a PDF file. PPTX is not supported in this minimal version.")
        return
    tg_file = await doc.get_file()
    file_bytes = await tg_file.download_as_bytearray()
    path = save_uploaded_file(bytes(file_bytes), doc.file_name)
    state["file_path"] = path
    state["file_name"] = doc.file_name
    log(state, f"Uploaded {doc.file_name}")
    await update.message.reply_text(f"Uploaded {doc.file_name}. Now run /plan duration | audience | language | email")


async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(update.effective_user.id)
    raw = " ".join(context.args)
    if raw:
        parts = [p.strip() for p in raw.split("|")]
        if len(parts) >= 1 and parts[0]: state["duration"] = parts[0]
        if len(parts) >= 2 and parts[1]: state["audience"] = parts[1]
        if len(parts) >= 3 and parts[2]: state["language"] = parts[2]
        if len(parts) >= 4 and parts[3]: state["recipient_email"] = parts[3]
    await update.message.reply_text("Generating preview with the local LLM...")
    package = build_package(state)
    email_preview = prepare_email(state)
    preview = f"LESSON PACKAGE PREVIEW\n\n{package}\n\nEMAIL PREVIEW\n\n{email_preview}\n\nReply /approve before /send."
    await update.message.reply_text(preview[:3900])


async def research_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(update.effective_user.id)
    text = research(state)
    await update.message.reply_text(text[:3900])


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(update.effective_user.id)
    if not state.get("email_body"):
        await update.message.reply_text("No email preview exists yet. Run /plan first.")
        return
    state["approved"] = True
    log(state, "User approved email preview.")
    await update.message.reply_text("Approved. You can now run /send.")


async def send_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(update.effective_user.id)
    if not state.get("approved"):
        await update.message.reply_text("Email not sent. Please review the preview and run /approve first.")
        return
    if not state.get("recipient_email"):
        await update.message.reply_text("Email not sent. Missing recipient email. Run /plan with an email address.")
        return
    result = send_email(state["recipient_email"], "Generated Teaching Package", state.get("email_body", ""))
    log(state, result)
    await update.message.reply_text(result)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(update.effective_user.id)
    text = (
        f"File: {state.get('file_name', 'none')}\n"
        f"Duration: {state.get('duration', 'not set')}\n"
        f"Audience: {state.get('audience', 'not set')}\n"
        f"Language: {state.get('language', 'not set')}\n"
        f"Recipient: {state.get('recipient_email', 'not set')}\n"
        f"Approved: {state.get('approved', False)}\n\n"
        "Logs:\n" + "\n".join(state.get("logs", [])[-10:])
    )
    await update.message.reply_text(text[:3900])


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN. Put it in .env")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("plan", plan))
    app.add_handler(CommandHandler("research", research_cmd))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("send", send_cmd))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    print("Bot is running. Open Telegram and send /start")
    app.run_polling()


import asyncio

if __name__ == "__main__":
    asyncio.set_event_loop(asyncio.new_event_loop())
    main()
