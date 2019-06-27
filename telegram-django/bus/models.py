from django.db import models


class BusGo(models.Model):
    chat_id = models.CharField(max_length=20)
    go_bus_number = models.CharField(max_length=10)
    go_station_id = models.CharField(max_length=20)
    go_route_id = models.CharField(max_length=20)
    go_station_order = models.CharField(max_length=5)

    def __str__(self):
        return f'{self.id}, {self.chat_id} {self.go_bus_number} {self.go_station_id} {self.go_route_id} {self.go_station_order}'


class BusOut(models.Model):
    chat_id = models.CharField(max_length=20)
    out_bus_number = models.CharField(max_length=10)
    out_station_id = models.CharField(max_length=20)
    out_route_id = models.CharField(max_length=20)
    out_station_order = models.CharField(max_length=5)

    def __str__(self):
        return f'{self.id}, {self.chat_id} {self.out_bus_number} {self.out_station_id} {self.out_route_id} {self.out_station_order}'


class News(models.Model):
    news_title = models.TextField()
    news_time = models.CharField(max_length=20)
    news_url = models.TextField()

    def __str__(self):
        return f'{self.id}, {self.news_title} {self.news_time} {self.news_url}'
