import os
import sys
import time
import platform
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    print("[!] webdriver-manager not installed. Install with: pip install webdriver-manager")

class DiscordBrowserLogin:
    def __init__(self, token):
        self.token = token
        self.driver = None
        self.system = platform.system()

    def get_default_browser(self):
        try:
            if self.system == "Windows":
                import winreg
                try:
                    key = winreg.OpenKey(
                        winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER),
                        r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice"
                    )
                    prog_id, _ = winreg.QueryValueEx(key, "ProgId")

                    browser_map = {
                        'ChromeHTML': 'chrome',
                        'FirefoxURL': 'firefox',
                        'MSEdgeHTM': 'edge',
                        'BraveHTML': 'brave',
                        'OperaStable': 'opera'
                    }

                    for key_name, browser in browser_map.items():
                        if key_name in prog_id:
                            return browser
                except:
                    pass

            elif self.system == "Linux":
                try:
                    result = subprocess.run(
                        ['xdg-settings', 'get', 'default-web-browser'],
                        capture_output=True,
                        text=True
                    )
                    browser_desktop = result.stdout.strip().lower()

                    if 'chrome' in browser_desktop:
                        return 'chrome'
                    elif 'firefox' in browser_desktop:
                        return 'firefox'
                    elif 'edge' in browser_desktop:
                        return 'edge'
                    elif 'brave' in browser_desktop:
                        return 'brave'
                    elif 'opera' in browser_desktop:
                        return 'opera'
                except:
                    pass
        except Exception as e:
            print(f"[!] Error detecting default browser: {e}")

        return 'chrome'

    def detect_browser_path(self, browser_name):
        paths = {
            'chrome': [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium"
            ],
            'firefox': [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                "/usr/bin/firefox",
                "/usr/bin/firefox-esr"
            ],
            'edge': [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                "/usr/bin/microsoft-edge"
            ],
            'brave': [
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                "/usr/bin/brave-browser",
                "/usr/bin/brave"
            ],
            'opera': [
                r"C:\Program Files\Opera\launcher.exe",
                r"C:\Program Files (x86)\Opera\launcher.exe",
                "/usr/bin/opera"
            ]
        }

        for path in paths.get(browser_name, []):
            if os.path.exists(path):
                return path
        return None

    def init_chrome(self):
        options = ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        browser_path = self.detect_browser_path('chrome')
        if browser_path:
            options.binary_location = browser_path

        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = ChromeService(ChromeDriverManager().install())
                return webdriver.Chrome(service=service, options=options)
            else:
                return webdriver.Chrome(options=options)
        except Exception as e:
            print(f"[!] Chrome driver error: {e}")
            return None

    def init_firefox(self):
        options = FirefoxOptions()

        browser_path = self.detect_browser_path('firefox')
        if browser_path:
            options.binary_location = browser_path

        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = FirefoxService(GeckoDriverManager().install())
                return webdriver.Firefox(service=service, options=options)
            else:
                return webdriver.Firefox(options=options)
        except Exception as e:
            print(f"[!] Firefox driver error: {e}")
            return None

    def init_edge(self):
        options = EdgeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")

        browser_path = self.detect_browser_path('edge')
        if browser_path:
            options.binary_location = browser_path

        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = EdgeService(EdgeChromiumDriverManager().install())
                return webdriver.Edge(service=service, options=options)
            else:
                return webdriver.Edge(options=options)
        except Exception as e:
            print(f"[!] Edge driver error: {e}")
            return None

    def init_driver(self, browser=None):
        if browser is None:
            browser = self.get_default_browser()

        print(f"[*] Attempting to launch {browser.upper()}...")

        if browser == 'chrome':
            self.driver = self.init_chrome()
        elif browser == 'firefox':
            self.driver = self.init_firefox()
        elif browser == 'edge':
            self.driver = self.init_edge()
        elif browser in ['brave', 'opera']:
            self.driver = self.init_chrome()

        if self.driver is None:
            print("[!] Default browser failed. Trying fallbacks...")
            for fallback in ['chrome', 'firefox', 'edge']:
                if fallback != browser:
                    print(f"[*] Trying {fallback.upper()}...")
                    if fallback == 'chrome':
                        self.driver = self.init_chrome()
                    elif fallback == 'firefox':
                        self.driver = self.init_firefox()
                    elif fallback == 'edge':
                        self.driver = self.init_edge()

                    if self.driver:
                        break

        return self.driver is not None

    def inject_token(self):
        script = f"""
        const token = "{self.token}";
        setInterval(() => {{
            let iframe = document.createElement('iframe');
            document.body.appendChild(iframe);
            iframe.contentWindow.localStorage.token = `"${{token}}"`;
        }}, 50);
        setTimeout(() => {{
            location.reload();
        }}, 2500);
        """

        try:
            self.driver.execute_script(script)
            return True
        except Exception as e:
            print(f"[!] Error injecting token: {e}")
            return False

    def login(self):
        try:
            print("\n[+] Discord Browser Auto-Login")

            if not self.init_driver():
                print("\n[-] Failed to initialize any browser driver")
                print("[!] Make sure you have Chrome, Firefox, or Edge installed")
                print("[!] Install drivers with: pip install webdriver-manager")
                return False

            print(f"[+] Browser launched successfully")

            print("[*] Navigating to Discord...")
            self.driver.get("https://discord.com/login")

            print("[*] Waiting for page to load...")
            time.sleep(3)

            print("[*] Injecting token and logging in...")
            if self.inject_token():
                print("[+] Token injected successfully")
                print("[*] Reloading page...")

                time.sleep(5)

                print("\n[+] Login successful!")
                print("[*] You should now be logged in to Discord")
                print("[*] Browser will remain open. Close it manually when done.")
                print("\nPress Ctrl+C to close the browser and exit...")

                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n\n[*] Closing browser...")
                    self.driver.quit()
                    print("[+] Done!")

                return True
            else:
                print("[-] Failed to inject token")
                self.driver.quit()
                return False

        except KeyboardInterrupt:
            print("\n\n[*] Login cancelled by user")
            if self.driver:
                self.driver.quit()
            return False
        except Exception as e:
            print(f"\n[-] Error during login: {e}")
            if self.driver:
                self.driver.quit()
            return False

def main(token=None):
    if token is None:
        print("\n[+] Discord Browser Auto-Login")
        token = input("Enter your Discord token: ").strip()

    if not token:
        print("[-] No token provided")
        return

    login_manager = DiscordBrowserLogin(token)
    login_manager.login()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()