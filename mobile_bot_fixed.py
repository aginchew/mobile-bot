# mobile_bot_fixed.py
import os
import logging
import traceback
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------- COMPONENTS -----------------
components = {
    "battery": {
        "category": "Power & Energy",
        "function": "Stores and supplies power.",
        "problems": ["Drains quickly", "Overheating", "Not charging"],
        "solutions": ["Reduce brightness & apps", "Avoid heat/overcharging", "Replace cable or battery"],
    },
    "charging_port": {
        "category": "Power & Energy",
        "function": "Connects charger (USB-C / Micro-USB / Lightning).",
        "problems": ["Loose charging", "Not charging", "Dust inside"],
        "solutions": ["Clean carefully", "Replace cable/adapter", "Replace connector if damaged"],
    },
    "power_ic": {
        "category": "Power & Energy",
        "function": "Manages battery charging & power distribution.",
        "problems": ["Phone not powering on", "Charging issues"],
        "solutions": ["Reflow with hot air", "Replace Power IC"],
    },
    # Display & Input
    "screen": {
        "category": "Display & Input",
        "function": "LCD / OLED / AMOLED screen that displays visuals.",
        "problems": ["Cracked display", "Dead pixels", "Unresponsive touch"],
        "solutions": ["Replace glass/screen", "Use protector", "Recalibrate or replace"],
    },
    "touchscreen": {
        "category": "Display & Input",
        "function": "Digitizer that detects finger touch.",
        "problems": ["Unresponsive", "Ghost touches"],
        "solutions": ["Clean screen", "Replace digitizer"],
    },
    "backlight": {
        "category": "Display & Input",
        "function": "Provides illumination for LCD screens.",
        "problems": ["Dim screen", "No light"],
        "solutions": ["Replace backlight IC", "Replace LED strip"],
    },
    # Imaging & Sensors
    "camera_front": {
        "category": "Imaging & Sensors",
        "function": "Front camera for selfies and video calls.",
        "problems": ["Blurry image", "App crash"],
        "solutions": ["Clean lens", "Restart or replace module"],
    },
    "camera_rear": {
        "category": "Imaging & Sensors",
        "function": "Rear camera(s) for main photography.",
        "problems": ["No focus", "Shaking", "Blurry photos"],
        "solutions": ["Clean lens", "Replace camera module"],
    },
    "flash": {
        "category": "Imaging & Sensors",
        "function": "LED flash/torch for low-light photography.",
        "problems": ["Not working", "Too dim"],
        "solutions": ["Replace LED", "Check flashlight settings"],
    },
    "proximity_sensor": {
        "category": "Imaging & Sensors",
        "function": "Detects face during calls to turn off screen.",
        "problems": ["Screen stays on during call"],
        "solutions": ["Clean sensor area", "Replace sensor"],
    },
    # Audio
    "speaker": {
        "category": "Audio",
        "function": "Provides sound output for music, videos, notifications, and phone calls.",
        "problems": ["No sound", "Distorted sound", "Low or muffled audio"],
        "solutions": ["Clean speaker", "Clean the mesh", "Replace module"],
    },
    "earpiece": {
        "category": "Audio",
        "function": "Small speaker for call audio.",
        "problems": ["Low sound", "No sound"],
        "solutions": ["Clean mesh", "Replace earpiece"],
    },
    "mic": {
        "category": "Audio",
        "function": "Captures voice during calls/recordings.",
        "problems": ["Muted voice", "Noise"],
        "solutions": ["Clean mic hole", "Replace mic"],
    },
    "vibrator": {
        "category": "Audio",
        "function": "Provides vibration alerts.",
        "problems": ["No vibration", "Weak vibration"],
        "solutions": ["Enable vibration in settings", "Replace motor"],
    },
    # Main Electronics
    "cpu": {
        "category": "Main Electronics",
        "function": "Application Processor – the brain of the phone.",
        "problems": ["Overheating", "Lag"],
        "solutions": ["Close apps", "Update software"],
    },
    "gpu": {
        "category": "Main Electronics",
        "function": "Graphics rendering unit.",
        "problems": ["Games lagging", "Screen artifacts"],
        "solutions": ["Update drivers", "Replace GPU IC"],
    },
    "ram": {
        "category": "Main Electronics",
        "function": "Temporary working memory.",
        "problems": ["Apps crash", "Phone freezes"],
        "solutions": ["Restart device", "Replace RAM chip"],
    },
    "rom": {
        "category": "Main Electronics",
        "function": "Permanent storage (eMMC / UFS).",
        "problems": ["Data corruption", "Low storage"],
        "solutions": ["Factory reset", "Replace storage IC"],
    },
    "motherboard": {
        "category": "Main Electronics",
        "function": "Main circuit board (PCB) – holds all major components.",
        "problems": ["Physical damage", "Water damage", "Not powering on"],
        "solutions": ["Repair traces", "Replace motherboard"],
    },
    "baseband_processor": {
        "category": "Main Electronics",
        "function": "Handles network signals and communication.",
        "problems": ["No network", "SIM not detected"],
        "solutions": ["Reball or replace baseband IC", "Check SIM slot"],
    },
    "power_supply_circuit": {
        "category": "Main Electronics",
        "function": "Distributes and regulates power across components.",
        "problems": ["Phone not powering", "Overheating", "Voltage drop"],
        "solutions": ["Test voltages with multimeter", "Replace regulators"],
    },
    # ICs
    "network_ic": {
        "category": "ICs",
        "function": "Handles mobile network signals.",
        "problems": ["No service", "SIM not detected"],
        "solutions": ["Reflow or replace IC"],
    },
    "audio_ic": {
        "category": "ICs",
        "function": "Controls all sound/audio functions.",
        "problems": ["No audio", "Distorted sound"],
        "solutions": ["Reflow or replace IC"],
    },
    "charging_ic": {
        "category": "ICs",
        "function": "Manages charging process.",
        "problems": ["Not charging", "Overheating while charging"],
        "solutions": ["Reflow or replace IC"],
    },
    "display_ic": {
        "category": "ICs",
        "function": "Controls signals to the display.",
        "problems": ["No display", "Flickering screen"],
        "solutions": ["Replace or reflow display IC"],
    },
    "touch_ic": {
        "category": "ICs",
        "function": "Controls touchscreen input signals.",
        "problems": ["Touch not working", "Ghost touches"],
        "solutions": ["Reflow or replace touch IC"],
    },
    "rf_ic": {
        "category": "ICs",
        "function": "Handles radio frequency communication (Wi-Fi, GSM, LTE).",
        "problems": ["No network signal", "Connectivity issues"],
        "solutions": ["Reflow or replace RF IC"],
    },
    # Supporting Components
    "capacitor": {
        "category": "Supporting Components",
        "function": "Stores and releases small amounts of charge.",
        "problems": ["Short circuit", "Device not powering on"],
        "solutions": ["Test with multimeter", "Replace capacitor"],
    },
    "resistor": {
        "category": "Supporting Components",
        "function": "Controls current flow.",
        "problems": ["Open circuit"],
        "solutions": ["Replace faulty resistor"],
    },
    "housing": {
        "category": "Supporting Components",
        "function": "External shell (plastic/metal/glass).",
        "problems": ["Cracks", "Scratches"],
        "solutions": ["Replace housing", "Use protective case"],
    },
    # Toolkit
    "multimeter": {
        "category": "Toolkit",
        "function": "Measures voltage, current, and resistance.",
        "problems": ["Incorrect reading", "Dead battery"],
        "solutions": ["Check probes", "Replace battery"],
    },
    "gorack": {
        "category": "Toolkit",
        "function": "PCB holder / jig for repair work.",
        "problems": ["Loose PCB", "Slipping during soldering"],
        "solutions": ["Secure PCB properly", "Use clamps"],
    },
    "powersupply": {
        "category": "Toolkit",
        "function": "Provides regulated power to phone circuits.",
        "problems": ["Voltage not stable", "Overcurrent"],
        "solutions": ["Adjust voltage/current", "Use fuses"],
    },
    "jumper": {
        "category": "Toolkit",
        "function": "Wire used to bridge broken traces or connections.",
        "problems": ["Wrong connection", "Short circuit"],
        "solutions": ["Double-check connections", "Use insulation"],
    },
}

# ----------------- Build category & id maps (safe callback ids) -----------------
categories = {}
for comp_name, data in components.items():
    categories.setdefault(data["category"], []).append(comp_name)

# create short ids for categories and components to avoid spaces/long callback_data
cat_id_to_name = {}
cat_name_to_id = {}
for i, cat_name in enumerate(sorted(categories.keys())):
    cid = f"c{i}"
    cat_id_to_name[cid] = cat_name
    cat_name_to_id[cat_name] = cid

comp_id_to_name = {}
comp_name_to_id = {}
for i, comp_name in enumerate(sorted(components.keys())):
    pid = f"p{i}"
    comp_id_to_name[pid] = comp_name
    comp_name_to_id[comp_name] = pid

# mapping category id -> list of comp ids
cat_to_comp_ids = {
    cid: [comp_name_to_id[name] for name in sorted(categories[cat_id_to_name[cid]])]
    for cid in cat_id_to_name
}

# ----------------- Helpers -----------------
def pretty_name(key: str) -> str:
    return key.replace("_", " ").capitalize()

def component_text(comp_key: str) -> str:
    comp = components[comp_key]
    lines = [
        f"📱 {pretty_name(comp_key)}",
        "",
        f"⚙️ Function: {comp.get('function','')}",
        "",
        "❌ Problems:",
    ]
    for p in comp.get("problems", []):
        lines.append(f"- {p}")
    lines.append("")
    lines.append("🛠️ Solutions:")
    for s in comp.get("solutions", []):
        lines.append(f"- {s}")
    return "\n".join(lines)

# ----------------- Handlers -----------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for cid, catname in cat_id_to_name.items():
        keyboard.append([InlineKeyboardButton(catname, callback_data=f"cat:{cid}")])
    keyboard.append([InlineKeyboardButton("📄 PDFs", callback_data="pdf:menu")])
    await update.message.reply_text(
        "🤖 Mobile Helper Bot — choose a category or PDFs:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    chat_id = query.message.chat.id if query.message else None

    try:
        # Category clicked
        if data.startswith("cat:"):
            cid = data.split(":", 1)[1]
            if cid not in cat_id_to_name:
                await query.edit_message_text("❌ Category not found.")
                return
            cat_name = cat_id_to_name[cid]
            pid_list = cat_to_comp_ids.get(cid, [])
            kb = []
            for pid in pid_list:
                comp_name = comp_id_to_name[pid]
                kb.append([InlineKeyboardButton(pretty_name(comp_name), callback_data=f"comp:{pid}")])
            kb.append([InlineKeyboardButton("⬅ Back", callback_data="start")])
            await query.edit_message_text(f"📂 {cat_name} — select component:", reply_markup=InlineKeyboardMarkup(kb))

        # Component clicked
        elif data.startswith("comp:"):
            pid = data.split(":", 1)[1]
            if pid not in comp_id_to_name:
                await query.edit_message_text("❌ Component not found.")
                return
            comp_key = comp_id_to_name[pid]
            text = component_text(comp_key)
            back_cid = cat_name_to_id[components[comp_key]["category"]]
            kb = [[InlineKeyboardButton("⬅ Back to category", callback_data=f"cat:{back_cid}")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))

        # PDF menu
        elif data == "pdf:menu":
            kb = [[InlineKeyboardButton(f"PDF m{i}", callback_data=f"pdf:m{i}")] for i in range(1, 31)]
            kb.append([InlineKeyboardButton("⬅ Back", callback_data="start")])
            await query.edit_message_text("📄 Select a PDF to download:", reply_markup=InlineKeyboardMarkup(kb))

        # PDF selection
        elif data.startswith("pdf:"):
            part = data.split(":", 1)[1]
            # expect m1..m30
            if not part.startswith("m"):
                await query.edit_message_text("❌ Invalid PDF id.")
                return
            pdf_name = f"{part}.pdf"
            pdf_path = os.path.join(os.getcwd(), "pdfs", pdf_name)
            if os.path.exists(pdf_path):
                # send the PDF as a new message
                with open(pdf_path, "rb") as fh:
                    await context.bot.send_document(chat_id=chat_id, document=fh)
                # after sending, show PDF menu again (as a message with keyboard)
                kb = [[InlineKeyboardButton(f"PDF m{i}", callback_data=f"pdf:m{i}")] for i in range(1, 31)]
                kb.append([InlineKeyboardButton("⬅ Back", callback_data="start")])
                await context.bot.send_message(chat_id=chat_id, text="📄 Select another PDF or go back:", reply_markup=InlineKeyboardMarkup(kb))
            else:
                await query.edit_message_text(f"⚠️ {pdf_name} not found in the 'pdfs' folder.")

        # Back to start
        elif data == "start":
            kb = []
            for cid, catname in cat_id_to_name.items():
                kb.append([InlineKeyboardButton(catname, callback_data=f"cat:{cid}")])
            kb.append([InlineKeyboardButton("📄 PDFs", callback_data="pdf:menu")])
            await query.edit_message_text("🤖 Mobile Helper Bot — choose a category or PDFs:", reply_markup=InlineKeyboardMarkup(kb))

        else:
            await query.edit_message_text("❓ Unknown action.")
    except Exception as e:
        logger.error("Error in button_handler: %s\n%s", e, traceback.format_exc())
        # Send short error to user and log full traceback
        try:
            await query.message.reply_text("⚠️ An internal error occurred. Check bot logs.")
        except Exception:
            pass

# ----------------- Search (message) handler -----------------
async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip().lower()
    if not text:
        await update.message.reply_text("Please type a keyword to search (e.g., 'not charging').")
        return

    results = []
    for comp_key, comp in components.items():
        # check problems and component name
        if text in comp_key.lower() or any(text in p.lower() for p in comp.get("problems", [])):
            # short description + button to open component
            pid = comp_name_to_id[comp_key]
            results.append(f"• {pretty_name(comp_key)} — {comp.get('function','')}\n  (open with /show {pid})")

    if results:
        await update.message.reply_text("🔍 Search results:\n\n" + "\n\n".join(results))
    else:
        await update.message.reply_text("❌ No matches found. Try different keywords.")

# ----------------- Optional: /show command to open a specific component by id -----------------
async def cmd_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /show <component_id> (e.g. /show p0). Use search results to see ids.")
        return
    pid = args[0]
    if pid not in comp_id_to_name:
        await update.message.reply_text("Unknown component id.")
        return
    comp_key = comp_id_to_name[pid]
    text = component_text(comp_key)
    back_cid = cat_name_to_id[components[comp_key]["category"]]
    kb = [[InlineKeyboardButton("⬅ Back to category", callback_data=f"cat:{back_cid}")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

# ----------------- MAIN -----------------
def main():
    TOKEN = "8443686192:AAGNmXg0sI3jki-iYg2_dOBKCGc43621rLQ" # <<-- Replace with your token
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("show", cmd_show))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_handler))

    logger.info("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
