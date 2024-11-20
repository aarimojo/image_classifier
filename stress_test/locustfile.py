from typing import Optional

import requests
from locust import HttpUser, between, task

API_BASE_URL = "http://localhost:8000"


def login(username: str, password: str) -> Optional[str]:
    """This function calls the login endpoint of the API to authenticate the user and get a token.

    Args:
        username (str): email of the user
        password (str): password of the user

    Returns:
        Optional[str]: token if login is successful, None otherwise
    """
    # TODO: Implement the login function
    # 1 - make a request to the login endpoint
    # 2 - check if the response status code is 200
    # 3 - if it is, return the access_token
    # 4 - if it is not, return None
    url = f"{API_BASE_URL}/login"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None


class APIUser(HttpUser):
    wait_time = between(1, 5)
    token = None

    # Put your stress tests here.
    # See https://docs.locust.io/en/stable/writing-a-locustfile.html for help.
    # TODO
    # raise NotImplementedError
    def on_start(self):
        """Login once when the test starts"""
        self.token = login("admin@example.com", "admin")

    @task(1)  # Lower weight for the predict endpoint as it's more resource-intensive
    def predict(self):
        """Test the predict endpoint with image upload"""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        files = [("file", ("dog.jpeg", open("dog.jpeg", "rb"), "image/jpeg"))]
        
        self.client.post(
            "http://localhost:8000/model/predict",
            headers=headers,
            files=files,
        )
    
    @task(2)
    def predict_multiple_same_request(self):
        """Test the predict endpoint with multiple image uploads"""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        files = [
            ("file", ("dog.jpeg", open("dog.jpeg", "rb"), "image/jpeg")),
            ("file", ("0a7c757a80f2c5b13fa7a2a47a683593.jpeg", open("0a7c757a80f2c5b13fa7a2a47a683593.jpeg", "rb"), "image/jpeg")),
            ("file", ("0f036a47557e3f1f89d299175e85ae3e.png", open("0f036a47557e3f1f89d299175e85ae3e.png", "rb"), "image/jpeg")),
            ("file", ("6f37e6df23de9f5a4fb8801c1853b459.jpg", open("6f37e6df23de9f5a4fb8801c1853b459.jpeg", "rb"), "image/jpeg")),
            ("file", ("a13694e7d1f586ae3ecbf7edfaefd3f6.jpg", open("a13694e7d1f586ae3ecbf7edfaefd3f6.jpg", "rb"), "image/jpeg")),
        ]
        
        self.client.post(
            "http://localhost:8000/model/predict",
            headers=headers,
            files=files,
        )

    @task(3)
    def predict_multiple_different_request(self):
        """Test the predict endpoint with multiple image uploads"""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        files = [
            ("file", ("dog.jpeg", open("dog.jpeg", "rb"), "image/jpeg")),
            ("file", ("0a7c757a80f2c5b13fa7a2a47a683593.jpeg", open("0a7c757a80f2c5b13fa7a2a47a683593.jpeg", "rb"), "image/jpeg")),
            ("file", ("0f036a47557e3f1f89d299175e85ae3e.png", open("0f036a47557e3f1f89d299175e85ae3e.png", "rb"), "image/jpeg")),
            ("file", ("6f37e6df23de9f5a4fb8801c1853b459.jpg", open("6f37e6df23de9f5a4fb8801c1853b459.jpeg", "rb"), "image/jpeg")),
            ("file", ("a13694e7d1f586ae3ecbf7edfaefd3f6.jpg", open("a13694e7d1f586ae3ecbf7edfaefd3f6.jpg", "rb"), "image/jpeg")),
        ]
        
        for file in files:
            self.client.post(
                "http://localhost:8000/model/predict",
                headers=headers,
                files=[file],
            )

    @task(10)
    def predict_with_repeated_file_different_name(self):
        """Test the predict endpoint with a repeated file but with a different name"""
        if not self.token:
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        files = [
            ("file", ("dog.jpeg", open("dog.jpeg", "rb"), "image/jpeg")),
            ("file", ("0a7c757a80f2c5b13fa7a2a47a683593.jpeg", open("0a7c757a80f2c5b13fa7a2a47a683593.jpeg", "rb"), "image/jpeg")),
        ]
        
        self.client.post(
            "http://localhost:8000/model/predict",
            headers=headers,
            files=files,
        )
