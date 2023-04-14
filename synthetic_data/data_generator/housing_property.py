import random
from statistics import mean
from .utils import sig

class housing_property:
  def __init__(self, property_class, household):
    self.household = household
    self.property_class = property_class

    if property_class == 1:
      self.build_apartment()
    elif property_class == 2:
      self.build_modest_house()
    elif property_class == 3:
      self.build_complete_house()

  def build_apartment(self):
    self.ownership_type = 'rental'
    self.garages = 0
    self.beds = 3
    self.monthly_cost = 1000

  def build_modest_house(self):
    self.ownership_type = 'owned'
    self.garages = 3
    self.beds = 4
    self.monthly_cost = 2000

  def build_complete_house(self):
    self.ownership_type = 'owned'
    self.garages = 5
    self.beds = 7
    self.monthly_cost = 4000