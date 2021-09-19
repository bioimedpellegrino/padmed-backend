from django.db import models

class GenericPlace(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(blank=True, null=True, default="", max_length=2000)
    short_name = models.CharField(blank=True, null=True, max_length=2000)
    code = models.CharField(blank=True, null=True, max_length=2000)
    
    class Meta:
        abstract = True
        
class Country(GenericPlace):
    """
    Model Country
    """
    class Meta:
        verbose_name = "Nazione"
        verbose_name_plural = "Nazioni" 
        
class Province(GenericPlace):
    """
    Model Province
    """
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Provincia"
        verbose_name = "Province"
class City(GenericPlace):
    "Model City"
    province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Città"
        verbose_name_plural = "Città"