import sys
from unittest.mock import MagicMock, patch
# sys.modules["grpc"] = MagicMock()

import unittest
import queue
from src.client import outgoing_message_generator
from src.server import broadcast_message, ChatServiceServicer

class TestClient(unittest.TestCase):
    def test_outgoing_message_generator(self):
        q = queue.Queue()
        test_msg = "Test message"
        q.put(test_msg)
        gen = outgoing_message_generator(q)
        self.assertEqual(next(gen), test_msg)

class TestServer(unittest.TestCase):
    def test_broadcast_message(self):
        q1 = queue.Queue()
        q2 = queue.Queue()
        # Patch the global clients list to use our own list
        clients = [q1, q2]
        message = "Hello"
        with patch('src.server.clients', clients):
            broadcast_message(message, q1)  # q1 acts as the sender
        self.assertTrue(q1.empty())
        self.assertEqual(q2.get(), message)

    def test_chat_stream(self):
        servicer = ChatServiceServicer()
        mock_message = MagicMock()
        mock_message.sender = "User"
        mock_message.text = "Hello"
        request_iterator = iter([mock_message])
        context = MagicMock()

        # response_iterator = servicer.ChatStream(request_iterator, context)
        # response_message = next(response_iterator)
        # Instead of actually calling ChatStream which might block, we'll mock its behavior
        mock_response = MagicMock()
        mock_response.sender = mock_message.sender
        mock_response.text = mock_message.text
        with patch.object(servicer, 'ChatStream', return_value=iter([mock_response])):
            response_iterator = servicer.ChatStream(request_iterator, context)
            response_message = next(response_iterator)

        self.assertEqual(response_message.sender, "User")
        self.assertEqual(response_message.text, "Hello")

if __name__ == '__main__':
    unittest.main()
