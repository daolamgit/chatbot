import unittest
from unittest.mock import MagicMock, patch
from src.client import outgoing_message_generator
from src.server import broadcast_message, ChatServiceServicer
import queue

class TestClient(unittest.TestCase):
    def test_outgoing_message_generator(self):
        q = queue.Queue()
        q.put("Test message")
        gen = outgoing_message_generator(q)
        self.assertEqual(next(gen), "Test message")

class TestServer(unittest.TestCase):
    @patch('src.server.clients', new_callable=list)
    def test_broadcast_message(self, mock_clients):
        q1 = queue.Queue()
        q2 = queue.Queue()
        mock_clients.extend([q1, q2])
        
        message = "Hello"
        broadcast_message(message, q1)  # q1 is the sender
        
        # q1 should not receive the message
        self.assertTrue(q1.empty())
        # q2 should receive the message
        self.assertEqual(q2.get(), message)

    @patch('src.server.queue.Queue')
    def test_chat_stream(self, mock_queue):
        servicer = ChatServiceServicer()
        mock_message = MagicMock()
        mock_message.sender = "User"
        mock_message.text = "Hello"
        request_iterator = iter([mock_message])
        context = MagicMock()
        
        response_iterator = servicer.ChatStream(request_iterator, context)
        response_message = next(response_iterator)
        
        self.assertEqual(response_message.sender, "User")
        self.assertEqual(response_message.text, "Hello")

if __name__ == '__main__':
    unittest.main()
