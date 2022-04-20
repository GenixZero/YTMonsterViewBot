username = 'example@gmail.com'
password = 'ExamplePassword'

from ytmonsterclient import YTMonsterClient
import time
import os

clients = []

def main():
    for x in range(3):
        client = YTMonsterClient(username, password)
        client.startAsync()
        clients.append(client)

if __name__ == '__main__':
    try:
        main()
        while True: # to allow exits
            time.sleep(10000)
    except KeyboardInterrupt:
        print('\nExiting...')
        for client in clients:
            client.stop()
        os._exit(0)