from django.db import models


class Images(models.Model):
    name = models.CharField(max_length=1000)
    date_of_create = models.DateField(auto_now_add=True)
    image = models.ImageField()

    def __str__(self):
        return self.name


class ImageComment(models.Model):
    comment = models.CharField(max_length=1000)
    name = models.ForeignKey(Images, on_delete=models.CASCADE)
