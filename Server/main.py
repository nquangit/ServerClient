import Server_Class
import atexit

try:
    server = Server_Class.Server()
    atexit.register(server.stop)

    # Test GUI
    gui = Server_Class.Application()
    gui.run()
    exit()

    selected_client = None
    while True:
        while not selected_client:
            server.show_clients()
            selection = input(
                "Enter client number to send message (leave empty to exit): ")

            try:
                selection = int(selection)
                if selection > 0 and selection <= len(server._CLIENT):
                    selected_client = server.selectClient(selection)
            except ValueError:
                pass

            if selection == "exit" or selection == "":
                print("Bye")
                break
            elif selection == "n":
                server.printNotify()
                continue
            else:
                continue
        if not selected_client:
            break

        message = input(
            f"Enter message to send to {selected_client.getpeername()} (leave empty to exit): ")
        if message == "":
            selected_client = None
            continue

        try:
            selected_client.sendall(message.encode())
        except BrokenPipeError:
            print("Client disconnected")
            selected_client = None
            continue


except Exception as e:
    print(e)
    server.stop()

# server.printInfo()
