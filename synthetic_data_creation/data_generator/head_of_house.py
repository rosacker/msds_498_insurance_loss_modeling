import random
from .human import human
from .spouse import spouse
from .child import child


class head_of_house(human):
    """
    A very special instance of human.
    Like other humans, this class can drive vehicles and generate claims.
    They are special because each household has exactly once head of house, and they generate much of the rest of the household's data.
    The "upbringing score" of this object effectively decides most things.

    The head of house has an age where they will get married to a spouse at which point the spouse object is created and added to the household.
    The head of house also controls generating children. 
    This involves checks to make sure the household income is sufficent, there are enough beds, and there is an interest in having children.
    """

    def __init__(self, household):
        self.household = household

    def start_life(self, household):
        target_age = max(16, int(random.uniform(
            20, 70) + random.normalvariate(0, 3)))

        super().__init__(household, target_age)

    def get_married(self):
        super().get_married()
        self.household.significant_other = spouse(self.household, self)

    def child_check(self, years_remaining):
        finances_check = self.household.monthly_income > self.household.household_expenses * 1.2
        room_check = self.household.bed_count >= self.household.child_count + 1
        possible_check = self.married and self.household.child_interest

        if not (finances_check & room_check & possible_check):
            return None
        elif 20 <= self.age <= 25:
            p = 0.25
        elif 26 <= self.age <= 30:
            p = 0.5
        elif 31 <= self.age <= 36:
            p = 0.5
        elif 37 <= self.age <= 41:
            p = 0.35
        elif 41 <= self.age <= 45:
            p = 0.25
        else:
            # Shrug - could adopt a kid or something...
            p = 0.03
            return None

        if self.household.child_count >= 3:
            p = 0.25 * p

        if self.household.child_count >= 5:
            p = 0.25 * p

        if self.gender == self.household.significant_other.gender:
            p = 0.25 * p

        if p > random.uniform(0, 1):
            upbringing = self.household.combined_risk_score + \
                random.normalvariate(0, 0.5)
            new_child = child(self.household, years_remaining, upbringing)
            self.household.children.append(new_child)

            # Surprise Twins!
            if 0.05 > random.uniform(0, 1):
                new_child = child(self.household, years_remaining, upbringing)
                self.household.children.append(new_child)

            self.risk_mitigation_score += 0.1
            self.household.significant_other.risk_mitigation_score += 0.1

    def evaluate_housing(self):
        self.household.update_house()
