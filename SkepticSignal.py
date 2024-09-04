import telebot
from datetime import datetime, timedelta
import re
import os
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Initialize the bot with your bot token
bot_token = '6911302813:AAHBMovOyP5H_vhYc4zdTcMMNIIZczA3tJU'
bot = telebot.TeleBot(bot_token)

# Function to adjust time and generate signal message
def generate_signal_message(signal):
    try:
        if ',' in signal:
            # Handle the original formats: "HH:MM,PAIR-DIRECTION,CALL/PUT" or "HH:MM,PAIR-DIRECTION,CALL/PUT🔼/🔽"
            parts = signal.split(',')
            if len(parts) != 3:
                raise ValueError("Expected format: HH:MM,PAIR-DIRECTION,CALL/PUT")
            time_str, pair, direction = parts

        elif ';' in signal and '-' in signal:
            # Handle the new format: "PAIR;OTC-HH:MM;CALL/PUT🔼/🔽"
            parts = signal.split(';')
            if len(parts) != 3:
                raise ValueError("Expected format: PAIR;OTC-HH:MM;CALL/PUT")
            pair = parts[0]
            time_str = parts[1].split('-')[-1]
            direction = parts[2]

        else:
            raise ValueError("Unknown format. Please ensure the signal is in the correct format.")

        # Convert time to datetime object and adjust by -30 minutes
        time_obj = datetime.strptime(time_str.strip(), '%H:%M') - timedelta(minutes=30)

        # Format the pair to "USD/PKR OTC" style
        formatted_pair = re.sub(r"([A-Z]{3})([A-Z]{3})", r"\1/\2", pair.replace('-', ' '))

        # Determine the direction
        direction_text = 'UP 🟩' if 'CALL' in direction.upper() else 'DOWN 🟥'

        message = (f"📊 *PAIR:* {formatted_pair}\n\n"
                   f"⏰ *TIME:* {time_obj.strftime('%H:%M:%S')}\n\n"
                   f"⏳ *EXPIRY:* M1 [ 1 Minute ]\n\n"
                   f"↕️ *DIRECTION:* {direction_text}\n\n"
                   f"✅¹ 1 STEP MTG ✓\n\n"
                   f"🧔🏻 OWNER : [SKEPTIC TRADER](https://t.me/+905010726177)")

        return message

    except Exception as e:
        return f"Invalid signal format: {e}. Please ensure the signal is in the correct format."

# Function to process a list of signals
def process_signals(signals):
    messages = []
    for signal in signals.splitlines():
        if signal.strip():  # Skip empty lines
            formatted_signal = generate_signal_message(signal.strip())
            messages.append(formatted_signal)
    return messages

# Start command to explain the bot's functionality and usage
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    welcome_message = (
        "Welcome to the **_Skeptic Trader Bot_**! 📉🗿📈\n\n"
        "This bot helps you generate trading signals based on the input you provide. "
        "Here's how to use the bot:\n\n"
        "1️⃣ **Format for Input Signals**:\n"
        "   You can provide your signals in any of the following formats:\n"
        "   Format 1: `HH:MM,PAIR-DIRECTION,CALL/PUT🔼/🔽`\n"
        "   Format 2: `HH:MM,PAIR-DIRECTION,CALL/PUT`\n"
        "   Format 3: `PAIR;OTC-HH:MM;CALL/PUT🔼/🔽`\n"
        "   Example:\n"
        "   `04:48,USDPKR-OTC,CALL🔼`\n"
        "   `USDPHP;OTC-12:21;PUT🔽`\n\n"
        "   Make sure each signal is on a new line. The time should be in +06:00 timezone (e.g., Dhaka).\n\n"
        "2️⃣ **What the Bot Does**:\n"
        "   - The bot will adjust the provided time to be 30 minutes earlier.\n"
        "   - It will generate a separate message for each signal in a formatted way.\n\n"
        "3️⃣ **How to Use the Bot**:\n"
        "   - To generate signals, use the command `/process_signals` followed by your signals.\n"
        "   - Example:\n"
        "     `/process_signals\n"
        "     09:31,USDPKR-OTC,CALL\n"
        "     USDPHP;OTC-12:21;PUT🔽`\n\n"
        "   The bot will then send you formatted messages for each signal with the correct time adjusted by 30 minutes.\n\n"
        "Feel free to start by entering your signals in the specified format!"
    )
    bot.send_message(chat_id, welcome_message)

# Command to receive and process signals from the user
@bot.message_handler(commands=['process_signals'])
def receive_signals(message):
    chat_id = message.chat.id

    # Check if the command has any signals provided
    try:
        signals_text = message.text.split('/process_signals ', 1)[1]
        if not signals_text.strip():
            raise IndexError
    except IndexError:
        bot.send_message(chat_id, "Please provide the signals in the format: `/process_signals 09:31,USDPKR-OTC,CALL ...`")
        return

    # Generate signal messages
    formatted_signals = process_signals(signals_text)

    # Send each signal message separately
    for signal in formatted_signals:
        bot.send_message(chat_id, signal, parse_mode='Markdown')

# Function to run the bot in a separate thread
def run_bot():
    bot.polling()

# Function to start a simple web server to bind to a port
def run_server():
    port = int(os.environ.get('PORT', 5000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Serving on port {port}")
    httpd.serve_forever()

# Start both the bot and the web server
if __name__ == "__main__":
    # Start the bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # Start the web server
    run_server()
