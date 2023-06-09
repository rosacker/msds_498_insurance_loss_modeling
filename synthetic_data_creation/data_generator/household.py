import random
#from numpy.random import poisson
from statistics import mean
from math import sqrt
from uuid import uuid4

from .utils import sig, poisson

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
        self.driviness = random.normalvariate(1, 0.2)
        self.child_interest = random.choices([0, 1, 2, 3, 4, 5], [0.10, 0.15, 0.3, 0.3, 0.1, 0.05])[0]
        self.children = []
        self.properties = []
        self.claims = []
        self.vehicles = []
        self.significant_other = None
        self.head_of_household = head_of_house(self)
        self.head_of_household.start_life(self)
        self.tenure_years = 0
        self.update_house()
        self.update_vehicles()


        # Have to come up with how long they've owned the car!
        for veh in self.vehicles:
            if veh.age == 0:
                veh.years_owned = 0
            
            else:
                veh.years_owned = int(random.randint(0, veh.age))   

    def __hash__(self):
        return hash(self.id)

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

            if not self.inforce:
                return None
            
            if 0.5 < random.uniform(0, 1):
                    self.update_vehicles()
            
            self.generate_claims()


    def generate_claims(self):
        mileage = self.determine_mileage()

        for key, mileage in mileage.items():
            driver, veh, road_type = key

            driving_hazard = driver.driving_hazard

            hazards = {
                'single_car_collision': (
                    0.03 * sqrt(mileage/10000) *
                    (0.5 if road_type == 'highway' else 1) *
                    (driving_hazard ** 0.9) *
                    min(1, 1 + 0.01 * (veh.age - 5))
                ),
                'multi_car_collision': (
                    0.03 * sqrt(mileage/10000) *
                    (0.25 if road_type == 'highway' else 1) *
                    (driving_hazard) *
                    min(1, 1 + 0.0125 * (veh.age - 5))
                ),
                'theft': (
                    0.01 * sqrt(mileage/10000) *
                    (0.05 if road_type == 'highway' else 1) *
                    (driving_hazard ** 0.1) *
                    (1.5 if veh.household.primary_house.location == 'downtown' else 1)
                ),
                'hail': (                    
                    0.01 * sqrt(mileage/10000) *
                    (1.3 if road_type == 'highway' else 1) *
                    (driving_hazard ** 0.1) *
                    (0.6 if veh.household.primary_house.location == 'downtown' else 1)
                ),
                'glass': (
                    0.03 * sqrt(mileage/10000) *
                    (2.1 if road_type == 'highway' else 1) *
                    (driving_hazard ** 0.1)
                ),
                'ubi': (
                    0.03 * sqrt(mileage/10000) *
                    (0.3 if road_type == 'highway' else 1) *
                    (driving_hazard ** 0.4)
                ),
                'ers': (
                    0.03 * sqrt(mileage/10000) *
                    (1.5 if road_type == 'highway' else 1) *
                    (driving_hazard ** 0.3) *
                    min(1, 1 + 0.005 * veh.age + 0.1 * max(veh.age - 7, 0) + 0.1 * max(veh.age - 12, 0) - 0.1 * max(veh.age - 17, 0) - 0.05 * max(veh.age - 21, 0))
                ),
            }

            hazard_rates = list(hazards.values())
            claim_types = list(hazards.keys())
            #n = poisson(hazard_rates)
            n = [poisson(x) for x in hazard_rates]

            for i in range(len(n)):
                claim_type = claim_types[i]
                count = n[i]

                if count > 0:
                    for _ in range(count):
                        if claim_type in ['theft', 'hail']:
                            assigned_driver = None
                        else:
                            assigned_driver = driver

                        self.claims.append(claim(claim_type, self, vehicle=veh, driver=assigned_driver))
            
    def determine_mileage(self):
        mileage = {}

        veh_assigments = self.determine_veh_assignements()

        for driver in self.drivers:
            city_mileage, highway_mileage = driver.determine_mileage()

            for veh in self.vehicles:           
                allocation = veh_assigments[(driver, veh)]

                mileage.update({
                    (driver, veh, 'city'): city_mileage*allocation,
                    (driver, veh, 'highway'): highway_mileage*allocation,
                    (driver, veh, 'total'): (city_mileage+highway_mileage)*allocation,
                })

        return mileage
    
    def summarize_mileage(self, level = 'veh'):
        if level == 'veh':
            result = self.determine_mileage()
            final = {veh:0 for veh in self.vehicles}

            for key, value in result.items():
                _, veh, road_type = key
                if road_type == 'total':
                    final[veh] += value

            return final
        
        elif level == 'drv':
            result = self.determine_mileage()
            final = {drv:0 for drv in self.drivers}

            for key, value in result.items():
                driver, _, road_type = key
                if road_type == 'total':
                    final[driver] += value

            return final
    
    def determine_veh_assignements(self, vehicles = None):
        pick_nth = lambda list_val, select: [list_val.index(i) for i in sorted(list_val, reverse=True)][:select][0]

        vehicles = vehicles if vehicles is not None else self.vehicles
        veh_cnt = len(vehicles) 

        if len(vehicles) == 1:
            # Everyone drives that car
            return {
                (driver, veh): 1
                for driver in self.drivers
                for veh in vehicles
            }

        if self.significant_other is None:
            # Driver gets to drive everything, find their favorite
            head_of_house_preferences = [self.head_of_household.vehicle_interest(veh, vehicles) for veh in vehicles]             
            
            first_pick = pick_nth(head_of_house_preferences, 1)  
            if veh_cnt == 2:
                return {
                    (driver, veh): 0.85 if i == first_pick else 0.15
                    for driver in self.drivers
                    for i, veh in enumerate(vehicles)
                }
            else:
                second_pick = pick_nth(head_of_house_preferences, 2)
                rest = 0.05/(veh_cnt - 2)

                return {
                    (driver, veh): 0.85 if i == first_pick else (0.1 if i == second_pick else rest)
                    for driver in self.drivers
                    for i, veh in enumerate(vehicles)
                }

        else:
            # Got to pick which driver gets each car. Start by calculating the parents to their top 2 fav cars

            hoh_preferences = [self.head_of_household.vehicle_interest(veh, vehicles) for veh in vehicles]
            so_preferences = [self.significant_other.vehicle_interest(veh, vehicles) for veh in vehicles]

            hoh_first_pick = pick_nth(hoh_preferences, 1) 
            so_first_pick = pick_nth(so_preferences, 1)
            hoh_second_pick = pick_nth(hoh_preferences, 2) 
            so_second_pick = pick_nth(so_preferences, 2)

            if hoh_first_pick != so_first_pick:
                best_hoh_pick = hoh_first_pick
                best_so_pick = so_first_pick
            else:
                # Figure out who has to use their second fav car based on aggregate happiness
                score_1 = hoh_preferences[hoh_first_pick] + so_preferences[so_second_pick]
                score_2 = hoh_preferences[hoh_second_pick] + so_preferences[so_first_pick]

                if score_1 >= score_2:
                    best_hoh_pick = hoh_first_pick
                    best_so_pick = so_second_pick
                else:                    
                    best_hoh_pick = hoh_first_pick
                    best_so_pick = so_second_pick

        rest = 0.15/(veh_cnt - 1)        
        result = {
                    (self.head_of_household, veh): 0.85 if i == best_hoh_pick else rest
                    for i, veh in enumerate(vehicles)
                }
        
        result.update({
                    (self.significant_other, veh): 0.85 if i == best_so_pick else rest
                    for i, veh in enumerate(vehicles)
                })      

        if self.driver_count > 2:
            claimed_cars = [best_hoh_pick, best_so_pick]
            
            other_drivers = [driver for driver in self.children if driver.is_driving_age]
           
            preferences = [[x.vehicle_interest(veh, vehicles) ** 2 if i not in claimed_cars else (0.75 * x.vehicle_interest(veh, vehicles)) ** 2
                                for i, veh in enumerate(vehicles)] 
                                for x in other_drivers]
            balanced_preferences = [[x/sum(y) for x in y] for y in preferences]                
            sum_of_veh_pref = [sum(x[i] for x in preferences) for i in range(veh_cnt)]

            allocated_preferences = [[x/sum_of_veh_pref[i] for i, x in enumerate(y)] for y in balanced_preferences]
            final_preferences = [[x/sum(y) for x in y] for y in allocated_preferences]

            for i, x in enumerate(other_drivers):
                pref = final_preferences[i]
                result.update({
                                (x, veh): pref[j]
                                for j, veh in enumerate(vehicles)
                            })
                
        return result

    def remove_child(self, removal_child):
        """Remove a child when they get to an old enough age"""

        removal_child.inforce = False
        self.children = [x for x in self.children if x != removal_child]

    def generate_veh_list_from_scratch(self, n):
        vehicles = []

        for i in range(n):    
            age = int(random.triangular(0, 25, 5))
            vehicle_type = random.choice(['pickup', 'suv', 'sedan', 'sports car', 'van'])
            vehicles.append(vehicle(self, age, vehicle_type))
        
        return frozenset(vehicles)
    
    def generate_veh_list(self, add_car, remove_car_n):
        vehicles = self.vehicles.copy()
        
        if remove_car_n > 0:
            for i in range (remove_car_n):
                if len(vehicles) == 1:
                    break
                ids = len(vehicles)
                id = random.choice(range(ids))
                vehicles = [x for i, x in enumerate(vehicles) if i != id]

        # Randomly add 1 car
        if add_car:
            age = int(random.uniform(0, 25))
            vehicle_type = random.choice(['pickup', 'suv', 'sedan', 'sports car', 'van'])

            vehicles.append(vehicle(self, age, vehicle_type))
        
        return frozenset(vehicles)

    def evaluate_new_vehicles(self, vehicles):
        if len(vehicles) == 0:
            return -1000
        
        cost = 12 * sum([x.monthly_cost for x in vehicles])        
        excess_cost = (cost - self.annual_income * 0.2 * 0.7)
        if excess_cost >= 0:
            return -500
                
        drivers = self.drivers
        if abs(len(drivers) - len(vehicles)) > 2:
            return -250
        
        prefs = {(driver, veh): driver.vehicle_interest(veh, vehicles) for veh in vehicles for driver in drivers}
        allocation = self.determine_veh_assignements(vehicles)

        match_score = 0
        for key, value in prefs.items():
            driver, veh = key
            match_score += value * allocation[key]

        if len(drivers) != len(vehicles):
            match_score += -1.0 * (len(drivers) - len(vehicles)) ** 2

        # No one likes a giant army of matching cars
        unique_types = len(set([x.vehicle_type for x in vehicles]))
        if unique_types < len(vehicles):
            match_score += 0.5 * (unique_types - len(vehicles))

        return match_score
    
    def update_vehicles(self):       
        cnt = self.driver_count 

        # Probability of picking up coverages varies by risk mitigation score
        p_major = 0.5 + 0.5 * sig(self.head_of_household.risk_mitigation_score/5)
        p_minor = 0.3 + 0.6 * sig(self.head_of_household.risk_mitigation_score/5)

        if len(self.vehicles) == 0:
            coverages = {
                'bi' : True,
                'pd' : True,
                'coll' : p_major > random.uniform(0, 1),
                'comp' : p_major > random.uniform(0, 1),
                'mpc' : p_minor > random.uniform(0, 1),
                'ers' : p_minor > random.uniform(0, 1),
                'ubi' : p_minor > random.uniform(0, 1)
            }

            if self.driver_count <= 1:
                options = [
                    *[self.generate_veh_list_from_scratch(1) for i in range(10)],
                    *[self.generate_veh_list_from_scratch(2) for i in range(10)]
                ]
            else:
                options = [
                    *[self.generate_veh_list_from_scratch(cnt - 1) for i in range(5)],
                    *[self.generate_veh_list_from_scratch(cnt) for i in range(5)],
                    *[self.generate_veh_list_from_scratch(cnt + 1) for i in range(5)],
                ]

        else:
            vehicles = self.vehicles            
            
            coverages = {
                'coll' : any([x.coll_cov_ind > 0 for x in vehicles]),
                'comp' : any([x.comp_cov_ind > 0 for x in vehicles]),
                'mpc' : any([x.mpc_cov_ind > 0 for x in vehicles]),
                'ers' : any([x.ers_cov_ind > 0 for x in vehicles]),
                'ubi' : any([x.ubi_cov_ind > 0 for x in vehicles])
            }

            # Decide if we want to modify any of the coverages randomly
            p_upgrade = 0.12 * sig(self.head_of_household.risk_mitigation_score/5)
            p_downgrade = 0.05 - 0.05 * sig(self.head_of_household.risk_mitigation_score/5)
            coverages = {key: False if p_downgrade > random.uniform(0, 1) else value for key, value in coverages.items()}
            coverages = {key: value | (p_upgrade > random.uniform(0, 1)) for key, value in coverages.items()}
 
            # Mandatory!
            coverages['bi'] = True
            coverages['pd'] = True

            options = [
                frozenset(self.vehicles), 
                *[self.generate_veh_list(add_car = True, remove_car_n = 0) for i in range(5)],
                *[self.generate_veh_list(add_car = True, remove_car_n = 1) for i in range(3)],
                *[self.generate_veh_list(add_car = True, remove_car_n = 2) for i in range(3)],
                *[self.generate_veh_list(add_car = False, remove_car_n = 1) for i in range(3)],
                *[self.generate_veh_list(add_car = False, remove_car_n = 2) for i in range(1)],
                *[self.generate_veh_list(add_car = False, remove_car_n = 3) for i in range(1)],
                ]

        options = [list(x) for x in set(options)]
        scores = [self.evaluate_new_vehicles(x) for x in options]
        best_score = [scores.index(i) for i in sorted(scores, reverse=True)][:1][0]

        # If there are no good veh options, just buy a few crappy sedan I guess :P 
        if best_score < -100:
            self.vehicles = [vehicle(self, 'sedan', 20) for i in range(max(cnt, 1))]
        new_vehicles = options[best_score]

        for veh in new_vehicles:
            veh.bi_cov_ind = coverages['bi']
            veh.pd_cov_ind = coverages['pd']
            veh.coll_cov_ind = coverages['coll']
            veh.comp_cov_ind = coverages['comp']
            veh.mpc_cov_ind = coverages['mpc']
            veh.ers_cov_ind = coverages['ers']
            veh.ubi_cov_ind = coverages['ubi']

        self.vehicles = options[best_score]

    def update_house(self):
        if len(self.properties) <= 1:
            house_1 = housing_property(1, self)
            house_2 = housing_property(2, self)
            house_3 = housing_property(3, self)

            # A healthy financial siution is housing costs no more than 30% of take home pay
            # Gotta take 20% off the top for taxes first!
            # Gotta take another 10% for savings

            if 0.20 * self.monthly_income * 0.7 >= house_3.monthly_cost + house_2.monthly_cost:
                # Congrats on the vacation home you crazy people that make way too much money               
                house_2.is_primary = False
                self.properties = [house_3, house_2]
            elif 0.3 * self.monthly_income * 0.7 >= house_3.monthly_cost:
                self.properties = [house_3]
            elif 0.3 * self.monthly_income * 0.7 >= house_2.monthly_cost:
                self.properties = [house_2]
            else:
                self.properties = [house_1]
    
    def household_lapse_check(self):
        hh_age = self.head_of_household.age

        # Let's keep the households in the 2 digit ages
        if hh_age >= 99:
            self.inforce = False
            return None

        # Low credit score individuals will shop more
        score = self.credit_score
        if score <= 500:
            p = 0.10
        elif score <= 600:
            p = 0.05
        elif score <= 700:
            p = 0.025
        else:
            p = 0.01

        # General mortality
        if hh_age > 75:
            p += ((hh_age - 75)/95) ** 2

        if p > random.uniform(0, 1):
            self.inforce = False

    @property
    def summary(self):
        claims = [x for x in self.claims if (x.driver_in_force or x.driver is None) and x.how_old != 0 and x.paid_indicator]

        results = {
            'household_id': self.id,
            'inforce': self.inforce,
            'household_tenure': self.tenure_years,
            'min_driver_tenure': self.min_driver_tenure,
            'max_driver_tenure': self.max_driver_tenure,
            'driver_count': self.driver_count,
            'vehicle_count': self.vehicle_count,
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
            'claims_info': [x.summary for x in claims],
            'garaging_location': self.garaging_location
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
            f'household_claim_cnt_all_{age}': len([x for x in claims if x.how_old == age and x.paid_indicator])
            for age in range(1, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'household_claim_cnt_bi_{age}': len([x for x in claims if x.how_old == age and x.bi == 1 and x.paid_indicator])
            for age in range(1, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'household_claim_cnt_pd_{age}': len([x for x in claims if x.how_old == age and x.pd == 1 and x.paid_indicator])
            for age in range(1, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'household_claim_cnt_coll_{age}': len([x for x in claims if x.how_old == age and x.coll == 1 and x.paid_indicator])
            for age in range(1, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'household_claim_cnt_comp_{age}': len([x for x in claims if x.how_old == age and x.comp == 1 and x.paid_indicator])
            for age in range(1, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'household_claim_cnt_mpc_{age}': len([x for x in claims if x.how_old == age and x.mpc == 1 and x.paid_indicator])
            for age in range(1, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'household_claim_cnt_ers_{age}': len([x for x in claims if x.how_old == age and x.ers == 1 and x.paid_indicator])
            for age in range(1, 16)
        }
        results.update(**claim_counts)

        claim_counts = {
            f'household_claim_cnt_ubi_{age}': len([x for x in claims if x.how_old == age and x.ubi == 1 and x.paid_indicator])
            for age in range(1, 16)
        }
        results.update(**claim_counts)

        # Time Since Claim
        def min_with_none(x): return min(x) if len(x) > 0 else None
        claim_counts = {
            'household_claim_time_since_all': min_with_none([x.how_old for x in claims if 1 <= x.how_old <= 16]),
            'household_claim_time_since_bi': min_with_none([x.how_old for x in claims if 1 <= x.how_old <= 16 and x.bi == 1]),
            'household_claim_time_since_pd': min_with_none([x.how_old for x in claims if 1 <= x.how_old <= 16 and x.pd == 1]),
            'household_claim_time_since_comp': min_with_none([x.how_old for x in claims if 1 <= x.how_old <= 16 and x.comp == 1]),
            'household_claim_time_since_coll': min_with_none([x.how_old for x in claims if 1 <= x.how_old <= 16 and x.coll == 1]),
            'household_claim_time_since_mpc': min_with_none([x.how_old for x in claims if 1 <= x.how_old <= 16 and x.mpc == 1]),
            'household_claim_time_since_ers': min_with_none([x.how_old for x in claims if 1 <= x.how_old <= 16 and x.ers == 1]),
            'household_claim_time_since_ubi': min_with_none([x.how_old for x in claims if 1 <= x.how_old <= 16 and x.ubi == 1])
        }
        results.update(**claim_counts)

        return results

    @property
    def summary_per_vehicle(self):
        results = self.summary
        claims_info = results.pop('claims_info')
        vehicle_info = results.pop('vehicle_info')
        mileage_info = self.summarize_mileage('veh')

        selection = ['vehicle_id', 'vehicle_age', 'vehicle_years_owned', 'vehicle_type']
        household_vehicle_info = [
            {key:value for key,value in x.items() if key in selection}
            for x in vehicle_info
            ]

        summary = [dict(results,
                        **x,
                        annual_mileage = max(1000, round([value for key, value in mileage_info.items() if key.id == x['vehicle_id']][0], -3) + 
                                             random.choices([-2000, -1000, 0, 1000, 2000], [0.1, 0.2, 0.3, 0.2, 0.1])[0]
                                             ),
                        vehicle_claims=[
                            y for y in claims_info if y['vehicle_id'] == x['vehicle_id']],
                        other_claims=[
                            y for y in claims_info if y['vehicle_id'] != x['vehicle_id']],
                        household_vehicles_info = [dict(y, this_vehicle_ind = y['vehicle_id'] == x['vehicle_id']) for y in household_vehicle_info]
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
            'best_job': max([x.job_class for x in self.household_members]),
            'hoh_education': self.head_of_household.education,
            'net_monthly': self.monthly_income - self.household_expenses,
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
    def non_driver_cnt(self):
        if len(self.children) == 0:
            return 0
        
        return len([x for x in self.children if not x.is_driving_age])

    @property
    def annual_income(self):
        x = 0
        x += self.head_of_household.annual_income

        if self.significant_other is not None:
            x+= self.significant_other.annual_income

        if len(self.children) > 0:
            x+= sum([x.annual_income for x in self.children])
            
        return x

    @property
    def monthly_income(self):
        return self.annual_income/12

    @property
    def household_expenses(self):
        cost = self.people_count * 1_000
        cost += self.monthly_income * 0.2  # darn taxes
        cost += self.monthly_income * 0.1 # savings!
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
        if len(self.properties) == 0:
            return 0
        
        return self.primary_house.garages

    @property
    def bed_count(self):
        if len(self.properties) == 0:
            return 0
        
        return self.primary_house.beds
    
    @property
    def vehicle_count(self):
        return len(self.vehicles)

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
    
    @property
    def primary_house(self):
        if len(self.properties) == 0:
            return None
        
        return [x for x in self.properties if x.is_primary][0]
    
    @property
    def garaging_location(self):
        return self.primary_house.location
