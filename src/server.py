import grpc
from concurrent import futures
import time
import threading
import queue

import chat_pb2
import chat_pb2_grpc

# Global list of client queues
clients = []
clients_lock = threading.Lock()

def broadcast_message(message, sender):
    with clients_lock:
        for q in clients:
            # Only send the message to clients that are not the sender
            if q != sender:
                q.put(message)

class ChatServiceServicer(chat_pb2_grpc.ChatServiceServicer):
    def ChatStream(self, request_iterator, context):
        # Create a queue for this client
        q = queue.Queue()
        with clients_lock:
            clients.append(q)
        
        # Thread to handle incoming messages from this client
        def read_requests():
            for message in request_iterator:
                print(f"Received from {message.sender}: {message.text}")
                # Pass the sender's queue to the broadcast function
                broadcast_message(message, q)
        threading.Thread(target=read_requests, daemon=True).start()

        try:
            while True:
                # Yield messages from the queue (blocking call)
                message = q.get()
                yield message
        except Exception as e:
            print(f"Stream exception: {e}")
        finally:
            with clients_lock:
                clients.remove(q)

def server_console():
    """Read messages from the server operator and broadcast them."""
    while True:
        msg_text = input()
        if msg_text:
            message = chat_pb2.ChatMessage(sender="Server", text=msg_text)
            broadcast_message(message, None)  # No sender for server messages

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    
    # Start a thread for the server operator's console input
    threading.Thread(target=server_console, daemon=True).start()
    
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
