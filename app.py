import re
import os
import logging
from functools import lru_cache
from flask import Flask, render_template

app = Flask(__name__)

# --- Logging Configuration ---
LOG_LEVEL = os.environ.get('WHATSAPP_LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# --- Configuration ---
# Set these environment variables before running the script,
# otherwise the default values will be used.
# Example (Mac/Linux): export WHATSAPP_CHAT_DIR="My Chat Export"
# Example (Windows CMD): set WHATSAPP_CHAT_DIR="My Chat Export"
# Example (Windows PowerShell): $env:WHATSAPP_CHAT_DIR="My Chat Export"
CHAT_EXPORT_DIR = os.environ.get('WHATSAPP_CHAT_DIR', 'WhatsApp Chat - Tough Mudder')
YOUR_NAME = os.environ.get('WHATSAPP_YOUR_NAME', 'Andrew Allen')
# --- End Configuration ---

CHAT_FILE_PATH = os.path.join("static", CHAT_EXPORT_DIR, "_chat.txt")
MEDIA_FOLDER = os.path.join('static', CHAT_EXPORT_DIR) # Store media in static for serving

# --- Precompiled Regex Patterns ---
# Regex for standard messages: [DD/MM/YYYY, HH:MM:SS] Sender: Message
# Made sender part non-greedy and message part greedy
message_pattern = re.compile(
    r'^\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] (.+?): (.*)$',
    re.DOTALL
)
# Regex for system messages (joining, creating group, etc.)
system_pattern = re.compile(
    r'^\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] (.*)$'
)
# Regex for media attachments - use search to find it anywhere in the message
media_pattern = re.compile(r'<attached: (.+?)>')
# Regex for date separators (assuming they are on their own line like DD/MM/YYYY)
date_separator_pattern = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4})$')
# --- End Precompiled Patterns ---

def parse_chat_file(file_path):
    messages = []
    media_items = []  # Add list to store media items
    current_date = None

    logger.debug(f"Attempting to read chat file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            line_num = 0
            for line in file:
                line_num += 1
                # *** Ensure LRM is removed from the START of the line FIRST ***
                line = line.lstrip('\u200e').strip()
                logger.debug(f"\n--- Processing Line {line_num}: {line[:100]}...")

                if not line: # Skip empty lines
                    logger.debug("Skipping empty line.")
                    continue

                # Check for date separator first
                date_sep_match = date_separator_pattern.match(line)
                if date_sep_match:
                    date_str = date_sep_match.group(1)
                    # Attempt to standardise date format if needed (e.g., YYYY from YY)
                    # For simplicity, we'll just use the matched string for now
                    if date_str != current_date:
                         logger.debug(f"Found Date Separator: {date_str}")
                         messages.append({'type': 'date_separator', 'text': date_str})
                         current_date = date_str # Update current date based on separator
                    continue # Move to next line after handling date separator


                # Check for standard message format
                msg_match = message_pattern.match(line)
                if msg_match:
                    date, time, sender, message_text = msg_match.groups()
                    # Still remove LRM from sender/text just in case, though start-of-line was main issue
                    sender = sender.replace('\u200e', '').strip()
                    message_text = message_text.replace('\u200e', '').strip()

                    logger.debug(
                        f"Matched Standard Message: Date={date}, Time={time}, "
                        f"Sender='{sender}', Text='{message_text[:50]}...'"
                    )

                    if date != current_date:
                         # Check if a date separator was *just* added for this date
                         if not messages or messages[-1].get('text') != date or messages[-1].get('type') != 'date_separator':
                            logger.debug(f"Adding implicit Date Separator: {date}")
                            messages.append({'type': 'date_separator', 'text': date})
                         current_date = date

                    # Check for media within the message text using search
                    media_match = media_pattern.search(message_text)
                    if media_match:
                        filename = media_match.group(1).strip()
                        logger.debug(f"Found Media: '{filename}'")
                        media_rel_path = os.path.join(CHAT_EXPORT_DIR, filename)
                        media_type = 'unknown'
                        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                            media_type = 'image'
                        elif filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                            media_type = 'video'
                        # Remove sticker distinction for gallery, treat as image
                        # elif filename.lower().endswith('.webp'): # Treat webp as stickers/images
                        #     media_type = 'sticker'

                        # Extract caption (text before/after the media tag)
                        # Replacing the found tag, then stripping.
                        caption = message_text.replace(media_match.group(0), '').strip()
                        logger.debug(
                            f"Media Type: {media_type}, Relative Path: {media_rel_path}, Caption: '{caption}'"
                        )

                        messages.append({
                            'type': 'media',
                            'date': date,
                            'time': time,
                            'sender': sender,
                            'media_rel_path': media_rel_path,
                            'media_type': media_type,
                            'caption': caption
                        })
                        # Add to media gallery list if it's an image or video
                        if media_type in ['image', 'video']:
                            media_items.append({
                                'media_rel_path': media_rel_path,
                                'media_type': media_type,
                                'filename': filename  # Keep filename for reference if needed
                            })
                    elif message_text: # Only add if there's actual text content left
                        logger.debug("Added as Text Message.")
                        messages.append({
                            'type': 'text',
                            'date': date,
                            'time': time,
                            'sender': sender,
                            'text': message_text
                        })
                    else:
                         logger.debug("Media matched, but no remaining text, skipping separate text message add.")

                else:
                    # Attempt to match system messages
                    sys_match = system_pattern.match(line)
                    if sys_match:
                        date, time, sys_text = sys_match.groups()
                        sys_text = sys_text.strip()
                        logger.debug(f"Matched System Message: '{sys_text}'")
                        # Optional: Add date separator if date changed
                        if date != current_date:
                            if not messages or messages[-1].get('text') != date or messages[-1].get('type') != 'date_separator':
                                logger.debug(f"Adding implicit Date Separator: {date}")
                                messages.append({'type': 'date_separator', 'text': date})
                            current_date = date

                        messages.append({'type': 'system', 'text': sys_text, 'date': date, 'time': time})
                    # Handle potential multi-line messages (append to previous message if conditions met)
                    elif messages and line and messages[-1]['type'] == 'text':
                        logger.debug(f"Appending to previous message: {line[:50]}...")
                        messages[-1]['text'] += '\n' + line
                    else:
                        logger.debug(f"Line did not match any pattern: {line[:100]}")


    except FileNotFoundError:
        logger.debug(f"Error: Chat file not found at {file_path}")
        return None, None
    except Exception as e:
        logger.debug(f"Error parsing chat file: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for debugging
        return None, None

    logger.debug("\nParsing complete.")
    if not messages:
        logger.debug("Warning: No messages were parsed.")
    else:
        logger.debug(
            f"Successfully parsed {len(messages)} items (messages/separators) and found {len(media_items)} media items."
        )

    return messages, media_items


def _get_file_mtime(path):
    """Return file modification time or None if unavailable."""
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


@lru_cache(maxsize=1)
def _cached_parse(path, mtime):
    """Parse chat file with caching based on modification time."""
    return parse_chat_file(path)


def load_chat():
    """Return cached messages and media items, refreshing if the file changed."""
    mtime = _get_file_mtime(CHAT_FILE_PATH)
    return _cached_parse(CHAT_FILE_PATH, mtime)

# Prime cache at startup
load_chat()


@app.route('/')
def index():
    messages, media_items = load_chat()
    if messages is None:
        return "Error reading or parsing chat file. Check console for details.", 500
    # Use the directory name as the title (can be refined later if needed)
    chat_title = CHAT_EXPORT_DIR
    # Pass media_items to the template
    return render_template('index.html', messages=messages, chat_title=chat_title, your_name=YOUR_NAME, media_items=media_items)

if __name__ == '__main__':
    app.run(debug=True)
