import grpc
import threading
import queue

from protobuf import chat_pb2
from protobuf import chat_pb2_grpc

def outgoing_message_generator(q):
    """Generator function that yields messages from the outgoing queue."""
    while True:
        message = q.get()  # blocks until a message is available
        yield message

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        # Create a stub (client)
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        
        # Get username from user
        username = input("Enter your username: ")
        print(f"Welcome, {username}! Type your messages below.")
        
        # Request recent chat history (optional)
        try:
            # You would need to add a new RPC method for this
            # This is just a placeholder for the concept
            print("--- Recent Chat History ---")
            # If you implement a GetChatHistory RPC method
            # history = stub.GetChatHistory(chat_pb2.HistoryRequest(limit=10))
            # for msg in history.messages:
            #     print(f"{msg.sender}: {msg.text}")
            print("-------------------------")
        except Exception as e:
            print(f"Could not retrieve chat history: {e}")
        
        outgoing_q = queue.Queue()

        # Start the bidirectional stream with the outgoing message generator.
        responses = stub.ChatStream(outgoing_message_generator(outgoing_q))
        
        # Thread to process incoming messages from the server.
        def read_responses():
            for response in responses:
                print(f"\n{response.sender}: {response.text}")
        threading.Thread(target=read_responses, daemon=True).start()

        # Main loop: read user input and send messages.
        while True:
            msg_text = input(f"{username}: ")
            if msg_text:
                message = chat_pb2.ChatMessage(sender=username, text=msg_text)
                outgoing_q.put(message)

if __name__ == '__main__':
    run()
