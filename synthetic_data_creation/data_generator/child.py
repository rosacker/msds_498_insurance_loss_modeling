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
