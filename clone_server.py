import requests
import os
import time
import base64
from datetime import datetime

class ServerCloner:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://discord.com/api/v10"
        self.headers = {"Authorization": token}
        self.source_id = None
        self.target_id = None
        self.source_data = None
        self.target_data = None
        self.time_sleep = 0.3

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def banner(self):
        print(r"""
·▄▄▄▄  ▪  .▄▄ ·  ▄▄·       ▄▄▄  ·▄▄▄▄       ▄▄· ▄▄▌         ▐ ▄ ▄▄▄ .
██▪ ██ ██ ▐█ ▀. ▐█ ▌▪▪     ▀▄ █·██▪ ██     ▐█ ▌▪██•  ▪     •█▌▐█▀▄.▀·
▐█· ▐█▌▐█·▄▀▀▀█▄██ ▄▄ ▄█▀▄ ▐▀▀▄ ▐█· ▐█▌    ██ ▄▄██▪   ▄█▀▄ ▐█▐▐▌▐▀▀▪▄
██. ██ ▐█▌▐█▄▪▐█▐███▌▐█▌.▐▌▐█•█▌██. ██     ▐███▌▐█▌▐▌▐█▌.▐▌██▐█▌▐█▄▄▌
▀▀▀▀▀• ▀▀▀ ▀▀▀▀ ·▀▀▀  ▀█▄▀▪.▀  ▀▀▀▀▀▀•     ·▀▀▀ .▀▀▀  ▀█▄▀▪▀▀ █▪ ▀▀▀
""")

    def load_source_server(self, server_id):
        try:
            response = requests.get(
                f"{self.base_url}/guilds/{server_id}?with_counts=true",
                headers=self.headers
            )

            if response.status_code != 200:
                print(f"[-] Failed to load source server (Status: {response.status_code})")
                return False

            self.source_data = response.json()
            self.source_id = server_id
            return True

        except Exception as e:
            print(f"[-] Error loading source server: {e}")
            return False

    def create_new_server(self):
        try:
            server_data = {
                "name": "My Server",
                "icon": None,
                "channels": [],
                "system_channel_id": None,
                "afk_channel_id": None
            }

            response = requests.post(
                f"{self.base_url}/guilds",
                headers=self.headers,
                json=server_data
            )

            if response.status_code in [200, 201]:
                self.target_data = response.json()
                self.target_id = self.target_data.get('id')
                print(f"[+] New server created: My Server")
                print(f"[+] Server ID: {self.target_id}")
                return True
            else:
                error_data = response.json() if response.text else {}
                print(f"[-] Failed to create server (Status: {response.status_code})")
                if error_data.get('message'):
                    print(f"    Error: {error_data['message']}")
                if error_data.get('code'):
                    print(f"    Code: {error_data['code']}")
                return False

        except Exception as e:
            print(f"[-] Error creating server: {e}")
            return False

    def load_target_server(self, server_id):
        try:
            response = requests.get(
                f"{self.base_url}/guilds/{server_id}?with_counts=true",
                headers=self.headers
            )

            if response.status_code != 200:
                print(f"[-] Failed to load target server (Status: {response.status_code})")
                return False

            self.target_data = response.json()
            self.target_id = server_id

            user_response = requests.get(f"{self.base_url}/users/@me", headers=self.headers)
            if user_response.status_code != 200:
                print("[-] Failed to get user info")
                return False

            user_data = user_response.json()
            user_id = user_data.get('id')

            if self.target_data.get('owner_id') == user_id:
                return True

            guilds_response = requests.get(f"{self.base_url}/users/@me/guilds", headers=self.headers)
            if guilds_response.status_code == 200:
                guilds = guilds_response.json()
                guild_info = next((g for g in guilds if g.get('id') == server_id), None)

                if guild_info:
                    perms = guild_info.get('permissions', 0)
                    is_admin = bool(int(perms) & 0x8) if perms else False

                    if is_admin:
                        return True
                    else:
                        print("[-] Insufficient permissions on target server (Admin required)")
                        return False

            print("[-] Failed to verify permissions")
            return False

        except Exception as e:
            print(f"[-] Error loading target server: {e}")
            return False

    def clean_target_server(self):
        print("\n[+] Cleaning target server...")

        try:
            response = requests.get(
                f"{self.base_url}/guilds/{self.target_id}/channels",
                headers=self.headers
            )

            if response.status_code == 200:
                channels = response.json()
                print(f"    Deleting {len(channels)} channels...")

                for channel in channels:
                    try:
                        requests.delete(
                            f"{self.base_url}/channels/{channel['id']}",
                            headers=self.headers
                        )
                        time.sleep(self.time_sleep)
                    except:
                        pass

        except Exception as e:
            print(f"    [-] Error deleting channels: {e}")

        try:
            response = requests.get(
                f"{self.base_url}/guilds/{self.target_id}/roles",
                headers=self.headers
            )

            if response.status_code == 200:
                roles = [r for r in response.json() if r['name'] != '@everyone']
                print(f"    Deleting {len(roles)} roles...")

                for role in roles:
                    try:
                        requests.delete(
                            f"{self.base_url}/guilds/{self.target_id}/roles/{role['id']}",
                            headers=self.headers
                        )
                        time.sleep(self.time_sleep)
                    except:
                        pass

        except Exception as e:
            print(f"    [-] Error deleting roles: {e}")

        try:
            response = requests.get(
                f"{self.base_url}/guilds/{self.target_id}/emojis",
                headers=self.headers
            )

            if response.status_code == 200:
                emojis = response.json()
                if emojis:
                    print(f"    Deleting {len(emojis)} emojis...")

                    for emoji in emojis:
                        try:
                            requests.delete(
                                f"{self.base_url}/guilds/{self.target_id}/emojis/{emoji['id']}",
                                headers=self.headers
                            )
                            time.sleep(self.time_sleep)
                        except:
                            pass

        except Exception as e:
            print(f"    [-] Error deleting emojis: {e}")

        print("    [+] Target server cleaned")

    def clone_server_info(self):
        print("\n[+] Cloning server information...")

        try:
            update_data = {}

            if self.source_data.get('name'):
                update_data['name'] = self.source_data['name']

            if self.source_data.get('icon'):
                icon_url = f"https://cdn.discordapp.com/icons/{self.source_id}/{self.source_data['icon']}.png"
                try:
                    img_response = requests.get(icon_url)
                    if img_response.status_code == 200:
                        img_data = base64.b64encode(img_response.content).decode('utf-8')
                        update_data['icon'] = f"data:image/png;base64,{img_data}"
                        print("    [+] Server icon cloned")
                except:
                    print("    [-] Failed to clone icon")

            if self.source_data.get('banner'):
                banner_url = f"https://cdn.discordapp.com/banners/{self.source_id}/{self.source_data['banner']}.png"
                try:
                    img_response = requests.get(banner_url)
                    if img_response.status_code == 200:
                        img_data = base64.b64encode(img_response.content).decode('utf-8')
                        update_data['banner'] = f"data:image/png;base64,{img_data}"
                        print("    [+] Server banner cloned")
                except:
                    pass

            if self.source_data.get('splash'):
                splash_url = f"https://cdn.discordapp.com/splashes/{self.source_id}/{self.source_data['splash']}.png"
                try:
                    img_response = requests.get(splash_url)
                    if img_response.status_code == 200:
                        img_data = base64.b64encode(img_response.content).decode('utf-8')
                        update_data['splash'] = f"data:image/png;base64,{img_data}"
                        print("    [+] Server splash cloned")
                except:
                    pass

            if self.source_data.get('verification_level') is not None:
                update_data['verification_level'] = self.source_data['verification_level']

            if self.source_data.get('default_message_notifications') is not None:
                update_data['default_message_notifications'] = self.source_data['default_message_notifications']

            if self.source_data.get('explicit_content_filter') is not None:
                update_data['explicit_content_filter'] = self.source_data['explicit_content_filter']

            if update_data:
                response = requests.patch(
                    f"{self.base_url}/guilds/{self.target_id}",
                    headers=self.headers,
                    json=update_data
                )

                if response.status_code == 200:
                    print(f"    [+] Server name cloned: {update_data.get('name', 'N/A')}")
                    if 'verification_level' in update_data:
                        print(f"    [+] Verification level cloned")
                    if 'default_message_notifications' in update_data:
                        print(f"    [+] Notification settings cloned")
                else:
                    print("    [-] Failed to update server info")

        except Exception as e:
            print(f"    [-] Error cloning server info: {e}")

    def clone_roles(self):
        print("\n[+] Cloning roles...")

        try:
            response = requests.get(
                f"{self.base_url}/guilds/{self.source_id}/roles",
                headers=self.headers
            )

            if response.status_code != 200:
                print("    [-] Failed to get source roles")
                return {}

            source_roles = response.json()
            everyone_role = next((r for r in source_roles if r['name'] == '@everyone'), None)
            source_roles = sorted([r for r in source_roles if r['name'] != '@everyone'],
                                key=lambda x: x.get('position', 0))

            role_mapping = {}
            created = 0

            target_roles_response = requests.get(
                f"{self.base_url}/guilds/{self.target_id}/roles",
                headers=self.headers
            )
            
            if target_roles_response.status_code == 200:
                target_everyone = next((r for r in target_roles_response.json() if r['name'] == '@everyone'), None)
                if target_everyone and everyone_role:
                    role_mapping[everyone_role['id']] = target_everyone['id']

            for role in source_roles:
                try:
                    role_data = {
                        "name": role.get('name', 'new-role'),
                        "permissions": str(role.get('permissions', '0')),
                        "color": role.get('color', 0),
                        "hoist": role.get('hoist', False),
                        "mentionable": role.get('mentionable', False)
                    }

                    if role.get('unicode_emoji'):
                        role_data['unicode_emoji'] = role['unicode_emoji']
                    elif role.get('icon'):
                        role_data['icon'] = role['icon']

                    create_response = requests.post(
                        f"{self.base_url}/guilds/{self.target_id}/roles",
                        headers=self.headers,
                        json=role_data
                    )

                    if create_response.status_code in [200, 201]:
                        new_role = create_response.json()
                        role_mapping[role['id']] = new_role['id']
                        created += 1
                        print(f"    [+] Created role: {role.get('name', 'Unknown')}")

                    time.sleep(self.time_sleep)

                except Exception as e:
                    print(f"    [-] Error creating role: {e}")

            print(f"    [+] Cloned {created}/{len(source_roles)} roles")
            return role_mapping

        except Exception as e:
            print(f"    [-] Error cloning roles: {e}")
            return {}

    def clone_channels(self, role_mapping):
        print("\n[+] Cloning channels...")

        try:
            response = requests.get(
                f"{self.base_url}/guilds/{self.source_id}/channels",
                headers=self.headers
            )

            if response.status_code != 200:
                print("    [-] Failed to get source channels")
                return

            source_channels = response.json()
            categories = sorted([c for c in source_channels if c.get('type') == 4],
                              key=lambda x: x.get('position', 0))
            other_channels = sorted([c for c in source_channels if c.get('type') != 4],
                                  key=lambda x: x.get('position', 0))

            category_mapping = {}
            created = 0

            for category in categories:
                try:
                    channel_data = {
                        "name": category.get('name', 'new-category'),
                        "type": 4,
                        "position": category.get('position', 0)
                    }

                    if category.get('permission_overwrites'):
                        overwrites = []
                        for overwrite in category['permission_overwrites']:
                            new_overwrite = {
                                'type': overwrite.get('type', 0),
                                'allow': str(overwrite.get('allow', '0')),
                                'deny': str(overwrite.get('deny', '0'))
                            }
                            
                            if overwrite.get('type') == 0:
                                if overwrite['id'] in role_mapping:
                                    new_overwrite['id'] = role_mapping[overwrite['id']]
                                    overwrites.append(new_overwrite)
                            elif overwrite.get('type') == 1:
                                new_overwrite['id'] = overwrite['id']
                                overwrites.append(new_overwrite)

                        if overwrites:
                            channel_data['permission_overwrites'] = overwrites

                    create_response = requests.post(
                        f"{self.base_url}/guilds/{self.target_id}/channels",
                        headers=self.headers,
                        json=channel_data
                    )

                    if create_response.status_code in [200, 201]:
                        new_channel = create_response.json()
                        category_mapping[category['id']] = new_channel['id']
                        created += 1
                        perms_count = len(category.get('permission_overwrites', []))
                        perms_text = f" ({perms_count} permissions)" if perms_count > 0 else ""
                        print(f"    [+] Created category: {category.get('name', 'Unknown')}{perms_text}")

                    time.sleep(self.time_sleep)

                except Exception as e:
                    print(f"    [-] Error creating category: {e}")

            for channel in other_channels:
                try:
                    channel_data = {
                        "name": channel.get('name', 'new-channel'),
                        "type": channel.get('type', 0),
                        "position": channel.get('position', 0)
                    }

                    if channel.get('topic'):
                        channel_data['topic'] = channel['topic']

                    if channel.get('nsfw') is not None:
                        channel_data['nsfw'] = channel['nsfw']

                    if channel.get('rate_limit_per_user'):
                        channel_data['rate_limit_per_user'] = channel['rate_limit_per_user']

                    if channel.get('bitrate'):
                        channel_data['bitrate'] = channel['bitrate']

                    if channel.get('user_limit'):
                        channel_data['user_limit'] = channel['user_limit']

                    if channel.get('parent_id') and channel['parent_id'] in category_mapping:
                        channel_data['parent_id'] = category_mapping[channel['parent_id']]

                    if channel.get('permission_overwrites'):
                        overwrites = []
                        for overwrite in channel['permission_overwrites']:
                            new_overwrite = {
                                'type': overwrite.get('type', 0),
                                'allow': str(overwrite.get('allow', '0')),
                                'deny': str(overwrite.get('deny', '0'))
                            }
                            
                            if overwrite.get('type') == 0:
                                if overwrite['id'] in role_mapping:
                                    new_overwrite['id'] = role_mapping[overwrite['id']]
                                    overwrites.append(new_overwrite)
                            elif overwrite.get('type') == 1:
                                new_overwrite['id'] = overwrite['id']
                                overwrites.append(new_overwrite)

                        if overwrites:
                            channel_data['permission_overwrites'] = overwrites

                    create_response = requests.post(
                        f"{self.base_url}/guilds/{self.target_id}/channels",
                        headers=self.headers,
                        json=channel_data
                    )

                    if create_response.status_code in [200, 201]:
                        created += 1
                        channel_type = {0: "text", 2: "voice", 5: "announcement", 13: "stage", 15: "forum"}.get(channel.get('type'), "channel")
                        perms_count = len(channel.get('permission_overwrites', []))
                        perms_text = f" ({perms_count} permissions)" if perms_count > 0 else ""
                        print(f"    [+] Created {channel_type}: {channel.get('name', 'Unknown')}{perms_text}")

                    time.sleep(self.time_sleep)

                except Exception as e:
                    print(f"    [-] Error creating channel: {e}")

            total = len(categories) + len(other_channels)
            print(f"    [+] Cloned {created}/{total} channels")

        except Exception as e:
            print(f"    [-] Error cloning channels: {e}")

    def clone_emojis(self):
        print("\n[+] Cloning emojis...")

        try:
            response = requests.get(
                f"{self.base_url}/guilds/{self.source_id}/emojis",
                headers=self.headers
            )

            if response.status_code != 200:
                print("    [-] Failed to get source emojis")
                return

            source_emojis = response.json()

            if not source_emojis:
                print("    [+] No emojis to clone")
                return

            created = 0
            failed = 0

            for emoji in source_emojis:
                try:
                    emoji_url = f"https://cdn.discordapp.com/emojis/{emoji['id']}.{'gif' if emoji.get('animated') else 'png'}"

                    img_response = requests.get(emoji_url)
                    if img_response.status_code == 200:
                        img_data = base64.b64encode(img_response.content).decode('utf-8')
                        img_format = 'gif' if emoji.get('animated') else 'png'
                        image_data = f"data:image/{img_format};base64,{img_data}"

                        emoji_data = {
                            "name": emoji.get('name', 'emoji'),
                            "image": image_data
                        }

                        if emoji.get('roles'):
                            emoji_data['roles'] = emoji['roles']

                        create_response = requests.post(
                            f"{self.base_url}/guilds/{self.target_id}/emojis",
                            headers=self.headers,
                            json=emoji_data
                        )

                        if create_response.status_code in [200, 201]:
                            created += 1
                            emoji_type = "animated" if emoji.get('animated') else "static"
                            print(f"    [+] Created {emoji_type} emoji: {emoji.get('name', 'Unknown')}")
                        else:
                            failed += 1
                    else:
                        failed += 1

                    time.sleep(self.time_sleep)

                except Exception as e:
                    failed += 1

            print(f"    [+] Cloned {created}/{len(source_emojis)} emojis ({failed} failed)")

        except Exception as e:
            print(f"    [-] Error cloning emojis: {e}")

    def show_clone_summary(self):
        print("\n[+] Clone Summary")

        if self.source_data:
            print(f"\n    Source Server:")
            print(f"    Name: {self.source_data.get('name', 'N/A')}")
            print(f"    ID: {self.source_id}")

        if self.target_data:
            print(f"\n    Target Server:")
            print(f"    Name: {self.target_data.get('name', 'N/A')}")
            print(f"    ID: {self.target_id}")

    def run(self):
        self.clear()
        self.banner()

        source_id = input("\nSource Server ID: ").strip()
        if not source_id:
            print("[-] Source server ID required")
            return

        print("[+] Loading source server...")
        if not self.load_source_server(source_id):
            return

        print(f"[+] Source server loaded: {self.source_data.get('name', 'Unknown')}")

        target_id = input("\nTarget Server ID (press ENTER to create new): ").strip()

        if target_id:
            print("[+] Loading target server...")
            if not self.load_target_server(target_id):
                return
            print(f"[+] Target server loaded: {self.target_data.get('name', 'Unknown')}")
        else:
            print("[+] Creating new server...")
            if not self.create_new_server():
                return
            time.sleep(2)
            
            if not self.load_target_server(self.target_id):
                print("[-] Failed to load newly created server")
                return

        print("\n[!] Clone Configuration")
        print(f"    Source: {self.source_data.get('name', 'Unknown')} ({self.source_id})")
        print(f"    Target: {self.target_data.get('name', 'Unknown')} ({self.target_id})")

        confirm = input("\n[!] Start cloning? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("[-] Cancelled")
            return

        print("\n[+] Starting clone process...")

        self.clean_target_server()
        time.sleep(1)

        self.clone_server_info()
        time.sleep(1)

        role_mapping = self.clone_roles()
        time.sleep(1)

        self.clone_channels(role_mapping)
        time.sleep(1)

        self.clone_emojis()

        self.show_clone_summary()
        print("\n[+] Clone process completed!")

def main(token):
    cloner = ServerCloner(token)
    cloner.run()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        token = input("Token: ").strip()
        main(token)