
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-07-29 at 09:10

@author: cook
"""
from aperocore.base import base
from aperocore.drs_lang import drs_lang_list


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.lang.tables.spirou_help.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# =============================================================================
# Define functions
# =============================================================================
# Get the language list
langlist = drs_lang_list.LanguageList(__NAME__)


# =============================================================================
# DRS_DESCRIPTION 
# =============================================================================
item = langlist.create('DRS_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'This is the SPIROU description message'
item.value['FR'] = 'Ceci est le message de description SPIROU'
item.value['ES'] = 'Este es el mensaje de descripción de SPIROU'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# OBS_DIR_HELP
# =============================================================================
item = langlist.create('OBS_DIR_HELP', kind='HELP')
item.value['ENG'] = ('[STRING] The directory to find the data files in. '
                     'Most of the time this is organised by nightly '
                     'observation directory')
item.value['FR'] = ('[STRING] Le répertoire où trouver les fichiers de '
                    'données. Le plus souvent organisé par répertoire '
                    "d'observation nocturne")
item.value['ES'] = ('[STRING] El directorio donde encontrar los archivos de '
                    'datos. Normalmente organizado por directorio de '
                    'observación nocturna')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# BACKSUB_HELP 
# =============================================================================
item = langlist.create('BACKSUB_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Whether to do background subtraction'
item.value['ES'] = '[BOOLEAN] Si hacer la sustracción de fondo'
item.value['FR'] = '[BOOLEAN] S\'il faut faire une soustraction de fond '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# BADFILE_HELP 
# =============================================================================
item = langlist.create('BADFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Define a custom file to use for bad pixel correction. Checks for an absolute path and then checks \'directory\''
item.value['ES'] = ('[STRING] Definir un archivo personalizado para la '
                    'corrección de píxeles malos. Comprueba una ruta absoluta '
                    "y luego 'directory'")
item.value['FR'] = '[STRING] Définissez un fichier personnalisé à utiliser pour corriger les pixels défectueux. Vérifie un chemin absolu puis vérifie \'répertoire\' '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# BADPIX_DARKFILE_HELP 
# =============================================================================
item = langlist.create('BADPIX_DARKFILE_HELP', kind='HELP')
item.value['ENG'] = 'Current allowed types: DARK_DARK'
item.value['ES'] = 'Tipos permitidos actualmente: DARK_DARK'
item.value['FR'] = 'Types actuellement autorisés: DARK_DARK '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# BADPIX_DESC 
# =============================================================================
item = langlist.create('BADPIX_DESC', kind='HELP')
item.value['ENG'] = 'Bad pixel finding recipe for SPIRou @ CFHT'
item.value['ES'] = 'Receta de búsqueda de píxeles malos para SPIRou @ CFHT'
item.value['FR'] = 'Mauvaise recette de recherche de pixels pour SPIRou @ CFHT '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# BADPIX_EXAMPLE 
# =============================================================================
item = langlist.create('BADPIX_EXAMPLE', kind='HELP')
item.value['ENG'] = 'cal_BADPIX_spirou.py [NIGHT_NAME]  -flatfiles [FLAT_FLAT] -darkfiles [DARK_DARK] \n cal_BADPIX_spirou.py -flatfiles 2018-08-05 2295524f_pp.fits -darkfiles dark_dark_P5_003d_pp.fits \n cal_BADPIX_spirou.py 2018-08-05 -flatfiles 2295524f_pp -darkfiles dark_dark_P5_003d_pp \n cal_BADPIX_spirou.py 2018-08-05 -flatfiles 229552*f_pp  -darkfiles d_pp'
item.value['ES'] = ('cal_BADPIX_spirou.py [NIGHT_NAME]  -flatfiles '
                    '[FLAT_FLAT] -darkfiles [DARK_DARK] \n '
                    'cal_BADPIX_spirou.py -flatfiles 2018-08-05 '
                    '2295524f_pp.fits -darkfiles dark_dark_P5_003d_pp.fits \n '
                    'cal_BADPIX_spirou.py 2018-08-05 -flatfiles 2295524f_pp '
                    '-darkfiles dark_dark_P5_003d_pp \n cal_BADPIX_spirou.py '
                    '2018-08-05 -flatfiles 229552*f_pp  -darkfiles d_pp')
item.value['FR'] = 'cal_BADPIX_spirou.py [NIGHT_NAME] [FLAT_FLAT] [DARK_DARK] \n cal_BADPIX_spirou.py 2018-08-05 2295524f_pp.fits dark_dark_P5_003d_pp.fits \n cal_BADPIX_spirou.py 2018-08-05 2295524f_pp dark_dark_P5_003d_pp \n cal_BADPIX_spirou.py 2018-08-05 229552*f_pp d_pp'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# BADPIX_FLATFILE_HELP 
# =============================================================================
item = langlist.create('BADPIX_FLATFILE_HELP', kind='HELP')
item.value['ENG'] = 'Current allowed types: FLAT_FLAT'
item.value['ES'] = 'Tipos permitidos actualmente: FLAT_FLAT'
item.value['FR'] = 'Types actuellement autorisés: FLAT_FLAT '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# BLAZEFILE_HELP 
# =============================================================================
item = langlist.create('BLAZEFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Define a custom file to use for blaze correction. If unset uses closest file from calibDB. Checks for an absolute path and then checks \'directory\' (CALIBDB=BADPIX)'
item.value['ES'] = ('[STRING] Definir un archivo personalizado para la '
                    'corrección del blaze. Si no se define usa el archivo más '
                    'cercano de calibDB. Comprueba una ruta absoluta y luego '
                    "'directory' (CALIBDB=BADPIX)")
item.value['FR'] = '[STRING] Définissez un fichier personnalisé à utiliser pour la correction de flamme. Si non défini, utilise le fichier le plus proche de calibDB. Vérifie un chemin absolu puis vérifie \'répertoire\' '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# COMBINE_HELP 
# =============================================================================
item = langlist.create('COMBINE_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Whether to combine fits files in file list or to process them separately'
item.value['ES'] = ('[BOOLEAN] Si combinar los archivos fits de la lista o '
                    'procesarlos por separado')
item.value['FR'] = '[BOOLEAN] S\'il faut combiner des fichiers de la liste de fichiers ou les traiter séparément '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DARK_DESC 
# =============================================================================
item = langlist.create('DARK_DESC', kind='HELP')
item.value['ENG'] = 'Dark finding recipe for SPIRou @ CFHT'
item.value['ES'] = 'Receta de búsqueda de dark para SPIRou @ CFHT'
item.value['FR'] = 'Recette Dark Find pour SPIRou @ CFHT '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DARK_EXAMPLE 
# =============================================================================
item = langlist.create('DARK_EXAMPLE', kind='HELP')
item.value['ENG'] = 'cal_DARK_spirou.py [NIGHT_NAME] [FILES] \n cal_DARK_spirou.py 2018-08-05 dark_dark_P5_003d_pp.fits \n cal_DARK_spirou.py 2018-08-05 dark_dark_P5_003d_pp \n cal_DARK_spirou.py 2018-08-05 *d_pp'
item.value['ES'] = ('cal_DARK_spirou.py [NIGHT_NAME] [FILES] \n '
                    'cal_DARK_spirou.py 2018-08-05 '
                    'dark_dark_P5_003d_pp.fits \n cal_DARK_spirou.py '
                    '2018-08-05 dark_dark_P5_003d_pp \n cal_DARK_spirou.py '
                    '2018-08-05 *d_pp')
item.value['FR'] = 'cal_DARK_spirou.py [NIGHT_NAME] [FILES] \n cal_DARK_spirou.py 2018-08-05 dark_dark_P5_003d_pp.fits \n cal_DARK_spirou.py 2018-08-05 dark_dark_P5_003d_pp \n cal_DARK_spirou.py 2018-08-05 *d_pp'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DARK_FILES_HELP 
# =============================================================================
item = langlist.create('DARK_FILES_HELP', kind='HELP')
item.value['ENG'] = 'Current allowed types: DARK_DARK_INT, DARK_DARK_TEL, DARK_DARK_SKY'
item.value['ES'] = ('Tipos permitidos actualmente: DARK_DARK_INT, '
                    'DARK_DARK_TEL, DARK_DARK_SKY')
item.value['FR'] = 'Types actuellement autorisés: DARK_DARK_INT, DARK_DARK_TEL, DARK_DARK_SKY'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DARKFILE_HELP 
# =============================================================================
item = langlist.create('DARKFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The Dark file to use (CALIBDB=DARKM)'
item.value['FR'] = '[STRING] Le fichier dark à utiliser (CALIBDB=DARKM)'
item.value['ES'] = '[STRING] El archivo dark a usar (CALIBDB=DARKM)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DOBAD_HELP 
# =============================================================================
item = langlist.create('DOBAD_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Whether to correct for the bad pixel file'
item.value['ES'] = '[BOOLEAN] Si corregir con el archivo de píxeles malos'
item.value['FR'] = '[BOOLEAN] S\'il faut corriger le fichier de pixels défectueux '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DODARK_HELP 
# =============================================================================
item = langlist.create('DODARK_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Whether to correct for the dark file'
item.value['ES'] = '[BOOLEAN] Si corregir con el archivo dark'
item.value['FR'] = '[BOOLEAN] S\'il faut corriger pour le fichier sombre '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXTFIBER_HELP 
# =============================================================================
item = langlist.create('EXTFIBER_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Define which fibers to extract'
item.value['ES'] = '[STRING] Definir qué fibras extraer'
item.value['FR'] = '[STRING] Définir les fibres à extraire '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXTRACT_DESC 
# =============================================================================
item = langlist.create('EXTRACT_DESC', kind='HELP')
item.value['ENG'] = 'Extraction recipe for SPIRou @ CFHT'
item.value['ES'] = 'Receta de extracción para SPIRou @ CFHT'
item.value['FR'] = 'Recette d\'extraction pour SPIRou @ CFHT '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXTRACT_EXAMPLE 
# =============================================================================
item = langlist.create('EXTRACT_EXAMPLE', kind='HELP')
item.value['ENG'] = ' cal_extract_RAW_spirou.py [NIGHT_NAME] [FILES] \n cal_extract_RAW_spirou.py 2018-08-05 2295525a_pp.fits \n cal_extract_RAW_spirou.py 2018-08-05 2295545o_pp.fits \n cal_extract_RAW_spirou.py 2018-08-05 2295525a_pp \n cal_extract_RAW_spirou.py 2018-08-05 2'
item.value['ES'] = (' cal_extract_RAW_spirou.py [NIGHT_NAME] [FILES] \n '
                    'cal_extract_RAW_spirou.py 2018-08-05 2295525a_pp.fits \n '
                    'cal_extract_RAW_spirou.py 2018-08-05 2295545o_pp.fits \n '
                    'cal_extract_RAW_spirou.py 2018-08-05 2295525a_pp \n '
                    'cal_extract_RAW_spirou.py 2018-08-05 2')
item.value['FR'] = ' cal_extract_RAW_spirou.py [NIGHT_NAME] [FILES] \n cal_extract_RAW_spirou.py 2018-08-05 2295525a_pp.fits \n cal_extract_RAW_spirou.py 2018-08-05 2295545o_pp.fits \n cal_extract_RAW_spirou.py 2018-08-05 2295525a_pp \n cal_extract_RAW_spirou.py 2018-08-05 2'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXTRACT_FILES_HELP 
# =============================================================================
item = langlist.create('EXTRACT_FILES_HELP', kind='HELP')
item.value['ENG'] = 'Current accepts all preprocessed filetypes. All files used will be combined into a single frame.'
item.value['ES'] = ('Actualmente acepta todos los tipos de archivo '
                    'preprocesados. Todos los archivos usados se combinarán '
                    'en un único fotograma.')
item.value['FR'] = 'Current accepte tous les types de fichiers prétraités. Tous les fichiers utilisés seront combinés dans un seul cadre. '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXTRACT_METHOD_HELP 
# =============================================================================
item = langlist.create('EXTRACT_METHOD_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Define a custom extraction method'
item.value['ES'] = '[STRING] Definir un método de extracción personalizado'
item.value['FR'] = '[STRING] Définir une méthode d\'extraction personnalisée '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUICK_LOOK_EXT_HELP 
# =============================================================================
item = langlist.create('QUICK_LOOK_EXT_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Sets whether extraction done in quick look mode'
item.value['FR'] = ("[BOOLEAN] Définit si l'extraction est faite en mode "
                    'aperçu rapide')
item.value['ES'] = ('[BOOLEAN] Define si la extracción se hace en modo de '
                    'vista rápida')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FLAT_DESC 
# =============================================================================
item = langlist.create('FLAT_DESC', kind='HELP')
item.value['ENG'] = 'Flat/Blaze finding recipe for SPIRou @ CFHT'
item.value['ES'] = 'Receta de búsqueda de flat/blaze para SPIRou @ CFHT'
item.value['FR'] = 'Recette de recherche de plat / feu pour SPIRou @ CFHT '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FLAT_EXAMPLE 
# =============================================================================
item = langlist.create('FLAT_EXAMPLE', kind='HELP')
item.value['ENG'] = ' cal_FF_RAW_spirou.py [NIGHT_NAME] [FLAT_FLAT] \n cal_FF_RAW_spirou.py [NIGHT_NAME] [DARK_FLAT] \n cal_FF_RAW_spirou.py [NIGHT_NAME] [FLAT_DARK] \n cal_FF_RAW_spirou.py 2018-08-05 2295520f_pp.fits 2295521f_pp.fits \n cal_FF_RAW_spirou.py 2018-08-05 229552'
item.value['ES'] = (' cal_FF_RAW_spirou.py [NIGHT_NAME] [FLAT_FLAT] \n '
                    'cal_FF_RAW_spirou.py [NIGHT_NAME] [DARK_FLAT] \n '
                    'cal_FF_RAW_spirou.py [NIGHT_NAME] [FLAT_DARK] \n '
                    'cal_FF_RAW_spirou.py 2018-08-05 2295520f_pp.fits '
                    '2295521f_pp.fits \n cal_FF_RAW_spirou.py 2018-08-05 '
                    '229552')
item.value['FR'] = ' cal_FF_RAW_spirou.py [NIGHT_NAME] [FLAT_FLAT] \n cal_FF_RAW_spirou.py [NIGHT_NAME] [DARK_FLAT] \n cal_FF_RAW_spirou.py [NIGHT_NAME] [FLAT_DARK] \n cal_FF_RAW_spirou.py 2018-08-05 2295520f_pp.fits 2295521f_pp.fits \n cal_FF_RAW_spirou.py 2018-08-05 229552'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FLAT_FILES_HELP 
# =============================================================================
item = langlist.create('FLAT_FILES_HELP', kind='HELP')
item.value['ENG'] = 'Current allowed types: FLAT_FLAT or DARK_FLAT or FLAT_DARK but not a mixture (exclusive)'
item.value['ES'] = ('Tipos permitidos actualmente: FLAT_FLAT o DARK_FLAT o '
                    'FLAT_DARK pero no una mezcla (exclusivo)')
item.value['FR'] = 'Types actuellement autorisés: FLAT_FLAT ou DARK_FLAT ou FLAT_DARK mais pas un mélange (exclusif) '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FLATFILE_HELP 
# =============================================================================
item = langlist.create('FLATFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Define a custom file to use for flat correction. If unset uses closest file from calibDB. Checks for an absolute path and then checks \'directory\''
item.value['ES'] = ('[STRING] Definir un archivo personalizado para la '
                    'corrección del flat. Si no se define usa el archivo más '
                    'cercano de calibDB. Comprueba una ruta absoluta y luego '
                    "'directory'")
item.value['FR'] = '[STRING] Définissez un fichier personnalisé à utiliser pour la correction à plat. Si non défini, utilise le fichier le plus proche de calibDB. Vérifie un chemin absolu puis vérifie \'répertoire\' '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FLIPIMAGE_HELP 
# =============================================================================
item = langlist.create('FLIPIMAGE_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Whether to flip fits image'
item.value['ES'] = '[BOOLEAN] Si voltear la imagen fits'
item.value['FR'] = '[BOOLEAN] Faut-il retourner l\'image? '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FLUXUNITS_HELP 
# =============================================================================
item = langlist.create('FLUXUNITS_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Output units for flux'
item.value['ES'] = '[STRING] Unidades de salida del flujo'
item.value['FR'] = '[STRING] Unités de sortie pour flux '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# HC_E2DS_DESC 
# =============================================================================
item = langlist.create('HC_E2DS_DESC', kind='HELP')
item.value['ENG'] = 'Wavelength solution finding recipe for SPIRou @ CFHT. \n\n Uses the less accurate method using only a HCONE_HCONE file'
item.value['ES'] = ('Receta de búsqueda de la solución de longitud de onda '
                    'para SPIRou @ CFHT. \n\n Usa el método menos preciso con '
                    'solo un archivo HCONE_HCONE')
item.value['FR'] = 'La recette de recherche de solution de longueur d\'onde pour SPIRou @ CFHT. \n\n Utilise la méthode la moins précise en utilisant uniquement un fichier HCONE_HCONE. '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# HC_E2DS_EXAMPLE 
# =============================================================================
item = langlist.create('HC_E2DS_EXAMPLE', kind='HELP')
item.value['ENG'] = 'cal_HC_E2DS_EA_spirou.py [NIGHT_NAME] [FILES] \n'
item.value['ES'] = 'cal_HC_E2DS_EA_spirou.py [NIGHT_NAME] [FILES] \n'
item.value['FR'] = 'cal_HC_E2DS_EA_spirou.py [NIGHT_NAME] [FILES] \n '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# HC_E2DS_FILES_HELP 
# =============================================================================
item = langlist.create('HC_E2DS_FILES_HELP', kind='HELP')
item.value['ENG'] = 'Currently allowed type:\n\tDRS_EOUT = EXT_E2DS_AB (HCONE_HCONE) or EXT_E2DS_A (HCONE_HCONE)\n\tor EXT_E2DS_B (HCONE_HCONE) or EXT_E2DS_C (HCONE_HCONE)'
item.value['ES'] = ('Tipo permitido actualmente:\n\tDRS_EOUT = EXT_E2DS_AB '
                    '(HCONE_HCONE) o EXT_E2DS_A (HCONE_HCONE)\n\to EXT_E2DS_B '
                    '(HCONE_HCONE) o EXT_E2DS_C (HCONE_HCONE)')
item.value['FR'] = 'Type actuellement autorisé:\n\tDRS_EOUT = EXT_E2DS_AB (HCONE_HCONE) ou EXT_E2DS_A (HCONE_HCONE)\n\tor EXT_E2DS_B (HCONE_HCONE) ou EXT_E2DS_C (HCONE_HCONE)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LOC_DESC 
# =============================================================================
item = langlist.create('LOC_DESC', kind='HELP')
item.value['ENG'] = 'Localisation finding recipe for SPIRou @ CFHT'
item.value['ES'] = 'Receta de búsqueda de localización para SPIRou @ CFHT'
item.value['FR'] = 'Recette de localisation pour SPIRou @ CFHT '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LOC_EXAMPLE 
# =============================================================================
item = langlist.create('LOC_EXAMPLE', kind='HELP')
item.value['ENG'] = ' cal_loc_RAW_spirou.py [NIGHT_NAME] [DARK_FLAT] \n cal_loc_RAW_spirou.py [NIGHT_NAME] [FLAT_DARK] \n cal_loc_RAW_spirou 2018-08-05 2295510f_pp.fits 2295511f_pp.fits 2295512f_pp.fits \n  cal_loc_RAW_spirou 2018-08-05 2295515f_pp.fits 2295516f_pp.fits 22955'
item.value['ES'] = (' cal_loc_RAW_spirou.py [NIGHT_NAME] [DARK_FLAT] \n '
                    'cal_loc_RAW_spirou.py [NIGHT_NAME] [FLAT_DARK] \n '
                    'cal_loc_RAW_spirou 2018-08-05 2295510f_pp.fits '
                    '2295511f_pp.fits 2295512f_pp.fits \n  cal_loc_RAW_spirou '
                    '2018-08-05 2295515f_pp.fits 2295516f_pp.fits 22955')
item.value['FR'] = ' cal_loc_RAW_spirou.py [NIGHT_NAME] [DARK_FLAT] \n cal_loc_RAW_spirou.py [NIGHT_NAME] [FLAT_DARK] \n cal_loc_RAW_spirou 2018-08-05 2295510f_pp.fits 2295511f_pp.fits 2295512f_pp.fits \n  cal_loc_RAW_spirou 2018-08-05 2295515f_pp.fits 2295516f_pp.fits 22955'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LOC_FILES_HELP 
# =============================================================================
item = langlist.create('LOC_FILES_HELP', kind='HELP')
item.value['ENG'] = 'Current allowed types: DARK_FLAT OR FLAT_DARK but not both (exclusive)'
item.value['ES'] = ('Tipos permitidos actualmente: DARK_FLAT O FLAT_DARK pero '
                    'no ambos (exclusivo)')
item.value['FR'] = 'Types actuellement autorisés: DARK_FLAT OU FLAT_DARK mais pas les deux (exclusif) '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PREPROCESS_DESC 
# =============================================================================
item = langlist.create('PREPROCESS_DESC', kind='HELP')
item.value['ENG'] = 'Pre-processing recipe for SPIRou @ CFHT'
item.value['ES'] = 'Receta de preprocesamiento para SPIRou @ CFHT'
item.value['FR'] = 'Recette de pré-traitement pour SPIRou @ CFHT '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PREPROCESS_EXAMPLE 
# =============================================================================
item = langlist.create('PREPROCESS_EXAMPLE', kind='HELP')
item.value['ENG'] = ' cal_preprocess_spirou.py [NIGHT_NAME] [FILES] \n cal_preprocess_spirou.p 2018-08-05 *.fits \n cal_preprocess_spirou.p 2018-08-05 dark_dark_P5_003d_pp.fits \n cal_preprocess_spirou.p 2018-08-05 *d_pp'
item.value['ES'] = (' cal_preprocess_spirou.py [NIGHT_NAME] [FILES] \n '
                    'cal_preprocess_spirou.p 2018-08-05 *.fits \n '
                    'cal_preprocess_spirou.p 2018-08-05 '
                    'dark_dark_P5_003d_pp.fits \n cal_preprocess_spirou.p '
                    '2018-08-05 *d_pp')
item.value['FR'] = ' cal_preprocess_spirou.py [NIGHT_NAME] [FILES] \n cal_preprocess_spirou.p 2018-08-05 * .fits \n cal_preprocess_spirou.p 2018-08-05 dark_dark_P5_003d_pp.fits \n cal_preprocess_spirou.p 2018-08-08 *.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PREPROCESS_UFILES_HELP 
# =============================================================================
item = langlist.create('PREPROCESS_UFILES_HELP', kind='HELP')
item.value['ENG'] = 'Any raw files are currently allowed. Multiple files inputted are handled separately (one after the other).'
item.value['ES'] = ('Actualmente se permite cualquier archivo bruto. Varios '
                    'archivos introducidos se procesan por separado (uno tras '
                    'otro).')
item.value['FR'] = 'Tous les fichiers bruts sont actuellement autorisés. Plusieurs fichiers entrés sont traités séparément (les uns après les autres). '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESIZE_HELP 
# =============================================================================
item = langlist.create('RESIZE_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Whether to resize image'
item.value['ES'] = '[BOOLEAN] Si redimensionar la imagen'
item.value['FR'] = '[BOOLEAN] S\'il faut redimensionner l\'image '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SHAPE_DESC 
# =============================================================================
item = langlist.create('SHAPE_DESC', kind='HELP')
item.value['ENG'] = 'Shape finding recipe for SPIRou @ CFHT'
item.value['ES'] = 'Receta de búsqueda de shape para SPIRou @ CFHT'
item.value['FR'] = 'Recette de recherche de forme pour SPIRou @ CFHT '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SHAPE_EXAMPLE 
# =============================================================================
item = langlist.create('SHAPE_EXAMPLE', kind='HELP')
item.value['ENG'] = 'cal_SHAPE_spirou.py [NIGHT_NAME] [HCONE_HCONE] [FP_FP] \n cal_SHAPE_spirou.py 2018-08-05 2295680c_pp.fits 2295525a_pp.fits \n cal_SHAPE_spirou.py 2018-08-05 2295680c_pp 2295525a_pp \n cal_SHAPE_spirou.py 2018-08-05 2295680c_pp *a_pp.fits'
item.value['FR'] = ('cal_SHAPE_spirou.py [NIGHT_NAME] [HCONE_HCONE] '
                    '[FP_FP] \n cal_SHAPE_spirou.py 2018-08-05 '
                    '2295680c_pp.fits 2295525a_pp.fits \n cal_SHAPE_spirou.py '
                    '2018-08-05 2295680c_pp 2295525a_pp \n '
                    'cal_SHAPE_spirou.py 2018-08-05 2295680c_pp *a_pp.fits')
item.value['ES'] = ('cal_SHAPE_spirou.py [NIGHT_NAME] [HCONE_HCONE] '
                    '[FP_FP] \n cal_SHAPE_spirou.py 2018-08-05 '
                    '2295680c_pp.fits 2295525a_pp.fits \n cal_SHAPE_spirou.py '
                    '2018-08-05 2295680c_pp 2295525a_pp \n '
                    'cal_SHAPE_spirou.py 2018-08-05 2295680c_pp *a_pp.fits')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SHAPEREF_EXAMPLE 
# =============================================================================
item = langlist.create('SHAPEREF_EXAMPLE', kind='HELP')
item.value['ENG'] = 'cal_shape_reference_spirou.py 2019-04-20 --fpfiles 2400565a_pp.fits 2400566a_pp.fits 2400567a_pp.fits 2400568a_pp.fits 2400569a_pp.fits'
item.value['FR'] = ('cal_shape_reference_spirou.py 2019-04-20 --fpfiles '
                    '2400565a_pp.fits 2400566a_pp.fits 2400567a_pp.fits '
                    '2400568a_pp.fits 2400569a_pp.fits')
item.value['ES'] = ('cal_shape_reference_spirou.py 2019-04-20 --fpfiles '
                    '2400565a_pp.fits 2400566a_pp.fits 2400567a_pp.fits '
                    '2400568a_pp.fits 2400569a_pp.fits')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SHAPE_FPFILES_HELP 
# =============================================================================
item = langlist.create('SHAPE_FPFILES_HELP', kind='HELP')
item.value['ENG'] = 'Current allowed types: FP_FP'
item.value['ES'] = 'Tipos permitidos actualmente: FP_FP'
item.value['FR'] = 'Types actuellement autorisés: FP_FP '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SHAPE_HCFILES_HELP 
# =============================================================================
item = langlist.create('SHAPE_HCFILES_HELP', kind='HELP')
item.value['ENG'] = 'Current allowed types: HC_HC'
item.value['ES'] = 'Tipos permitidos actualmente: HC_HC'
item.value['FR'] = 'Types actuellement autorisés: DARK_DARK '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SHAPEFILE_HELP 
# =============================================================================
item = langlist.create('SHAPEFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Define a custom file to use for shape correction. If unset uses closest file from calibDB. Checks for an absolute path and then checks \'directory\'.'
item.value['ES'] = ('[STRING] Definir un archivo personalizado para la '
                    'corrección de shape. Si no se define usa el archivo más '
                    'cercano de calibDB. Comprueba una ruta absoluta y luego '
                    "'directory'.")
item.value['FR'] = '[STRING] Définissez un fichier personnalisé à utiliser pour la correction de forme. Si non défini, utilise le fichier le plus proche de calibDB. Recherche un chemin absolu, puis \'répertoire\'. '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SHAPE_FPREF_HELP 
# =============================================================================
item = langlist.create('SHAPE_FPREF_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Define a custom file to use for the FP reference (skips the FP reference step) - this file must have been produced by a previous run of cal_shape_reference'
item.value['FR'] = ('[STRING] Définir un fichier personnalisé pour la '
                    "référence FP (ignore l'étape de référence FP) - ce "
                    'fichier doit avoir été produit par une exécution '
                    'précédente de cal_shape_reference')
item.value['ES'] = ('[STRING] Definir un archivo personalizado para la '
                    'referencia FP (omite el paso de referencia FP) - este '
                    'archivo debe haberse producido en una ejecución previa '
                    'de cal_shape_reference')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SLIT_DESC 
# =============================================================================
item = langlist.create('SLIT_DESC', kind='HELP')
item.value['ENG'] = 'Tilt finding recipe for SPIRou @ CFHT \n\n Warning: Deprecated (old) recipe - use cal_SHAPE_spirou.py instead'
item.value['ES'] = ('Receta de búsqueda de inclinación para SPIRou @ '
                    'CFHT \n\n Advertencia: receta obsoleta (antigua) - use '
                    'cal_SHAPE_spirou.py en su lugar')
item.value['FR'] = 'Recette de recherche d\'inclinaison pour SPIRou @ CFHT \n\n Avertissement: recette obsolète (ancienne) - utilisez cal_SHAPE_spirou.py à la place '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SLIT_EXAMPLE 
# =============================================================================
item = langlist.create('SLIT_EXAMPLE', kind='HELP')
item.value['ENG'] = ' cal_SLIT_spirou.py [NIGHT_NAME] [FP_FP] \n cal_SLIT_spirou.py 2018-08-05 2295525a_pp.fits \n cal_SLIT_spirou.py 2018-08-05 2295525a_pp \n cal_SLIT_spirou.py 2018-08-05 *a_pp.fits'
item.value['ES'] = (' cal_SLIT_spirou.py [NIGHT_NAME] [FP_FP] \n '
                    'cal_SLIT_spirou.py 2018-08-05 2295525a_pp.fits \n '
                    'cal_SLIT_spirou.py 2018-08-05 2295525a_pp \n '
                    'cal_SLIT_spirou.py 2018-08-05 *a_pp.fits')
item.value['FR'] = ' cal_SLIT_spirou.py [NIGHT_NAME] [FP_FP] \n cal_SLIT_spirou.py 2018-08-05 2295525a_pp.fits \n cal_SLIT_spirou.py 2018-08-05 2295525a_pp \n cal_SLIT_spirou.py 2018-08-05 *a_pp.fits'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SLIT_FILES_HELP 
# =============================================================================
item = langlist.create('SLIT_FILES_HELP', kind='HELP')
item.value['ENG'] = 'Current allowed types: FP_FP'
item.value['ES'] = 'Tipos permitidos actualmente: FP_FP'
item.value['FR'] = 'Types actuellement autorisés: FP_FP '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TILTFILE_HELP 
# =============================================================================
item = langlist.create('TILTFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Define a custom file to use for tilt  correction. If unset uses closest file from calibDB. Checks for an absolute path and then checks \'directory\''
item.value['ES'] = ('[STRING] Definir un archivo personalizado para la '
                    'corrección de inclinación. Si no se define usa el '
                    'archivo más cercano de calibDB. Comprueba una ruta '
                    "absoluta y luego 'directory'")
item.value['FR'] = '[STRING] Définissez un fichier personnalisé à utiliser pour la correction d\'inclinaison. Si non défini, utilise le fichier le plus proche de calibDB. Vérifie un chemin absolu puis vérifie \'répertoire\''
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# WAVE_DESC 
# =============================================================================
item = langlist.create('WAVE_DESC', kind='HELP')
item.value['ENG'] = 'Wavelength solution finding recipe for SPIRou @ CFHT. \n\n Uses HCONE_HCONE to find an initial solution and optionally FP_FP files to find more accurate solution.'
item.value['ES'] = ('Receta de búsqueda de la solución de longitud de onda '
                    'para SPIRou @ CFHT. \n\n Usa HCONE_HCONE para encontrar '
                    'una solución inicial y opcionalmente archivos FP_FP para '
                    'una solución más precisa.')
item.value['FR'] = 'La recette de recherche de solution de longueur d\'onde pour SPIRou @ CFHT. \n \n Utilise les fichiers HCONE_HCONE et FP_FP pour trouver la solution (plus précise). '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# WAVE_FPFILES_HELP 
# =============================================================================
item = langlist.create('WAVE_FPFILES_HELP', kind='HELP')
item.value['ENG'] = 'Current allowed types: FP_FP'
item.value['ES'] = 'Tipos permitidos actualmente: FP_FP'
item.value['FR'] = 'Types actuellement autorisés: FP_FP '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# WAVE_HCFILES_HELP 
# =============================================================================
item = langlist.create('WAVE_HCFILES_HELP', kind='HELP')
item.value['ENG'] = 'Current allowed types: HC1_HC1'
item.value['ES'] = 'Tipos permitidos actualmente: HC1_HC1'
item.value['FR'] = 'Types actuellement autorisés: HC1_HC1'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# WAVEFILE_HELP 
# =============================================================================
item = langlist.create('WAVEFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Define a custom file to use for the wave solution. If unset uses closest file from header or calibDB (depending on setup). Checks for an absolute path and then checks \'directory\''
item.value['ES'] = ('[STRING] Definir un archivo personalizado para la '
                    'solución de longitud de onda. Si no se define usa el '
                    'archivo más cercano de la cabecera o de calibDB (según '
                    'la configuración). Comprueba una ruta absoluta y luego '
                    "'directory'")
item.value['FR'] = '[STRING] Définissez un fichier personnalisé à utiliser pour la solution wave. Si non défini, utilise le fichier le plus proche de l\'en-tête ou de calibDB (selon la configuration). Vérifie un chemin absolu puis vérifie \'répertoire\' '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# WAVE_EXTRACT_HELP 
# =============================================================================
item = langlist.create('WAVE_EXTRACT_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Sets whether to extract input files if files found on disk (defaults to WAVE_ALWAYS_EXTRACT)'
item.value['FR'] = ("[BOOLEAN] Définit s'il faut extraire les fichiers "
                    "d'entrée si des fichiers sont trouvés sur le disque (par "
                    'défaut WAVE_ALWAYS_EXTRACT)')
item.value['ES'] = ('[BOOLEAN] Define si extraer los archivos de entrada si '
                    'se encuentran archivos en disco (por defecto '
                    'WAVE_ALWAYS_EXTRACT)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DARK_REF_DESC 
# =============================================================================
item = langlist.create('DARK_REF_DESC', kind='HELP')
item.value['ENG'] = 'Dark finding recipe for SPIRou @ CFHT'
item.value['ES'] = 'Receta de búsqueda de dark para SPIRou @ CFHT'
item.value['FR'] = 'Recette Dark Find pour SPIRou @ CFHT '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DARK_REF_EXAMPLE 
# =============================================================================
item = langlist.create('DARK_REF_EXAMPLE', kind='HELP')
item.value['ENG'] = 'cal_dark_reference_spirou.py'
item.value['ES'] = 'cal_dark_reference_spirou.py'
item.value['FR'] = 'cal_dark_reference_spirou.py'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DARK_REF_FILETYPE 
# =============================================================================
item = langlist.create('DARK_REF_FILETYPE', kind='HELP')
item.value['ENG'] = 'Current allowed types: DARK_DARK'
item.value['ES'] = 'Tipos permitidos actualmente: DARK_DARK'
item.value['FR'] = 'Types actuellement autorisés: DARK_DARK '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# OBJNAME_HELP 
# =============================================================================
item = langlist.create('OBJNAME_HELP', kind='HELP')
item.value['ENG'] = 'Sets the object name to extract (filters input files)'
item.value['FR'] = ("Définit le nom de l'objet à extraire (filtre les "
                    "fichiers d'entrée)")
item.value['ES'] = ('Define el nombre del objeto a extraer (filtra los '
                    'archivos de entrada)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DPRTYPE_HELP 
# =============================================================================
item = langlist.create('DPRTYPE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Sets the DPRTYPE to extract (filters input files)'
item.value['FR'] = ('[STRING] Définit le DPRTYPE à extraire (filtre les '
                    "fichiers d'entrée)")
item.value['ES'] = ('[STRING] Define el DPRTYPE a extraer (filtra los '
                    'archivos de entrada)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LOCOFILE_HELP 
# =============================================================================
item = langlist.create('LOCOFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Sets the LOCO file used to get the coefficients (CALIBDB=LOC_{fiber})'
item.value['FR'] = ('[STRING] Définit le fichier LOCO utilisé pour obtenir '
                    'les coefficients (CALIBDB=LOC_{fiber})')
item.value['ES'] = ('[STRING] Define el archivo LOCO usado para obtener los '
                    'coeficientes (CALIBDB=LOC_{fiber})')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ORDERPFILE_HELP 
# =============================================================================
item = langlist.create('ORDERPFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Sets the Order Profile file used to get the coefficients (CALIBDB=ORDER_PROFILE_{fiber}'
item.value['FR'] = ("[STRING] Définit le fichier de profil d'ordres utilisé "
                    'pour obtenir les coefficients '
                    '(CALIBDB=ORDER_PROFILE_{fiber}')
item.value['ES'] = ('[STRING] Define el archivo de perfil de órdenes usado '
                    'para obtener los coeficientes '
                    '(CALIBDB=ORDER_PROFILE_{fiber}')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SHAPEXFILE_HELP 
# =============================================================================
item = langlist.create('SHAPEXFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Sets the SHAPE DXMAP file used to get the dx correction map (CALIBDB=SHAPEX)'
item.value['FR'] = ('[STRING] Définit le fichier SHAPE DXMAP utilisé pour '
                    'obtenir la carte de correction dx (CALIBDB=SHAPEX)')
item.value['ES'] = ('[STRING] Define el archivo SHAPE DXMAP usado para '
                    'obtener el mapa de corrección dx (CALIBDB=SHAPEX)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SHAPEYFILE_HELP 
# =============================================================================
item = langlist.create('SHAPEYFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Sets the SHAPE DYMAP file used to get the dy correction map (CALIBDB=SHAPEY)'
item.value['FR'] = ('[STRING] Définit le fichier SHAPE DYMAP utilisé pour '
                    'obtenir la carte de correction dy (CALIBDB=SHAPEY)')
item.value['ES'] = ('[STRING] Define el archivo SHAPE DYMAP usado para '
                    'obtener el mapa de corrección dy (CALIBDB=SHAPEY)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SHAPELFILE_HELP 
# =============================================================================
item = langlist.create('SHAPELFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Sets the SHAPE local file used to get the local transforms (CALIBDB = SHAPEL)'
item.value['FR'] = ('[STRING] Définit le fichier SHAPE local utilisé pour '
                    'obtenir les transformations locales (CALIBDB = SHAPEL)')
item.value['ES'] = ('[STRING] Define el archivo SHAPE local usado para '
                    'obtener las transformaciones locales (CALIBDB = SHAPEL)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FPREFFILE_HELP 
# =============================================================================
item = langlist.create('FPREFFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Sets the FP reference file to use (CALIBDB = FPREF)'
item.value['FR'] = ('[STRING] Définit le fichier de référence FP à utiliser '
                    '(CALIBDB = FPREF)')
item.value['ES'] = ('[STRING] Define el archivo de referencia FP a usar '
                    '(CALIBDB = FPREF)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# THERMALFILE_HELP 
# =============================================================================
item = langlist.create('THERMALFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Sets the Thermal correction file to use (CAILBDB = THERMAL_{fiber})'
item.value['FR'] = ('[STRING] Définit le fichier de correction thermique à '
                    'utiliser (CAILBDB = THERMAL_{fiber})')
item.value['ES'] = ('[STRING] Define el archivo de corrección térmica a usar '
                    '(CAILBDB = THERMAL_{fiber})')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# THERMAL_HELP 
# =============================================================================
item = langlist.create('THERMAL_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Sets whether to do the thermal correction (else defaults to THERMAL_CORRECT value in constants)'
item.value['FR'] = ('[BOOLEAN] Définit si la correction thermique est faite '
                    '(sinon valeur THERMAL_CORRECT des constantes)')
item.value['ES'] = ('[BOOLEAN] Define si se hace la corrección térmica (si '
                    'no, se usa el valor THERMAL_CORRECT de las constantes)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# THERMAL_EXTRACT_HELP 
# =============================================================================
item = langlist.create('THERMAL_EXTRACT_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Sets whether to extract input files if files found on disk (defaults to THERMAL_ALWAYS_EXTRACT)'
item.value['FR'] = ("[BOOLEAN] Définit s'il faut extraire les fichiers "
                    "d'entrée si des fichiers sont trouvés sur le disque (par "
                    'défaut THERMAL_ALWAYS_EXTRACT)')
item.value['ES'] = ('[BOOLEAN] Define si extraer los archivos de entrada si '
                    'se encuentran archivos en disco (por defecto '
                    'THERMAL_ALWAYS_EXTRACT)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# BACKFILE_HELP 
# =============================================================================
item = langlist.create('BACKFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Sets the Background map file to use (CALIBDB = BKGRDMAP)'
item.value['FR'] = ('[STRING] Définit le fichier de carte de fond à utiliser '
                    '(CALIBDB = BKGRDMAP)')
item.value['ES'] = ('[STRING] Define el archivo de mapa de fondo a usar '
                    '(CALIBDB = BKGRDMAP)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# MKTELL_DESC 
# =============================================================================
item = langlist.create('MKTELL_DESC', kind='HELP')
item.value['ENG'] = 'Telluric recipe to take hot stars and calculation their atmospheric transmission (to add to pca database)'
item.value['FR'] = ('Recette tellurique qui prend les étoiles chaudes et '
                    'calcule leur transmission atmosphérique (à ajouter à la '
                    'base ACP)')
item.value['ES'] = ('Receta telúrica que toma estrellas calientes y calcula '
                    'su transmisión atmosférica (para añadir a la base de '
                    'datos PCA)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# MKTELL_EXAMPLE 
# =============================================================================
item = langlist.create('MKTELL_EXAMPLE', kind='HELP')
item.value['ENG'] = 'obj_mk_tellu_spirou.py [NIGHT_NAME] [OBJ_DARK E2DSFF AB] \n obj_mk_tellu_spirou.py [NIGHT_NAME] [OBJ_FP E2DSFF AB] '
item.value['FR'] = ('obj_mk_tellu_spirou.py [NIGHT_NAME] [OBJ_DARK E2DSFF '
                    'AB] \n obj_mk_tellu_spirou.py [NIGHT_NAME] [OBJ_FP '
                    'E2DSFF AB] ')
item.value['ES'] = ('obj_mk_tellu_spirou.py [NIGHT_NAME] [OBJ_DARK E2DSFF '
                    'AB] \n obj_mk_tellu_spirou.py [NIGHT_NAME] [OBJ_FP '
                    'E2DSFF AB] ')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# MKTELL_FILES_HELP 
# =============================================================================
item = langlist.create('MKTELL_FILES_HELP', kind='HELP')
item.value['ENG'] = 'Currently  allowed types: E2DS, E2DSFF'
item.value['FR'] = 'Types actuellement autorisés : E2DS, E2DSFF'
item.value['ES'] = 'Tipos permitidos actualmente: E2DS, E2DSFF'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FTELLU_DESC 
# =============================================================================
item = langlist.create('FTELLU_DESC', kind='HELP')
item.value['ENG'] = 'Telluric recipe to correct science spectra using transmission maps and pca fit.'
item.value['FR'] = ('Recette tellurique pour corriger les spectres science '
                    'avec les cartes de transmission et un ajustement ACP.')
item.value['ES'] = ('Receta telúrica para corregir espectros de ciencia '
                    'usando mapas de transmisión y un ajuste PCA.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FTELLU_EXAMPLE 
# =============================================================================
item = langlist.create('FTELLU_EXAMPLE', kind='HELP')
item.value['ENG'] = 'obj_fit_tellu_spirou.py [NIGHT_NAME] [OBJ_DARK E2DSFF AB] \n obj_fit_tellu_spirou.py [NIGHT_NAME] [OBJ_FP E2DSFF AB]'
item.value['FR'] = ('obj_fit_tellu_spirou.py [NIGHT_NAME] [OBJ_DARK E2DSFF '
                    'AB] \n obj_fit_tellu_spirou.py [NIGHT_NAME] [OBJ_FP '
                    'E2DSFF AB]')
item.value['ES'] = ('obj_fit_tellu_spirou.py [NIGHT_NAME] [OBJ_DARK E2DSFF '
                    'AB] \n obj_fit_tellu_spirou.py [NIGHT_NAME] [OBJ_FP '
                    'E2DSFF AB]')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FTELLU_FILES_HELP 
# =============================================================================
item = langlist.create('FTELLU_FILES_HELP', kind='HELP')
item.value['ENG'] = 'Currently  allowed types: E2DS, E2DSFF'
item.value['FR'] = 'Types actuellement autorisés : E2DS, E2DSFF'
item.value['ES'] = 'Tipos permitidos actualmente: E2DS, E2DSFF'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# USE_TEMP_HELP 
# =============================================================================
item = langlist.create('USE_TEMP_HELP', kind='HELP')
item.value['ENG'] = 'Whether to use the template provided from the telluric database'
item.value['FR'] = ('Utiliser ou non le modèle fourni par la base de données '
                    'tellurique')
item.value['ES'] = ('Si usar la plantilla proporcionada por la base de datos '
                    'telúrica')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TEMPLATE_FILE_HELP 
# =============================================================================
item = langlist.create('TEMPLATE_FILE_HELP', kind='HELP')
item.value['ENG'] = 'Filename of the custom template to use (instead of from telluric database)'
item.value['FR'] = ('Nom de fichier du modèle personnalisé à utiliser (au '
                    'lieu de celui de la base de données tellurique)')
item.value['ES'] = ('Nombre de archivo de la plantilla personalizada a usar '
                    '(en lugar de la de la base de datos telúrica)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# MKTEMP_DESC 
# =============================================================================
item = langlist.create('MKTEMP_DESC', kind='HELP')
item.value['ENG'] = 'Telluric recipe to create template spectra (median of many observations) of the same object. Used to provide a better SED of stars in obj_mk_tellu and obj_fit_tellu. Note only needs to be run once for each science / hot star target.'
item.value['FR'] = ('Recette tellurique pour créer des spectres modèles '
                    "(médiane de nombreuses observations) d'un même objet. "
                    'Sert à fournir une meilleure SED des étoiles dans '
                    'obj_mk_tellu et obj_fit_tellu. À exécuter une seule fois '
                    'par cible science / étoile chaude.')
item.value['ES'] = ('Receta telúrica para crear espectros de plantilla '
                    '(mediana de muchas observaciones) del mismo objeto. Se '
                    'usa para obtener una mejor SED de las estrellas en '
                    'obj_mk_tellu y obj_fit_tellu. Solo es necesario '
                    'ejecutarla una vez por objetivo de ciencia / estrella '
                    'caliente.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# MKTEMP_EXAMPLE 
# =============================================================================
item = langlist.create('MKTEMP_EXAMPLE', kind='HELP')
item.value['ENG'] = 'obj_mk_template_spirou.py [OBJNAME] \n obj_mk_template_spirou.py Gl699'
item.value['FR'] = ('obj_mk_template_spirou.py [OBJNAME] \n '
                    'obj_mk_template_spirou.py Gl699')
item.value['ES'] = ('obj_mk_template_spirou.py [OBJNAME] \n '
                    'obj_mk_template_spirou.py Gl699')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# MKTEMP_OBJNAME_HELP 
# =============================================================================
item = langlist.create('MKTEMP_OBJNAME_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The object name to process'
item.value['FR'] = "[STRING] Le nom de l'objet à traiter"
item.value['ES'] = '[STRING] El nombre del objeto a procesar'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# MKTEMP_FILETYPE 
# =============================================================================
item = langlist.create('MKTEMP_FILETYPE', kind='HELP')
item.value['ENG'] = '[STRING] optional, the filetype (KW_OUTPUT) to use when processing files'
item.value['FR'] = ('[STRING] optionnel, le type de fichier (KW_OUTPUT) à '
                    'utiliser pour traiter les fichiers')
item.value['ES'] = ('[STRING] opcional, el tipo de archivo (KW_OUTPUT) a usar '
                    'al procesar archivos')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# MKTEMP_FIBER 
# =============================================================================
item = langlist.create('MKTEMP_FIBER', kind='HELP')
item.value['ENG'] = '[STRING] optional, the fiber type to use when processing files'
item.value['FR'] = ('[STRING] optionnel, le type de fibre à utiliser pour '
                    'traiter les fichiers')
item.value['ES'] = ('[STRING] opcional, el tipo de fibra a usar al procesar '
                    'archivos')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# MKTELLDB_DESC 
# =============================================================================
item = langlist.create('MKTELLDB_DESC', kind='HELP')
item.value['ENG'] = 'Make telluric database on all found, extracted telluric stars (runs mk_tellu, fit_tellu, mk_template, mk_tellu)'
item.value['FR'] = ('Créer la base de données tellurique sur toutes les '
                    'étoiles telluriques extraites trouvées (exécute '
                    'mk_tellu, fit_tellu, mk_template, mk_tellu)')
item.value['ES'] = ('Crear la base de datos telúrica con todas las estrellas '
                    'telúricas extraídas encontradas (ejecuta mk_tellu, '
                    'fit_tellu, mk_template, mk_tellu)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# MKTELLDB_EXAMPLE 
# =============================================================================
item = langlist.create('MKTELLDB_EXAMPLE', kind='HELP')
item.value['ENG'] = 'obj_mk_tellu_db_spirou.py \n\t obj_mk_tellu_db_spirou.py --cores=10 --filetype=EXT_E2DS_FF –fiber=AB'
item.value['FR'] = ('obj_mk_tellu_db_spirou.py \n\t obj_mk_tellu_db_spirou.py '
                    '--cores=10 --filetype=EXT_E2DS_FF –fiber=AB')
item.value['ES'] = ('obj_mk_tellu_db_spirou.py \n\t obj_mk_tellu_db_spirou.py '
                    '--cores=10 --filetype=EXT_E2DS_FF –fiber=AB')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# MKTELLDB_FILETYPE 
# =============================================================================
item = langlist.create('MKTELLDB_FILETYPE', kind='HELP')
item.value['ENG'] = '[STRING] optional, the filetype (KW_OUTPUT) to use when processing files'
item.value['FR'] = ('[STRING] optionnel, le type de fichier (KW_OUTPUT) à '
                    'utiliser pour traiter les fichiers')
item.value['ES'] = ('[STRING] opcional, el tipo de archivo (KW_OUTPUT) a usar '
                    'al procesar archivos')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# MKTELLDB_FIBER 
# =============================================================================
item = langlist.create('MKTELLDB_FIBER', kind='HELP')
item.value['ENG'] = '[STRING] optional, the fiber type to use when processing files'
item.value['FR'] = ('[STRING] optionnel, le type de fibre à utiliser pour '
                    'traiter les fichiers')
item.value['ES'] = ('[STRING] opcional, el tipo de fibra a usar al procesar '
                    'archivos')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# MKTELLDB_CORES 
# =============================================================================
item = langlist.create('MKTELLDB_CORES', kind='HELP')
item.value['ENG'] = '[INTEGER] The number of cores to use'
item.value['FR'] = '[INTEGER] Le nombre de cœurs à utiliser'
item.value['ES'] = '[INTEGER] El número de núcleos a usar'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FTELLUDB_DESC 
# =============================================================================
item = langlist.create('FTELLUDB_DESC', kind='HELP')
item.value['ENG'] = 'Make telluric database on all found, extracted science targets (runs fit_tellu, mk_template, fit_tellu)'
item.value['FR'] = ('Créer la base de données tellurique sur toutes les '
                    'cibles science extraites trouvées (exécute fit_tellu, '
                    'mk_template, fit_tellu)')
item.value['ES'] = ('Crear la base de datos telúrica con todos los objetivos '
                    'de ciencia extraídos encontrados (ejecuta fit_tellu, '
                    'mk_template, fit_tellu)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FTELLUDB_EXAMPLE 
# =============================================================================
item = langlist.create('FTELLUDB_EXAMPLE', kind='HELP')
item.value['ENG'] = 'obj_fit_tellu_db_spirou.py \n\t obj_fit_tellu_db_spirou.py --cores=10 --filetype=EXT_E2DS_FF –fiber=AB'
item.value['FR'] = ('obj_fit_tellu_db_spirou.py \n\t '
                    'obj_fit_tellu_db_spirou.py --cores=10 '
                    '--filetype=EXT_E2DS_FF –fiber=AB')
item.value['ES'] = ('obj_fit_tellu_db_spirou.py \n\t '
                    'obj_fit_tellu_db_spirou.py --cores=10 '
                    '--filetype=EXT_E2DS_FF –fiber=AB')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FTELLUDB_FILETYPE 
# =============================================================================
item = langlist.create('FTELLUDB_FILETYPE', kind='HELP')
item.value['ENG'] = '[STRING] optional, the filetype (KW_OUTPUT) to use when processing files'
item.value['FR'] = ('[STRING] optionnel, le type de fichier (KW_OUTPUT) à '
                    'utiliser pour traiter les fichiers')
item.value['ES'] = ('[STRING] opcional, el tipo de archivo (KW_OUTPUT) a usar '
                    'al procesar archivos')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FTELLUDB_FIBER 
# =============================================================================
item = langlist.create('FTELLUDB_FIBER', kind='HELP')
item.value['ENG'] = '[STRING] optional, the fiber type to use when processing files'
item.value['FR'] = ('[STRING] optionnel, le type de fibre à utiliser pour '
                    'traiter les fichiers')
item.value['ES'] = ('[STRING] opcional, el tipo de fibra a usar al procesar '
                    'archivos')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FTELLUDB_CORES 
# =============================================================================
item = langlist.create('FTELLUDB_CORES', kind='HELP')
item.value['ENG'] = '[INTEGER] The number of cores to use'
item.value['FR'] = '[INTEGER] Le nombre de cœurs à utiliser'
item.value['ES'] = '[INTEGER] El número de núcleos a usar'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FTELLUDB_DPRTYPES 
# =============================================================================
item = langlist.create('FTELLUDB_DPRTYPES', kind='HELP')
item.value['ENG'] = '[STRING] the DPRTYPE (i.e. OBJ_FP or OBJ_DARK) used for telluric database. Can be a list (separate by commas)'
item.value['FR'] = ('[STRING] le DPRTYPE (c.-à-d. OBJ_FP ou OBJ_DARK) utilisé '
                    'pour la base tellurique. Peut être une liste (séparée '
                    'par des virgules)')
item.value['ES'] = ('[STRING] el DPRTYPE (es decir OBJ_FP u OBJ_DARK) usado '
                    'para la base telúrica. Puede ser una lista (separada por '
                    'comas)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FTELLUDB_OBJNAME 
# =============================================================================
item = langlist.create('FTELLUDB_OBJNAME', kind='HELP')
item.value['ENG'] = '[STRING] the object name to process (optional if not set will do all non-telluric objects)'
item.value['FR'] = ("[STRING] le nom d'objet à traiter (optionnel ; si non "
                    'défini, traite tous les objets non telluriques)')
item.value['ES'] = ('[STRING] el nombre de objeto a procesar (opcional; si no '
                    'se define procesa todos los objetos no telúricos)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# CCF_DESC 
# =============================================================================
item = langlist.create('CCF_DESC', kind='HELP')
item.value['ENG'] = 'Run the cross-correlation recipe in order to calculate the RV of an object.'
item.value['FR'] = ('Exécuter la recette de corrélation croisée pour calculer '
                    "la RV d'un objet.")
item.value['ES'] = ('Ejecutar la receta de correlación cruzada para calcular '
                    'la RV de un objeto.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# CCF_EXAMPLE 
# =============================================================================
item = langlist.create('CCF_EXAMPLE', kind='HELP')
item.value['ENG'] = 'cal_ccf_spirou.py [NIGHT_NAME] [EXT_E2DS] \ncal_ccf_spirou.py [NIGHT_NAME] [EXT_E2DSFF]\ncal_ccf_spirou.py [NIGHT_NAME] [TELLU_OBJ]  '
item.value['FR'] = ('cal_ccf_spirou.py [NIGHT_NAME] [EXT_E2DS] \n'
                    'cal_ccf_spirou.py [NIGHT_NAME] [EXT_E2DSFF]\n'
                    'cal_ccf_spirou.py [NIGHT_NAME] [TELLU_OBJ]  ')
item.value['ES'] = ('cal_ccf_spirou.py [NIGHT_NAME] [EXT_E2DS] \n'
                    'cal_ccf_spirou.py [NIGHT_NAME] [EXT_E2DSFF]\n'
                    'cal_ccf_spirou.py [NIGHT_NAME] [TELLU_OBJ]  ')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# CCF_FILES_HELP 
# =============================================================================
item = langlist.create('CCF_FILES_HELP', kind='HELP')
item.value['ENG'] = 'Currently allowed types: E2DS, E2DSFF, TELLU_OBJ (For dprtype = OBJ_FP, OBJ_DARK)'
item.value['FR'] = ('Types actuellement autorisés : E2DS, E2DSFF, TELLU_OBJ '
                    '(pour dprtype = OBJ_FP, OBJ_DARK)')
item.value['ES'] = ('Tipos permitidos actualmente: E2DS, E2DSFF, TELLU_OBJ '
                    '(para dprtype = OBJ_FP, OBJ_DARK)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# CCF_MASK_HELP 
# =============================================================================
item = langlist.create('CCF_MASK_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Define the filename to the CCF mask to use. Can be full path or a file in the ./data/spirou/ccf/ folder'
item.value['FR'] = ('[STRING] Définir le nom du fichier masque CCF à '
                    'utiliser. Chemin complet ou fichier du dossier '
                    './data/spirou/ccf/')
item.value['ES'] = ('[STRING] Definir el nombre del archivo de máscara CCF a '
                    'usar. Puede ser una ruta completa o un archivo de la '
                    'carpeta ./data/spirou/ccf/')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# CCF_RV_HELP 
# =============================================================================
item = langlist.create('CCF_RV_HELP', kind='HELP')
item.value['ENG'] = '[FLOAT] The target RV to use as a center for the CCF fit (in km/s)'
item.value['FR'] = ('[FLOAT] La RV cible à utiliser comme centre pour '
                    "l'ajustement de la CCF (en km/s)")
item.value['ES'] = ('[FLOAT] La RV objetivo a usar como centro para el ajuste '
                    'de la CCF (en km/s)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# CCF_WIDTH_HELP 
# =============================================================================
item = langlist.create('CCF_WIDTH_HELP', kind='HELP')
item.value['ENG'] = '[FLOAT] The CCF width to use for the CCF fit (in km/s)'
item.value['FR'] = ('[FLOAT] La largeur de la CCF à utiliser pour '
                    "l'ajustement de la CCF (en km/s)")
item.value['ES'] = ('[FLOAT] El ancho de la CCF a usar para el ajuste de la '
                    'CCF (en km/s)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# CCF_STEP_HELP 
# =============================================================================
item = langlist.create('CCF_STEP_HELP', kind='HELP')
item.value['ENG'] = '[FLOAT] The CCF step to use for the CCF fit (in km/s)'
item.value['FR'] = ("[FLOAT] Le pas de la CCF à utiliser pour l'ajustement de "
                    'la CCF (en km/s)')
item.value['ES'] = ('[FLOAT] El paso de la CCF a usar para el ajuste de la '
                    'CCF (en km/s)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# CCF_MASK_NORM_HELP 
# =============================================================================
item = langlist.create('CCF_MASK_NORM_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Define the type of normalization to apply to ccf masks, \'all\' normalized across all orders, \'order\' normalizes independently for each order, \'None\' applies no mask normalization'
item.value['FR'] = ('[STRING] Définir le type de normalisation des masques '
                    "ccf, 'all' normalise sur tous les ordres, 'order' "
                    "normalise chaque ordre indépendamment, 'None' n'applique "
                    'aucune normalisation')
item.value['ES'] = ('[STRING] Definir el tipo de normalización de las '
                    "máscaras ccf, 'all' normaliza en todos los órdenes, "
                    "'order' normaliza cada orden de forma independiente, "
                    "'None' no aplica normalización")
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LEAKREF_DESC 
# =============================================================================
item = langlist.create('LEAKREF_DESC', kind='HELP')
item.value['ENG'] = 'Creates the reference dark_fp used for correcting the leakage from fiber C for extraction products'
item.value['FR'] = ('Crée le dark_fp de référence utilisé pour corriger la '
                    "fuite de la fibre C dans les produits d'extraction")
item.value['ES'] = ('Crea el dark_fp de referencia usado para corregir la '
                    'fuga de la fibra C en los productos de extracción')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LEAKREF_EXAMPLE 
# =============================================================================
item = langlist.create('LEAKREF_EXAMPLE', kind='HELP')
item.value['ENG'] = 'cal_leak_reference_spirou.py [NIGHT_NAME]'
item.value['FR'] = 'cal_leak_reference_spirou.py [NIGHT_NAME]'
item.value['ES'] = 'cal_leak_reference_spirou.py [NIGHT_NAME]'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LEAKREF_HELP_FILETYPE 
# =============================================================================
item = langlist.create('LEAKREF_HELP_FILETYPE', kind='HELP')
item.value['ENG'] = '[STRING] Specify the DPRTYPE for DARK_FP files'
item.value['FR'] = '[STRING] Spécifier le DPRTYPE des fichiers DARK_FP'
item.value['ES'] = '[STRING] Especificar el DPRTYPE de los archivos DARK_FP'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LEAK_DESC 
# =============================================================================
item = langlist.create('LEAK_DESC', kind='HELP')
item.value['ENG'] = 'Correct the FP leakage on extraction files using the leak reference files'
item.value['FR'] = ("Corriger la fuite FP sur les fichiers d'extraction avec "
                    'les fichiers de référence de fuite')
item.value['ES'] = ('Corregir la fuga FP en los archivos de extracción usando '
                    'los archivos de referencia de fuga')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LEAK_EXAMPLE 
# =============================================================================
item = langlist.create('LEAK_EXAMPLE', kind='HELP')
item.value['ENG'] = 'cal_leak_spirou.py [NIGHT_NAME] [OBJ_FP E2DSFF AB] \n cal_leak_spirou 2018-08-05 '
item.value['FR'] = ('cal_leak_spirou.py [NIGHT_NAME] [OBJ_FP E2DSFF AB] \n '
                    'cal_leak_spirou 2018-08-05 ')
item.value['ES'] = ('cal_leak_spirou.py [NIGHT_NAME] [OBJ_FP E2DSFF AB] \n '
                    'cal_leak_spirou 2018-08-05 ')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LEAK_FILES_HELP 
# =============================================================================
item = langlist.create('LEAK_FILES_HELP', kind='HELP')
item.value['ENG'] = 'Current accepts EXT_E2DSFF OBJ_FP files'
item.value['FR'] = 'Accepte actuellement les fichiers EXT_E2DSFF OBJ_FP'
item.value['ES'] = 'Actualmente acepta archivos EXT_E2DSFF OBJ_FP'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LEAK_LEAKFILE_HELP 
# =============================================================================
item = langlist.create('LEAK_LEAKFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] optional, the leak reference file to use'
item.value['FR'] = ('[STRING] optionnel, le fichier de référence de fuite à '
                    'utiliser')
item.value['ES'] = '[STRING] opcional, el archivo de referencia de fuga a usar'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# OUT_DESC_HELP 
# =============================================================================
item = langlist.create('OUT_DESC_HELP', kind='HELP')
item.value['ENG'] = 'Post processing of reduced files into the final outputs'
item.value['FR'] = 'Post-traitement des fichiers réduits en produits finaux'
item.value['ES'] = ('Post-procesamiento de los archivos reducidos en las '
                    'salidas finales')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# OUT_CLEAR_HELP 
# =============================================================================
item = langlist.create('OUT_CLEAR_HELP', kind='HELP')
item.value['ENG'] = 'Clear the reduced folder after post-processing. WARNING removes all files from the reduced directory.'
item.value['FR'] = ('Vider le dossier reduced après le post-traitement. '
                    'ATTENTION : supprime tous les fichiers du répertoire '
                    'reduced.')
item.value['ES'] = ('Vaciar la carpeta reduced tras el post-procesamiento. '
                    'ADVERTENCIA: elimina todos los archivos del directorio '
                    'reduced.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# OUT_OVERWRITE_HELP 
# =============================================================================
item = langlist.create('OUT_OVERWRITE_HELP', kind='HELP')
item.value['ENG'] = 'Overwrites post processed files if they exist (default is False)'
item.value['FR'] = ("Écrase les fichiers post-traités s'ils existent (par "
                    'défaut False)')
item.value['ES'] = ('Sobrescribe los archivos post-procesados si existen (por '
                    'defecto False)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# OUT_NIGHT_HELP 
# =============================================================================
item = langlist.create('OUT_NIGHT_HELP', kind='HELP')
item.value['ENG'] = 'Define a single night to produce post processed files for'
item.value['FR'] = ('Définir une seule nuit pour laquelle produire des '
                    'fichiers post-traités')
item.value['ES'] = ('Definir una sola noche para la que producir archivos '
                    'post-procesados')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# OUT_WNIGHTLIST_HELP 
# =============================================================================
item = langlist.create('OUT_WNIGHTLIST_HELP', kind='HELP')
item.value['ENG'] = 'Define a list (comma separated no spaces) of nights to produce post processed files for'
item.value['FR'] = ('Définir une liste (séparée par des virgules, sans '
                    'espaces) de nuits pour lesquelles produire des fichiers '
                    'post-traités')
item.value['ES'] = ('Definir una lista (separada por comas sin espacios) de '
                    'noches para las que producir archivos post-procesados')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# OUT_BNIGHTLIST_HELP 
# =============================================================================
item = langlist.create('OUT_BNIGHTLIST_HELP', kind='HELP')
item.value['ENG'] = 'Define a list (comma separated no spaces) of nights to NOT produce post processed files for'
item.value['FR'] = ('Définir une liste (séparée par des virgules, sans '
                    'espaces) de nuits pour lesquelles NE PAS produire de '
                    'fichiers post-traités')
item.value['ES'] = ('Definir una lista (separada por comas sin espacios) de '
                    'noches para las que NO producir archivos post-procesados')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# WAVEM_CAVFILE_HELP 
# =============================================================================
item = langlist.create('WAVEM_CAVFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Define a custom cavity file (overrides default)'
item.value['FR'] = ('[STRING] Définir un fichier de cavité personnalisé '
                    '(remplace la valeur par défaut)')
item.value['ES'] = ('[STRING] Definir un archivo de cavidad personalizado '
                    '(reemplaza el valor por defecto)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LEAKCORR_HELP 
# =============================================================================
item = langlist.create('LEAKCORR_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Sets whether to do the leak correction (else defaults to CORRECT_LEAKAGE value in constants)'
item.value['FR'] = ('[BOOLEAN] Définit si la correction de fuite est faite '
                    '(sinon valeur CORRECT_LEAKAGE des constantes)')
item.value['ES'] = ('[BOOLEAN] Define si se hace la corrección de fuga (si '
                    'no, se usa el valor CORRECT_LEAKAGE de las constantes)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
