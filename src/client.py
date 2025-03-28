import grpc
import threading
import queue

import chat_pb2
import chat_pb2_grpc

def outgoing_message_generator(q):
    """Generator function that yields messages from the outgoing queue."""
    while True:
        message = q.get()  # blocks until a message is available
        yield message

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = chat_pb2_grpc.ChatServiceStub(channel)
    
    outgoing_q = queue.Queue()
    username = input("Enter your username: ")

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
