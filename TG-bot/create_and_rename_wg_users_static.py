import json
import requests
from requests.exceptions import HTTPError




class AddWgUser:
    def __init__(self, name_user):
        self.headers = {
            'Content-Type': 'application/json',
            'wg-dashboard-apikey': '5e94mvLZ8EVs17UaL10gyXih3DFb3HxIlUB-OTVjkl0'
        }
        self.recently_created = []
        self.name = []
        self.user_names = []
        self.peer_id = []
        self.filename_peers = 'peers.json'

        """Необходимо будет создать функционал в будущем для проверки инстансов, свободных конфигураций и т.д."""
        self.ip = "91.196.32.98"  # IP адрес сервера WGDashboard
        self.port = "10086"  # Порт сервера WGDashboard
        self.config_name = "wg0"  # Имя конфигурации
        self.amount = 1  # Кол-во пользователей
        self.dns = "8.8.8.8"  # DNS сервер
        self.mtu = "1420"  # MTU
        self.keepalive = "21"  # Keepalive
        self.name_user = name_user  # Имя файла конфига для пользователя

    # Функция проверки на наличие пользователя
    def check_client_configuration(self):
        peer_url = f"http://{self.ip}:{self.port}/api/getWireguardConfigurationInfo"
        params = {
            "configurationName": self.config_name
        }
        try:
            response = requests.get(peer_url, headers=self.headers, params=params)
            if response.status_code != 200:
                print(f"Ошибка при получении списка пиров: HTTP {response.status_code}")

            data = response.json()

            if not data.get("status") or "configurationPeers" not in data.get("data", {}):
                print(f"Ошибка при получении списка пиров: {data.get('message')}")

            peers = data["data"]["configurationPeers"]

            self.user_names = [user.get("name") for user in peers if user.get("name")]

            return self.user_names

        except Exception as e:
            print(f"Ошибка при получении списка пиров: {e}")


    # Функция создания пользователя
    def create_wg_users(self):
        url = f"http://{self.ip}:{self.port}/api/addPeers/{self.config_name}"
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
            "bulkAddAmount": self.amount,
            "endpoint_allowed_ip": "0.0.0.0/0",
            "DNS": self.dns,
            "mtu": self.mtu,
            "keepalive": self.keepalive,
        }
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            data = response.json()
            if response.status_code == 200:
                if data.get("status"):
                    self.name = [item.get("name") for item in data["data"] if item.get("name")]
                    return self.name

                else:
                    print(f"Ошибка: {data.get('message')}")
            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

        return self.name, self.headers

    # Функция нахождения необходимого пользователя и получения необходимой информации
    def parse_peer_name(self):
        peer_url = f"http://{self.ip}:{self.port}/api/getWireguardConfigurationInfo"  # По данной ручке можно попробовать собирать метрики. Либо посмотреть в сторону из подкапота (нужно углубиться)
        params = {
            "configurationName": self.config_name
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
                    self.peer_id = peer.get("id")
            with open('peers.json', 'w') as file:
                json.dump(self.recently_created, file, indent=4)
            return self.recently_created, self.peer_id

        except Exception as e:
            print(f"Ошибка при получении списка пиров: {e}")

    #Функция ренейминга пользователя от формата: BulkPeer #1_20250408_143028 на id пользователя в ТГ
    def reconfig_peer(self):
        update_url = f"http://{self.ip}:{self.port}/api/updatePeerSettings/{self.config_name}"
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
                        "name": self.name_user,
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
                        test = print(f"Пользователь {self.name_user} успешно переименован!")
                        return test
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

    # Функция скачивания конфигурации
    def download_peer_config(self):
        url = f"http://{self.ip}:{self.port}/api/downloadPeer/{self.config_name}"

        params = {
            'id': self.peer_id
        }

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200 and response.json()['status']:

            config_data = response.json()['data']
            file_name = f"{self.name_user}.conf"
            file_content = config_data['file']


            with open(file_name, 'w') as f:
                f.write(file_content)

            return file_name

        else:
            print(f"Ошибка: {response.json().get('message', 'Неизвестная ошибка')}")
            return None


if __name__ == "__main__":
    add_user = AddWgUser(name_user="qweqweqwe")
    add_user.check_client_configuration()
    add_user.create_wg_users()
    add_user.parse_peer_name()
    add_user.reconfig_peer()
    add_user.download_peer_config()

