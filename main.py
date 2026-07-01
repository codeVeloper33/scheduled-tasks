import csv
import random
import smtplib
import datetime as dt
import time
import os
import schedule
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed. Using system environment variables.")

# Get credentials from environment variables
MY_EMAIL = os.getenv('MY_EMAIL')
PASSWORD = os.getenv('PASSWORD')

# Check if credentials are set
if not MY_EMAIL or not PASSWORD:
    print("❌ ERROR: Email or password not found in environment variables!")
    print("Please create a .env file with:")
    print("MY_EMAIL=your_email@gmail.com")
    print("PASSWORD=your_app_password")
    exit(1)

def read_csv_file(filename="birthdays.csv"):
    """Read the CSV file and return list of dictionaries"""
    birthdays = []
    try:
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                birthday = {
                    'name': row['name'].strip(),
                    'email': row['email'].strip(),
                    'year': int(row['year'].strip()),
                    'month': int(row['month'].strip()),
                    'day': int(row['day'].strip())
                }
                birthdays.append(birthday)
        return birthdays
    except FileNotFoundError:
        print(f"❌ Error: {filename} not found!")
        return []
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return []

def get_random_wish(person_name):
    """Pick a random birthday wish and replace [name] with the person's name"""
    wish_files = ["letter_templates/letter_1.txt", "letter_templates/letter_2.txt", "letter_templates/letter_3.txt"]
    wishes = []
    
    for file in wish_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                wish_content = f.read().strip()
                wish_content = wish_content.replace('[name]', person_name)
                wishes.append(wish_content)
        except FileNotFoundError:
            print(f"⚠️ Warning: {file} not found, skipping...")
    
    if not wishes:
        return f"Happy Birthday {person_name}! 🎂"
    
    return random.choice(wishes)

def send_birthday_email(recipient_name, recipient_email, wish):
    """Send birthday email with proper UTF-8 encoding"""
    try:
        msg = MIMEMultipart()
        msg['From'] = MY_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = f"Happy Birthday {recipient_name}! 🎉"
        msg.attach(MIMEText(wish, 'plain', 'utf-8'))
        
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=PASSWORD)
            connection.send_message(msg)
            
        print(f"✅ Birthday wish sent to {recipient_name} ({recipient_email})")
        return True
    except Exception as e:
        print(f"❌ Failed to send to {recipient_name}: {e}")
        return False

def check_and_send_birthdays():
    """Check today's birthdays and automatically send wishes"""
    today = dt.datetime.now()
    today_month = today.month
    today_day = today.day
    
    print(f"\n{'='*60}")
    print(f"⏰ Checking birthdays at {today.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 Today is {today.strftime('%B %d, %Y')}")
    print(f"{'='*60}")
    
    birthdays = read_csv_file()
    if not birthdays:
        print("❌ No birthday data available!")
        return
    
    todays_birthdays = []
    for person in birthdays:
        if person['month'] == today_month and person['day'] == today_day:
            todays_birthdays.append(person)
    
    if not todays_birthdays:
        print(f"🎯 No birthdays today!")
        return
    
    print(f"🎂 Found {len(todays_birthdays)} birthday(s) today!")
    
    for person in todays_birthdays:
        wish = get_random_wish(person['name'])
        
        print(f"\n📝 Sending to {person['name']}...")
        print(f"   Email: {person['email']}")
        print(f"   Wish: {wish[:100]}...")
        
        send_birthday_email(
            person['name'],
            person['email'],
            wish
        )
        
        time.sleep(2)
    
    print(f"\n✅ All birthday wishes sent for today!")
    print(f"{'='*60}\n")

def run_automated():
    """Run the automated birthday bot with scheduling"""
    print("🎂 BIRTHDAY BOT STARTED")
    print("="*60)
    print(f"📅 Current date: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔄 Will check birthdays every day at 9:00 AM")
    print("📧 Will automatically send wishes to birthday people")
    print("="*60)
    print("Press Ctrl+C to stop\n")
    
    schedule.every().day.at("09:00").do(check_and_send_birthdays)
    
    print("🚀 Running initial check...")
    check_and_send_birthdays()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_automated()
