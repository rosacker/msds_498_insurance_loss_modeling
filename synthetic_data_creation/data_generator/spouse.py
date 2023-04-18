import random
from statistics import mean
from .utils import sig

from .human import human


class spouse(human):
    """
    The least special of the human classes 😝
    A spouse's age/upbrining score/etc... is mostly determined by the head_of_house.
    Often the gender will be opposite that of the head_of_house object, but there is a chance to have a gay couple.

    For all other purposes they are a normal human that drives cars and generates claims.
    """

    def __init__(self, household, so, years_remaining):
        # Pick an age that is slightly lower than the head of house
        age_lowerbound = max(int(so.age/2 + 7), 18, so.age - 10)
        age_upperbound = so.age
        age_mode = so.age-2

        if age_lowerbound < age_mode < age_upperbound:
            target_age = random.triangular(
                age_lowerbound, age_upperbound, mode=age_mode)
            
            target_age = int(target_age)
        else:
            target_age = so.age

        # Decide if the couple is same or different sex
        straight_couple = random.choices([True, False], weights=[0.9, 0.1])[0]
        if not straight_couple:
            target_gender = so.gender
        else:
            target_gender = 'm' if so.gender == 'f' else 'f'

        # Pick an upbringing that is similar to the head of house
        target_upbringing_score = so.upbringing_score + \
            random.normalvariate(0, 0.5)

        super().__init__(household=household,
                         target_age=target_age+years_remaining,
                         target_gender=target_gender,
                         upbringing_score=target_upbringing_score)

        self.get_married()

    def determine_mileage(self):
        mileage = 10_000
        
        # Men drive a bit more!
        # According to the Federal Highway Administration, female drivers travel about 6,408 miles less than men annually.
        if self.gender == 'm':
            mileage *= 1.2

        # Unemployed people don't drive as much!
        if self.job_class == 0:
            mileage *= 0.5

        # Share rides with our spouse!
        if self.household.head_of_household is not None:
            mileage *= 0.7

        # Kids have their own activities
        if self.household.non_driver_cnt > 0:
            extra_mileage = 2_000 * self.household.non_driver_cnt
            extra_mileage = extra_mileage/self.household.driver_count
            mileage += extra_mileage
        
        city_mileage = mileage * 0.55 * self.household.primary_house.city_driving_ratio
        highway_mileage = mileage * 0.45 * self.household.primary_house.highway_driving_ratio
        
        return (city_mileage, highway_mileage)