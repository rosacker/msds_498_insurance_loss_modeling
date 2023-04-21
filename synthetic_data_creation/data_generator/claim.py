import random
from statistics import mean
from .utils import sig
from uuid import uuid4


class claim:
    """
    This represents an insurance claim occuring. 
    An insurance claim must relate to a vehicle object. 
    It may or may not have a driver (i.e. a car can get hit by hail without anyone actively driving it!)
    """

    def __init__(self, claim_type, household, vehicle, driver=None):
        self.household = household
        self.vehicle = vehicle
        self.vehicle_id = vehicle.id
        self.driver = driver

        if self.driver is not None:
            self.driver_id = driver.id
        else:
            self.driver_id = None

        self.id = uuid4().hex

        self.when_occured = self.household.tenure_years
        
        self.veh_had_bi_cov_ind = self.vehicle.bi_cov_ind
        self.veh_had_pd_cov_ind = self.vehicle.pd_cov_ind
        self.veh_had_coll_cov_ind = self.vehicle.coll_cov_ind
        self.veh_had_comp_cov_ind = self.vehicle.comp_cov_ind
        self.veh_had_mpc_cov_ind = self.vehicle.mpc_cov_ind
        self.veh_had_ers_cov_ind = self.vehicle.ers_cov_ind
        self.veh_had_ubi_cov_ind = self.vehicle.ubi_cov_ind

        if claim_type == 'single_car_collision':
            self.build_single_car_collision()
        elif claim_type == 'multi_car_collision':
            self.build_multi_car_collision()
        elif claim_type == 'theft':
            self.build_theft()
        elif claim_type == 'hail':
            self.build_hail()
        elif claim_type == 'glass':
            self.build_glass()
        elif claim_type == 'ubi':
            self.build_ubi()
        elif claim_type == 'ers':
            self.build_ers()

    def build_single_car_collision(self):
        crash_type = random.choices(['tree', 'fence', 'parked_car', 'pedestrian'], [0.4, 0.3, 0.2, 0.1])[0]
        protection = self.vehicle.protection
        hurt_others = self.vehicle.hurt_others
        income = self.household.annual_income

        if hurt_others == 1:
            mult = 0.8
        elif hurt_others == 3:
            mult = 1.2
        else: 
            mult = 1

        p = {'pedestrian': 0.9, 'parked_car': 0.3 * mult}
        p = p.get(crash_type, 0)
        self.bi = int(p > random.uniform(0, 1) and self.veh_had_bi_cov_ind)

        p = {'pedestrian': 0.05, 'parked_car': 0.9 * mult, 'fence': 0.9, 'tree': 0.05}
        p = p.get(crash_type, 0)
        self.pd = int(p > random.uniform(0, 1) and self.veh_had_pd_cov_ind)

        p = {'parked_car': 0.85, 'fence': 0.15, 'tree': 0.9, 'pedestrian': 0.15}
        p = p.get(crash_type, 0)
        if income > 150_000:
            mult = 0.8
        elif income > 120_000:
            mult = 0.85
        elif income > 90_000:
            mult = 0.9
        else:
            mult = 1
        self.coll = int(mult * p > random.uniform(0, 1) and self.veh_had_coll_cov_ind)

        self.comp = 0

        p = {'parked_car': 0.3, 'tree': 0.8}
        p = p.get(crash_type, 0.05)
        if protection == 1:
            mult = 1.2
        elif protection == 3:
            mult = 0.8
        else: 
            mult = 1

        self.mpc = int(mult * p > random.uniform(0, 1) and self.veh_had_mpc_cov_ind)

        self.ers = 0
        self.ubi = 0

    def build_multi_car_collision(self):
        crash_type = random.choices(['fender_bender', 'serious'], [0.5, 0.5])[0]        
        protection = self.vehicle.protection
        hurt_others = self.vehicle.hurt_others
        income = self.household.annual_income

        if hurt_others == 1:
            mult = 0.8
        elif hurt_others == 3:
            mult = 1.2
        else: 
            mult = 1

        p = {'fender_bender': 0.05, 'serious': 0.6}
        p = p.get(crash_type, 0)
        self.bi = int(p*mult > random.uniform(0, 1) and self.veh_had_bi_cov_ind)

        p = {'fender_bender': 0.35 * mult, 'serious': 0.95}
        p = p.get(crash_type, 0)
        self.pd = int(p > random.uniform(0, 1) and self.veh_had_pd_cov_ind)

        if income > 150_000:
            mult = 0.5
        elif income > 120_000:
            mult = 0.6
        elif income > 90_000:
            mult = 0.7
        else:
            mult = 1

        p = {'fender_bender': 0.3 * mult, 'serious': 0.95}
        p = p.get(crash_type, 0)

        self.coll = int(p > random.uniform(0, 1) and self.veh_had_coll_cov_ind)

        self.comp = 0

        p = {'fender_bender': 0.05, 'serious': 0.6}
        p = p.get(crash_type, 0.05)

        if protection == 1:
            mult = 1.2
        elif protection == 3:
            mult = 0.8
        else: 
            mult = 1

        self.mpc = int(mult * p > random.uniform(0, 1) and self.veh_had_mpc_cov_ind)

        self.ers = 0
        self.ubi = 0

    def build_theft(self):
        self.bi = 0
        self.pd = 0
        self.coll = 0

        income = self.household.annual_income
        if income > 150_000:
            mult = 0.5
        elif income > 120_000:
            mult = 0.6
        elif income > 90_000:
            mult = 0.7
        else:
            mult = 1

        # Check if the vehicle was garaged at the time!
        garages = self.household.garage_count
        veh_cnt = len(self.household.vehicles)
        if garages > veh_cnt:
            mult *= 0.25
        elif garages > 0:            
            mult *= 1 - 0.75 * (1.0 * veh_cnt/garages)

        self.comp = int(mult * 1 > random.uniform(0, 1) and self.veh_had_comp_cov_ind)
        self.mpc = 0
        self.ers = 0
        self.ubi = 0

    def build_hail(self):
        self.bi = 0
        self.pd = 0
        self.coll = 0

        income = self.household.annual_income
        if income > 150_000:
            mult = 0.5
        elif income > 120_000:
            mult = 0.6
        elif income > 90_000:
            mult = 0.7
        else:
            mult = 1

        # Check if the vehicle was garaged at the time!
        garages = self.household.garage_count
        veh_cnt = len(self.household.vehicles)
        if garages > veh_cnt:
            mult *= 0.25
        elif garages > 0:    
            mult *= 1 - 0.75 * (1.0 * veh_cnt/garages)

        self.comp = int(mult * 1 > random.uniform(0, 1) and self.veh_had_comp_cov_ind)

        self.mpc = 0
        self.ers = 0
        self.ubi = 0

    def build_glass(self):
        
        income = self.household.annual_income
        if income > 150_000:
            mult = 0.2
        elif income > 120_000:
            mult = 0.4
        elif income > 90_000:
            mult = 0.6
        elif income > 70_000:
            mult = 0.8
        else:
            mult = 1

        self.bi = 0
        self.pd = 0
        self.coll = 0

        self.comp = int(mult * 1 > random.uniform(0, 1) and self.veh_had_comp_cov_ind)

        self.mpc = 0
        self.ers = 0
        self.ubi = 0

    def build_ubi(self): 
        protection = self.vehicle.protection
        crash_type = random.choices(['fender_bender', 'serious'], [0.5, 0.5])[0]
        income = self.household.annual_income

        self.bi = 0
        self.pd = 0

        if income > 150_000:
            mult = 0.5
        elif income > 120_000:
            mult = 0.6
        elif income > 90_000:
            mult = 0.7
        else:
            mult = 1

        p = {'fender_bender': 0.2 * mult, 'serious': 0.8}
        p = p.get(crash_type, 0)

        self.coll = int(p > random.uniform(0, 1) and self.veh_had_coll_cov_ind)

        self.comp = 0
        self.mpc = 0
        self.ers = 0

        if protection == 1:
            mult = 1.2
        elif protection == 3:
            mult = 0.8
        else: 
            mult = 1

        p = {'fender_bender': 0.3, 'serious': 0.8}
        p = p.get(crash_type, 0)
        
        self.ubi = int(p * mult > random.uniform(0, 1) and self.veh_had_ubi_cov_ind)

    def build_ers(self):

        if self.driver.gender == 'm':
            p = 0.7        
        elif self.driver.gender == 'f':
            p = 0.85     
        
        self.ers = int(p > random.uniform(0, 1) and self.veh_had_ubi_cov_ind)
    
        self.bi = 0
        self.pd = 0
        self.coll = 0
        self.comp = 0
        self.mpc = 0
        self.ubi = 0

    @property
    def summary(self):
        results = {
            'claim_id': self.id,
            'vehicle_id': self.vehicle_id,
            'driver_id': self.driver_id,
            'driver_claim': self.driver_id is not None,
            'bi_ind': self.bi,
            'pd_ind': self.pd,
            'coll_ind': self.coll,
            'comp_ind': self.comp,
            'mpc_ind': self.mpc,
            'ers_ind': self.ers,
            'ubi_ind': self.ubi,
            'claim_age': self.how_old # Subtract 1 so subsequent claims would be 0
        }

        return results

    @property
    def vehicle_in_force(self):
        return any(self.vehicle == x for x in self.household.vehicles)

    @property
    def driver_in_force(self):
        if self.driver is None or self.household.drivers is None:
            return False

        return self.driver.inforce

    @property
    def how_old(self):
        return self.household.tenure_years - self.when_occured
    
    @property
    def paid_indicator(self):
        return (self.bi + self.pd + self.coll + self.comp + self.mpc + self.ers + self.ubi) > 0
