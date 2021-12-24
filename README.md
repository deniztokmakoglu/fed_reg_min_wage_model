# Examining the Federal Minimum Wage
## The Performance of the Federal Minimum Wage Relative to County-Level Living Wages in Illinois

## Authors
* Caton Brewster
* Jacob Jameson
* Deniz Tokmakoğlu

## Overview:
Our project evaluates how changes in a proposed federal minimum wage affect welfare relative to a living wage throughout the 102 counties of Illinois.
We use data on income and household compositions from the US Census Bureau and data on estimated living wages from MIT’s Living Wage Calculator. We account for changes in employment due to changes in the minimum wage using the US Congressional Budget Office’s (CBO’s) model, “The Effects on Employment and Family Income of Increasing the Federal Minimum Wage.”
Run “$ . /run_model.sh” from the terminal to run the project.
The user will be asked if they would like to regenerate all of the underlying data for the model (optional). The user is then prompted to enter a proposed federal minimum wage. Finally, the user is able to select from a number of visuals to view the new wage’s effect:
* Wage Comparison
* Percent Affected by New Wage
* Effectiveness of New Wage Relative to Conservative Living Wage
* Difference in New Wage and Conservative Living Wage
* Difference in New Wage and Generous Living Wage
* Unemployment Repercussions
The user will continue to be prompted to view visuals during which they can enter “8” to exit the program.

## Goals & Findings:
Our goal was to understand the effect of a federal minimum wage relative to a county-dependent minimum wage that accounts for cost of living.
Assumption made due to limitations in data access:
* A linear distribution of income within each income bracket in a county
* Predicted unemployment rate from new federal minimum wage constant in each county
* Any unemployed incurred only affects minimum wage workers
* Two versions of living wage per county:
* Conservative Lower Bound: assumes 2 workers per households and remaining members dependent
* Generous Upper Bound: assumes 1 worker per households and remaining members dependent

We found that a federal minimum wage of $15 would result in many counties having a minimum wage above their conservative living wage, 
leading to higher unemployment relative to what it would be at the living wage, while other counties would have people earning below their living wage. 
If we assumed household compositions in line with our upper bound living wage, all counties remain below the living wage when the federal minimum wage is $15. 
While additional robustness checks are recommended, our analysis suggests that setting the minimum wage relative to cost of living would be better than a fixed 
federal minimum wage.

## Software Structure:
