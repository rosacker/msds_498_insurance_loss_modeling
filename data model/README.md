# Data Model

## Conceptual

The major concepts in this data model are as follows:
+ A household entity - captures all the relationships together for a auto insurance rating "customer". All data used to rate the policy needs to link to this object because this captures what data is available as of a snapshot date for the household.
+ A vehicle entity - This captures the vehicles being insured by the company. Each vehicle insured in the household has one row in this table (hence 1 to many relationship with households)
+ A driver entity - Each household has 1 to many human drivers of the vehicles within the household. This entity captures information about each driver such as their age and how long they've been insured.
+ A claims entity - This captures data about any prior insurance claims that have occured in the household. This includes linking the claim to vehicles (there must be exactly 1 vehicle per claim) and drivers (there can be 0 or 1 drivers assigned as "involved" in the claim).
+ Other Insurance Products - This relationship captures other products (such as homeowners products or umbrella policies) that the household may have with the company. These are used to offer "multi-line discounts". 

<img src="./Conceptual Data Model.svg">

## Logical

Moving to the logical diagram, there isn't much for surprising decisions. 

+ Each entity is captured as a seperate table.
+ Data types are mostly string, int, bool or date. There are no complex types.

<img src="./Logical Data Model.svg">

## Physical

With the physical plan, we decided to model the data in Amazon Redshift. Redshift was chosen for a few reasons:
+ Many major insurance companies are moving towards AWS, which meant picking an Amazon product was critical.
+ It follows the traditional relational database design. This will be useful for insolating legacy systems that may need to interact with this database.
+ Redshift integrates easily with BI tools such as Quicksight which will help to enable analytics in this data.
+ Redshift can scale to arbitrary scales which is needed for insurance companies which may have 50 million households worth of data that need to fit into the architecture.

<img src="./Physical Data Model.svg">