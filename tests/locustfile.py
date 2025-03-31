from locust import HttpUser, task, between

class UrlShortenerUser(HttpUser):
    wait_time = between(1, 3)  # Задержка между запросами (1-3 секунды)

    def on_start(self):
        """Метод, выполняющийся перед началом теста."""
        # Регистрация пользователя
        self.username = "testuser"
        self.password = "testpassword"
        self.email = "testuser@example.com"

        self.client.post("/auth/register", json={
            "username": self.username,
            "password": self.password,
            "email": self.email
        })

        # Получение токена авторизации
        response = self.client.post("/auth/token", json={
            "username": self.username,
            "password": self.password
        })
        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(2)
    def shorten_link(self):
        """Тест создания короткой ссылки."""
        self.client.post("/links/shorten", json={
            "original_url": "https://example.com"
        }, headers=self.headers)

    @task(3)
    def redirect_link(self):
        """Тест перенаправления по короткому коду."""
        # Создаем короткую ссылку
        response = self.client.post("/links/shorten", json={
            "original_url": "https://example.com"
        }, headers=self.headers)
        short_code = response.json().get("short_code")

        # Перенаправляемся по короткому коду
        if short_code:
            self.client.get(f"/{short_code}")

    @task(1)
    def get_link_stats(self):
        """Тест получения статистики по короткой ссылке."""
        # Создаем короткую ссылку
        response = self.client.post("/links/shorten", json={
            "original_url": "https://example.com"
        }, headers=self.headers)
        short_code = response.json().get("short_code")

        # Получаем статистику
        if short_code:
            self.client.get(f"/links/{short_code}/stats", headers=self.headers)