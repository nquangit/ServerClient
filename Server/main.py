import Server_Class
import atexit

try:
    server = Server_Class.Server()
    atexit.register(server.stop)

    gui = Server_Class.Application()
    gui.run()
    exit()

except Exception as e:
    print(e)
    server.stop()

# server.printInfo()
