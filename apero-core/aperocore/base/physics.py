import astropy.constants as cc
from astropy import units as uu

# =============================================================================
# Define variables
# =============================================================================
# Speed of light
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
speed_of_light_kms = cc.c.to(uu.km / uu.s).value