# Application directory

Flask application functionality goes here

## APERO profile edits

The APERO Profiles editor defaults the instrument dropdown to the profile's
current instrument. Selecting another instrument and saving moves the profile
without copying it. A same-named profile at the destination blocks the move
instead of being overwritten. Cancel leaves the profile where it was.

The save endpoint accepts `original_instrument` for edits; `instrument` is the
destination. Both locations are updated in one profile-configuration save.