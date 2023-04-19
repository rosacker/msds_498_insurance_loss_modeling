import random
from statistics import mean
from .utils import sig
from uuid import uuid4


class vehicle:
    """
    The class of object that humans drive in order to generate claims.
    The value of the vehicle can determine the probability of causing a claim.
    The value of the vehicle depreciates as the vehicle ages.

    All claims are assigned to exactly 1 vehicle, so a vehicle has a claim history of any claims that it was invovled in.
    """

    def __init__(self, household, age, vehicle_type):
        self.household = household
        self.id = uuid4().hex
        self.age = age
        self.years_owned = 0
        self.vehicle_type = vehicle_type
        self.depreciation_rate = 0.95

        self.bi_cov_ind = True
        self.pd_cov_ind = True
        self.coll_cov_ind = False
        self.comp_cov_ind = False
        self.mpc_cov_ind = False
        self.ers_cov_ind = False
        self.ubi_cov_ind = False
        self.coll_cov = None
        self.comp_cov = None

        if vehicle_type == 'pickup':
            self.build_pickup()
        elif vehicle_type == 'suv':
            self.build_suv()
        elif vehicle_type == 'sedan':
            self.build_sedan()
        elif vehicle_type == 'sports car':
            self.build_sports_car()
        elif vehicle_type == 'van':
            self.build_van()

        self.purchase_price = self.msrp * self.depreciation_rate ** age
        self.value = self.purchase_price

        self.determine_coverages(first_time = True)

    def __hash__(self):
        return hash(self.id)

    def build_pickup(self):
        self.seats = 3
        self.msrp = 60_000
        self.male_interest = 0.75
        self.female_interest = -0.4
        self.child_interest = 0.3
        self.parent_interest = -0.3
        self.protection = 2
        self.hurt_others = 3

    def build_suv(self):
        self.seats = 6
        self.msrp = 60_000
        self.male_interest = 0.7
        self.female_interest = -0.5
        self.child_interest = -0.5
        self.parent_interest = 0.4
        self.protection = 3
        self.hurt_others = 3

    def build_sedan(self):
        self.seats = 4
        self.msrp = 20_000
        self.male_interest = -0.3
        self.female_interest = 0.6
        self.child_interest = -0.4
        self.parent_interest = 0.4
        self.protection = 1
        self.hurt_others = 1

    def build_sports_car(self):
        self.seats = 2
        self.msrp = 25_000
        self.male_interest = 0.6
        self.female_interest = -0.4
        self.child_interest = 0.6
        self.parent_interest = -0.3
        self.protection = 1
        self.hurt_others = 2

    def build_van(self):
        self.seats = 6
        self.msrp = 30_000
        self.male_interest = -0.4
        self.female_interest = 0.7
        self.child_interest = -0.5
        self.parent_interest = 0.9
        self.protection = 2
        self.hurt_others = 2

    def determine_coverages(self, first_time = False):
        self.coll_cov_ind = False
        self.comp_cov_ind = False
        self.mpc_cov_ind = False
        self.ers_cov_ind = False
        self.ubi_cov_ind = False

        if self.coll_cov_ind:
            self.coll_cov = 50
        
        if self.comp_cov_ind:
            self.comp_cov = 50

    def move_forward_n_years(self, n):
        self.age += n
        self.years_owned += n
        self.value = self.value * self.depreciation_rate ** n

    @property
    def loan_cost(self):
        # assume 5 year loan, monthly payments, with some interest
        if self.years_owned <= 5:
            return 1.1 * self.purchase_price / (5 * 12)
        else:
            return 0

    @property
    def maintanance_cost(self):
        if self.age < 10:
            return 50
        elif self.age < 15:
            return 100
        elif self.age < 20:
            return 150
        else:
            return 200

    @property
    def monthly_cost(self):
        return self.loan_cost + self.maintanance_cost

    @property
    def prior_claims(self):
        return [x for x in self.household.claims if x.vehicle == self]

    @property
    def summary(self):
        results = {
            'vehicle_id': self.id,
            'vehicle_age': self.age,
            'vehicle_years_owned': self.years_owned,
            'vehicle_type': self.vehicle_type
        }

        claims = self.prior_claims

        # Count of claims
        claim_counts = {
            f'vehicle_claim_cnt_all_{age-1}': len([x for x in claims if x.how_old == age and x.paid_indicator and (x.driver_in_force  or x.driver is None)])
            for age in range(0, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'vehicle_claim_cnt_bi_{age-1}': len([x for x in claims if x.how_old == age and x.bi == 1 and x.paid_indicator and (x.driver_in_force  or x.driver is None)])
            for age in range(0, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'vehicle_claim_cnt_pd_{age-1}': len([x for x in claims if x.how_old == age and x.pd == 1 and x.paid_indicator and (x.driver_in_force  or x.driver is None)])
            for age in range(0, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'vehicle_claim_cnt_coll_{age-1}': len([x for x in claims if x.how_old == age and x.coll == 1 and x.paid_indicator and (x.driver_in_force  or x.driver is None)])
            for age in range(0, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'vehicle_claim_cnt_comp_{age-1}': len([x for x in claims if x.how_old == age and x.comp == 1 and x.paid_indicator and (x.driver_in_force  or x.driver is None)])
            for age in range(0, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'vehicle_claim_cnt_mpc_{age-1}': len([x for x in claims if x.how_old == age and x.mpc == 1 and x.paid_indicator and (x.driver_in_force  or x.driver is None)])
            for age in range(0, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'vehicle_claim_cnt_ers_{age-1}': len([x for x in claims if x.how_old == age and x.ers == 1 and x.paid_indicator and (x.driver_in_force  or x.driver is None)])
            for age in range(0, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'vehicle_claim_cnt_ubi_{age-1}': len([x for x in claims if x.how_old == age and x.ubi == 1 and x.paid_indicator and (x.driver_in_force  or x.driver is None)])
            for age in range(0, 16)
        }
        results.update(**claim_counts)

        # Time Since Claim
        def min_with_none(x): return min(x) - 1 if len(x) > 0 else None
        claim_counts = {
            'vehicle_claim_time_since_all': min_with_none([x.how_old for x in claims if 1 <= x.how_old <= 16 and x.paid_indicator and (x.driver_in_force  or x.driver is None)]),
            'vehicle_claim_time_since_bi': min_with_none([x.how_old for x in claims if 1 <= x.how_old <= 16 and x.bi == 1 and x.paid_indicator and (x.driver_in_force  or x.driver is None)]),
            'vehicle_claim_time_since_pd': min_with_none([x.how_old for x in claims if 1 <= x.how_old <= 16 and x.pd == 1 and x.paid_indicator and (x.driver_in_force  or x.driver is None)]),
            'vehicle_claim_time_since_comp': min_with_none([x.how_old for x in claims if 1 <= x.how_old <= 16 and x.comp == 1 and x.paid_indicator and (x.driver_in_force  or x.driver is None)]),
            'vehicle_claim_time_since_coll': min_with_none([x.how_old for x in claims if 1 <= x.how_old <= 16 and x.coll == 1 and x.paid_indicator and (x.driver_in_force  or x.driver is None)]),
            'vehicle_claim_time_since_mpc': min_with_none([x.how_old for x in claims if 1 <= x.how_old <= 16 and x.mpc == 1 and x.paid_indicator and (x.driver_in_force  or x.driver is None)]),
            'vehicle_claim_time_since_ers': min_with_none([x.how_old for x in claims if 1 <= x.how_old <= 16 and x.ers == 1 and x.paid_indicator and (x.driver_in_force  or x.driver is None)]),
            'vehicle_claim_time_since_ubi': min_with_none([x.how_old for x in claims if 1 <= x.how_old <= 16 and x.ubi == 1 and x.paid_indicator and (x.driver_in_force  or x.driver is None)])
        }
        results.update(**claim_counts)

        return results
