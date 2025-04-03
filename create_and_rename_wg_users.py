import json
import requests
from requests.exceptions import HTTPError
import argparse


parser = argparse.ArgumentParser(description="Cоздать WireGuard-пользователей через API WGDashboard")
parser.add_argument("--ip", "-i", required=True, help="ip адрес сервера WGDashboard (Например: 1.1.1.1)")
parser.add_argument("--port", "-p", required=True, help="порт сервера WGDashboard (например 443")
parser.add_argument("--api_key", "-k", required=True, help="API ключ")
parser.add_argument("--config_name", "-c", required=True, help="Имя конфигурации")
parser.add_argument("--amount", "-a", type=int, default=1, help="Кол-во пользователей (По умолчанию 1)")
parser.add_argument("--dns", "-d", default="8.8.8.8", help="DNS сервер (По умолчанию 8.8.8.8)")
parser.add_argument("--mtu", "-m", default="1420", help="MTU (По умолчанию 1420)")
parser.add_argument("--keepalive", "-l", default="21", help="Keepalive (по умолчанию 21)")
parser.add_argument("--name_user", "-n", required=True, help="Имя файла конфиги для пользователя")

args = parser.parse_args()

if args.amount < 1:
    print("Не правильное кол-во пользователей. Не должно ровняться нулю")


class AddWgUser:
    def __init__(self, args):
        self.args = args
        self.headers = {
            'Content-Type': 'application/json',
            'wg-dashboard-apikey': self.args.api_key
        }
        self.recently_created = []
        self.name = []
        self.filename_peers = 'peers.json'


    def create_wg_users(self):
        url = f"http://{self.args.ip}:{self.args.port}/api/addPeers/{self.args.config_name}"
        """
        # "bulkAdd": false,            // Добавление нескольких клиентов сразу
        # "bulkAddAmount": 0,          // Количество клиентов при массовом добавлении
        # "public_key": "ключ...",     // Публичный ключ клиента
        # "allowed_ips": ["10.0.0.2"], // Массив разрешенных IP-адресов
        # "endpoint_allowed_ip": "0.0.0.0/0", // Разрешенный IP для подключения
        # "DNS": "1.1.1.1",            // DNS-серверы
        # "mtu": "1420",               // MTU
        # "keepalive": "25",           // Интервал keepalive
        # "preshared_key": "",         // Пред-общий ключ (при необходимости)
        # "name": "Имя клиента",       // Имя клиента
        # "private_key": "ключ..."     // Приватный ключ клиента
        """

        payload = {
            "bulkAdd": True,
            "bulkAddAmount": self.args.amount,
            "endpoint_allowed_ip": "0.0.0.0/0",
            "DNS": self.args.dns,
            "mtu": self.args.mtu,
            "keepalive": self.args.keepalive,
        }
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            data = response.json()
            if response.status_code == 200:
                if data.get("status"):
                    print(f"Успешно создано {self.args.amount} пользователей!")


                    self.name = [item.get("name") for item in data["data"] if item.get("name")]
                    print(f"Созданы пользователи с именами: {self.name}")
                    return self.name
                else:
                    print(f"Ошибка: {data.get('message')}")
            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

        return self.name, self.headers


    def parse_peer_name(self):
        peer_url = f"http://{self.args.ip}:{self.args.port}/api/getWireguardConfigurationInfo" # По данной ручке можно попробовать собирать метрики. Либо посмотреть в сторону из подкапота (нужно углубиться)
        params = {
            "configurationName": self.args.config_name
        }
        try:
            response = requests.get(peer_url, headers=self.headers, params=params)
            if response.status_code != 200:
                print(f"Ошибка при получении списка пиров: HTTP {response.status_code}")

            data = response.json()
            """
            Запись файла, для исследования ответа в удобном формате. В будущем можно запилить как постоянный лог и контроль каких либо действий
            """
            with open('getWireguardConfigurationInfo.json', 'w') as file:
                json.dump(data, file, indent=4)

            if not data.get("status") or "configurationPeers" not in data.get("data", {}):
                print(f"Ошибка при получении списка пиров: {data.get('message')}")


            peers = data["data"]["configurationPeers"]

            for peer in peers:
                if peer.get("name") in self.name:
                    filtered_peer = {
                        "id": peer.get("id"),
                        "name": peer.get("name"),
                        "private_key": peer.get("private_key"),
                        "DNS": peer.get("DNS"),
                        "allowed_ip": peer.get("allowed_ip"),
                        "endpoint_allowed_ip": peer.get("endpoint_allowed_ip"),
                        "mtu": peer.get("mtu", "1420"),
                        "keepalive": peer.get("keepalive", "21"),
                        "preshared_key": peer.get("preshared_key", "")
                    }
                    self.recently_created.append(filtered_peer)
            with open('peers.json', 'w') as file:
                json.dump(self.recently_created, file, indent=4)
            return self.recently_created

        except Exception as e:
            print(f"Ошибка при получении списка пиров: {e}")

    def reconfig_peer(self):
        update_url = f"http://{self.args.ip}:{self.args.port}/api/updatePeerSettings/{self.args.config_name}"
        payload = None
        
        try:
            with open(self.filename_peers, 'r') as file:
                all_peers = json.load(file)

                for peer_data in self.recently_created:
                    target_name = peer_data.get('name')
                    target_peer = None

                    for peer in all_peers:
                        if peer.get('name') == target_name:
                            target_peer = peer
                            break
                    if not target_peer:
                        print(f"Пир с именем '{target_name}' не найден.")
                        continue

                    payload = {
                        "id": target_peer["id"],
                        "name": self.args.name_user,
                        "private_key": target_peer.get("private_key"),
                        "DNS": target_peer.get("DNS"),
                        "allowed_ip": target_peer.get("allowed_ip"),
                        "endpoint_allowed_ip": target_peer.get("endpoint_allowed_ip"),
                        "mtu": target_peer.get("mtu", 1420),
                        "keepalive": target_peer.get("keepalive", 21),
                        "preshared_key": target_peer.get("preshared_key", "")
                    }

                    
        except FileNotFoundError:
            print(f"Файл {self.filename_peers} не найден!")
        except json.JSONDecodeError:
            print(f"Ошибка чтения JSON из файла {self.filename_peers}!")
        except Exception as e:
            print(f"Неизвестная ошибка при чтении файла: {e}")


        if payload:
            try:
                response = requests.post(update_url, json=payload, headers=self.headers)
                data = response.json()

                if response.status_code == 200:
                    if data.get("status"):
                        print(f"Пользователь {self.args.name_user} успешно переименован!")
                    else:
                        print(f"Ошибка: {data.get('message')}")
                else:
                    print(f"Ошибка HTTP: {response.status_code}. Message: {data.get('message')}")
            except HTTPError as htt_err:
                print(f"Ошибка: {htt_err}")
            except Exception as e:
                print(f"Неизвестная ошибка при отправке запроса: {e}")
        else:
            print("Не удалось создать данные для обновления пира")

add_user = AddWgUser(args)
add_user.create_wg_users()
add_user.parse_peer_name()
add_user.reconfig_peer()

