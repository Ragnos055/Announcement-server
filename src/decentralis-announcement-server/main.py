import socket
import threading
import json
import time
import uuid
import sys
import os

# Global mapping of peer UUID to peer info
peers = {}
PEER_TIMEOUT = 30  # seconds


def clean_peers():
    """Remove peers that haven't announced within the timeout period."""
    while True:
        now = time.time()
        to_remove = [
            peer_uuid
            for peer_uuid, info in list(peers.items())
            if now - info["last_seen"] > PEER_TIMEOUT
        ]
        for peer_uuid in to_remove:
            peer_info = peers.pop(peer_uuid, None)
            if peer_info:
                print(f"Removing inactive peer: {peer_uuid} ({peer_info['ip']}:{peer_info['port']})")
        time.sleep(PEER_TIMEOUT)


def handle_client(conn, addr):
    try:
        data = conn.recv(1024).decode()
        request = json.loads(data)

        if request["action"] == "announce":
            incoming_uuid = request.get("uuid")

            if incoming_uuid and incoming_uuid in peers:
                client_uuid = incoming_uuid
                print(f"Existing peer re-announced: {client_uuid}")
            else:
                client_uuid = str(uuid.uuid4())
                print(f"New peer assigned UUID {client_uuid}")

            peers[client_uuid] = {
                "ip": request["ip"],
                "port": request["port"],
                "last_seen": time.time(),
            }
            conn.sendall(json.dumps({"status": "ok", "uuid": client_uuid}).encode())

        elif request["action"] == "getpeers":
            requester_uuid = request.get("uuid")
            peer_list = [
                f"{info['ip']}:{info['port']}"
                for uuid_key, info in peers.items()
                if uuid_key != requester_uuid
            ]
            response = {"peers": peer_list}
            conn.sendall(json.dumps(response).encode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def tracker_server(host="0.0.0.0", port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Tracker listening on {host}:{port}")

    # Start thread for cleaning inactive peers
    threading.Thread(target=clean_peers, daemon=True).start()

    server.settimeout(1.0)

    while True:
        try:
            conn, addr = server.accept()
        except socket.timeout:
            continue
        except KeyboardInterrupt:
            break
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

    server.close()


if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", "5000"))
        tracker_server(port=port)
    except KeyboardInterrupt:
        print("\nServeur arrêté")
        sys.exit(0)