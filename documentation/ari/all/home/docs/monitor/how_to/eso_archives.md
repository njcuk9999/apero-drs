---
card_label: ESO Archive
card_icon: fa-solid fa-circle-question
---

# How to check for data on the ESO Archives

## Step 1

Open the archive page:

- Public: http://archive.eso.org/eso/eso_archive_main.html
- Special access (GTO): https://archive.eso.org/wdb/forms/cas/eso_archive_main.html

![ESO archive whole page](/doc-images/eso_archive_whole_page.png)

## Step 2

Set the observation night (or start/end range).

To remove solar observations, set `Target Name` to `not SUN` and select
`OBJECT - FITS keyword`.

![ESO archive night box](/doc-images/eso_archive_night_box.png)

## Step 3

Enable instrument filter for NIRPS/La Silla and run search.

![ESO archive instrument filter](/doc-images/eso_archive_inst_box.png)

## Useful filters

- In `Data Product Info`, enable `OB Name` and `Category` (SCIENCE/CALIB)
	when needed.
- Increase `Return max` above 200 rows when doing broad searches.

![ESO archive data info](/doc-images/eso_archive_data_info.png)
![ESO archive row limit](/doc-images/eso_archive_nrows.png)