# Country Boundaries

`countries.geojson` contains Natural Earth's 1:110m Admin 0 country polygons.
The original geometry is unchanged; properties are reduced to the country name
and ISO alpha-2 code (`ISO_A2_EH`, falling back to `ISO_A2`). These small-scale
boundaries are for aggregate visualization, not legal boundary interpretation.

Source: https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson

Downloaded: 2026-11-11. Natural Earth data is public domain:
https://www.naturalearthdata.com/about/terms-of-use/

The map uses these local polygons with Bokeh; it makes no external tile or
geolocation requests. Small territories absent at this scale still appear in
the country/region tables. Unknown locations are included in tables, not mapped.

# Time Zone Coordinates

`zone.tab` is the IANA time zone database's public-domain table of
representative coordinates, from tzdb 2026c. The clocks page uses it to place
configured time zones on its world map. Coordinates represent the time zone's
reference location, not necessarily the named clock's exact location.

Source: https://data.iana.org/time-zones/tzdb/zone.tab