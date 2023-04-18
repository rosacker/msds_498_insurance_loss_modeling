import random

from .human import human


class child(human):
    """
    A child of the household. This child is a human that doesn't run the household.
    This means the child can learn to drive once they are old enough, but they won't generate their own spouse or children (i.e. no grand kids!)
    When children get old enough, they try to leave the household. Ever getting married will also cause them to leave.
    """

    def __init__(self, house, target_age, upbringing_score):
        super().__init__(household=house,
                         target_age=target_age,
                         upbringing_score=upbringing_score)

    def leave_household(self):
        self_sufficent = (self.annual_income >= 35_000)
        older_kid = (self.age >= 25)

        score = 0.5 * self_sufficent + 0.25 * older_kid

        if score > random.uniform(0, 1):
            self.household.remove_child(self)

    def get_married(self, years_remaining = 0):
        """Assuming any child that gets married would leave their parents house..."""
        self.household.remove_child(self)

    def determine_mileage(self):
        if self.age <= 18:
            mileage = 6_000
        elif self.age <= 20:
            mileage = 8_000
        else:
            mileage = 10_000
                
        # Men drive a bit more!
        # According to the Federal Highway Administration, female drivers travel about 6,408 miles less than men annually.
        if self.gender == 'm':
            mileage *= 1.2

        # If they've got a job we've got extra driving to do!
        if self.job_class != 0:
            mileage *= 1.2

        # Share rides with other kids
        if self.household.driver_count > 3:
            mileage *= (0.7 ** (self.household.driver_count - 3))

        # Kids have their own activities
        if self.household.non_driver_cnt > 0:
            extra_mileage = 2_000 * self.household.non_driver_cnt
            extra_mileage = extra_mileage/self.household.driver_count
            mileage += extra_mileage
        
        city_mileage = mileage * 0.55 * self.household.primary_house.city_driving_ratio
        highway_mileage = mileage * 0.45 * self.household.primary_house.highway_driving_ratio
        
        return (city_mileage, highway_mileage)