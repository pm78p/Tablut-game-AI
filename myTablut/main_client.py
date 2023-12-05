import sys
from my_ai_logic import main  # Import the main function from your AI logic module

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: main_client.py [white|black] [timeout] [server_ip]")
        sys.exit(1)

    color = sys.argv[1].upper()  # 'white' or 'black'
    timeout = int(sys.argv[2])  # Timeout in seconds
    server_ip = sys.argv[3]  # IP address of the server
    player_name = "Tycoons"

    main(player_name, color, timeout, server_ip)
