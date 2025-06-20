# 👑 XkingTool 👑

Welcome to **XkingTool**, a powerful and feature-rich suite of tools designed for various automation and utility tasks. This project provides a collection of scripts to help you manage your Discord experience, from profile customization to server administration. 🚀

## 📜 Table of Contents

- [✨ Features](#-features)
- [🚀 Getting Started](#-getting-started)
- [🛠️ Usage](#️-usage)
- [🐍 Programmatic Usage](#-programmatic-usage)
- [🤝 Contributing](#-contributing)
- [⚠️ Disclaimer](#️-disclaimer)
- [📄 License](#-license)

## ✨ Features

This toolkit provides a wide range of functionalities, including:

| Category                  | Script                  | Description                                      | Emoji |
| ------------------------- | ----------------------- | ------------------------------------------------ | :---: |
| **User & Profile**        | `profile_changer.py`    | Change your profile information.                 |  👤   |
|                           | `animated_status.py`    | Set an animated status.                          |  💫   |
| **Token Management**      | `token_checker.py`      | Check the validity of tokens.                    |  ✔️   |
|                           | `token_disabler.py`     | Disable a token.                                 |  🚫   |
|                           | `token_info.py`         | Get detailed information about a token.          |  ℹ️   |
|                           | `token_payments.py`     | Manage token payments.                           |  💳   |
| **Server & Guild Ops**    | `server_archiver.py`    | Archive a server's content.                      |  📦   |
|                           | `server_joiner.py`      | Automatically join a server.                     |  🚪   |
|                           | `server_nuker.py`       | Nuke a server (use with caution!).               |  ☢️   |
|                           | `guild_cloner.py`       | Clone a guild's structure.                       |  👯   |
| **Channel & Group Mgmt**  | `channel_monitoring.py` | Monitor channel activity.                        |  👀   |
|                           | `channel_spammer.py`    | Spam a channel with messages.                    |  💬   |
|                           | `group_clearer.py`      | Clear messages in a group.                       |  🗑️   |
| **Webhook Tools**         | `webhook_deleter.py`    | Delete webhooks.                                 |  ❌   |
|                           | `webhook_info.py`       | Get information about a webhook.                 |  ❓   |
|                           | `webhook_spammer.py`    | Spam a webhook.                                  |  🎣   |
| **Utilities**             | `asset_scraper.py`      | Scrape assets.                                   |  🖼️   |
|                           | `ip_lookup.py`          | Look up IP address information.                  |  🌐   |

## 🚀 Getting Started

To get started with XkingTool, follow these simple steps:

### Prerequisites

Make sure you have Python 3.x installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/XkingTool.git
    cd XkingTool
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 🛠️ Usage

To run any of the tools, simply execute the Python script from your terminal:

```bash
python <tool_name>.py
```

For example, to run the Webhook Spammer:

```bash
python webhook_spammer.py
```

Alternatively, you can use the main GUI application:

```bash
python KingMod.py
```

## 🐍 Programmatic Usage

While the tools are designed with a GUI, you can also use the core logic in your own Python scripts. Here's an example of how you could get information about a webhook programmatically:

```python
import requests

def get_webhook_info(webhook_url):
    """
    Fetches and prints information about a Discord webhook.

    :param webhook_url: The URL of the webhook to inspect.
    """
    try:
        response = requests.get(webhook_url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        data = response.json()
        print("🎉 Webhook Information Retrieved Successfully! 🎉")
        print("="*40)
        print(f"  Name: {data.get('name', 'N/A')}")
        print(f"  Avatar URL: {data.get('avatar', 'N/A')}")
        print(f"  Channel ID: {data.get('channel_id', 'N/A')}")
        print(f"  Guild ID: {data.get('guild_id', 'N/A')}")
        print(f"  Token: {data.get('token', 'N/A')}")
        print("="*40)

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching webhook information: {e}")
    except ValueError:
        print("❌ Error: Invalid JSON response from the server.")

if __name__ == "__main__":
    # Replace with your webhook URL
    example_webhook_url = "https://discord.com/api/webhooks/your/webhook/url"
    get_webhook_info(example_webhook_url)

```

This example uses the `requests` library to send a GET request to the webhook URL and prints the information, similar to how the `webhook_info.py` tool works.

## 🤝 Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or create a pull request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## ⚠️ Disclaimer

This tool is for educational purposes only. The misuse of this software is not the responsibility of the author. Be responsible and use it at your own risk.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
