# 🔧 Discord Tools Suite

<div align="center">

![Discord](https://img.shields.io/badge/Discord-API%20v10-5865F2?style=for-the-badge&logo=discord&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A comprehensive Discord server management and analysis toolkit**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Warning](#-warning) • [License](#-license)

</div>

---

## 📋 Overview

Discord Tools Suite is a powerful collection of Python scripts designed for advanced Discord server management, analysis, and automation. This toolkit provides administrators with comprehensive control over their Discord servers.

## ✨ Features

### 🔍 Discord Analyzer (`discord_checker.py`)
- **Account Information**: View detailed account stats, email, MFA status, Nitro subscription
- **Server Management**: List all servers with roles and join dates
- **Social Insights**: View friends list with relationship history
- **Security Analysis**: Check active sessions, authorized IPs, and security settings
- **Payment Methods**: View linked payment information
- **Connections**: Display linked social media accounts
- **Report Generation**: Export complete account analysis to file
- **Browser Auto-Login**: Automated browser login using Selenium

### 🔄 Server Cloner (`clone_server.py`)
- **Complete Server Replication**: Clone entire server structure
- **Roles & Permissions**: Copy all roles with exact permissions
- **Channel Hierarchy**: Recreate channels, categories, and permissions
- **Visual Assets**: Clone server icon, banner, and splash images
- **Emoji Migration**: Transfer all custom emojis
- **Settings Preservation**: Maintain verification levels and notification settings

### ⚙️ Server Settings (`settings.py`)
- **Mass Actions**: Bulk ban/kick members with bot support
- **Channel Management**: Create, delete, or spam multiple channels
- **Role Operations**: Mass create or delete roles
- **Visual Customization**: Change server name, icon, banner
- **Cleanup Tools**: Delete all webhooks, emojis, channels, or roles
- **Bot Integration**: Enhanced performance with bot token support
- **Judgament Mode**: Complete server transformation tool

### 🌐 Browser Login (`login.py`)
- **Auto-Detection**: Automatically detects default browser
- **Multi-Browser Support**: Chrome, Firefox, Edge, Brave, Opera
- **Token Injection**: Seamless Discord login via token
- **Cross-Platform**: Works on Windows, Linux, and macOS

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Chrome, Firefox, or Edge browser (for browser login feature)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/sofiaelena777/discord-tools-suite.git
cd discord-tools-suite
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Verify installation**
```bash
python discord_checker.py
```

## 📖 Usage

### Discord Analyzer

```bash
python discord_checker.py
```

**Features available:**
- View guilds, connections, payment methods
- Check Nitro status and friends list
- Analyze active sessions and security
- Generate comprehensive reports
- Access server settings
- Clone servers
- Auto-login to browser

### Server Cloner

```bash
python clone_server.py
```

**Cloning process:**
1. Enter your Discord token
2. Provide source server ID
3. Choose to clone to existing server or create new one
4. Confirm cloning operation
5. Wait for completion

### Server Settings

```bash
python settings.py
```

**Available operations:**
- Mass member management (ban/kick)
- Bulk channel/role creation or deletion
- Server customization (name, icon)
- Webhook and emoji management
- Complete server transformation (Judgament)

### Browser Login

```bash
python login.py
```

**Auto-login features:**
- Automatic browser detection
- Token injection
- Session persistence
- Multi-browser fallback

## 🔑 Getting Your Discord Token

### Desktop/Browser Method

1. Open Discord in your browser or desktop app
2. Press `Ctrl + Shift + I` (Windows/Linux) or `Cmd + Option + I` (Mac)
3. Go to the **Console** tab
4. Paste this code and press Enter:
```javascript
(webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()
```
5. Your token will appear - copy it (don't share it with anyone!)

### Mobile Method

1. Open Discord mobile app
2. Go to Settings → Advanced
3. Enable Developer Mode
4. Use a token grabber script (search for safe methods)

> **⚠️ Security Warning**: Never share your token with anyone! Treat it like a password.

## 🤖 Bot Token Support

For enhanced server management (better member fetching, faster operations):

1. Create a Discord bot at [Discord Developer Portal](https://discord.com/developers/applications)
2. Enable required intents: Server Members, Message Content
3. Copy bot token
4. Enter bot token when prompted in server settings
5. Bot will be auto-injected when needed

## ⚠️ Warning

This tool is intended for **educational purposes** and **legitimate server management** only. 

### Important Notes:

- ⚠️ **Against Discord ToS**: Using self-bots violates Discord's Terms of Service
- 🔒 **Account Risk**: Your account may be banned for using these tools
- 📜 **Legal Responsibility**: Use only on servers you own or have explicit permission to manage
- 🛡️ **Security**: Never share your token or use it on untrusted tools
- ⚖️ **Ethical Use**: Respect Discord's community guidelines and other users

**The author is not responsible for any misuse, damages, or consequences resulting from using this software.**

## 🐛 Troubleshooting

### Common Issues

**"Invalid token"**
- Ensure token is copied correctly
- Check if token has expired
- Verify you're using a user token, not a bot token (for discord_checker.py)

**"Failed to load server"**
- Verify server ID is correct
- Ensure you're a member of the server
- Check if you have required permissions

**"Browser driver error"**
- Install webdriver-manager: `pip install webdriver-manager`
- Ensure browser is installed
- Try a different browser

**"Rate limited"**
- Wait a few minutes before trying again
- Reduce operation speed (increase time_sleep)
- Use bot token for better rate limits

## 🛠️ Technical Details

### Dependencies
- **requests**: HTTP library for Discord API calls
- **selenium**: Browser automation for token injection
- **webdriver-manager**: Automatic webdriver installation

### API Endpoints
- Discord API v10
- RESTful HTTP requests
- Rate limit handling
- Error management

## 📝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2024 sofiaelena777

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👤 Author

**sofiaelena777**

- GitHub: [@sofiaelena777](https://github.com/sofiaelena777)

## 🙏 Acknowledgments

- Discord API documentation
- Python community
- Open source contributors

---

<div align="center">

**⚠️ Use Responsibly | 🔒 Keep Your Token Safe | 📖 Read Discord ToS**

Made with ❤️ by sofiaelena777

</div>
