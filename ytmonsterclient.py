import base64
import requests
import time
import threading

def rotateString(str):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    newStr = ''
    for char in str:
        if char in alphabet:
            newStr += alphabet[(alphabet.index(char) + 13) % 26]
        else:
            newStr += char
    return newStr

class YTMonsterClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.session()
        self.session.keep_alive = False
        loginPage = self.session.post('https://app.ytmonster.net/login?login=ok', data={
            'usernames': username,
            'passwords': password
        }, headers={
            'user-agent': 'Windows_NT (ytm-dc: 0.3.2-beta)'
        })
        self.userID = loginPage.history[-1].headers['location'].split('/')[-1]
        self.sessionID = self.session.cookies['PHPSESSID']
        print('Logged in as ' + self.userID + ', ' + self.sessionID)
        self.headers = {
            'accept': '*/*',
            'accept-Language': 'en-US',
            'origin': 'https://app.ytmonster.net',
            'referer': 'https://app.ytmonster.net/client/' + self.userID,
            'user-Agent': 'Windows_NT (ytm-dc: 0.3.2-beta)'
        }
        self.token = None
        self.pingRunning = True
        self.videoRunning = True
        self.canStart = True
        for line in loginPage.text.split('\n'):
            if 'https://client.ytmonster.net/end/' in line:
                self.token = line.split('https://client.ytmonster.net/end/')[1].split('"')[0]
        if self.token is None:
            #print(resp)
            print('Failed to get token: ' + self.username + ', ' + self.userID)
            self.canStart = False
        self.reversedUser = base64.b64encode(rotateString(self.userID[::-1]).encode('utf-8')).decode('utf-8')

    def stop(self):
        self.pingRunning = False
        self.videoRunning = False
        self.session.get(f'https://client.ytmonster.net/end/{self.token}', headers=self.headers)

    def pingThread(self):
        while self.pingRunning:
            self.session.get(f'https://client.ytmonster.net/ping/{self.reversedUser}/{self.token}', headers=self.headers)
            time.sleep(30)

    def watchVideo(self):
        if self.videoRunning:
            videoData = self.session.get(f'https://client.ytmonster.net/watch/{self.reversedUser}/{self.token}', headers=self.headers).json()
            try:
                #videoData['img'] = None
                print('Watching "' + str(videoData['title']) + '" for ' + str(videoData['length']) + ' seconds')
                time.sleep(videoData['length'])
                vidID = base64.b64encode(str(float(videoData["id"]) * 37.5).encode('utf-8')).decode('utf-8')
                print(self.session.get(f'https://client.ytmonster.net/mark/{self.reversedUser}/{self.token}/{vidID}', headers=self.headers).text)
                print('Marked video')
            except Exception as e:
                print('ERROR: ' + str(e))
                print(videoData)
                if 'error' in videoData and videoData['error'] == '9': # Not enough available sessions
                    self.stop()
                    print(self.session.get(f'https://www.ytmonster.net/c/end-all', headers=self.headers, cookies={
                        'PHPSESSID': self.sessionID
                    }).text)
                    print('Restarting because client died')
                    time.sleep(10)
                    YTMonsterClient(self.username, self.password).startAsync()

    def startSync(self):
        if not self.canStart:
            return
        threading.Thread(target=self.pingThread, args=()).start()
        time.sleep(2)

        while self.videoRunning:
            self.watchVideo()
    
    def startAsync(self):
        threading.Thread(target=self.startSync, args=()).start()