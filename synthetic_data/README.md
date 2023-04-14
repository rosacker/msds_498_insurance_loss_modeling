# Data Generator

A main challenge in this project is finding appropriate data. The type of data that would ideally be used is not freely available publicly. For that reason, we decided to instead make synthetic data. This folder of the project captures the python scripts used to build that data.

## High Level Class Structure

```mermaid
graph TD;
household[Household]
human[Human] --> child[Child] & spouse[Spouse] & head_of_house[Head of House]
household <|Members of|-- human
spouse <|Married To|-- head_of_house
child <|Raised By|-- spouse & head_of_house
household --|Owns|> vehicle[Vehicle] & housing_property[Housing Property]
claims[Claims] <|Cause|-- vehicle & human

```