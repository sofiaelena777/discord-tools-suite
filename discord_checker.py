import requests
import json
from datetime import datetime
import os
from settings import ServerSettings
from login import DiscordBrowserLogin

class DiscordAnalyzer:
    def __init__(self):
        self.token = None
        self.user_data = None
        self.base_url = "https://discord.com/api/v10"
        self.headers = {}

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def banner(self):
        print(r"""
·▄▄▄▄  ▪  .▄▄ ·  ▄▄·       ▄▄▄  ·▄▄▄▄      ▄▄▄▄▄            ▄▄▌  .▄▄ ·
██▪ ██ ██ ▐█ ▀. ▐█ ▌▪▪     ▀▄ █·██▪ ██     •██  ▪     ▪     ██•  ▐█ ▀.
▐█· ▐█▌▐█·▄▀▀▀█▄██ ▄▄ ▄█▀▄ ▐▀▀▄ ▐█· ▐█▌     ▐█.▪ ▄█▀▄  ▄█▀▄ ██▪  ▄▀▀▀█▄
██. ██ ▐█▌▐█▄▪▐█▐███▌▐█▌.▐▌▐█•█▌██. ██      ▐█▌·▐█▌.▐▌▐█▌.▐▌▐█▌▐▌▐█▄▪▐█
▀▀▀▀▀• ▀▀▀ ▀▀▀▀ ·▀▀▀  ▀█▄▀▪.▀  ▀▀▀▀▀▀•      ▀▀▀  ▀█▄▀▪ ▀█▄▀▪.▀▀▀  ▀▀▀▀
""")

    def validate(self, token):
        self.headers = {"Authorization": token}
        try:
            response = requests.get(f"{self.base_url}/users/@me", headers=self.headers)
            if response.status_code == 200:
                self.user_data = response.json()
                self.token = token
                return True
            return False
        except:
            return False

    def show_account(self):
        if not self.user_data:
            return
        d = self.user_data
        avatar_id = d.get('avatar')
        user_id = d.get('id')
        avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_id}.png" if avatar_id else "No avatar"

        print("\n[+] Account Information")
        print(f"    ID: {d.get('id')}")
        print(f"    Username: {d.get('username')}")
        print(f"    Global Name: {d.get('global_name', 'N/A')}")
        print(f"    Email: {d.get('email', 'N/A')}")
        print(f"    Verified: {d.get('verified')}")
        print(f"    MFA: {d.get('mfa_enabled')}")
        print(f"    Avatar: {avatar_url}")

    def show_guilds(self):
        try:
            response = requests.get(f"{self.base_url}/users/@me/guilds", headers=self.headers)
            if response.status_code != 200:
                print("\n[-] Failed to retrieve guilds")
                return

            guilds = response.json()
            print(f"\n[+] Guilds ({len(guilds)})")
            print("    Fetching details...\n")

            for guild in guilds:
                gid = guild.get('id')
                name = guild.get('name')
                perms = guild.get('permissions', 0)
                is_admin = bool(int(perms) & 0x8) if perms else False
                is_owner = guild.get('owner', False)

                role = "OWNER" if is_owner else ("ADMIN" if is_admin else "MEMBER")
                joined = "N/A"

                try:
                    mr = requests.get(f"{self.base_url}/users/@me/guilds/{gid}/member", headers=self.headers)
                    if mr.status_code == 200:
                        jt = mr.json().get('joined_at')
                        if jt:
                            dt = datetime.fromisoformat(jt.replace('Z', '+00:00'))
                            joined = dt.strftime('%d/%m/%Y %H:%M:%S UTC')
                    else:
                        mr = requests.get(f"{self.base_url}/guilds/{gid}/members/@me", headers=self.headers)
                        if mr.status_code == 200:
                            jt = mr.json().get('joined_at')
                            if jt:
                                dt = datetime.fromisoformat(jt.replace('Z', '+00:00'))
                                joined = dt.strftime('%d/%m/%Y %H:%M:%S UTC')
                except:
                    pass

                print(f"    {name}")
                print(f"    ID: {gid} | Role: {role} | Joined: {joined}\n")
        except Exception as e:
            print(f"\n[-] Error: {e}")

    def show_connections(self):
        try:
            response = requests.get(f"{self.base_url}/users/@me/connections", headers=self.headers)
            if response.status_code != 200:
                print("\n[-] Failed to retrieve connections")
                return

            conns = response.json()
            print(f"\n[+] Connections ({len(conns)})")
            if conns:
                for c in conns:
                    print(f"    {c.get('type').upper()}: {c.get('name')}")
            else:
                print("    None")
        except Exception as e:
            print(f"\n[-] Error: {e}")

    def show_billing(self):
        try:
            response = requests.get(f"{self.base_url}/users/@me/billing/payment-sources", headers=self.headers)
            if response.status_code != 200:
                print("\n[-] Failed to retrieve payment methods")
                return

            payments = response.json()
            print("\n[+] Payment Methods")
            if payments:
                for p in payments:
                    brand = p.get('brand', 'N/A')
                    last4 = p.get('last_4', 'N/A')
                    print(f"    {brand} **** **** **** {last4}")
            else:
                print("    None")
        except Exception as e:
            print(f"\n[-] Error: {e}")

    def show_nitro(self):
        if not self.user_data:
            return
        types = {0: "None", 1: "Nitro Classic", 2: "Nitro", 3: "Nitro Basic"}
        pt = self.user_data.get('premium_type', 0)
        print(f"\n[+] Nitro Status: {types.get(pt, 'Unknown')}")

    def show_friends(self):
        try:
            response = requests.get(f"{self.base_url}/users/@me/relationships", headers=self.headers)
            if response.status_code != 200:
                print(f"\n[-] Failed to retrieve friends (Status: {response.status_code})")
                return

            rels = response.json()
            friends = [r for r in rels if r.get('type') == 1]
            print(f"\n[+] Friends ({len(friends)})")

            if friends:
                for f in friends:
                    user = f.get('user', {})
                    uid = user.get('id')
                    username = user.get('username')
                    gname = user.get('global_name', 'N/A')
                    disc = user.get('discriminator', '0')

                    since = f.get('since')
                    fdate = "N/A"
                    if since:
                        try:
                            dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
                            fdate = dt.strftime('%d/%m/%Y %H:%M:%S UTC')
                        except:
                            fdate = since

                    utype = "BOT" if user.get('bot') else "USER"
                    tag = f"{username}#{disc}" if disc != '0' else username

                    print(f"\n    Name: {gname} (@{tag})")
                    print(f"    ID: {uid}")
                    print(f"    Type: {utype}")
                    print(f"    Friends since: {fdate}")
            else:
                print("    None")
        except Exception as e:
            print(f"\n[-] Error: {e}")

    def show_sessions(self):
        try:
            response = requests.get(f"{self.base_url}/auth/sessions", headers=self.headers)
            if response.status_code != 200:
                print(f"\n[-] Failed to retrieve sessions (Status: {response.status_code})")
                return

            data = response.json()
            sessions = data.get('user_sessions', []) if isinstance(data, dict) else data

            print(f"\n[+] Active Sessions ({len(sessions)})")
            if sessions:
                for s in sessions:
                    if not isinstance(s, dict):
                        continue

                    ci = s.get('client_info', {})
                    print(f"\n    Device: {ci.get('os', 'N/A')} - {ci.get('platform', 'N/A')}")
                    print(f"    Client: {ci.get('client', 'N/A')}")
                    print(f"    Location: {ci.get('location', 'N/A')}")
                    print(f"    Session ID: {s.get('id_hash', 'N/A')}")

                    last = s.get('approx_last_used_time') or s.get('last_used_time') or s.get('created_at')
                    if last:
                        print(f"    Last used: {last}")
            else:
                print("    None")
        except Exception as e:
            print(f"\n[-] Error: {e}")

    def show_security(self):
        try:
            print("\n[+] Security & Location Information")

            response = requests.get(f"{self.base_url}/users/@me/authorized-ip-addresses", headers=self.headers)
            if response.status_code == 200:
                ips = response.json()
                if ips and len(ips) > 0:
                    print("\n    Authorized IPs:")
                    for ip in ips:
                        print(f"    IP: {ip.get('ip', 'N/A')}")
                        if ip.get('last_used'):
                            print(f"    Last used: {ip.get('last_used')}")
                        if ip.get('location'):
                            print(f"    Location: {ip.get('location')}")
            else:
                print("\n    IP endpoint unavailable")

            try:
                cr = requests.get(f"{self.base_url}/users/@me/consent", headers=self.headers)
                if cr.status_code == 200:
                    cd = cr.json()
                    print("\n    Consent:")
                    print(f"    Personalization: {cd.get('personalization', {}).get('consented', 'N/A')}")
                    print(f"    Usage statistics: {cd.get('usage_statistics', {}).get('consented', 'N/A')}")
            except:
                pass

            if self.user_data:
                print("\n    Account Security:")
                print(f"    Email verified: {self.user_data.get('verified')}")
                print(f"    MFA enabled: {self.user_data.get('mfa_enabled')}")
                print(f"    Phone linked: {bool(self.user_data.get('phone'))}")
                print(f"    Account flags: {self.user_data.get('flags', 0)}")
                print(f"    Public flags: {self.user_data.get('public_flags', 0)}")
        except Exception as e:
            print(f"\n[-] Error: {e}")

    def clone_server(self):
        try:
            import clone_server
            clone_server.main(self.token)
        except ImportError:
            print("\n[-] Error: clone_server.py not found")
        except Exception as e:
            print(f"\n[-] Error running clone server: {e}")

    def browser_login(self):
        try:
            if not self.token:
                print("\n[-] No token available")
                return
            
            print("\n[+] Starting browser auto-login...")
            login_manager = DiscordBrowserLogin(self.token)
            login_manager.login()
        except Exception as e:
            print(f"\n[-] Error during browser login: {e}")

    def save_report(self):
        if not self.user_data:
            print("\n[-] No data to save")
            return

        gname = self.user_data.get('global_name') or self.user_data.get('username') or 'report'
        filename = f"{gname.replace(' ', '_')}.txt"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("DISCORD ACCOUNT REPORT\n")
                f.write("=" * 70 + "\n\n")

                f.write(f"TOKEN: {self.token}\n\n")

                d = self.user_data
                avatar_id = d.get('avatar')
                user_id = d.get('id')
                avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_id}.png" if avatar_id else "No avatar"

                f.write("ACCOUNT INFORMATION\n")
                f.write(f"ID: {d.get('id')}\n")
                f.write(f"Username: {d.get('username')}\n")
                f.write(f"Global Name: {d.get('global_name', 'N/A')}\n")
                f.write(f"Email: {d.get('email', 'N/A')}\n")
                f.write(f"Verified: {d.get('verified')}\n")
                f.write(f"MFA: {d.get('mfa_enabled')}\n")
                f.write(f"Avatar: {avatar_url}\n\n")

                types = {0: "None", 1: "Nitro Classic", 2: "Nitro", 3: "Nitro Basic"}
                pt = d.get('premium_type', 0)
                f.write(f"Nitro Status: {types.get(pt, 'Unknown')}\n\n")

                try:
                    response = requests.get(f"{self.base_url}/users/@me/guilds", headers=self.headers)
                    if response.status_code == 200:
                        guilds = response.json()
                        f.write(f"GUILDS ({len(guilds)})\n")
                        f.write("-" * 70 + "\n")

                        for guild in guilds:
                            gid = guild.get('id')
                            name = guild.get('name')
                            perms = guild.get('permissions', 0)
                            is_admin = bool(int(perms) & 0x8) if perms else False
                            is_owner = guild.get('owner', False)
                            role = "OWNER" if is_owner else ("ADMIN" if is_admin else "MEMBER")
                            joined = "N/A"

                            try:
                                mr = requests.get(f"{self.base_url}/users/@me/guilds/{gid}/member", headers=self.headers)
                                if mr.status_code == 200:
                                    jt = mr.json().get('joined_at')
                                    if jt:
                                        dt = datetime.fromisoformat(jt.replace('Z', '+00:00'))
                                        joined = dt.strftime('%d/%m/%Y %H:%M:%S UTC')
                            except:
                                pass

                            f.write(f"\nName: {name}\n")
                            f.write(f"ID: {gid}\n")
                            f.write(f"Role: {role}\n")
                            f.write(f"Joined: {joined}\n")
                except:
                    f.write("\nGUILDS: Error retrieving data\n")

                f.write("\n")

                try:
                    response = requests.get(f"{self.base_url}/users/@me/relationships", headers=self.headers)
                    if response.status_code == 200:
                        rels = response.json()
                        friends = [r for r in rels if r.get('type') == 1]
                        f.write(f"FRIENDS ({len(friends)})\n")
                        f.write("-" * 70 + "\n")

                        for fr in friends:
                            user = fr.get('user', {})
                            uid = user.get('id')
                            username = user.get('username')
                            gname_fr = user.get('global_name', 'N/A')
                            disc = user.get('discriminator', '0')
                            tag = f"{username}#{disc}" if disc != '0' else username
                            utype = "BOT" if user.get('bot') else "USER"

                            since = fr.get('since')
                            fdate = "N/A"
                            if since:
                                try:
                                    dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
                                    fdate = dt.strftime('%d/%m/%Y %H:%M:%S UTC')
                                except:
                                    fdate = since

                            f.write(f"\nName: {gname_fr} (@{tag})\n")
                            f.write(f"ID: {uid}\n")
                            f.write(f"Type: {utype}\n")
                            f.write(f"Friends since: {fdate}\n")
                except:
                    f.write("\nFRIENDS: Error retrieving data\n")

                f.write("\n")

                try:
                    response = requests.get(f"{self.base_url}/users/@me/connections", headers=self.headers)
                    if response.status_code == 200:
                        conns = response.json()
                        f.write(f"CONNECTIONS ({len(conns)})\n")
                        f.write("-" * 70 + "\n")
                        if conns:
                            for c in conns:
                                f.write(f"{c.get('type').upper()}: {c.get('name')}\n")
                        else:
                            f.write("None\n")
                except:
                    f.write("CONNECTIONS: Error retrieving data\n")

                f.write("\n")

                try:
                    response = requests.get(f"{self.base_url}/auth/sessions", headers=self.headers)
                    if response.status_code == 200:
                        data = response.json()
                        sessions = data.get('user_sessions', []) if isinstance(data, dict) else data
                        f.write(f"ACTIVE SESSIONS ({len(sessions)})\n")
                        f.write("-" * 70 + "\n")

                        for s in sessions:
                            if not isinstance(s, dict):
                                continue
                            ci = s.get('client_info', {})
                            f.write(f"\nDevice: {ci.get('os', 'N/A')} - {ci.get('platform', 'N/A')}\n")
                            f.write(f"Client: {ci.get('client', 'N/A')}\n")
                            f.write(f"Location: {ci.get('location', 'N/A')}\n")
                            f.write(f"Session ID: {s.get('id_hash', 'N/A')}\n")
                            last = s.get('approx_last_used_time') or s.get('last_used_time') or s.get('created_at')
                            if last:
                                f.write(f"Last used: {last}\n")
                except:
                    f.write("ACTIVE SESSIONS: Error retrieving data\n")

                f.write("\n")

                try:
                    response = requests.get(f"{self.base_url}/users/@me/billing/payment-sources", headers=self.headers)
                    if response.status_code == 200:
                        payments = response.json()
                        f.write("PAYMENT METHODS\n")
                        f.write("-" * 70 + "\n")
                        if payments:
                            for p in payments:
                                brand = p.get('brand', 'N/A')
                                last4 = p.get('last_4', 'N/A')
                                f.write(f"{brand} **** **** **** {last4}\n")
                        else:
                            f.write("None\n")
                except:
                    f.write("PAYMENT METHODS: Error retrieving data\n")

                f.write("\n")
                f.write("SECURITY INFORMATION\n")
                f.write("-" * 70 + "\n")
                f.write(f"Email verified: {d.get('verified')}\n")
                f.write(f"MFA enabled: {d.get('mfa_enabled')}\n")
                f.write(f"Phone linked: {bool(d.get('phone'))}\n")
                f.write(f"Account flags: {d.get('flags', 0)}\n")
                f.write(f"Public flags: {d.get('public_flags', 0)}\n")

                f.write("\n" + "=" * 70 + "\n")
                f.write("END OF REPORT\n")
                f.write("=" * 70 + "\n")

            print(f"\n[+] Report saved to: {filename}")
        except Exception as e:
            print(f"\n[-] Error saving report: {e}")

    def menu(self):
        print("""
[1] Guilds              [2] Connections
[3] Payment Methods     [4] Nitro Status
[5] Friends             [6] Active Sessions
[7] Security Info       [8] Full Report
[9] Save to File        [10] Server Settings
[11] Clone Server       [12] Browser Login
[13] Change Token       [0] Exit
""")

    def run(self):
        self.clear()
        self.banner()

        token = input("Token: ").strip()

        if not self.validate(token):
            print("\n[-] Invalid token")
            return

        self.clear()
        self.banner()
        self.show_account()

        while True:
            self.menu()
            choice = input("\nSelect: ").strip()

            if choice == "1":
                self.show_guilds()
            elif choice == "2":
                self.show_connections()
            elif choice == "3":
                self.show_billing()
            elif choice == "4":
                self.show_nitro()
            elif choice == "5":
                self.show_friends()
            elif choice == "6":
                self.show_sessions()
            elif choice == "7":
                self.show_security()
            elif choice == "8":
                self.show_account()
                self.show_nitro()
                self.show_guilds()
                self.show_friends()
                self.show_connections()
                self.show_sessions()
                self.show_security()
                self.show_billing()
            elif choice == "9":
                self.save_report()
            elif choice == "10":
                settings = ServerSettings(self.token, self.base_url)
                settings.run()
            elif choice == "11":
                self.clone_server()
            elif choice == "12":
                self.browser_login()
            elif choice == "13":
                self.clear()
                self.banner()
                token = input("Token: ").strip()
                if self.validate(token):
                    self.clear()
                    self.banner()
                    self.show_account()
                else:
                    print("\n[-] Invalid token")
                    break
            elif choice == "0":
                print("\nExiting...")
                break
            else:
                print("[-] Invalid option")

            input("\nPress ENTER to continue...")
            self.clear()
            self.banner()
            self.show_account()

if __name__ == "__main__":
    analyzer = DiscordAnalyzer()
    analyzer.run()