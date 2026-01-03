import random
import sqlite3
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Your bot token
TOKEN = "8192299530:AAFsDcjxj-vVgDRBaSii_k3nAswx4RioYjM"

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        join_date TEXT
    )''')
    conn.commit()
    conn.close()

def add_user(update):
    user = update.effective_user
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, join_date)
                      VALUES (?, ?, ?, ?, ?)''',
                   (user.id, user.username, user.first_name, user.last_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Enhanced BIN lookup with VBV info and fallback database
def lookup_bin_info(bin_code):
    # Real API lookup (with fallback)
    try:
        url = f"https://lookup.binlist.net/{bin_code[:6]}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            brand = data.get('scheme', 'Unknown').upper()
            bank = data.get('bank', {}).get('name', 'Unknown').upper()
            country = data.get('country', {}).get('name', 'Unknown').upper()
            flag = data.get('country', {}).get('emoji', '❓')
            
            # VBV info from API (if available)
            vbv_status = "VBV" if data.get('pay_by', {}).get('verified_by') else "NON-VBV"
            
            return {
                'brand': brand,
                'country': country,
                'bank': bank,
                'flag': flag,
                'vbv': vbv_status
            }
    except:
        pass  # If API fails, use fallback database

    # Enhanced fallback BIN database with VBV info
    fallback_bins = {
        '4': {
            'brand': 'VISA',
            'country': 'GLOBAL',
            'bank': 'VISA INC',
            'flag': '🌐',
            'vbv': 'VBV'
        },
        '51': {
            'brand': 'MASTERCARD',
            'country': 'GLOBAL',
            'bank': 'MASTERCARD',
            'flag': '🌐',
            'vbv': 'VBV'
        },
        '52': {
            'brand': 'MASTERCARD',
            'country': 'GLOBAL',
            'bank': 'MASTERCARD',
            'flag': '🌐',
            'vbv': 'VBV'
        },
        '53': {
            'brand': 'MASTERCARD',
            'country': 'GLOBAL',
            'bank': 'MASTERCARD',
            'flag': '🌐',
            'vbv': 'VBV'
        },
        '54': {
            'brand': 'MASTERCARD',
            'country': 'GLOBAL',
            'bank': 'MASTERCARD',
            'flag': '🌐',
            'vbv': 'VBV'
        },
        '55': {
            'brand': 'MASTERCARD',
            'country': 'GLOBAL',
            'bank': 'MASTERCARD',
            'flag': '🌐',
            'vbv': 'VBV'
        },
        '37': {
            'brand': 'AMERICAN EXPRESS',
            'country': 'GLOBAL',
            'bank': 'AMERICAN EXPRESS',
            'flag': '🌐',
            'vbv': 'VBV'
        },
        '60': {
            'brand': 'DISCOVER',
            'country': 'GLOBAL',
            'bank': 'DISCOVER',
            'flag': '🌐',
            'vbv': 'VBV'
        },
        '62': {
            'brand': 'UNIONPAY',
            'country': 'CHINA',
            'bank': 'UNIONPAY',
            'flag': '🇨🇳',
            'vbv': 'VBV'
        },
        '531260': {
            'brand': 'MASTERCARD DEBIT ENHANCED',
            'country': 'UNITED STATES',
            'bank': 'BANK OF AMERICA, NATIONAL ASSOCIATION',
            'flag': '🇺🇸',
            'vbv': 'VBV'
        },
        '453217': {
            'brand': 'VISA',
            'country': 'UNITED STATES',
            'bank': 'CHASE BANK',
            'flag': '🇺🇸',
            'vbv': 'VBV'
        },
        '512345': {
            'brand': 'MASTERCARD',
            'country': 'CANADA',
            'bank': 'ROYAL BANK OF CANADA',
            'flag': '🇨🇦',
            'vbv': 'NON-VBV'
        },
        '400000': {
            'brand': 'VISA',
            'country': 'UNITED STATES',
            'bank': 'TEST BANK',
            'flag': '🇺🇸',
            'vbv': 'NON-VBV'
        },
    }

    # Check for exact match first
    if bin_code[:6] in fallback_bins:
        return fallback_bins[bin_code[:6]]
    elif bin_code[:2] in fallback_bins:
        return fallback_bins[bin_code[:2]]
    elif bin_code[:1] in fallback_bins:
        return fallback_bins[bin_code[:1]]
    
    # Default fallback if nothing matches
    return {
        'brand': 'UNKNOWN',
        'country': 'UNKNOWN',
        'bank': 'UNKNOWN',
        'flag': '❓',
        'vbv': 'UNKNOWN'
    }

# Generate test card data (EXACT FORMAT: number|month|year|cvv)
def generate_test_card_data(bin_prefix):
    remaining_length = 16 - len(bin_prefix) - 1
    middle_part = ''.join([str(random.randint(0, 9)) for _ in range(remaining_length)])
    partial_number = bin_prefix + middle_part

    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10

    check_digit = (10 - luhn_checksum(partial_number + "0")) % 10
    card_number = partial_number + str(check_digit)

    # Generate expiry: month and 4-digit year
    expiry_month = f"{random.randint(1, 12):02d}"
    current_year = datetime.now().year
    expiry_year = current_year + random.randint(1, 5)

    cvv = f"{random.randint(100, 999)}"

    # EXACT FORMAT: number|month|year|cvv
    return f"{card_number}|{expiry_month}|{expiry_year}|{cvv}"

# Format output with enhanced BIN info (country, bank, VBV)
def format_card_output_with_enhanced_bin_info(bin_prefix, cards, bin_info):
    # Header with enhanced BIN info
    header = [
        f"┌─ Bin: {bin_prefix}",
        f"├─ Format: {bin_prefix}xxxxxx",
        f"├─ Brand: {bin_info['brand']} {bin_info['flag']}",
        f"├─ Country: {bin_info['country']}",
        f"├─ Bank: {bin_info['bank']}",
        f"└─ VBV: {bin_info['vbv']}",
        "──────────────────────────────",
    ]
    
    # Cards (in <code> blocks - individually copyable)
    card_blocks = [f"<code>{card}</code>" for card in cards]
    
    # Footer
    footer = [
        "──────────────────────────────",
        "└─ Bot by ➤ @platoonleaderr"
    ]
    
    # Combine all parts
    all_parts = header + card_blocks + footer
    return "\n".join(all_parts)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update)
    await update.message.reply_text(
        "Use `.gen [BIN]` to generate cards.\nExample: `.gen 531260`"
    )

# Handle .gen command (NO RATE LIMIT)
async def handle_gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.startswith('.gen'):
        return
    
    parts = text.split(maxsplit=1)
    bin_prefix = parts[1].strip() if len(parts) > 1 else '531260'

    if len(bin_prefix) < 6:
        bin_prefix = bin_prefix.ljust(6, '0')

    # Always get enhanced BIN info (with fallback)
    bin_info = lookup_bin_info(bin_prefix)
    
    cards = [generate_test_card_data(bin_prefix) for _ in range(15)]
    response = format_card_output_with_enhanced_bin_info(bin_prefix, cards, bin_info)
    
    await update.message.reply_text(response, parse_mode="HTML")

def main():
    init_db()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gen))

    print("Enhanced bot is running (BIN + VBV info)...")
    app.run_polling()

if __name__ == '__main__':
    main()
