import os

# Teszt környezeti változók
TEST_DATABASE_URL = "http://localhost:5000"
TEST_DATABASE_NAME = "memory_game_test"  # Külön teszt adatbázis
TEST_TIMEOUT = 30

# Teszt adatok
TEST_USER = {
    "username": "test_user",
    "email": "test@example.com",
    "password": "TestPassword123!",
    "confirm_password": "TestPassword123!"
}

TEST_PLAYER = {
    "name": "TestPlayer",
    "game_mode": "color-hunter",
    "difficulty": "easy"
}