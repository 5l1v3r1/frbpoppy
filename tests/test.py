"""Short example of how frbpoppy works."""
from frbpoppy import CosmicPopulation, Survey, SurveyPopulation, plot

PLOT = True

# Generate an FRB population
cosmic_pop = CosmicPopulation(10000, days=7, name='example')

# Setup a survey
survey = Survey('apertif')

# Observe the FRB population
survey_pop = SurveyPopulation(cosmic_pop, survey)

# Check the detection rates
print(survey_pop.rates())

# Plot populations
if PLOT:
    plot(cosmic_pop, survey_pop, mute=False)