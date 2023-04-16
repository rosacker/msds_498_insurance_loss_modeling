# Data Generator

A main challenge in this project is finding appropriate data. The type of data that would ideally be used is not freely available publicly. For that reason, we decided to instead make synthetic data. This folder of the project captures the python scripts used to build that data.

## Entity-Relationship Diagram 

<img src="./ER Diagram for Data.svg">

## High Level Class Structure

```mermaid
graph TD;
household[Household]
human[Human] -->|Subclass Of| child[Child] & spouse[Spouse] & head_of_house[Head of House]
household --> |includes| human
head_of_house -->|Married To| spouse
spouse & head_of_house -->|Raised By| child

household -->|Owns| vehicle[Vehicle] & housing_property[Housing Property]
human & vehicle -->|cause| claim[Claims]
household -->|Has History Of| claim

```

## To Do  

- [x] Rebalance the driver hazard attribute to be normally distributed  
- [x] Rebalance relationship between risk scores
- [ ] Add process for a household buying cars  
- [ ] Add process for a household selling cars  
- [ ] Add process for determining how many miles each person drives  
- [ ] Add process for determining which vehicle is driven  
- [ ] Add process for household picking insurance coverages  
- [ ] Add "insurance coverage at the time" to claims data  
- [ ] Write coverage specific logic for determining when claims occur  
- [ ] Build way to export data to Weights & Bias  
- [ ] Build way to export data at multiple levels (household, vehicle, all claims, etc)  
- [ ] Fix apparent defect with some "other vehicle" claims not coming through.  
- [ ] Write metadata on all fields  
- [ ] Run code profiler and figure out if anything is running too much
