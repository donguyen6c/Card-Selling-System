from locust import HttpUser, between, task

class MyTest(HttpUser):
    @task(1)
    def load_products(self):
        self.client.get("/")

    @task(2)
    def load_discounts(self):
        self.client.get("/promotion")