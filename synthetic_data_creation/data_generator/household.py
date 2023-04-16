import random
from numpy.random import poisson
from statistics import mean
from uuid import uuid4

from .utils import sig

from .head_of_house import head_of_house
from .housing_property import housing_property
from .vehicle import vehicle
from .claim import claim


class household:
    """
    This class is the main object of the process, and is what should be used when simulating data.
    The class is meant to represent a single household which might have multiple humans, vehicles, and other properties.
    Initializing this household object will generate a head of household, any other humans/property based upon the head of households age.
    You can then use move_forward_n_years() to move the hosuehold forward n years worth of experience. This will generate claims, and age other objects in the house.
    """

    def __init__(self):
        self.id = uuid4().hex
        self.inforce = True
        self.child_interest = random.choices([True, False], [0.85, 0.15])[0]
        self.children = []
        self.properties = []
        self.claims = []
        self.vehicles = [vehicle(self, 15, 'sedan'), vehicle(self, 3, 'suv')]
        self.significant_other = None
        self.head_of_household = head_of_house(self)
        self.head_of_household.start_life(self)
        self.tenure_years = 0

    def update_house(self):
        if len(self.properties) <= 1:
            house_1 = housing_property(1, self)
            house_2 = housing_property(2, self)
            house_3 = housing_property(3, self)

            if 0.20 * self.monthly_income >= house_3.monthly_cost + house_2.monthly_cost:
                # Congrats on the vacation home you crazy people...
                self.properties = [house_3, house_2]
            elif 0.3 * self.monthly_income >= house_3.monthly_cost:
                self.properties = [house_3]
            elif 0.3 * self.monthly_income >= house_2.monthly_cost:
                self.properties = [house_2]
            elif 0.3 * self.monthly_income >= house_1.monthly_cost:
                self.properties = [house_1]

    def move_forward_n_years(self, n):
        if not self.inforce:
            return None

        for _ in range(n):
            for x in self.children:
                x.move_forward_n_years(1)

            if self.significant_other is not None:
                self.significant_other.move_forward_n_years(1)

            self.head_of_household.move_forward_n_years(1)

            for x in self.vehicles:
                x.move_forward_n_years(1)

            # Update all the tenures
            self.tenure_years += 1
            for x in self.drivers:
                x.tenure_years += 1

            self.household_lapse_check()

            self.generate_claims()

            if not self.inforce:
                return None

    def generate_claims(self):
        mileage = self.determine_mileage()

        for key, mileage in mileage.items():
            driver, vehicle, road_type = key

            hazards = {
                'single_car_collision': 0.03 * (mileage/10000),
                'multi_car_collision': 0.03 * (mileage/10000),
                'theft': 0.03 * (mileage/10000),
                'hail': 0.03 * (mileage/10000),
                'glass': 0.03 * (mileage/10000),
                'ubi': 0.03 * (mileage/10000),
                'ers': 0.03 * (mileage/10000)
            }

            for claim_type, hazard in hazards.items():
                n = int(poisson(hazard, 1)[0])
                if n > 0:
                    for _ in range(n):
                        self.claims.append(claim(claim_type, self, vehicle=vehicle, driver=driver))
            

    def determine_mileage(self):
        mileage = {
            (driver, vehicle, road_type): 5_000
            for driver in self.drivers
            for vehicle in self.vehicles
            for road_type in ['highway', 'city']
        }

        return mileage

    def remove_child(self, removal_child):
        """Remove a child when they get to an old enough age"""

        self.children = [x for x in self.children if x != removal_child]

    def household_lapse_check(self):
        hh_age = self.head_of_household.age

        # Let's keep the households in the 2 digit ages
        if hh_age >= 99:
            self.inforce = False
            return None

        # Low credit score individuals will shop more
        score = self.credit_score
        if score <= 500:
            p = 0.125
        elif score <= 600:
            p = 0.075
        elif score <= 700:
            p = 0.05
        else:
            p = 0.025

        # General mortality
        if hh_age > 75:
            p += ((hh_age - 75)/95) ** 0.5

        if p > random.uniform(0, 1):
            self.inforce = False

    @property
    def summary(self):
        results = {
            'inforce': self.inforce,
            'household_tenure': self.tenure_years,
            'min_driver_tenure': self.min_driver_tenure,
            'max_driver_tenure': self.max_driver_tenure,
            'driver_count': self.driver_count,
            'youthful_driver_count': self.youthful_driver_count,
            'max_driver_age': self.max_driver_age,
            'min_driver_age': self.min_driver_age,
            'mean_driver_age': self.mean_driver_age,
            'credit_score': self.credit_score,
            'multiline_houses': self.multiline_houses,
            'multiline_rental': self.multiline_rental,
            'multiline_personal_liability_umbrella': self.multiline_personal_liability_umbrella,
            'multiline_personal_article_policy': self.multiline_personal_article_policy,
            'vehicle_info': [x.summary for x in self.vehicles],
            'driver_info': [x.summary for x in self.drivers],
            'claims_info': [x.summary for x in self.claims if (x.driver_in_force or x.driver is None)]
        }

        drivers_list = self.drivers

        driver_counts = {
            f'driver_cnt_{age}':  len([x for x in drivers_list if x.age == age])
            for age in range(16, 99)
        }
        results.update(**driver_counts)

        driver_counts = {
            f'driver_cnt_{age}_{gender}':  len([x for x in drivers_list if x.age == age and x.gender == gender])
            for age in range(16, 99)
            for gender in ['m', 'f']
        }

        results.update(**driver_counts)

        # Count of claims
        claim_counts = {
            f'household_claim_cnt_all_{age}': len([x for x in self.claims if x.driver_in_force and x.how_old == age])
            for age in range(1, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'household_claim_cnt_bi_{age}': len([x for x in self.claims if x.driver_in_force and x.how_old == age and x.bi == 1])
            for age in range(1, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'household_claim_cnt_pd_{age}': len([x for x in self.claims if x.driver_in_force and x.how_old == age and x.pd == 1])
            for age in range(1, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'household_claim_cnt_coll_{age}': len([x for x in self.claims if x.driver_in_force and x.how_old == age and x.coll == 1])
            for age in range(1, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'household_claim_cnt_comp_{age}': len([x for x in self.claims if x.driver_in_force and x.how_old == age and x.comp == 1])
            for age in range(1, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'household_claim_cnt_ers_{age}': len([x for x in self.claims if x.driver_in_force and x.how_old == age and x.ers == 1])
            for age in range(1, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'household_claim_cnt_ubi_{age}': len([x for x in self.claims if x.driver_in_force and x.how_old == age and x.ubi == 1])
            for age in range(1, 16)
        }
        results.update(**claim_counts)

        # Time Since Claim
        def min_with_none(x): return min(x) if len(x) > 0 else None
        claim_counts = {
            'household_claim_time_since_all': min_with_none([x.how_old for x in self.claims if x.driver_in_force and x.how_old <= 15]),
            'household_claim_time_since_bi': min_with_none([x.how_old for x in self.claims if x.driver_in_force and x.how_old <= 15 and x.bi == 1]),
            'household_claim_time_since_pd': min_with_none([x.how_old for x in self.claims if x.driver_in_force and x.how_old <= 15 and x.pd == 1]),
            'household_claim_time_since_comp': min_with_none([x.how_old for x in self.claims if x.driver_in_force and x.how_old <= 15 and x.comp == 1]),
            'household_claim_time_since_coll': min_with_none([x.how_old for x in self.claims if x.driver_in_force and x.how_old <= 15 and x.coll == 1]),
            'household_claim_time_since_mpc': min_with_none([x.how_old for x in self.claims if x.driver_in_force and x.how_old <= 15 and x.mpc == 1]),
            'household_claim_time_since_ers': min_with_none([x.how_old for x in self.claims if x.driver_in_force and x.how_old <= 15 and x.ers == 1]),
            'household_claim_time_since_ubi': min_with_none([x.how_old for x in self.claims if x.driver_in_force and x.how_old <= 15 and x.ubi == 1])
        }
        results.update(**claim_counts)

        return results

    @property
    def summary_per_vehicle(self):
        results = self.summary
        claims_info = results.pop('claims_info')
        vehicle_info = results.pop('vehicle_info')

        summary = [dict(results,
                        **x,
                        vehicle_claims=[
                            y for y in claims_info if y['vehicle_id'] == x['vehicle_id']],
                        other_claims=[
                            y for y in claims_info if y['vehicle_id'] != x['vehicle_id']],
                        )
                   for x in vehicle_info]

        return summary

    @property
    def summary_with_debugging(self):
        results = self.summary
        results.update({
            'child_count': self.child_count,
            'monthly_income': self.monthly_income,
            'monthly_expenses': self.household_expenses,
            'min_driver_hazard': self.min_driver_hazard,
            'max_driver_hazard': self.max_driver_hazard,
            'mean_driver_hazard': self.mean_driver_hazard,
            'min_risk_mitigiation_score': self.min_risk_mitigation,
            'max_risk_mitigiation_score': self.max_risk_mitigation,
            'mean_risk_mitigiation_score': self.mean_risk_mitigation,
            'head_of_house_upbringing_score': self.head_of_household.upbringing_score
        })

        return results

    @property
    def household_members(self):
        members = [self.head_of_household,
                   self.significant_other, *self.children]
        return [x for x in members if x is not None]

    @property
    def drivers(self):
        return [x for x in self.household_members if x.is_driving_age]

    @property
    def combined_risk_score(self):
        x = self.head_of_household.upbringing_score

        if self.significant_other is not None:
            x += self.significant_other.upbringing_score
            x = x/2

        return x

    @property
    def people_count(self):
        return len(self.household_members)

    @property
    def driver_count(self):
        return len(self.drivers)

    @property
    def youthful_driver_count(self):
        return len([x for x in self.drivers if x.age <= 25])

    @property
    def child_count(self):
        return len(self.children)
    
    @property
    def child_count_lt_18(self):
        return len([x for x in self.children if x.age < 18])

    @property
    def annual_income(self):
        return sum([x.annual_income for x in self.household_members])

    @property
    def monthly_income(self):
        return self.annual_income/12

    @property
    def household_expenses(self):
        cost = self.people_count * 1_000
        cost += self.monthly_income * 0.2  # darn taxes
        cost += sum([x.monthly_cost for x in self.properties])
        cost += sum([x.monthly_cost for x in self.vehicles])

        return cost

    @property
    def multiline_houses(self):
        report_rate = 0.85
        if report_rate >= random.uniform(0, 1):
            return len([x for x in self.properties if x.ownership_type == 'owned'])
        else:
            return 0

    @property
    def multiline_rental(self):
        report_rate = 0.45
        if report_rate >= random.uniform(0, 1):
            return len([x for x in self.properties if x.ownership_type == 'rental'])
        else:
            return 0

    @property
    def multiline_personal_liability_umbrella(self):
        """Represents an additional liability policy that high networth individuals should carry
           Would be highly correlated with income. Doctors/Lawyers would be common customers
        """
        report_rate = 0
        if self.annual_income > 95_000:
            report_rate += 0.05
        if self.annual_income > 115_000:
            report_rate += 0.05
        if self.annual_income > 135_000:
            report_rate += 0.05
        if self.annual_income > 155_000:
            report_rate += 0.1
        if self.annual_income > 195_000:
            report_rate += 0.1

        return 1 if report_rate >= random.uniform(0, 1) else 0

    @property
    def multiline_personal_article_policy(self):
        """Represents a policy for covering jewlery or other expensive items
           Would be correlated with high income or being married (wedding bands and engagement rings!)
        """
        report_rate = 0.15

        if self.significant_other is not None:
            return 1 if self.annual_income > 75_000 and report_rate >= random.uniform(0, 1) else 0

        return 1 if self.annual_income > 150_000 and report_rate >= random.uniform(0, 1) else 0

    @property
    def garage_count(self):
        return sum([x.garages for x in self.properties])

    @property
    def bed_count(self):
        return sum([x.beds for x in self.properties])

    @property
    def min_driver_age(self):
        if self.driver_count == 0:
            return None

        return min([x.age for x in self.drivers])

    @property
    def max_driver_age(self):
        if self.driver_count == 0:
            return None

        return max([x.age for x in self.drivers])

    @property
    def max_driver_tenure(self):
        if self.driver_count == 0:
            return None

        return max([x.tenure_years for x in self.drivers])

    @property
    def min_driver_tenure(self):
        if self.driver_count == 0:
            return None

        return min([x.tenure_years for x in self.drivers])

    @property
    def mean_driver_age(self):
        if self.driver_count == 0:
            return None

        return mean([x.age for x in self.drivers])

    @property
    def credit_score(self):
        return self.head_of_household.credit_score

    @property
    def min_driver_hazard(self):
        if self.driver_count == 0:
            return None

        return min([x.driving_hazard for x in self.drivers])

    @property
    def max_driver_hazard(self):
        if self.driver_count == 0:
            return None

        return max([x.driving_hazard for x in self.drivers])

    @property
    def mean_driver_hazard(self):
        if self.driver_count == 0:
            return None

        return mean([x.driving_hazard for x in self.drivers])

    @property
    def min_risk_mitigation(self):
        if self.driver_count == 0:
            return None

        return min([x.risk_mitigation_score for x in self.drivers])

    @property
    def max_risk_mitigation(self):
        if self.driver_count == 0:
            return None

        return max([x.risk_mitigation_score for x in self.drivers])

    @property
    def mean_risk_mitigation(self):
        if self.driver_count == 0:
            return None

        return mean([x.risk_mitigation_score for x in self.drivers])
