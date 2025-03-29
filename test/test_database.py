import pytest
import os
from src.database import ChatDatabase

@pytest.fixture
def db():
    """Create a test database."""
    test_db_path = "test_chat.db"
    # Remove the test database if it exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Create a new test database
    db = ChatDatabase(test_db_path)
    yield db
    
    # Clean up
    db.close()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

def test_save_and_retrieve_message(db):
    """Test saving and retrieving messages."""
    # Save a test message
    db.save_message("TestUser", "Hello, world!")
    
    # Retrieve recent messages
    messages = db.get_recent_messages(limit=1)
    
    # Check that we got the message back
    assert len(messages) == 1
    assert messages[0]['sender'] == "TestUser"
    assert messages[0]['text'] == "Hello, world!"

def test_get_messages_by_sender(db):
    """Test retrieving messages by sender."""
    # Save messages from different users
    db.save_message("User1", "Message 1")
    db.save_message("User2", "Message 2")
    db.save_message("User1", "Message 3")
    
    # Retrieve messages from User1
    messages = db.get_messages_by_sender("User1")
    
    # Check that we got the right messages
    assert len(messages) == 2
    assert messages[0]['text'] == "Message 1"
    assert messages[1]['text'] == "Message 3" 