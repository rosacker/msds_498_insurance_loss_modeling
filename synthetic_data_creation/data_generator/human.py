import random
from statistics import mean
from .utils import sig
from uuid import uuid4


class human:
    """
    Humans are one of the main classes of the process.
    Humans have an "upbringing score" that determines much of their life (occupation, income, driving ability, education, etc...)
    Each year the human ages up, improving their risk mitigation, potentially causing a wedding 🤵👰, updating their education status, etc...
    """

    def __init__(self, household, target_age, target_gender=None, upbringing_score=None):
        self.household = household
        self.id = uuid4().hex
        self.age = 0
        self.tenure_years = 0
        self.driving_experience = 0
        self.gender = random.choices(['m', 'f'], weights=[0.5, 0.5])[
            0] if target_gender is None else target_gender
        self.married = False
        self.education = 'uneducated'
        self.job_class = 0

        self.age_licensed = random.choices([16, 17, 18, 19, 20], weights=[
                                           0.7, 0.1, 0.1, 0.05, 0.05])[0]
        self.married_age = max(18,
                               random.choices(population=[22, 25, 29, 33, 37, 41, 1000],
                                              weights=[0.25, 0.15, 0.15, 0.1, 0.1, 0.1, 0.15])[0]
                               + int(random.uniform(-3, 3))
                               )

        self.upbringing_score = upbringing_score if upbringing_score is not None else random.normalvariate(
            0, 3)
        self.risk_mitigation_score = self.upbringing_score + \
            random.normalvariate(0, 0.5)
        self.job_risk_deviation = random.normalvariate(0, 0.5)
        self.financial_risk_deviation = random.normalvariate(0, 0.5)

        self.move_forward_n_years(target_age)

    def move_forward_n_years(self, n):
        for i in range(n):
            self.age += 1

            if not self.married and self.married_age <= self.age:
                self.get_married()

            self.evaluate_education()
            self.evaluate_job()

            # People don't shop for houses every year!
            if 0.33 > random.uniform(0, 1):
                self.evaluate_housing()

            if self.is_driving_age:
                self.driving_experience += random.uniform(0, 1)

            if self.gender == 'm' and (23 < self.age < 27):
                self.risk_mitigation_score += random.uniform(-0.05, 0.15)
            elif self.gender == 'f' and (18 < self.age < 23):
                self.risk_mitigation_score += random.uniform(-0.05, 0.15)
            elif self.age < 23:
                self.risk_mitigation_score += random.uniform(-0.05, 0.05)
            else:
                self.risk_mitigation_score += random.uniform(-0.05, 0.1)

            self.risk_mitigation_score += random.uniform(-0.05, 0.1)
            self.child_check(years_remaining=n - 1 - i)

            self.leave_household()

    def evaluate_education(self):
        if self.education == 'attending college':
            if self.age >= 26:
                self.education = 'high school degree'
                self.job_class = 1
            elif self.age >= 21:
                p = sig(self.upbringing_score/5+0.5)
                if p > random.uniform(0, 1):
                    self.education = 'college graduate'
                    self.job_class = min(max(2, self.job_class + 1), 6)
                elif self.upbringing_score < 0 and 0.2 > random.uniform(0, 1):
                    self.education = 'high school degree'
                    self.job_class = 1
        elif self.age < 17 or self.age > 40:
            return None
        elif 17 <= self.age <= 21:
            p = sig(self.upbringing_score/5+0.5)
            dice_roll = random.uniform(0, 1)
            if self.education == 'uneducated' and p > dice_roll:
                self.education = 'high school degree'
                self.job_class = 1
            elif self.education == 'high school degree' and p > dice_roll:
                self.education = 'attending college'
                self.job_class = 1
        elif 24 <= self.age <= 26 and self.education == 'college graduate':
            p = sig(self.upbringing_score/5 - 1)
            if p > random.uniform(0, 1):
                self.education = 'postbaccalaureate degree'
                self.job_class = min(max(4, self.job_class + 1), 6)
        elif self.education == 'college graduate' and self.job_class >= 3:
            if 0.03 > random.uniform(0, 1):
                self.education = 'postbaccalaureate degree'
                self.job_class = min(max(4, self.job_class + 1), 6)

    def evaluate_job(self):
        change_up_index = 0.5 * sig(-self.job_risk_score)
        if change_up_index > random.uniform(0, 1):
            allowed_ranges = {
                'uneducated': [0, 1, 2],
                'high school degree': [0, 1, 2, 3],
                'attending college': [0, 1, 2],
                'college graduate': [0, 2, 3, 4],
                'postbaccalaureate degree': [0, 3, 4, 5, 6],
            }
            allowed_range = allowed_ranges[self.education]
            if self.job_class not in allowed_range:
                return None

            movement = random.choice([-1, 1])
            current_index = allowed_range.index(self.job_class)
            new_index = max(
                min(current_index + movement, len(allowed_range)-1), 0)
            self.job_class = allowed_range[new_index]

    def evaluate_housing(self):
        return None

    def child_check(self, years_remaining):
        return None

    def leave_household(self):
        return None

    def get_married(self):
        self.married = True
        self.risk_mitigation_score += 0.15

    @property
    def wage(self):
        wage_map = {
            0: 0,
            1: 8,
            2: 15,
            3: 30,
            4: 50,
            5: 70,
            6: 125
        }

        return wage_map[self.job_class]

    @property
    def summary(self):
        results = {
            'driver_id': self.id,
            'driver_age': self.age,
            'driver_gender': self.gender,
            'driver_tenure': self.tenure_years
        }

        return results

    @property
    def hours_worked(self):
        if self.job_class == 0:
            return 0
        elif self.education == 'attending_college' or self.age <= 21:
            return random.uniform(5, 15)
        else:
            return 40

    @property
    def annual_income(self):
        return self.wage * self.hours_worked * 52

    @property
    def job_risk_score(self):
        return self.risk_mitigation_score + self.job_risk_deviation

    @property
    def financial_risk_score(self):
        return self.risk_mitigation_score + self.financial_risk_deviation

    @property
    def credit_score(self):
        return int(200 + 700 * sig(0.2 * self.financial_risk_score))

    @property
    def driving_experience_pct(self):
        return sig(2.5*self.driving_experience-5)

    @property
    def risk_mitigation_pct(self):
        return sig(self.risk_mitigation_score/10-0.5)

    @property
    def driving_hazard(self):
        return 0.5 + 1.5 * sig(3 - 3 * self.driving_experience_pct - 0.5 * self.risk_mitigation_pct + 0.25 * max(self.age-65, 0) - 0.15 * max(self.age-75, 0))

    @property
    def years_licensed(self):
        return self.age - self.age_licensed

    @property
    def is_driving_age(self):
        return self.years_licensed >= 0