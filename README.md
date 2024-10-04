# WhatsApp GroupChat Web Scraping Tool

This tool automates the process of scraping messages, images, and metadata from a WhatsApp Web group chat. It uses `Selenium` and `webdriver_manager` to interact with WhatsApp Web, scroll through chat history, and extract information such as message text, sender information, timestamps, and any shared images. The extracted data is saved locally for further analysis or storage.

## Features

- **Scrapes WhatsApp Web group chat messages**: Extracts message content, sender details, and timestamps.
- **Downloads shared images**: Saves images shared in the chat to a local folder.
- **Handles dynamic scrolling**: Automatically scrolls and loads older messages as needed.
- **Stores data in structured format**: Outputs the scraped data in a structured way (e.g., as a list of dictionaries).

## Prerequisites

- **Python 3.x**
- **Google Chrome** (ensure it's installed and up-to-date)
- **ChromeDriver**: The correct version of ChromeDriver is automatically managed via `webdriver_manager`.

## Installation

1. **Clone this repository**:

   ```bash
   git clone https://github.com/ahubler01/whatsapp_webscraper.git
   cd whatsapp-scraper
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. Configuring the `.env` File

You can store configuration variables such as the group chat name, Chrome profile path, and the oldest message date at which you want to scrape in a `.env` file to keep your settings separate from the code.

1. **Create a `.env` file** in the project root with the following content:

   ```plaintext
    GROUP_CHAT_NAME="family group ❤️"
    CHROME_PROFILE="/Users/johndoe/Library/Application Support/Google/Chrome/Profile 2"
    OLDEST_MESSAGE="[08:15, 01/01/2023]"
   ```

2. **Set up your Chrome profile** to avoid scanning the WhatsApp QR code each time:

   - Log into WhatsApp Web manually in Chrome.
   - Locate your Chrome profile path (usually under `~/.config/google-chrome/` or `C:\Users\<username>\AppData\Local\Google\Chrome\User Data`).
   - Specify your Chrome profile in the .env to reuse the session.

3. **Run the script**:

   ```bash
   python whatsapp_scraper.py
   ```

## Usage

- **Initial Setup**: Make sure you log into WhatsApp Web manually once to avoid scanning the QR code each time the script runs.
- **Configure Group Chat Name**: Update the group chat name in the script to match the group you want to scrape.
- **Output**: The scraped messages, sender details, timestamps, and images will be saved locally.

## Output

- **Messages**: Extracted text messages, sender information, and timestamps are stored as a list of dictionaries or any other structured format.
- **Images**: Images shared in the group chat are downloaded and saved locally in the `images` folder, with unique filenames based on hashes of the timestamp and random numbers.

## Example Output

```
[
    {
        'message': 'Hello, how are you?',
        'date': '2024-10-04T14:23:55',
        'sender': 'John Doe',
        'image': 'null'
    },
    {
        'message': 'Check out this image!',
        'date': '2024-10-04T14:25:10',
        'sender': 'Jane Doe',
        'image': 'a1b2c3d4e5f6.png'
    }
]
```

## Contribution

Feel free to submit pull requests or issues for improvements or bug fixes. Contributions are always welcome!

## Troubleshooting

If you encounter any issues, try the following:

1. **Outdated ChromeDriver**: Ensure that both Chrome and ChromeDriver are up-to-date. The script uses `webdriver_manager` to automatically manage this, but manual updates may be necessary in some cases.
2. **QR Code Scanning**: If you're prompted to scan the WhatsApp QR code repeatedly, make sure the script is using the correct Chrome profile.
3. **Missing Image Folder**: Ensure the `images` folder is created before running the script.
