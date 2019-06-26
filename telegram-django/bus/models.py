from django.db import models


class BusGo(models.Model):
    chat_id = models.CharField(max_length=20)
    go_station_id = models.CharField(max_length=20)
    go_route_id = models.CharField(max_length=20)
    go_station_order = models.CharField(max_length=5)

    def __str__(self):
        return f'{self.id}, {self.chat_id} {self.go_station_id} {self.go_route_id} {self.go_station_order}'


class BusOut(models.Model):
    chat_id = models.CharField(max_length=20)
    out_station_id = models.CharField(max_length=20)
    out_route_id = models.CharField(max_length=20)
    out_station_order = models.CharField(max_length=5)
