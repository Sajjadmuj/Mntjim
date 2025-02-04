import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Replace with your Telegram Bot Token
BOT_TOKEN = "7569613960:AAG-wqsR546J8WXPBp4s93AqaD-2zm5kj_I"

# URL for tracking mobile number
URL = "https://www.findandtrace.com/trace-mobile-number-location"

# Headers for the POST request
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://www.findandtrace.com",
    "Referer": "https://www.findandtrace.com/",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
}

# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = "👋 *Welcome to the Mobile Number Tracker Bot!* 🕵️‍♂️\n\n" \
                      "Send me a mobile number, and I will track its location for you. 📱📍\n\n" \
                      "Example: `9999999999`"
    await update.message.reply_text(welcome_message, parse_mode="Markdown")
HELP_RECEIVER_ID = 7463629732  # Yahan apni Telegram ID likhein

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.replace("/help", "").strip()
    user_id = update.message.chat_id

    if not user_message:
        await update.message.reply_text("📢 *Please describe your issue after /help.*\n\nExample: `/help Mera number track nahi ho raha`", parse_mode="Markdown")
        return

    # Complaint ka message format
    complaint_text = f"📢 *New Complaint Received!*\n\n👤 *User ID:* `{user_id}`\n📝 *Complaint:* {user_message}"

    try:
        # Aapke Telegram ID par message send karega
        await context.bot.send_message(chat_id=HELP_RECEIVER_ID, text=complaint_text, parse_mode="Markdown")
        await update.message.reply_text("✅ *Your complaint has been sent successfully!* Our team will review it soon. 📩", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("❌ *Failed to send your complaint.* Please try again later. 🚨", parse_mode="Markdown")
# Function to extract tracking information
def extract_information(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    
    tables = soup.find_all("table")
    if not tables:
        return "❌ No valid tracking data found!"
    
    data = {}
    for row in tables[0].find_all("tr"):
        cols = row.find_all("td")
        if len(cols) == 2:
            key = cols[0].text.strip()
            value = cols[1].text.strip()
            data[key] = value

    formatted_response = f"✅ *Tracking Information:*\n\n"
    formatted_response += f"📱 **Mobile Number:** {data.get('Mobile Number', 'N/A')}\n"
    formatted_response += f"📍 **Telecom Circle:** {data.get('Telecoms Circle / State', 'N/A')}\n"
    formatted_response += f"📡 **Original Network:** {data.get('Original Network (First SIM)', 'N/A')}\n"
    formatted_response += f"🔄 **Current Network:** {data.get('Current Network', 'N/A')}\n"
    formatted_response += f"📶 **Service Type:** {data.get('Service Type / Signal', 'N/A')}\n"
    formatted_response += f"✅ **Connection Status:** {data.get('Connection Status', 'N/A')}\n"

    return formatted_response

# Function to track the mobile number
async def track_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mobile_number = update.message.text.strip()

    if not mobile_number.isdigit() or len(mobile_number) != 10:
        await update.message.reply_text("❌ *Invalid mobile number!* Please enter a valid 10-digit number. 📵", parse_mode="Markdown")
        return

    loading_message = await update.message.reply_text("🔍 Tracking number... Please wait.")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    data = {"mobilenumber": mobile_number, "submit": "Track Phone Number"}

    try:
        response = requests.post(URL, headers=HEADERS, data=data)
        if response.status_code == 200:
            tracking_info = extract_information(response.text)
            await loading_message.edit_text(f"✅ Tracking information for {mobile_number}: 📍\n\n{tracking_info}", parse_mode="Markdown")
        else:
            await loading_message.edit_text("❌ *Failed to retrieve tracking information.* Please try again later. 🛑", parse_mode="Markdown")
    except Exception as e:
        await loading_message.edit_text(f"❌ *An error occurred:* {str(e)} 🚨", parse_mode="Markdown")

# Main function to run the bot
if __name__ == "__main__":
    print("Starting bot...")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_number))

    print("Polling started...")
    app.run_polling()  # Bot hamesha active rahega
