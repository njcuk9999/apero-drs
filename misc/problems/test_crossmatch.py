from astroquery.utils.tap.core import TapPlus
import warnings

# get the URL
URL = "https://gea.esac.esa.int/tap-server/tap"

# Must be on one line
QUERY = "SELECT ra as ra, dec as dec, source_id as gaiaid, parallax as plx, pmdec as pmde, pmra as pmra, radial_velocity as rv, phot_g_mean_mag as gmag, phot_bp_mean_mag as bpmag, phot_rp_mean_mag as rpmag FROM gaiadr2.gaia_source WHERE 1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 154.90116999999998, 19.87000388888889, 0.016666666666666666)) AND (parallax is not NULL) AND (pmdec is not NULL) AND (pmra is not NULL) AND (phot_rp_mean_mag < 15.0) AND (parallax > 5.0)"


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # run tap query
    with warnings.catch_warnings(record=True) as _:
        # construct gaia TapPlus instance
        gaia = TapPlus(url=URL)
        # launch gaia job
        job = gaia.launch_job(query=QUERY)
        # get gaia table
        table = job.get_results()

    # -------------------------------------------------------------------------
    # print results
    if len(table) == 0:
        print("No entries found for query")
    else:
        if len(table) == 1:
            print("Found 1 Entry")
        else:
            print("Found {0} Entries".format(len(table)))
        print("Columns found:")
        for col in table.colnames:
            print('\tColumn {0}'.format(col))
            print('\t\t Units: {0}'.format(table[col].unit))
            print('\t\t Data type: {0}'.format(table[col].dtype))

            if len(table[col]) > 0:
                print('\t\t Value[0]: {0}'.format(table[col][0]))


# =============================================================================
# End of code
# =============================================================================
