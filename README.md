# WhatsApp Chat Visualiser

This tool visualises an exported WhatsApp chat log in a web interface designed to resemble the WhatsApp application.

## Features

-   Displays text messages, system messages (like group creation, adding users), and date separators.
-   Shows sender names and timestamps for each message.
-   Highlights messages sent by a specified user (see Configuration).
-   Displays attached images and videos inline.
-   **Image Lightbox:** Click on any image in the chat to view a larger version in a modal overlay.
-   **Dynamic Title:** The chat name (taken from the export directory name) is displayed as the page title and header.
-   Basic WhatsApp-like styling.

## Configuration

Before running, you need to tell the application where your chat export is and who *you* are in the chat. The **recommended method** is using environment variables.

1.  **Environment Variables (Recommended):**
    *   Set the `WHATSAPP_CHAT_DIR` variable to the exact name of your chat export directory (the one containing `_chat.txt`).
    *   Set the `WHATSAPP_YOUR_NAME` variable to your name *exactly* as it appears in the `_chat.txt` file after the timestamp.

    **Examples:**
    *   **Mac/Linux (Terminal):**
        ```bash
        export WHATSAPP_CHAT_DIR="WhatsApp Chat - My Group"
        export WHATSAPP_YOUR_NAME="Your Name Here"
        python app.py
        ```
        *(Note: `export` sets the variable only for the current terminal session. Add it to your `.bashrc`, `.zshrc`, etc. for persistence.)*
    *   **Windows (Command Prompt):**
        ```cmd
        set WHATSAPP_CHAT_DIR="WhatsApp Chat - My Group"
        set WHATSAPP_YOUR_NAME="Your Name Here"
        python app.py
        ```
    *   **Windows (PowerShell):**
        ```powershell
        $env:WHATSAPP_CHAT_DIR="WhatsApp Chat - My Group"
        $env:WHATSAPP_YOUR_NAME="Your Name Here"
        python app.py
        ```

2.  **Editing `app.py` (Alternative):**
    *   If you don't set the environment variables, the application will use the default values hardcoded near the top of `app.py`.
    *   You can modify these default values directly in the script if you prefer:
        ```python
        # Configuration (Defaults if environment variables are not set)
        CHAT_EXPORT_DIR = os.environ.get('WHATSAPP_CHAT_DIR', 'WhatsApp Chat - Tough Mudder') # <<< DEFAULT VALUE
        YOUR_NAME = os.environ.get('WHATSAPP_YOUR_NAME', 'Andrew Allen') # <<< DEFAULT VALUE
        ```

**Important:** The application still expects your chat export directory to be located *inside* the `static/` folder.

## Setup

1.  **Prerequisites:**
    *   Python 3.x installed.
    *   pip (Python package installer).

2.  **Clone or Download:**
    *   Get the code: `git clone https://github.com/andrewallen/whatsapp-visualiser.git` or download the ZIP.
    *   Navigate into the project directory: `cd whatsapp-visualiser`

3.  **Create `static` Directory:**
    *   If it doesn't exist, create a `static` directory: `mkdir static`

4.  **Place Chat Export:**
    *   **Copy or move** your entire WhatsApp export directory (e.g., `WhatsApp Chat - Tough Mudder`) **inside** the `static` directory.

5.  **Configure Application:**
    *   Set the `WHATSAPP_CHAT_DIR` and `WHATSAPP_YOUR_NAME` environment variables as described in the **Configuration** section above (recommended).
    *   *Alternatively*, edit the default values in `app.py`.

6.  **Install Dependencies:**
    *   Create a virtual environment (recommended):
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows use `venv\Scripts\activate`
        ```
    *   Install required packages:
        ```bash
        pip install -r requirements.txt
        ```

## Running the Application

1.  Ensure your virtual environment is active (if you created one).
2.  **Set environment variables** (if using that method and haven't set them permanently).
3.  Run the Flask development server:
    ```bash
    python app.py
    ```
4.  Open your web browser and navigate to `http://127.0.0.1:5000` (or the address provided in the terminal output).

## How to Use

-   Scroll through the chat messages.
-   Click on any image to open it in a larger view (lightbox). Click the '×' or the dark background to close the lightbox.

## File Structure Overview

```
your-project-directory/
├── .gitignore          # Tells Git which files to ignore
├── app.py              # Main Flask application logic and chat parsing
├── README.md           # This file
├── requirements.txt    # Python package dependencies
├── static/             # Static files (CSS, JS, and your chat export)
│   ├── script.js       # JavaScript for lightbox functionality
│   ├── style.css       # CSS styles for the chat interface
│   └── WhatsApp Chat - Tough Mudder/  # <-- YOUR EXPORT FOLDER GOES HERE
│       ├── _chat.txt
│       └── ... (media files)
├── templates/
│   └── index.html      # HTML template for rendering the chat
└── venv/               # Virtual environment directory (if created)
```

## Limitations & Future Work

-   **Configuration:** Requires editing `app.py` directly or setting environment variables. Could be improved with a config file.
-   **Parsing:** The chat parsing logic relies on specific string formats (`(file attached)`) and regex, which might not work for all WhatsApp export languages or formats.
-   **Media Types:** Currently only displays images and videos directly supported by HTML `<img>` and `<video>` tags. Other attachments (audio, documents) are only indicated by text.
-   **Sender Identification:** Relies on exact name matching, which could be fragile.
-   **Performance:** For extremely large chat files, parsing and rendering might become slow.
-   **Styling:** Basic styling; could be enhanced further.
-   **Responsiveness:** Limited testing on different screen sizes.
