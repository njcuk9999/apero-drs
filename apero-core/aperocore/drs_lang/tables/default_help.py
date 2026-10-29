
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
__NAME__ = 'apero.lang.tables.default_help.py'
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
item.value['ENG'] = 'This is the default DRS description message'
item.value['FR'] = 'Ceci est le message de description par défaut du DRS'
item.value['ES'] = 'Este es el mensaje de descripción por defecto del DRS'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# KEYERROR
# =============================================================================
item = langlist.create('KEYERROR', kind='HELP')
item.value['ENG'] = 'Key {0} not found. Function = {1}'
item.value['ES'] = 'Clave {0} no encontrada. Función = {1}'
item.value['FR'] = 'Clé {0} introuvable. Fonction = {1}'
item.arguments = 'None'
item.comment = 'This is the default key error'
langlist.add(item)

# =============================================================================
# ADD_CAL_HELP
# =============================================================================
item = langlist.create('ADD_CAL_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Whether to add outputs to calibration/telluric databases'
item.value['ES'] = ('[BOOLEAN] Si añadir las salidas a las bases de datos de '
                    'calibración/telúricas')
item.value['FR'] = '[BOOLEAN] S\'il faut ajouter des sorties à la base de données d\'étalonnage/telluriques'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ALLLISTING_HELP
# =============================================================================
item = langlist.create('ALLLISTING_HELP', kind='HELP')
item.value['ENG'] = 'Lists ALL the night name directories in the input directory if used without a \'directory\' argument or lists the files in the given \'directory\' (if defined)'
item.value['ES'] = ('Lista TODOS los directorios de noche del directorio de '
                    "entrada si se usa sin el argumento 'directory', o lista "
                    "los archivos del 'directory' dado (si se define)")
item.value['FR'] = 'Répertorie TOUS les répertoires de noms de nuit du répertoire d\'entrée s\'il est utilisé sans l\'argument \'directory\' ou répertorie les fichiers du \'répertoire\' donné (si défini)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# AND_TEXT
# =============================================================================
item = langlist.create('AND_TEXT', kind='TEXT')
item.value['ENG'] = 'and'
item.value['ES'] = 'y'
item.value['FR'] = 'et'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ASTROMETRIC_DESCRIPTION
# =============================================================================
item = langlist.create('ASTROMETRIC_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Run this recipe to check, find and/or add targets to the online astrometric database'
item.value['FR'] = ('Exécutez cette recette pour vérifier, trouver et/ou '
                    'ajouter des cibles à la base de données astrométrique en '
                    'ligne')
item.value['ES'] = ('Ejecute esta receta para comprobar, encontrar y/o añadir '
                    'objetivos a la base de datos astrométrica en línea')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ASTROMETRIC_OBJ_HELP
# =============================================================================
item = langlist.create('ASTROMETRIC_OBJ_HELP', kind='HELP')
item.value['ENG'] = '[STRING] A list of object names to check, find and/or add to the online database. Should be comma separated without white spaces'
item.value['FR'] = ("[STRING] Une liste de noms d'objets à vérifier, trouver "
                    'et/ou ajouter à la base de données en ligne. Séparés par '
                    'des virgules sans espaces')
item.value['ES'] = ('[STRING] Una lista de nombres de objetos a comprobar, '
                    'encontrar y/o añadir a la base de datos en línea. '
                    'Separados por comas sin espacios')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# BREAKFUNC_HELP
# =============================================================================
item = langlist.create('BREAKFUNC_HELP', kind='HELP')
item.value['ENG'] = 'Given a function name will break when this function is found (only if function contains display_func)'
item.value['FR'] = ("Étant donné un nom de fonction, s'arrête lorsque cette "
                    'fonction est trouvée (seulement si la fonction contient '
                    'display_func)')
item.value['ES'] = ('Dado un nombre de función, se detendrá cuando se '
                    'encuentre esta función (solo si la función contiene '
                    'display_func)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# BREAKPOINTS_HELP
# =============================================================================
item = langlist.create('BREAKPOINTS_HELP', kind='HELP')
item.value['ENG'] = 'If set then any breakpoints in the code are executed'
item.value['FR'] = "Si défini, tous les points d'arrêt du code sont exécutés"
item.value['ES'] = ('Si se define, se ejecutan todos los puntos de '
                    'interrupción del código')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# C_OR
# =============================================================================
item = langlist.create('C_OR', kind='TEXT')
item.value['ENG'] = 'or'
item.value['FR'] = 'ou'
item.value['ES'] = 'o'
item.arguments = 'None'
item.comment = 'text for \"or\" logical condition'
langlist.add(item)

# =============================================================================
# C_AND
# =============================================================================
item = langlist.create('C_AND', kind='TEXT')
item.value['ENG'] = 'and'
item.value['FR'] = 'et'
item.value['ES'] = 'y'
item.arguments = 'None'
item.comment = 'text for \"and\" logical condition'
langlist.add(item)

# =============================================================================
# C_NO
# =============================================================================
item = langlist.create('C_NO', kind='TEXT')
item.value['ENG'] = 'N'
item.value['ES'] = 'N'
item.value['FR'] = 'N'
item.arguments = 'None'
item.comment = 'character for no'
langlist.add(item)

# =============================================================================
# C_YES
# =============================================================================
item = langlist.create('C_YES', kind='TEXT')
item.value['ENG'] = 'Y'
item.value['ES'] = 'Y'
item.value['FR'] = 'O'
item.arguments = 'None'
item.comment = 'character for yes'
langlist.add(item)

# =============================================================================
# C_YES_OR_NO
# =============================================================================
item = langlist.create('C_YES_OR_NO', kind='TEXT')
item.value['ENG'] = '[Y]es or [N]o'
item.value['ES'] = '[Y] sí o [N] no'
item.value['FR'] = '[O]ui ou [N[on'
item.arguments = 'None'
item.comment = 'question for yes or no characters'
langlist.add(item)

# =============================================================================
# C_OPTIONS_ARE
# =============================================================================
item = langlist.create('C_OPTIONS_ARE', kind='TEXT')
item.value['ENG'] = 'Options are'
item.value['FR'] = 'Les options sont'
item.value['ES'] = 'Las opciones son'
item.arguments = 'None'
item.comment = 'options are text'
langlist.add(item)

# =============================================================================
# C_DEFAULT_IS
# =============================================================================
item = langlist.create('C_DEFAULT_IS', kind='TEXT')
item.value['ENG'] = 'Default is'
item.value['FR'] = 'Par défaut'
item.value['ES'] = 'Por defecto es'
item.arguments = 'None'
item.comment = 'default is text'
langlist.add(item)

# =============================================================================
# CHANGELOG_DESCRIPTION
# =============================================================================
item = langlist.create('CHANGELOG_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Produces a nicely formatted change log (using git). Requires gitchangelog to be installed via \'pip install gitchangelog\''
item.value['FR'] = ('Produit un journal des modifications bien formaté (avec '
                    "git). Nécessite gitchangelog installé via 'pip install "
                    "gitchangelog'")
item.value['ES'] = ('Produce un registro de cambios bien formateado (usando '
                    "git). Requiere gitchangelog instalado con 'pip install "
                    "gitchangelog'")
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_CSVARG_HELP
# =============================================================================
item = langlist.create('DBMGR_CSVARG_HELP', kind='TEXT')
item.value['ENG'] = 'Path to csv file. For --importdb this is the csv file you wish to add. For --exportdb this is the csv file that will be saved.'
item.value['FR'] = ("Chemin du fichier csv. Pour --importdb c'est le fichier "
                    "csv à ajouter. Pour --exportdb c'est le fichier csv qui "
                    'sera enregistré.')
item.value['ES'] = ('Ruta al archivo csv. Para --importdb es el archivo csv '
                    'que desea añadir. Para --exportdb es el archivo csv que '
                    'se guardará.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_DESCRIPTION
# =============================================================================
item = langlist.create('DBMGR_DESCRIPTION', kind='TEXT')
item.value['ENG'] = 'APERO database manager functionality'
item.value['FR'] = 'Fonctionnalité du gestionnaire de bases de données APERO'
item.value['ES'] = 'Funcionalidad del gestor de bases de datos APERO'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_EXPORTDB_HELP
# =============================================================================
item = langlist.create('DBMGR_EXPORTDB_HELP', kind='TEXT')
item.value['ENG'] = 'Export a database to a csv file'
item.value['FR'] = 'Exporter une base de données vers un fichier csv'
item.value['ES'] = 'Exportar una base de datos a un archivo csv'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_IMPORTDB_HELP
# =============================================================================
item = langlist.create('DBMGR_IMPORTDB_HELP', kind='TEXT')
item.value['ENG'] = 'Import a csv file into a database'
item.value['FR'] = 'Importer un fichier csv dans une base de données'
item.value['ES'] = 'Importar un archivo csv a una base de datos'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_JOIN_HELP
# =============================================================================
item = langlist.create('DBMGR_JOIN_HELP', kind='TEXT')
item.value['ENG'] = 'How to add the csv file to database: append adds all lines to the end of current database, replace removes all previous lines from database. Default is ‘replace’.'
item.value['FR'] = ('Comment ajouter le fichier csv à la base de données : '
                    'append ajoute toutes les lignes à la fin de la base '
                    'actuelle, replace supprime toutes les lignes '
                    'précédentes. Par défaut ‘replace’.')
item.value['ES'] = ('Cómo añadir el archivo csv a la base de datos: append '
                    'añade todas las líneas al final de la base actual, '
                    'replace elimina todas las líneas previas. Por defecto es '
                    '‘replace’.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_KILLARG_HELP
# =============================================================================
item = langlist.create('DBMGR_KILLARG_HELP', kind='TEXT')
item.value['ENG'] = 'Use this when database is stuck and you have no other opens (mysql only)'
item.value['FR'] = ('À utiliser lorsque la base de données est bloquée et '
                    "qu'il n'y a pas d'autre solution (mysql uniquement)")
item.value['ES'] = ('Úselo cuando la base de datos esté bloqueada y no tenga '
                    'otras opciones (solo mysql)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_UPDATE_HELP
# =============================================================================
item = langlist.create('DBMGR_UPDATE_HELP', kind='TEXT')
item.value['ENG'] = 'Use this to update the database based on files on disk in the correct directories (Currently updates calib/tellu/log and index databases)'
item.value['FR'] = ('Utiliser ceci pour mettre à jour la base de données à '
                    'partir des fichiers sur disque dans les bons répertoires '
                    '(met actuellement à jour les bases calib/tellu/log et '
                    'index)')
item.value['ES'] = ('Use esto para actualizar la base de datos a partir de '
                    'los archivos en disco en los directorios correctos '
                    '(actualmente actualiza las bases calib/tellu/log e index)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DEBUG_HELP
# =============================================================================
item = langlist.create('DEBUG_HELP', kind='HELP')
item.value['ENG'] = 'Activates debug mode (Advanced mode [INTEGER] value must be an integer greater than 0, setting the debug level)'
item.value['ES'] = ('Activa el modo depuración (modo avanzado: el valor '
                    '[INTEGER] debe ser un entero mayor que 0, que define el '
                    'nivel de depuración)')
item.value['FR'] = 'Active le mode débogage (la valeur en mode avancé [INTEGER] doit être un entier supérieur à 0, définissant le niveau de débogage)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DEPENDENCIES_DESCRIPTION
# =============================================================================
item = langlist.create('DEPENDENCIES_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Run a dependency check on the DRS (Will display all modules required and some stats)'
item.value['FR'] = ('Effectuer une vérification des dépendances du DRS '
                    '(affiche tous les modules requis et des statistiques)')
item.value['ES'] = ('Realizar una comprobación de dependencias del DRS '
                    '(muestra todos los módulos requeridos y algunas '
                    'estadísticas)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DESCRIPTION_TEXT
# =============================================================================
item = langlist.create('DESCRIPTION_TEXT', kind='TEXT')
item.value['ENG'] = ' Description:'
item.value['ES'] = ' Descripción:'
item.value['FR'] = ' La description: '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DIRECTORY_HELP
# =============================================================================
item = langlist.create('DIRECTORY_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The \'night_name\' or absolute path of the directory'
item.value['ES'] = "[STRING] El 'night_name' o la ruta absoluta del directorio"
item.value['FR'] = '[STRING] Le \'night_name\' ou chemin absolu du répertoire '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXAMPLES_TEXT
# =============================================================================
item = langlist.create('EXAMPLES_TEXT', kind='TEXT')
item.value['ENG'] = ' Example uses:'
item.value['ES'] = ' Ejemplos de uso:'
item.value['FR'] = ' Exemple d\'utilisation: '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXPLORER_DESCRIPTION
# =============================================================================
item = langlist.create('EXPLORER_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Opens a GUI browser to help one navigate the raw, working and reduced directories. Displays all files and a select set of header keys'
item.value['FR'] = ('Ouvre un navigateur graphique pour parcourir les '
                    'répertoires raw, working et reduced. Affiche tous les '
                    "fichiers et une sélection de clés d'en-tête")
item.value['ES'] = ('Abre un navegador gráfico para recorrer los directorios '
                    'raw, working y reduced. Muestra todos los archivos y una '
                    'selección de claves de cabecera')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXPLORER_HASH
# =============================================================================
item = langlist.create('EXPLORER_HASH', kind='TEXT')
item.value['ENG'] = 'Display all hash columns (hidden by default)'
item.value['FR'] = ('Afficher toutes les colonnes de hachage (masquées par '
                    'défaut)')
item.value['ES'] = 'Mostrar todas las columnas de hash (ocultas por defecto)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXPLORER_INST_HEPL
# =============================================================================
item = langlist.create('EXPLORER_INST_HEPL', kind='HELP')
item.value['ENG'] = '[STRING] The instrument to nagivate'
item.value['FR'] = "[STRING] L'instrument à parcourir"
item.value['ES'] = '[STRING] El instrumento a explorar'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FILE_HELP
# =============================================================================
item = langlist.create('FILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] A single fits files. '
item.value['ES'] = '[STRING] Un único archivo fits. '
item.value['FR'] = '[STRING] Un seul correspond à des fichiers. '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FILES_HELP
# =============================================================================
item = langlist.create('FILES_HELP', kind='HELP')
item.value['ENG'] = '[STRING/STRINGS] A list of fits files to use separated by spaces. '
item.value['ES'] = ('[STRING/STRINGS] Una lista de archivos fits a usar '
                    'separados por espacios. ')
item.value['FR'] = '[STRING / STRINGS] Liste des fichiers de correspondance à utiliser séparés par des espaces. '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FPMODE_HELP
# =============================================================================
item = langlist.create('FPMODE_HELP', kind='HELP')
item.value['ENG'] = '[INTEGER] the mode to calculate the fp+hc wave solution. 0 = following Bauer et al 15 (previously WAVE_E2DS_EA), 1 = following C Lovis (previously WAVE_NEW)'
item.value['FR'] = ('[INTEGER] le mode de calcul de la solution en longueur '
                    "d'onde fp+hc. 0 = selon Bauer et al 15 (anciennement "
                    'WAVE_E2DS_EA), 1 = selon C Lovis (anciennement WAVE_NEW)')
item.value['ES'] = ('[INTEGER] el modo para calcular la solución de longitud '
                    'de onda fp+hc. 0 = según Bauer et al 15 (antes '
                    'WAVE_E2DS_EA), 1 = según C Lovis (antes WAVE_NEW)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# HCMODE_HELP
# =============================================================================
item = langlist.create('HCMODE_HELP', kind='HELP')
item.value['ENG'] = '[INTEGER] the mode to calculate the hc wave solution. 0 = Etienne method'
item.value['FR'] = ('[INTEGER] le mode de calcul de la solution en longueur '
                    "d'onde hc. 0 = méthode d'Etienne")
item.value['ES'] = ('[INTEGER] el modo para calcular la solución de longitud '
                    'de onda hc. 0 = método de Etienne')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INFO_HELP
# =============================================================================
item = langlist.create('INFO_HELP', kind='HELP')
item.value['ENG'] = 'Displays the short version of the help menu'
item.value['ES'] = 'Muestra la versión corta del menú de ayuda'
item.value['FR'] = 'Affiche la version courte du menu d\'aide'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INTERACTIVE_HELP
# =============================================================================
item = langlist.create('INTERACTIVE_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Whether to run in interactive mode – 0 to be in non-interactive mode'
item.value['FR'] = ("[BOOLEAN] S'il faut exécuter en mode interactif – 0 pour "
                    'le mode non interactif')
item.value['ES'] = ('[BOOLEAN] Si ejecutar en modo interactivo – 0 para modo '
                    'no interactivo')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# IS_REFERENCE_HELP
# =============================================================================
item = langlist.create('IS_REFERENCE_HELP', kind='HELP')
item.value['ENG'] = 'If set then recipe is a reference recipe (e.g. reference recipes write to calibration database as reference calibrations)'
item.value['FR'] = ('Si défini, la recette est une recette de référence (ex. '
                    'les recettes de référence écrivent dans la base de '
                    'calibration comme calibrations de référence)')
item.value['ES'] = ('Si se define, la receta es una receta de referencia (p. '
                    'ej. las recetas de referencia escriben en la base de '
                    'calibración como calibraciones de referencia)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LISTING_DESC
# =============================================================================
item = langlist.create('LISTING_DESC', kind='HELP')
item.value['ENG'] = 'Rebuilds index files'
item.value['FR'] = "Reconstruit les fichiers d'index"
item.value['ES'] = 'Reconstruye los archivos de índice'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LISTING_HELP
# =============================================================================
item = langlist.create('LISTING_HELP', kind='HELP')
item.value['ENG'] = 'Lists the night name directories in the input directory if used without a \'directory\' argument or lists the files in the given \'directory\' (if defined). Only lists up to {0} files/directories'
item.value['ES'] = ('Lista los directorios de noche del directorio de entrada '
                    "si se usa sin el argumento 'directory', o lista los "
                    "archivos del 'directory' dado (si se define). Solo lista "
                    'hasta {0} archivos/directorios')
item.value['FR'] = 'Répertorie les répertoires de noms de nuit dans le répertoire d\'entrée s\'ils sont utilisés sans l\'argument \'directory\' ou répertorie les fichiers du \'répertoire\' donné (si défini). Ne répertorie que jusqu\'à {0} fichiers / répertoires'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LISTING_HELP_INSTRUMENT
# =============================================================================
item = langlist.create('LISTING_HELP_INSTRUMENT', kind='HELP')
item.value['ENG'] = '[STRING] The instrument to rebuild for'
item.value['FR'] = "[STRING] L'instrument pour lequel reconstruire"
item.value['ES'] = '[STRING] El instrumento para el que reconstruir'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LISTING_HELP_KIND
# =============================================================================
item = langlist.create('LISTING_HELP_KIND', kind='HELP')
item.value['ENG'] = '[STRING] The kind of indexs to rebuild (i.e. raw, tmp or reduced)'
item.value['FR'] = ("[STRING] Le type d'index à reconstruire (c.-à-d. raw, "
                    'tmp ou reduced)')
item.value['ES'] = ('[STRING] El tipo de índices a reconstruir (es decir raw, '
                    'tmp o reduced)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LISTING_HELP_NIGHTNAME
# =============================================================================
item = langlist.create('LISTING_HELP_NIGHTNAME', kind='HELP')
item.value['ENG'] = '[STRING] The directory/nightname to rebuild for (default is to do all directories)'
item.value['FR'] = ('[STRING] Le répertoire/nom de nuit à reconstruire (par '
                    'défaut tous les répertoires)')
item.value['ES'] = ('[STRING] El directorio/nombre de noche a reconstruir '
                    '(por defecto todos los directorios)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LOGSTAT_DESC
# =============================================================================
item = langlist.create('LOGSTAT_DESC', kind='HELP')
item.value['ENG'] = 'Performs a log analysis on the log.fits files generated by recipes'
item.value['ES'] = ('Realiza un análisis de los archivos log.fits generados '
                    'por las recetas')
item.value['FR'] = 'Répertorie les répertoires de noms de nuit dans le répertoire d\'entrée s\'ils sont utilisés sans l\'argument \'directory\' ou répertorie les fichiers du \'répertoire\' donné (si défini). Ne répertorie que jusqu\'à {0} fichiers / répertoires'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# NO_TEXT
# =============================================================================
item = langlist.create('NO_TEXT', kind='TEXT')
item.value['ENG'] = 'no'
item.value['ES'] = 'no'
item.value['FR'] = 'non'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# OPTIONS_TEXT
# =============================================================================
item = langlist.create('OPTIONS_TEXT', kind='TEXT')
item.value['ENG'] = ' options'
item.value['ES'] = ' opciones'
item.value['FR'] = ' les options '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# OR_TEXT
# =============================================================================
item = langlist.create('OR_TEXT', kind='TEXT')
item.value['ENG'] = 'or'
item.value['ES'] = 'o'
item.value['FR'] = 'ou'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PLOT_HELP
# =============================================================================
item = langlist.create('PLOT_HELP', kind='HELP')
item.value['ENG'] = '[INTEGER] Plot level. 0 = off, 1=save plots only, 2=interactive plots, 3=interactive with loop, 4=advanced mode'
item.value['FR'] = ('[INTEGER] Niveau de graphiques. 0 = désactivé, 1 = '
                    'enregistrer seulement, 2 = graphiques interactifs, 3 = '
                    'interactifs avec boucle, 4 = mode avancé')
item.value['ES'] = ('[INTEGER] Nivel de gráficos. 0 = desactivado, 1 = solo '
                    'guardar gráficos, 2 = gráficos interactivos, 3 = '
                    'interactivos con bucle, 4 = modo avanzado')
item.arguments = 'None'
item.comment = ''
langlist.add(item)


# =============================================================================
# POS_ARG_TEXT
# =============================================================================
item = langlist.create('POS_ARG_TEXT', kind='TEXT')
item.value['ENG'] = ' positional arguments'
item.value['ES'] = ' argumentos posicionales'
item.value['FR'] = ' arguments de position'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PPSKIP_HELP
# =============================================================================
item = langlist.create('PPSKIP_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] If True skips preprocessed files that are already found'
item.value['FR'] = ('[BOOLEAN] Si True ignore les fichiers prétraités déjà '
                    'trouvés')
item.value['ES'] = ('[BOOLEAN] Si es True omite los archivos preprocesados ya '
                    'encontrados')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PREVIEW_HELP
# =============================================================================
item = langlist.create('PREVIEW_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] If True previews the changelog before making any changes if False makes changes without preview'
item.value['FR'] = ('[BOOLEAN] Si True prévisualise le journal des '
                    'modifications avant toute modification, si False '
                    'effectue les modifications sans prévisualisation')
item.value['ES'] = ('[BOOLEAN] Si es True previsualiza el registro de cambios '
                    'antes de hacer cambios, si es False hace los cambios sin '
                    'previsualizar')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_BNIGHTNAMES_HELP
# =============================================================================
item = langlist.create('PROCESS_BNIGHTNAMES_HELP', kind='HELP')
item.value['ENG'] = '[STRING] List of \'night_name\'s or directories to black list (will not process these directories)'
item.value['FR'] = ("[STRING] Liste de 'night_name' ou de répertoires en "
                    'liste noire (ne seront pas traités)')
item.value['ES'] = ("[STRING] Lista de 'night_name' o directorios en lista "
                    'negra (no se procesarán)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_CORES_HELP
# =============================================================================
item = langlist.create('PROCESS_CORES_HELP', kind='HELP')
item.value['ENG'] = '[INTEGER] Number of cores to use in processing'
item.value['FR'] = '[INTEGER] Nombre de cœurs à utiliser pour le traitement'
item.value['ES'] = '[INTEGER] Número de núcleos a usar en el procesamiento'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_DESCRIPTION
# =============================================================================
item = langlist.create('PROCESS_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Process a night or a set of nights or all nights given some options and a run file'
item.value['FR'] = ('Traiter une nuit, un ensemble de nuits ou toutes les '
                    "nuits selon des options et un fichier d'exécution")
item.value['ES'] = ('Procesar una noche, un conjunto de noches o todas las '
                    'noches según algunas opciones y un archivo de ejecución')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_FILENAME_HELP
# =============================================================================
item = langlist.create('PROCESS_FILENAME_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The \'filename\' to reprocess (default is None for all files)'
item.value['FR'] = ("[STRING] Le 'filename' à retraiter (par défaut None pour "
                    'tous les fichiers)')
item.value['ES'] = ("[STRING] El 'filename' a reprocesar (por defecto None "
                    'para todos los archivos)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_INST_HELP
# =============================================================================
item = langlist.create('PROCESS_INST_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The instrument to reprocess'
item.value['FR'] = "[STRING] L'instrument à retraiter"
item.value['ES'] = '[STRING] El instrumento a reprocesar'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_NIGHTNAME_HELP
# =============================================================================
item = langlist.create('PROCESS_NIGHTNAME_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The \'night_name\' or directory to reprocess (default is None for all directories)'
item.value['FR'] = ("[STRING] Le 'night_name' ou le répertoire à retraiter "
                    '(par défaut None pour tous les répertoires)')
item.value['ES'] = ("[STRING] El 'night_name' o directorio a reprocesar (por "
                    'defecto None para todos los directorios)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_RUNFILE_HELP
# =============================================================================
item = langlist.create('PROCESS_RUNFILE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The run file to use in reprocessing'
item.value['FR'] = ("[STRING] Le fichier d'exécution à utiliser pour le "
                    'retraitement')
item.value['ES'] = ('[STRING] El archivo de ejecución a usar en el '
                    'reprocesamiento')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_SCI_TARGETS
# =============================================================================
item = langlist.create('PROCESS_SCI_TARGETS', kind='HELP')
item.value['ENG'] = '[STRING] A list of object names to process as science targets (if unsets default to the run.in file) must be separated by a comma and surrounded with speech-marks i.e. \'target1,target2,target3\''
item.value['FR'] = ("[STRING] Une liste de noms d'objets à traiter comme "
                    'cibles science (si non défini, utilise le fichier '
                    'run.ini) séparés par une virgule et entourés de '
                    "guillemets, ex. 'target1,target2,target3'")
item.value['ES'] = ('[STRING] Una lista de nombres de objetos a procesar como '
                    'objetivos de ciencia (si no se define se usa el archivo '
                    'run.ini) separados por comas y entre comillas, p. ej. '
                    "'target1,target2,target3'")
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_TELLU_TARGETS
# =============================================================================
item = langlist.create('PROCESS_TELLU_TARGETS', kind='HELP')
item.value['ENG'] = '[STRING] A list of object names to process as telluric targets (if unsets default to the run.in file) must be separated by a commas and surrounded with speech-marks i.e. \'target1,target2,target3\''
item.value['FR'] = ("[STRING] Une liste de noms d'objets à traiter comme "
                    'cibles telluriques (si non défini, utilise le fichier '
                    'run.ini) séparés par des virgules et entourés de '
                    "guillemets, ex. 'target1,target2,target3'")
item.value['ES'] = ('[STRING] Una lista de nombres de objetos a procesar como '
                    'objetivos telúricos (si no se define se usa el archivo '
                    'run.ini) separados por comas y entre comillas, p. ej. '
                    "'target1,target2,target3'")
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_TEST_HELP
# =============================================================================
item = langlist.create('PROCESS_TEST_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] If True does not process any files just prints an output of what recipes would be run'
item.value['FR'] = ('[BOOLEAN] Si True ne traite aucun fichier, affiche '
                    'seulement les recettes qui seraient exécutées')
item.value['ES'] = ('[BOOLEAN] Si es True no procesa ningún archivo, solo '
                    'muestra qué recetas se ejecutarían')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_TRIGGER_HELP
# =============================================================================
item = langlist.create('PROCESS_TRIGGER_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] If True activates trigger mode (i.e. will stop processing at the first point we do not find required files). Note one must define --night in trigger mode'
item.value['FR'] = ('[BOOLEAN] Si True active le mode déclencheur (c.-à-d. '
                    'arrête le traitement au premier point où les fichiers '
                    'requis sont introuvables). Il faut définir --night en '
                    'mode déclencheur')
item.value['ES'] = ('[BOOLEAN] Si es True activa el modo disparador (es '
                    'decir, detiene el procesamiento en el primer punto en '
                    'que no se encuentran los archivos requeridos). Debe '
                    'definirse --night en modo disparador')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_UPDATE_OBJDB
# =============================================================================
item = langlist.create('PROCESS_UPDATE_OBJDB', kind='HELP')
item.value['ENG'] = 'Update the object database - only recommended if doing a full reprocess with all data.'
item.value['FR'] = ("Mettre à jour la base de données d'objets - recommandé "
                    "uniquement lors d'un retraitement complet avec toutes "
                    'les données.')
item.value['ES'] = ('Actualizar la base de datos de objetos - solo '
                    'recomendado al hacer un reprocesamiento completo con '
                    'todos los datos.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_WNIGHTNAMES_HELP
# =============================================================================
item = langlist.create('PROCESS_WNIGHTNAMES_HELP', kind='HELP')
item.value['ENG'] = '[STRING] List of \'night_name\'s or directories to white list (will only process these directories)'
item.value['FR'] = ("[STRING] Liste de 'night_name' ou de répertoires en "
                    'liste blanche (seuls ceux-ci seront traités)')
item.value['ES'] = ("[STRING] Lista de 'night_name' o directorios en lista "
                    'blanca (solo se procesarán estos)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_WNIGHTNAMES_HELP
# =============================================================================
item = langlist.create('PROCESS_TO_FILE_HELP', kind='HELP')
item.value['ENG'] = ('[STRING] Output recipes to run to text file '
                     '(sets --test=True)')
item.value['FR'] = ('[STRING] Écrire les recettes à exécuter dans un fichier '
                    'texte (active --test=True)')
item.value['ES'] = ('[STRING] Escribir las recetas a ejecutar en un archivo '
                    'de texto (activa --test=True)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESS_WNIGHTNAMES_HELP
# =============================================================================
item = langlist.create('PROCESS_VERIFY_HELP', kind='HELP')
item.value['ENG'] = ('[SWITCH] Verify input run file (but do not run)')
item.value['FR'] = ("[SWITCH] Vérifier le fichier d'exécution d'entrée (sans "
                    "l'exécuter)")
item.value['ES'] = ('[SWITCH] Verificar el archivo de ejecución de entrada '
                    '(sin ejecutarlo)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# Q_NO
# =============================================================================
item = langlist.create('Q_NO', kind='TEXT')
item.value['ENG'] = '[N]o'
item.value['ES'] = '[N] no'
item.value['FR'] = '[N]on'
item.arguments = 'None'
item.comment = 'Used for input of no'
langlist.add(item)

# =============================================================================
# Q_YES
# =============================================================================
item = langlist.create('Q_YES', kind='TEXT')
item.value['ENG'] = '[Y]es'
item.value['ES'] = '[Y] sí'
item.value['FR'] = '[O]ui'
item.arguments = 'None'
item.comment = 'Used for input of yes'
langlist.add(item)

# =============================================================================
# QUIET_HELP
# =============================================================================
item = langlist.create('QUIET_HELP', kind='HELP')
item.value['ENG'] = 'Run recipe without start up text'
item.value['FR'] = 'Exécuter la recette sans le texte de démarrage'
item.value['ES'] = 'Ejecutar la receta sin el texto de inicio'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DESC
# =============================================================================
item = langlist.create('REMAKE_DESC', kind='HELP')
item.value['ENG'] = 'Remake a database'
item.value['FR'] = 'Reconstruire une base de données'
item.value['ES'] = 'Reconstruir una base de datos'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DOC_DESCRIPTION
# =============================================================================
item = langlist.create('REMAKE_DOC_DESCRIPTION', kind='TEXT')
item.value['ENG'] = 'Re-make the apero documentation'
item.value['FR'] = 'Régénérer la documentation apero'
item.value['ES'] = 'Regenerar la documentación de apero'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DOC_UPLOADARG_HELP
# =============================================================================
item = langlist.create('REMAKE_DOC_UPLOADARG_HELP', kind='TEXT')
item.value['ENG'] = '[Bool] If True upload documentation to defined server (for web access)'
item.value['FR'] = ('[Bool] Si True téléverse la documentation sur le serveur '
                    "défini (pour l'accès web)")
item.value['ES'] = ('[Bool] Si es True sube la documentación al servidor '
                    'definido (para acceso web)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DOC_COMPILE_HELP
# =============================================================================
item = langlist.create('REMAKE_DOC_COMPILE_HELP', kind='HELP')
item.value['ENG'] = 'Compile all rst pages'
item.value['FR'] = 'Compiler toutes les pages rst'
item.value['ES'] = 'Compilar todas las páginas rst'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DOC_FILEDEF_HELP
# =============================================================================
item = langlist.create('REMAKE_DOC_FILEDEF_HELP', kind='HELP')
item.value['ENG'] = 'Compile the docs for file definitions'
item.value['FR'] = 'Compiler la documentation des définitions de fichiers'
item.value['ES'] = 'Compilar la documentación de definiciones de archivos'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DOC_RECIPEDEF_HELP
# =============================================================================
item = langlist.create('REMAKE_DOC_RECIPEDEF_HELP', kind='HELP')
item.value['ENG'] = 'Compile the docs for recipe definitions'
item.value['FR'] = 'Compiler la documentation des définitions de recettes'
item.value['ES'] = 'Compilar la documentación de definiciones de recetas'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DOC_RECIPESEQ_HELP
# =============================================================================
item = langlist.create('REMAKE_DOC_RECIPESEQ_HELP', kind='HELP')
item.value['ENG'] = 'Compile the docs for recipe sequences'
item.value['FR'] = 'Compiler la documentation des séquences de recettes'
item.value['ES'] = 'Compilar la documentación de secuencias de recetas'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_HELP_INSTRUMENT
# =============================================================================
item = langlist.create('REMAKE_HELP_INSTRUMENT', kind='HELP')
item.value['ENG'] = '[STRING] The instrument to remake the database for'
item.value['FR'] = ("[STRING] L'instrument pour lequel refaire la base de "
                    'données')
item.value['ES'] = ('[STRING] El instrumento para el que rehacer la base de '
                    'datos')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_HELP_KIND
# =============================================================================
item = langlist.create('REMAKE_HELP_KIND', kind='HELP')
item.value['ENG'] = '[STRING] The kind of database to remake (i.e. calibration or telluric)'
item.value['FR'] = ('[STRING] Le type de base de données à refaire (c.-à-d. '
                    'calibration ou tellurique)')
item.value['ES'] = ('[STRING] El tipo de base de datos a rehacer (es decir '
                    'calibración o telúrica)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_DESCRIPTION
# =============================================================================
item = langlist.create('RESET_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Resets the DRS raw/tmp/db/reduced files based on user input'
item.value['FR'] = ('Réinitialise les fichiers raw/tmp/db/reduced du DRS '
                    "selon les choix de l'utilisateur")
item.value['ES'] = ('Reinicia los archivos raw/tmp/db/reduced del DRS según '
                    'la entrada del usuario')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_INST_HELP
# =============================================================================
item = langlist.create('RESET_INST_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The instrument to reset'
item.value['FR'] = "[STRING] L'instrument à réinitialiser"
item.value['ES'] = '[STRING] El instrumento a reiniciar'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_LOG_HELP
# =============================================================================
item = langlist.create('RESET_LOG_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] If True logs the reset else is quite'
item.value['FR'] = ('[BOOLEAN] Si True journalise la réinitialisation, sinon '
                    'silencieux')
item.value['ES'] = ('[BOOLEAN] Si es True registra el reinicio, si no es '
                    'silencioso')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_WARN_HELP
# =============================================================================
item = langlist.create('RESET_WARN_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] If True asks for user to type \'YES\' before each reset'
item.value['FR'] = ("[BOOLEAN] Si True demande à l'utilisateur de taper 'YES' "
                    'avant chaque réinitialisation')
item.value['ES'] = ("[BOOLEAN] Si es True pide al usuario que escriba 'YES' "
                    'antes de cada reinicio')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_DATABASE_TIMEOUT_HELP
# =============================================================================
item = langlist.create('RESET_DATABASE_TIMEOUT_HELP', kind='HELP')
item.value['ENG'] = '[INTEGER] Set the database timeout number of tries'
item.value['FR'] = ('[INTEGER] Définit le nombre de tentatives avant '
                    'expiration de la base de données')
item.value['ES'] = ('[INTEGER] Define el número de intentos antes del tiempo '
                    'de espera de la base de datos')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_INPUT_DIR_HELP
# =============================================================================
item = langlist.create('SET_INPUT_DIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Force the default input directory (Normally set by recipe)'
item.value['FR'] = ("[STRING] Forcer le répertoire d'entrée par défaut "
                    '(normalement défini par la recette)')
item.value['ES'] = ('[STRING] Forzar el directorio de entrada por defecto '
                    '(normalmente definido por la receta)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_IPYTHON_RETURN_HELP
# =============================================================================
item = langlist.create('SET_IPYTHON_RETURN_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] If True always returns to ipython (or python) at end (via ipdb or pdb)'
item.value['FR'] = ('[BOOLEAN] Si True revient toujours à ipython (ou python) '
                    'à la fin (via ipdb ou pdb)')
item.value['ES'] = ('[BOOLEAN] Si es True siempre vuelve a ipython (o python) '
                    'al final (vía ipdb o pdb)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_OUTPUT_DIR_HELP
# =============================================================================
item = langlist.create('SET_OUTPUT_DIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Force the default output directory (Normally set by recipe)'
item.value['FR'] = ('[STRING] Forcer le répertoire de sortie par défaut '
                    '(normalement défini par la recette)')
item.value['ES'] = ('[STRING] Forzar el directorio de salida por defecto '
                    '(normalmente definido por la receta)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_PARALLEL_HELP
# =============================================================================
item = langlist.create('SET_PARALLEL_HELP', kind='TEXT')
item.value['ENG'] = '[BOOL] If True this is a run in parellel - disable some features (normally only used in apero_processing.py)'
item.value['FR'] = ("[BOOL] Si True il s'agit d'une exécution en parallèle - "
                    'désactive certaines fonctionnalités (normalement utilisé '
                    'seulement dans apero_processing.py)')
item.value['ES'] = ('[BOOL] Si es True es una ejecución en paralelo - '
                    'desactiva algunas funciones (normalmente solo se usa en '
                    'apero_processing.py)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_PROGRAM_HELP
# =============================================================================
item = langlist.create('SET_PROGRAM_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The name of the program to display and use (mostly for logging purpose) log becomes date | {THIS STRING} | Message'
item.value['FR'] = ('[STRING] Le nom du programme à afficher et utiliser '
                    '(surtout pour la journalisation), le journal devient '
                    'date | {THIS STRING} | Message')
item.value['ES'] = ('[STRING] El nombre del programa a mostrar y usar (sobre '
                    'todo para el registro), el registro queda fecha | {THIS '
                    'STRING} | Mensaje')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_RECIPE_KIND_HELP
# =============================================================================
item = langlist.create('SET_RECIPE_KIND_HELP', kind='TEXT')
item.value['ENG'] = '[STRING] The recipe kind for this recipe run (normally only used in apero_processing.py)'
item.value['FR'] = ('[STRING] Le type de recette pour cette exécution '
                    '(normalement utilisé seulement dans apero_processing.py)')
item.value['ES'] = ('[STRING] El tipo de receta para esta ejecución '
                    '(normalmente solo se usa en apero_processing.py)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_SHORTNAME_HELP
# =============================================================================
item = langlist.create('SET_SHORTNAME_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Set a shortname for a recipe to distinguish it from other runs - this is mainly for use with apero processing but will appear in the log database'
item.value['FR'] = ('[STRING] Définir un nom court pour une recette pour la '
                    'distinguer des autres exécutions - surtout pour apero '
                    'processing mais apparaît dans la base de données du '
                    'journal')
item.value['ES'] = ('[STRING] Definir un nombre corto para una receta para '
                    'distinguirla de otras ejecuciones - principalmente para '
                    'apero processing pero aparece en la base de datos del '
                    'registro')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TEST_DESC
# =============================================================================
item = langlist.create('TEST_DESC', kind='HELP')
item.value['ENG'] = 'Test recipe - used to test the argument parser of the DRS'
item.value['ES'] = ('Receta de prueba - usada para probar el analizador de '
                    'argumentos del DRS')
item.value['FR'] = 'Test recipe - utilisé pour tester l\'analyseur d\'arguments du DRS '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TEST_DESCRIPTION
# =============================================================================
item = langlist.create('TEST_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'This is the top level test recipe'
item.value['FR'] = 'Ceci est la recette de test de premier niveau'
item.value['ES'] = 'Esta es la receta de prueba de nivel superior'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TEST_EXAMPLE
# =============================================================================
item = langlist.create('TEST_EXAMPLE', kind='HELP')
item.value['ENG'] = ' test.py [NIGHT_NAME] [DARK_DARK] [FLAT_FLAT] \n test.py 2018-08-05 2295520f_pp.fits dark_dark_P5_003d_pp.fits \n test.py 2018-08-05 2295520f_pp dark_dark_P5_003d_pp.fits \n test.py 2018-08-05 *f_pp *d_pp'
item.value['ES'] = (' test.py [NIGHT_NAME] [DARK_DARK] [FLAT_FLAT] \n test.py '
                    '2018-08-05 2295520f_pp.fits dark_dark_P5_003d_pp.fits \n '
                    'test.py 2018-08-05 2295520f_pp '
                    'dark_dark_P5_003d_pp.fits \n test.py 2018-08-05 *f_pp '
                    '*d_pp')
item.value['FR'] = ' test.py [NIGHT_NAME] [DARK_DARK] [FLAT_FLAT] \n test.py 2018-08-05 2295520f_pp.fits dark_dark_P5_003d_pp.fits \n test.py 2018-08-05 2295520f_pp dark_dark_P5_003d_pp.fits \n test.py 2018-08-05 *f_pp *d_pp'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TEST_FILELIST1_HELP
# =============================================================================
item = langlist.create('TEST_FILELIST1_HELP', kind='HELP')
item.value['ENG'] = 'Currently allowed types: -DARK_DARK -FLAT_FLAT'
item.value['ES'] = 'Tipos permitidos actualmente: -DARK_DARK -FLAT_FLAT'
item.value['FR'] = 'Types actuellement autorisés: -DARK_DARK -FLAT_FLAT '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TEST_FILELIST2_HELP
# =============================================================================
item = langlist.create('TEST_FILELIST2_HELP', kind='HELP')
item.value['ENG'] = 'Currently allowed types: -FP_FP'
item.value['ES'] = 'Tipos permitidos actualmente: -FP_FP'
item.value['FR'] = 'Types actuellement autorisés: -FP_FP '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# USAGE_TEXT
# =============================================================================
item = langlist.create('USAGE_TEXT', kind='TEXT')
item.value['ENG'] = ' Usage:'
item.value['ES'] = ' Uso:'
item.value['FR'] = ' L\'utilisation:'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# VALIDATE_DESCRIPTION
# =============================================================================
item = langlist.create('VALIDATE_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Runs the DRS validate script (If this script runs the APERO frame work has been installed successfully)'
item.value['FR'] = ('Exécute le script de validation du DRS (si ce script '
                    "s'exécute, le framework APERO a été installé avec succès)")
item.value['ES'] = ('Ejecuta el script de validación del DRS (si este script '
                    'se ejecuta, el framework APERO se instaló correctamente)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# VERSION_HELP
# =============================================================================
item = langlist.create('VERSION_HELP', kind='HELP')
item.value['ENG'] = 'Displays the current version of this recipe.'
item.value['ES'] = 'Muestra la versión actual de esta receta.'
item.value['FR'] = 'Affiche la version actuelle de cette recette.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# YES_TEXT
# =============================================================================
item = langlist.create('YES_TEXT', kind='TEXT')
item.value['ENG'] = 'yes'
item.value['ES'] = 'yes'
item.value['FR'] = 'oui'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_GUI_HELP
# =============================================================================
item = langlist.create('GET_GUI_HELP', kind='HELP')
item.value['ENG'] = 'Use a gui to filter files (Currently not ready)'
item.value['FR'] = ('Utiliser une interface graphique pour filtrer les '
                    'fichiers (pas encore prête)')
item.value['ES'] = ('Usar una interfaz gráfica para filtrar archivos (aún no '
                    'está lista)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_OBJNAME_HELP
# =============================================================================
item = langlist.create('GET_OBJNAME_HELP', kind='HELP')
item.value['ENG'] = 'The object names separated by a comma. Use \'\' for objects with whitespaces i.e \'obj1,obj2,obj 3\''
item.value['FR'] = ("Les noms d'objets séparés par une virgule. Utilisez '' "
                    "pour les objets avec des espaces, ex. 'obj1,obj2,obj 3'")
item.value['ES'] = ("Los nombres de objetos separados por comas. Use '' para "
                    "objetos con espacios, p. ej. 'obj1,obj2,obj 3'")
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_DPRTYPES_HELP
# =============================================================================
item = langlist.create('GET_DPRTYPES_HELP', kind='HELP')
item.value['ENG'] = 'The DPRTYPES to use (multiple dprtypes combined with OR logic) separate dprtypes with commas. Leaving blank will not use DPRTYPE to filter files.'
item.value['FR'] = ('Les DPRTYPES à utiliser (plusieurs dprtypes combinés '
                    'avec une logique OU), séparés par des virgules. Laisser '
                    'vide pour ne pas filtrer par DPRTYPE.')
item.value['ES'] = ('Los DPRTYPES a usar (varios dprtypes combinados con '
                    'lógica O), separados por comas. Dejar en blanco para no '
                    'filtrar por DPRTYPE.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_OUTTYPES_HELP
# =============================================================================
item = langlist.create('GET_OUTTYPES_HELP', kind='HELP')
item.value['ENG'] = 'The drs output file types to use (multiple output type combined  with OR logic) separate output types with commas. Leaving blank will not use output type to filter files.'
item.value['FR'] = ('Les types de fichiers de sortie drs à utiliser '
                    '(plusieurs types combinés avec une logique OU), séparés '
                    'par des virgules. Laisser vide pour ne pas filtrer par '
                    'type de sortie.')
item.value['ES'] = ('Los tipos de archivo de salida drs a usar (varios tipos '
                    'combinados con lógica O), separados por comas. Dejar en '
                    'blanco para no filtrar por tipo de salida.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FIBERS_HELP
# =============================================================================
item = langlist.create('GET_FIBERS_HELP', kind='HELP')
item.value['ENG'] = 'The fibres to use (multiple output type combined  with OR logic) separate fibers with commas. Leaving blank will not use fiber to filter files.'
item.value['FR'] = ('Les fibres à utiliser (plusieurs combinées avec une '
                    'logique OU), séparées par des virgules. Laisser vide '
                    'pour ne pas filtrer par fibre.')
item.value['ES'] = ('Las fibras a usar (varias combinadas con lógica O), '
                    'separadas por comas. Dejar en blanco para no filtrar por '
                    'fibra.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_OUTPATH_HELP
# =============================================================================
item = langlist.create('GET_OUTPATH_HELP', kind='HELP')
item.value['ENG'] = 'This is the directory where copied files will be placed. Must be a valid path and must have permission be able to write.'
item.value['FR'] = ("C'est le répertoire où seront placés les fichiers "
                    'copiés. Doit être un chemin valide avec les droits '
                    "d'écriture.")
item.value['ES'] = ('Este es el directorio donde se colocarán los archivos '
                    'copiados. Debe ser una ruta válida con permisos de '
                    'escritura.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_SYMLINKS_HELP
# =============================================================================
item = langlist.create('GET_SYMLINKS_HELP', kind='HELP')
item.value['ENG'] = 'Create symlinks to the file instead of copying'
item.value['FR'] = ('Créer des liens symboliques vers le fichier au lieu de '
                    'le copier')
item.value['ES'] = 'Crear enlaces simbólicos al archivo en lugar de copiarlo'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_TEST_HELP
# =============================================================================
item = langlist.create('GET_TEST_HELP', kind='HELP')
item.value['ENG'] = 'Does not copy files - prints copy as a debug test. Recommended for first time use.'
item.value['FR'] = ('Ne copie pas les fichiers - affiche la copie comme test '
                    'de débogage. Recommandé pour une première utilisation.')
item.value['ES'] = ('No copia los archivos - muestra la copia como prueba de '
                    'depuración. Recomendado para el primer uso.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_RAW_DESC
# =============================================================================
item = langlist.create('DATA_RAW_DESC', kind='TEXT')
item.value['ENG'] = 'Raw data directory'
item.value['FR'] = 'Répertoire des données brutes'
item.value['ES'] = 'Directorio de datos brutos'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_TMP_DESC
# =============================================================================
item = langlist.create('DATA_TMP_DESC', kind='TEXT')
item.value['ENG'] = 'Temporary data directory'
item.value['FR'] = 'Répertoire de données temporaires'
item.value['ES'] = 'Directorio de datos temporales'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_REDUC_DESC
# =============================================================================
item = langlist.create('DATA_REDUC_DESC', kind='TEXT')
item.value['ENG'] = 'Reduced data directory'
item.value['FR'] = 'Répertoire des données réduites'
item.value['ES'] = 'Directorio de datos reducidos'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_OUT_DESC
# =============================================================================
item = langlist.create('DATA_OUT_DESC', kind='TEXT')
item.value['ENG'] = 'Post process directory'
item.value['FR'] = 'Répertoire de post-traitement'
item.value['ES'] = 'Directorio de post-procesamiento'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_CALIB_DESC
# =============================================================================
item = langlist.create('DATA_CALIB_DESC', kind='TEXT')
item.value['ENG'] = 'Calibration DB data directory'
item.value['FR'] = 'Répertoire de données de la base de calibration'
item.value['ES'] = 'Directorio de datos de la base de calibración'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_TELLU_DESC
# =============================================================================
item = langlist.create('DATA_TELLU_DESC', kind='TEXT')
item.value['ENG'] = 'Telluric DB data directory'
item.value['FR'] = 'Répertoire de données de la base tellurique'
item.value['ES'] = 'Directorio de datos de la base telúrica'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_PLOT_DESC
# =============================================================================
item = langlist.create('DATA_PLOT_DESC', kind='TEXT')
item.value['ENG'] = 'Plotting directory'
item.value['FR'] = 'Répertoire des graphiques'
item.value['ES'] = 'Directorio de gráficos'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_RUN_DESC
# =============================================================================
item = langlist.create('DATA_RUN_DESC', kind='TEXT')
item.value['ENG'] = 'Run directory'
item.value['FR'] = 'Répertoire run'
item.value['ES'] = 'Directorio run'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_ASSETS_DESC
# =============================================================================
item = langlist.create('DATA_ASSETS_DESC', kind='TEXT')
item.value['ENG'] = 'Assets directory'
item.value['FR'] = 'Répertoire des ressources'
item.value['ES'] = 'Directorio de recursos'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATA_LOG_DESC
# =============================================================================
item = langlist.create('DATA_LOG_DESC', kind='TEXT')
item.value['ENG'] = 'Log directory'
item.value['FR'] = 'Répertoire des journaux'
item.value['ES'] = 'Directorio de registros'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_PROFILE_MSG
# =============================================================================
item = langlist.create('INSTALL_PROFILE_MSG', kind='TEXT')
item.value['ENG'] = 'APERO profile name:      \n\nThis is the profile name to associate with this installation\nDo not include spaces or wildcards (alpha-numeric only)\nNote you can create multiple profiles for different instruments\nso the name should be logical and unique'
item.value['FR'] = ("Nom du profil APERO :      \n\nC'est le nom de profil à "
                    "associer à cette installation\nN'incluez ni espaces ni "
                    'caractères génériques (alphanumérique seulement)\nNotez '
                    'que vous pouvez créer plusieurs profils pour différents '
                    'instruments\nle nom doit donc être logique et unique')
item.value['ES'] = ('Nombre del perfil APERO:      \n\nEste es el nombre de '
                    'perfil asociado a esta instalación\nNo incluya espacios '
                    'ni comodines (solo alfanuméricos)\nTenga en cuenta que '
                    'puede crear varios perfiles para distintos instrumentos\n'
                    'por lo que el nombre debe ser lógico y único')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_CONFIG_PATH_MSG
# =============================================================================
item = langlist.create('INSTALL_CONFIG_PATH_MSG', kind='TEXT')
item.value['ENG'] = 'User config path:      \n\nThis is the path where your user configuration will be saved.     \nIf it doesn\'t exist you will be prompted to create it.      \nNote please make sure directory is EMPTY.      \nNote the \"profile name\" sub-directory will be created under this path.'
item.value['FR'] = ("Chemin de configuration utilisateur :      \n\nC'est le "
                    'chemin où votre configuration utilisateur sera '
                    "enregistrée.     \nS'il n'existe pas, il vous sera "
                    'proposé de le créer.      \nAssurez-vous que le '
                    'répertoire est VIDE.      \nLe sous-répertoire "nom du '
                    'profil" sera créé sous ce chemin.')
item.value['ES'] = ('Ruta de configuración de usuario:      \n\nEsta es la '
                    'ruta donde se guardará su configuración de '
                    'usuario.     \nSi no existe se le pedirá que la '
                    'cree.      \nAsegúrese de que el directorio está '
                    'VACÍO.      \nEl subdirectorio "nombre del perfil" se '
                    'creará bajo esta ruta.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DATA_PATH_MSG
# =============================================================================
item = langlist.create('INSTALL_DATA_PATH_MSG', kind='TEXT')
item.value['ENG'] = 'Setup paths invidiually? [Y]es or [N]o        \n\nIf [Y]es it will allow you to set each path separately      \n(i.e. for raw, tmp, reduced, calibDB etc).      \nIf [N]o you will just set one path and all folders      \n(raw, tmp, reduced, calibDB etc) will be created under this      \ndirectory.'
item.value['FR'] = ('Configurer les chemins individuellement ? [Y]es ou '
                    '[N]o        \n\nSi [Y]es vous pourrez définir chaque '
                    'chemin séparément      \n(c.-à-d. raw, tmp, reduced, '
                    'calibDB etc).      \nSi [N]o vous définirez un seul '
                    'chemin et tous les dossiers      \n(raw, tmp, reduced, '
                    'calibDB etc) seront créés dans ce      \nrépertoire.')
item.value['ES'] = ('¿Configurar las rutas individualmente? [Y]es o '
                    '[N]o        \n\nSi [Y]es podrá definir cada ruta por '
                    'separado      \n(es decir, raw, tmp, reduced, calibDB '
                    'etc).      \nSi [N]o definirá una sola ruta y todas las '
                    'carpetas      \n(raw, tmp, reduced, calibDB etc) se '
                    'crearán bajo este      \ndirectorio.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_CLEAN_MSG
# =============================================================================
item = langlist.create('INSTALL_CLEAN_MSG', kind='TEXT')
item.value['ENG'] = 'Clean install? [Y]es or [N]o      \n\nWARNING: If you type [Y]es you will be prompted (later) to reset     \nthe directories this means any previous data in these directories     \nwill be removed.  \n\nNote you can always say later to individual cases.  \n\nNote if you have given empty directories you MUST run a clean install to copy the required files to the given directories.'
item.value['FR'] = ('Installation propre ? [Y]es ou [N]o      \n\nATTENTION : '
                    'si vous tapez [Y]es il vous sera demandé (plus tard) de '
                    'réinitialiser     \nles répertoires, ce qui signifie que '
                    'toutes les données précédentes de ces répertoires     \n'
                    'seront supprimées.  \n\nVous pourrez toujours refuser '
                    'plus tard au cas par cas.  \n\nSi vous avez fourni des '
                    'répertoires vides vous DEVEZ faire une installation '
                    'propre pour copier les fichiers requis dans ces '
                    'répertoires.')
item.value['ES'] = ('¿Instalación limpia? [Y]es o [N]o      \n\nADVERTENCIA: '
                    'si escribe [Y]es se le pedirá (más tarde) '
                    'reiniciar     \nlos directorios, lo que significa que '
                    'todos los datos previos en esos directorios     \nserán '
                    'eliminados.  \n\nSiempre podrá decir que no más tarde '
                    'caso por caso.  \n\nSi ha indicado directorios vacíos '
                    'DEBE realizar una instalación limpia para copiar los '
                    'archivos requeridos a esos directorios.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_ALIAS_MSG
# =============================================================================
item = langlist.create('INSTALL_ALIAS_MSG', kind='TEXT')
item.value['ENG'] = 'Add an alias in your ~/.bashrc or ~/.bash_profile or ~/.tcshrc or ~/.profile or ~/.zshrc or ~/.zprofile         \nand then type \"{NAME}\" every time you wish to run apero.          \n\ni.e. for bash              \nalias {NAME}=\"source {DRS_UCONFIG}{NAME}.bash.setup\"          \n\ni.e. for sh             \nalias {NAME} \"source {DRS_UCONFIG}{NAME}.sh.setup\"         \n\ni.e. for zsh              \nalias {NAME} \"source {DRS_UCONFIG}{NAME}.zsh.setup\"'
item.value['FR'] = ('Ajoutez un alias dans votre ~/.bashrc ou ~/.bash_profile '
                    'ou ~/.tcshrc ou ~/.profile ou ~/.zshrc ou '
                    '~/.zprofile         \npuis tapez "{NAME}" chaque fois '
                    'que vous voulez exécuter apero.          \n\nc.-à-d. '
                    'pour bash              \nalias {NAME}="source '
                    '{DRS_UCONFIG}{NAME}.bash.setup"          \n\nc.-à-d. '
                    'pour sh             \nalias {NAME} "source '
                    '{DRS_UCONFIG}{NAME}.sh.setup"         \n\nc.-à-d. pour '
                    'zsh              \nalias {NAME} "source '
                    '{DRS_UCONFIG}{NAME}.zsh.setup"')
item.value['ES'] = ('Añada un alias en su ~/.bashrc o ~/.bash_profile o '
                    '~/.tcshrc o ~/.profile o ~/.zshrc o '
                    '~/.zprofile         \ny luego escriba "{NAME}" cada vez '
                    'que desee ejecutar apero.          \n\nes decir, para '
                    'bash              \nalias {NAME}="source '
                    '{DRS_UCONFIG}{NAME}.bash.setup"          \n\nes decir, '
                    'para sh             \nalias {NAME} "source '
                    '{DRS_UCONFIG}{NAME}.sh.setup"         \n\nes decir, para '
                    'zsh              \nalias {NAME} "source '
                    '{DRS_UCONFIG}{NAME}.zsh.setup"')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DB_MSG
# =============================================================================
item = langlist.create('INSTALL_DB_MSG', kind='TEXT')
item.value['ENG'] = 'For MySQL you must define some parameters, these will take the form:\n\n    >> mysql -h {HOSTNAME} -n {USERNAME} -p {PASSWORD}\n\n- Note the password will be stored as plain text.\n\nYou will also need a database name (within mysql) \n- if it does not exist we will attempt to create it (but may not have permissions to do so)\n\nYou may also link the database to a specific apero profile\nby default this is the profile name you set up here\nhowever you may want to link this database to another apero profile'
item.value['FR'] = ('Pour MySQL vous devez définir quelques paramètres, sous '
                    'la forme :\n\n    >> mysql -h {HOSTNAME} -n {USERNAME} '
                    '-p {PASSWORD}\n\n- Notez que le mot de passe sera stocké '
                    'en clair.\n\nIl vous faudra aussi un nom de base de '
                    "données (dans mysql) \n- s'il n'existe pas nous "
                    "tenterons de le créer (mais nous n'en avons peut-être "
                    'pas les droits)\n\nVous pouvez aussi lier la base de '
                    "données à un profil apero spécifique\npar défaut c'est "
                    'le nom de profil défini ici\nmais vous pouvez vouloir '
                    'lier cette base de données à un autre profil apero')
item.value['ES'] = ('Para MySQL debe definir algunos parámetros, con la '
                    'forma:\n\n    >> mysql -h {HOSTNAME} -n {USERNAME} -p '
                    '{PASSWORD}\n\n- Tenga en cuenta que la contraseña se '
                    'almacenará como texto plano.\n\nTambién necesitará un '
                    'nombre de base de datos (dentro de mysql) \n- si no '
                    'existe intentaremos crearla (pero puede que no tengamos '
                    'permisos para ello)\n\nTambién puede vincular la base de '
                    'datos a un perfil de apero específico\npor defecto es el '
                    'nombre de perfil definido aquí\npero puede que quiera '
                    'vincular esta base de datos a otro perfil de apero')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_UPDATE_HELP
# =============================================================================
item = langlist.create('INSTALL_UPDATE_HELP', kind='HELP')
item.value['ENG'] = 'updates installation (not clean install) and checks for updates to your current config files'
item.value['FR'] = ("met à jour l'installation (pas une installation propre) "
                    'et vérifie les mises à jour de vos fichiers de '
                    'configuration actuels')
item.value['ES'] = ('actualiza la instalación (no es una instalación limpia) '
                    'y comprueba las actualizaciones de sus archivos de '
                    'configuración actuales')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_SKIP_HELP
# =============================================================================
item = langlist.create('INSTALL_SKIP_HELP', kind='HELP')
item.value['ENG'] = 'skip the python module checks (Not recommended for first time installation)'
item.value['FR'] = ('ignorer les vérifications des modules python '
                    '(déconseillé pour une première installation)')
item.value['ES'] = ('omitir las comprobaciones de módulos de python (no '
                    'recomendado en la primera instalación)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DEV_HELP
# =============================================================================
item = langlist.create('INSTALL_DEV_HELP', kind='HELP')
item.value['ENG'] = 'activate developer mode (prompts for all config/constant groups and add them to your config/constant files)'
item.value['FR'] = ('activer le mode développeur (demande tous les groupes de '
                    'config/constantes et les ajoute à vos fichiers de '
                    'config/constantes)')
item.value['ES'] = ('activar el modo desarrollador (pregunta por todos los '
                    'grupos de config/constantes y los añade a sus archivos '
                    'de config/constantes)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_GUI_HELP
# =============================================================================
item = langlist.create('INSTALL_GUI_HELP', kind='HELP')
item.value['ENG'] = 'use GUI to install (Not yet supported) '
item.value['FR'] = ("utiliser l'interface graphique pour installer (pas "
                    'encore supporté) ')
item.value['ES'] = 'usar la interfaz gráfica para instalar (aún no soportado) '
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_NAME_HELP
# =============================================================================
item = langlist.create('INSTALL_NAME_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The name for this specific installation (Allows the creation of multiple profiles with different settings)'
item.value['FR'] = ('[STRING] Le nom de cette installation (permet de créer '
                    'plusieurs profils avec des paramètres différents)')
item.value['ES'] = ('[STRING] El nombre de esta instalación (permite crear '
                    'varios perfiles con configuraciones distintas)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DESCRIPTION
# =============================================================================
item = langlist.create('INSTALL_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Install {0} software for reducing observational data'
item.value['FR'] = ('Installer le logiciel {0} de réduction des données '
                    "d'observation")
item.value['ES'] = 'Instalar el software {0} para reducir datos de observación'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_ROOT_HELP
# =============================================================================
item = langlist.create('INSTALL_ROOT_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The installation directory (if not given tries to find the path and if not found prompts the user)'
item.value['FR'] = ("[STRING] Le répertoire d'installation (si non fourni, "
                    'tente de trouver le chemin et sinon demande à '
                    "l'utilisateur)")
item.value['ES'] = ('[STRING] El directorio de instalación (si no se da '
                    'intenta encontrar la ruta y si no la encuentra pregunta '
                    'al usuario)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_CONFIG_HELP
# =============================================================================
item = langlist.create('INSTALL_CONFIG_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The user configuration path (if not given prompts the user)'
item.value['FR'] = ('[STRING] Le chemin de configuration utilisateur (si non '
                    "fourni, demande à l'utilisateur)")
item.value['ES'] = ('[STRING] La ruta de configuración de usuario (si no se '
                    'da se pregunta al usuario)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_INSTRUMENT_HELP
# =============================================================================
item = langlist.create('INSTALL_INSTRUMENT_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The instrument to install (if not given prompts the user for each available instrument). THIS ARGUMENT IS REQUIRED TO SET --datadir, --rawdir, --tmpdir, --reddir, --calibdir, --telludir, --plotdir, --rundir, --assetdir, --logdir'
item.value['FR'] = ("[STRING] L'instrument à installer (si non fourni, "
                    "demande à l'utilisateur pour chaque instrument "
                    'disponible). CET ARGUMENT EST REQUIS POUR DÉFINIR '
                    '--datadir, --rawdir, --tmpdir, --reddir, --calibdir, '
                    '--telludir, --plotdir, --rundir, --assetdir, --logdir')
item.value['ES'] = ('[STRING] El instrumento a instalar (si no se da se '
                    'pregunta al usuario para cada instrumento disponible). '
                    'ESTE ARGUMENTO ES NECESARIO PARA DEFINIR --datadir, '
                    '--rawdir, --tmpdir, --reddir, --calibdir, --telludir, '
                    '--plotdir, --rundir, --assetdir, --logdir')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DATADIR_HELP
# =============================================================================
item = langlist.create('INSTALL_DATADIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The data directory (if given overrides all sub-data directories - i.e. raw/tmp/red/plot) if not given and other paths not given prompts the user for input.'
item.value['FR'] = ('[STRING] Le répertoire de données (si fourni, remplace '
                    'tous les sous-répertoires de données - c.-à-d. '
                    'raw/tmp/red/plot) ; si non fourni et autres chemins non '
                    "fournis, l'utilisateur est invité à le saisir.")
item.value['ES'] = ('[STRING] El directorio de datos (si se da reemplaza '
                    'todos los subdirectorios de datos - es decir '
                    'raw/tmp/red/plot); si no se da y no se dan otras rutas '
                    'se pide al usuario.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_RAWDIR_HELP
# =============================================================================
item = langlist.create('INSTALL_RAWDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The raw directory where input files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately)'
item.value['FR'] = ('[STRING] Le répertoire raw où sont stockés les fichiers '
                    "d'entrée. (si non fourni et --datadir non fourni, "
                    "l'utilisateur est invité à le saisir s'il choisit "
                    "d'installer chaque répertoire séparément)")
item.value['ES'] = ('[STRING] El directorio raw donde se guardan los archivos '
                    'de entrada. (si no se da y no se da --datadir se pide al '
                    'usuario que lo introduzca si elige instalar cada '
                    'directorio por separado)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_TMPDIR_HELP
# =============================================================================
item = langlist.create('INSTALL_TMPDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The tmp directory where preprocessed files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately)'
item.value['FR'] = ('[STRING] Le répertoire tmp où sont stockés les fichiers '
                    'prétraités. (si non fourni et --datadir non fourni, '
                    "l'utilisateur est invité à le saisir s'il choisit "
                    "d'installer chaque répertoire séparément)")
item.value['ES'] = ('[STRING] El directorio tmp donde se guardan los archivos '
                    'preprocesados. (si no se da y no se da --datadir se pide '
                    'al usuario que lo introduzca si elige instalar cada '
                    'directorio por separado)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_REDDIR_HELP
# =============================================================================
item = langlist.create('INSTALL_REDDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The reduced directory where output files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately)'
item.value['FR'] = ('[STRING] Le répertoire reduced où sont stockés les '
                    'fichiers de sortie. (si non fourni et --datadir non '
                    "fourni, l'utilisateur est invité à le saisir s'il "
                    "choisit d'installer chaque répertoire séparément)")
item.value['ES'] = ('[STRING] El directorio reduced donde se guardan los '
                    'archivos de salida. (si no se da y no se da --datadir se '
                    'pide al usuario que lo introduzca si elige instalar cada '
                    'directorio por separado)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_OUTDIR_HELP
# =============================================================================
item = langlist.create('INSTALL_OUTDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The post process directory where output files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately).'
item.value['FR'] = ('[STRING] Le répertoire de post-traitement où sont '
                    'stockés les fichiers de sortie. (si non fourni et '
                    "--datadir non fourni, l'utilisateur est invité à le "
                    "saisir s'il choisit d'installer chaque répertoire "
                    'séparément).')
item.value['ES'] = ('[STRING] El directorio de post-procesamiento donde se '
                    'guardan los archivos de salida. (si no se da y no se da '
                    '--datadir se pide al usuario que lo introduzca si elige '
                    'instalar cada directorio por separado).')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_CALIBDIR_HELP
# =============================================================================
item = langlist.create('INSTALL_CALIBDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The calibration database directory where calibrations used in the database files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately)'
item.value['FR'] = ('[STRING] Le répertoire de la base de calibration où sont '
                    'stockées les calibrations utilisées dans la base de '
                    'données. (si non fourni et --datadir non fourni, '
                    "l'utilisateur est invité à le saisir s'il choisit "
                    "d'installer chaque répertoire séparément)")
item.value['ES'] = ('[STRING] El directorio de la base de calibración donde '
                    'se guardan las calibraciones usadas en la base de datos. '
                    '(si no se da y no se da --datadir se pide al usuario que '
                    'lo introduzca si elige instalar cada directorio por '
                    'separado)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_TELLUDIR_HELP
# =============================================================================
item = langlist.create('INSTALL_TELLUDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The telluric database directory where telluric database files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately)'
item.value['FR'] = ('[STRING] Le répertoire de la base tellurique où sont '
                    'stockés les fichiers de la base tellurique. (si non '
                    "fourni et --datadir non fourni, l'utilisateur est invité "
                    "à le saisir s'il choisit d'installer chaque répertoire "
                    'séparément)')
item.value['ES'] = ('[STRING] El directorio de la base telúrica donde se '
                    'guardan sus archivos. (si no se da y no se da --datadir '
                    'se pide al usuario que lo introduzca si elige instalar '
                    'cada directorio por separado)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_PLOTDIR_HELP
# =============================================================================
item = langlist.create('INSTALL_PLOTDIR_HELP', kind='HELP')
item.value['ENG'] = 'The plot directory where plots/summary documents are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately)'
item.value['FR'] = ('Le répertoire des graphiques où sont stockés les '
                    'graphiques/documents récapitulatifs. (si non fourni et '
                    "--datadir non fourni, l'utilisateur est invité à le "
                    "saisir s'il choisit d'installer chaque répertoire "
                    'séparément)')
item.value['ES'] = ('El directorio de gráficos donde se guardan los '
                    'gráficos/documentos de resumen. (si no se da y no se da '
                    '--datadir se pide al usuario que lo introduzca si elige '
                    'instalar cada directorio por separado)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_RUNDIR_HELP
# =============================================================================
item = langlist.create('INSTALL_RUNDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The run directory where run/batch files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately)'
item.value['FR'] = ('[STRING] Le répertoire run où sont stockés les fichiers '
                    'run/batch. (si non fourni et --datadir non fourni, '
                    "l'utilisateur est invité à le saisir s'il choisit "
                    "d'installer chaque répertoire séparément)")
item.value['ES'] = ('[STRING] El directorio run donde se guardan los archivos '
                    'run/batch. (si no se da y no se da --datadir se pide al '
                    'usuario que lo introduzca si elige instalar cada '
                    'directorio por separado)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_ASSETDIR_HELP
# =============================================================================
item = langlist.create('INSTALL_ASSETDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The assets directory where assets files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install each directory separately)'
item.value['FR'] = ('[STRING] Le répertoire des ressources où sont stockés '
                    'les fichiers de ressources. (si non fourni et --datadir '
                    "non fourni, l'utilisateur est invité à le saisir s'il "
                    "choisit d'installer chaque répertoire séparément)")
item.value['ES'] = ('[STRING] El directorio de recursos donde se guardan los '
                    'archivos de recursos. (si no se da y no se da --datadir '
                    'se pide al usuario que lo introduzca si elige instalar '
                    'cada directorio por separado)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_LOGDIR_HELP
# =============================================================================
item = langlist.create('INSTALL_LOGDIR_HELP', kind='HELP')
item.value['ENG'] = 'The log directory where log and lock files are stored. (if not given and --datadir not given prompts the user to input if user chooses to install  each directory separately)'
item.value['FR'] = ('Le répertoire des journaux où sont stockés les fichiers '
                    'de journal et de verrou. (si non fourni et --datadir non '
                    "fourni, l'utilisateur est invité à le saisir s'il "
                    "choisit d'installer chaque répertoire séparément)")
item.value['ES'] = ('El directorio de registros donde se guardan los archivos '
                    'de registro y de bloqueo. (si no se da y no se da '
                    '--datadir se pide al usuario que lo introduzca si elige '
                    'instalar cada directorio por separado)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_PLOTMODE_HELP
# =============================================================================
item = langlist.create('INSTALL_PLOTMODE_HELP', kind='HELP')
item.value['ENG'] = '[INT] The plot mode. 0=Summary plots only 1=Plot at end of run 2=Plot at creation (pauses code). If unset user is prompted for choice.'
item.value['FR'] = ('[INT] Le mode de graphiques. 0=graphiques récapitulatifs '
                    "seulement 1=graphiques à la fin de l'exécution "
                    '2=graphiques à la création (met le code en pause). Si '
                    "non défini, l'utilisateur doit choisir.")
item.value['ES'] = ('[INT] El modo de gráficos. 0=solo gráficos de resumen '
                    '1=gráficos al final de la ejecución 2=gráficos al '
                    'crearse (pausa el código). Si no se define se pregunta '
                    'al usuario.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_CLEAN_HELP
# =============================================================================
item = langlist.create('INSTALL_CLEAN_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Whether to run from clean directories -  RECOMMENDED - clears out old files and copies over all required default data files. If unset user is prompted for  choice.'
item.value['FR'] = ("[BOOLEAN] S'il faut partir de répertoires propres - "
                    'RECOMMANDÉ - supprime les anciens fichiers et copie tous '
                    'les fichiers de données par défaut requis. Si non '
                    "défini, l'utilisateur doit choisir.")
item.value['ES'] = ('[BOOLEAN] Si ejecutar desde directorios limpios - '
                    'RECOMENDADO - elimina los archivos antiguos y copia '
                    'todos los archivos de datos por defecto requeridos. Si '
                    'no se define se pregunta al usuario.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_CLEAN_NO_WARNING_HELP
# =============================================================================
item = langlist.create('INSTALL_CLEAN_NO_WARNING_HELP', kind='HELP')
item.value['ENG'] = '[BOOLEAN] Whether to warn about cleaning populated directories - WARNING if set to True will delete all tmp/reduced/calibDB etc. data without prompt'
item.value['FR'] = ("[BOOLEAN] S'il faut avertir avant de nettoyer des "
                    'répertoires remplis - ATTENTION si True, supprime toutes '
                    'les données tmp/reduced/calibDB etc. sans confirmation')
item.value['ES'] = ('[BOOLEAN] Si advertir antes de limpiar directorios con '
                    'contenido - ADVERTENCIA si es True eliminará todos los '
                    'datos tmp/reduced/calibDB etc. sin preguntar')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DBMODE_HELP
# =============================================================================
item = langlist.create('INSTALL_DBMODE_HELP', kind='HELP')
item.value['ENG'] = '[INTEGER] Database mode (1: sqlite, 2: mysql). If unset user is prompted for choice.'
item.value['FR'] = ('[INTEGER] Mode de base de données (1 : sqlite, 2 : '
                    "mysql). Si non défini, l'utilisateur doit choisir.")
item.value['ES'] = ('[INTEGER] Modo de base de datos (1: sqlite, 2: mysql). '
                    'Si no se define se pregunta al usuario.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DB_HOST_HELP
# =============================================================================
item = langlist.create('INSTALL_DB_HOST_HELP', kind='HELP')
item.value['ENG'] = '[STRING] MySQL database hostname (Only required if --databasemode=2. If unset user is prompted for choice.'
item.value['FR'] = ("[STRING] Nom d'hôte de la base de données MySQL (requis "
                    'seulement si --databasemode=2. Si non défini, '
                    "l'utilisateur doit choisir.")
item.value['ES'] = ('[STRING] Nombre de host de la base de datos MySQL (solo '
                    'requerido si --databasemode=2. Si no se define se '
                    'pregunta al usuario.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DB_USER_HELP
# =============================================================================
item = langlist.create('INSTALL_DB_USER_HELP', kind='HELP')
item.value['ENG'] = '[STRING] MySQL database username (Only required if --databasemode=2. If unset user is prompted for choice.'
item.value['FR'] = ("[STRING] Nom d'utilisateur de la base de données MySQL "
                    '(requis seulement si --databasemode=2. Si non défini, '
                    "l'utilisateur doit choisir.")
item.value['ES'] = ('[STRING] Usuario de la base de datos MySQL (solo '
                    'requerido si --databasemode=2. Si no se define se '
                    'pregunta al usuario.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DB_PASS_HELP
# =============================================================================
item = langlist.create('INSTALL_DB_PASS_HELP', kind='HELP')
item.value['ENG'] = '[STRING] MySQL database password (Only required if --databasemode=2. If unset user is prompted for choice.'
item.value['FR'] = ('[STRING] Mot de passe de la base de données MySQL '
                    '(requis seulement si --databasemode=2. Si non défini, '
                    "l'utilisateur doit choisir.")
item.value['ES'] = ('[STRING] Contraseña de la base de datos MySQL (solo '
                    'requerido si --databasemode=2. Si no se define se '
                    'pregunta al usuario.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_DB_NAME_HELP
# =============================================================================
item = langlist.create('INSTALL_DB_NAME_HELP', kind='HELP')
item.value['ENG'] = '[STRING] MySQL database name (Only required if --databasemode=2. If unset user is prompted for choice.'
item.value['FR'] = ('[STRING] Nom de la base de données MySQL (requis '
                    'seulement si --databasemode=2. Si non défini, '
                    "l'utilisateur doit choisir.")
item.value['ES'] = ('[STRING] Nombre de la base de datos MySQL (solo '
                    'requerido si --databasemode=2. Si no se define se '
                    'pregunta al usuario.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_CALIBTABLE_HELP
# =============================================================================
item = langlist.create('INSTALL_CALIBTABLE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] APERO database table name suffix for the calibration database (default is the APERO profile name). If unset user is prompted for choice.'
item.value['FR'] = ('[STRING] Suffixe du nom de table APERO pour la base de '
                    'calibration (par défaut le nom du profil APERO). Si non '
                    "défini, l'utilisateur doit choisir.")
item.value['ES'] = ('[STRING] Sufijo del nombre de tabla APERO para la base '
                    'de calibración (por defecto el nombre del perfil APERO). '
                    'Si no se define se pregunta al usuario.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_TELLUTABLE_HELP
# =============================================================================
item = langlist.create('INSTALL_TELLUTABLE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] APERO database table name suffix for the telluric database (default is the APERO profile name). If unset user is prompted for choice.'
item.value['FR'] = ('[STRING] Suffixe du nom de table APERO pour la base '
                    'tellurique (par défaut le nom du profil APERO). Si non '
                    "défini, l'utilisateur doit choisir.")
item.value['ES'] = ('[STRING] Sufijo del nombre de tabla APERO para la base '
                    'telúrica (por defecto el nombre del perfil APERO). Si no '
                    'se define se pregunta al usuario.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_INDEXTABLE_HELP
# =============================================================================
item = langlist.create('INSTALL_INDEXTABLE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] APERO database table name suffix for the index database (default is the APERO profile name).'
item.value['FR'] = ('[STRING] Suffixe du nom de table APERO pour la base '
                    "d'index (par défaut le nom du profil APERO).")
item.value['ES'] = ('[STRING] Sufijo del nombre de tabla APERO para la base '
                    'de índice (por defecto el nombre del perfil APERO).')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_LOGTABLE_HELP
# =============================================================================
item = langlist.create('INSTALL_LOGTABLE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] APERO database table name suffix for the log database (default is the APERO profile name).'
item.value['FR'] = ('[STRING] Suffixe du nom de table APERO pour la base du '
                    'journal (par défaut le nom du profil APERO).')
item.value['ES'] = ('[STRING] Sufijo del nombre de tabla APERO para la base '
                    'del registro (por defecto el nombre del perfil APERO).')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_OBJTABLE_HELP
# =============================================================================
item = langlist.create('INSTALL_OBJTABLE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] APERO database table name suffix for the object database (default is the APERO profile name).'
item.value['FR'] = ('[STRING] Suffixe du nom de table APERO pour la base '
                    "d'objets (par défaut le nom du profil APERO).")
item.value['ES'] = ('[STRING] Sufijo del nombre de tabla APERO para la base '
                    'de objetos (por defecto el nombre del perfil APERO).')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_LANGTABLE_HELP
# =============================================================================
item = langlist.create('INSTALL_LANGTABLE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] APERO database table name suffix for the language database (default is the APERO profile name).'
item.value['FR'] = ('[STRING] Suffixe du nom de table APERO pour la base de '
                    'langue (par défaut le nom du profil APERO).')
item.value['ES'] = ('[STRING] Sufijo del nombre de tabla APERO para la base '
                    'de idioma (por defecto el nombre del perfil APERO).')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXECUTE_DESCRIPTION
# =============================================================================
item = langlist.create('EXECUTE_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Run APERO recipe for this apero profile.'
item.value['FR'] = 'Exécuter une recette APERO pour ce profil apero.'
item.value['ES'] = 'Ejecutar una receta APERO para este perfil de apero.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXECUTE_LIST_HELP
# =============================================================================
item = langlist.create('EXECUTE_XHELP_HELP', kind='HELP')
item.value['ENG'] = 'Display all usable recipes for this apero profile.'
item.value['FR'] = "Afficher l'aide pour la recette donnée"
item.value['ES'] = 'Mostrar la ayuda de la receta indicada'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXECUTE_RECIPE_HELP
# =============================================================================
item = langlist.create('EXECUTE_RECIPE_HELP', kind='HELP')
item.value['ENG'] = 'The recipe to run'
item.value['FR'] = 'La recette à exécuter'
item.value['ES'] = 'La receta a ejecutar'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXECUTE_ARGS_HELP
# =============================================================================
item = langlist.create('EXECUTE_ARGS_HELP', kind='HELP')
item.value['ENG'] = 'The args to pass to the recipe'
item.value['FR'] = 'Les arguments à passer à la recette'
item.value['ES'] = 'Los argumentos a pasar a la receta'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXECUTE_XHELP_HELP
# =============================================================================
item = langlist.create('EXECUTE_XHELP_HELP', kind='HELP')
item.value['ENG'] = 'Display help for the given recipe'
item.value['FR'] = "Afficher l'aide pour la recette donnée"
item.value['ES'] = 'Mostrar la ayuda de la receta indicada'
item.arguments = 'None'
item.comment = ''
langlist.add(item)


# =============================================================================
# ALL_TEXT
# =============================================================================
item = langlist.create('ALL_TEXT', kind='TEXT')
item.value['ENG'] = 'all'
item.value['FR'] = 'all'
item.value['ES'] = 'all'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GO_DESCRIPTION
# =============================================================================
item = langlist.create('GO_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Use this tool to find current paths set by current profile'
item.value['FR'] = ('Utiliser cet outil pour trouver les chemins définis par '
                    'le profil actuel')
item.value['ES'] = ('Use esta herramienta para encontrar las rutas definidas '
                    'por el perfil actual')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GO_DATA_HELP
# =============================================================================
item = langlist.create('GO_DATA_HELP', kind='HELP')
item.value['ENG'] = 'Find the current data directory'
item.value['FR'] = 'Trouver le répertoire de données actuel'
item.value['ES'] = 'Encontrar el directorio de datos actual'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GO_BLOCK_HELP
# =============================================================================
item = langlist.create('GO_BLOCK_HELP', kind='HELP')
item.value['ENG'] = 'Find the current {0} data directory'
item.value['FR'] = 'Trouver le répertoire de données {0} actuel'
item.value['ES'] = 'Encontrar el directorio de datos {0} actual'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LANGDB_DESC
# =============================================================================
item = langlist.create('LANGDB_DESC', kind='HELP')
item.value['ENG'] = 'Language database tools'
item.value['FR'] = 'Outils de la base de données de langue'
item.value['ES'] = 'Herramientas de la base de datos de idioma'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LANGDB_FIND_HELP
# =============================================================================
item = langlist.create('LANGDB_FIND_HELP', kind='HELP')
item.value['ENG'] = 'Displays the message locator GUI'
item.value['FR'] = "Affiche l'interface de recherche de messages"
item.value['ES'] = 'Muestra la interfaz de localización de mensajes'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LANGDB_UPDATE_HELP
# =============================================================================
item = langlist.create('LANGDB_UPDATE_HELP', kind='HELP')
item.value['ENG'] = 'Updates local language database and local text files with any changes'
item.value['FR'] = ('Met à jour la base de données de langue locale et les '
                    'fichiers texte locaux avec les modifications')
item.value['ES'] = ('Actualiza la base de datos de idioma local y los '
                    'archivos de texto locales con cualquier cambio')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LANGDB_RELOAD_HELP
# =============================================================================
item = langlist.create('LANGDB_RELOAD_HELP', kind='HELP')
item.value['ENG'] = 'Reloads the local language database (with text file changes)'
item.value['FR'] = ('Recharge la base de données de langue locale (avec les '
                    'modifications des fichiers texte)')
item.value['ES'] = ('Recarga la base de datos de idioma local (con los '
                    'cambios de los archivos de texto)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# INSTALL_REJECTTABLE_HELP
# =============================================================================
item = langlist.create('INSTALL_REJECTTABLE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] APERO database table name suffix for the reject database (default is the APERO profile name).'
item.value['FR'] = ('[STRING] Suffixe du nom de table APERO pour la base de '
                    'rejet (par défaut le nom du profil APERO).')
item.value['ES'] = ('[STRING] Sufijo del nombre de tabla APERO para la base '
                    'de rechazo (por defecto el nombre del perfil APERO).')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXTENDED_HELP
# =============================================================================
item = langlist.create('EXTENDED_HELP', kind='HELP')
item.value['ENG'] = 'Extended help menu (with all advanced arguments)'
item.value['FR'] = "Menu d'aide étendu (avec tous les arguments avancés)"
item.value['ES'] = ('Menú de ayuda extendido (con todos los argumentos '
                    'avanzados)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PRECHECK_DESCREIPTION
# =============================================================================
item = langlist.create('PRECHECK_DESCREIPTION', kind='HELP')
item.value['ENG'] = 'Run a check before running apero processing to check on the number of calibrations, number of telluric and science raw files and/or check if any objects astrometric data are coming from the header'
item.value['FR'] = ('Effectuer une vérification avant apero processing pour '
                    'contrôler le nombre de calibrations, de fichiers bruts '
                    'telluriques et science et/ou si des données '
                    "astrométriques d'objets proviennent de l'en-tête")
item.value['ES'] = ('Realizar una comprobación antes de apero processing para '
                    'revisar el número de calibraciones, de archivos brutos '
                    'telúricos y de ciencia y/o si algún dato astrométrico de '
                    'objetos procede de la cabecera')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PRECHECK_NOFILECHECK_HELP
# =============================================================================
item = langlist.create('PRECHECK_NOFILECHECK_HELP', kind='HELP')
item.value['ENG'] = 'Don’t check the number of files on disk and don’t flag these errors'
item.value['FR'] = ('Ne pas vérifier le nombre de fichiers sur disque et ne '
                    'pas signaler ces erreurs')
item.value['ES'] = ('No comprobar el número de archivos en disco y no señalar '
                    'estos errores')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PRECHECK_NOOBJCHECK_HELP
# =============================================================================
item = langlist.create('PRECHECK_NOOBJCHECK_HELP', kind='HELP')
item.value['ENG'] = 'Don’t check object database with current set of raw files and don’t flag these errors'
item.value['FR'] = ("Ne pas vérifier la base de données d'objets avec "
                    "l'ensemble actuel de fichiers bruts et ne pas signaler "
                    'ces erreurs')
item.value['ES'] = ('No comprobar la base de datos de objetos con el conjunto '
                    'actual de archivos brutos y no señalar estos errores')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TRIGGER_DESCRIPTION
# =============================================================================
item = langlist.create('TRIGGER_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Basic (brute force) trigger for APERO'
item.value['FR'] = 'Déclencheur basique (force brute) pour APERO'
item.value['ES'] = 'Disparador básico (fuerza bruta) para APERO'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TRIGGER_INDIR_HELP
# =============================================================================
item = langlist.create('TRIGGER_INDIR_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The input directory to scan for new data. (This is not the apero defined raw directory)'
item.value['FR'] = ("[STRING] Le répertoire d'entrée à analyser pour de "
                    "nouvelles données. (Ce n'est pas le répertoire raw "
                    'défini par apero)')
item.value['ES'] = ('[STRING] El directorio de entrada a explorar en busca de '
                    'nuevos datos. (No es el directorio raw definido por '
                    'apero)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TRIGGER_RESET_HELP
# =============================================================================
item = langlist.create('TRIGGER_RESET_HELP', kind='HELP')
item.value['ENG'] = 'Reset the trigger (default is False and thus we use cached files to speed up trigger). This means after nights are marked done (calib/sci) they will not be reprocessed. Thus --reset to avoid this.'
item.value['FR'] = ('Réinitialiser le déclencheur (par défaut False, on '
                    'utilise des fichiers en cache pour accélérer le '
                    'déclencheur). Une fois les nuits marquées terminées '
                    '(calib/sci) elles ne sont plus retraitées ; utilisez '
                    '--reset pour éviter cela.')
item.value['ES'] = ('Reiniciar el disparador (por defecto False, por lo que '
                    'se usan archivos en caché para acelerarlo). Esto '
                    'significa que una vez que las noches se marcan como '
                    'terminadas (calib/sci) no se reprocesan. Use --reset '
                    'para evitarlo.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TRIGGER_IGNORE_HELP
# =============================================================================
item = langlist.create('TRIGGER_IGNORE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Ignore certain obs_dir (observation directories) by default all directories in --indir are reduced. Using ignore will ignore certain directories and not add them to the the sym-linked (DRS_DATA_RAW) directory.'
item.value['FR'] = ('[STRING] Ignorer certains obs_dir (répertoires '
                    "d'observation) ; par défaut tous les répertoires de "
                    '--indir sont réduits. Les répertoires ignorés ne sont '
                    'pas ajoutés au répertoire lié symboliquement '
                    '(DRS_DATA_RAW).')
item.value['ES'] = ('[STRING] Ignorar ciertos obs_dir (directorios de '
                    'observación); por defecto se reducen todos los '
                    'directorios de --indir. Los directorios ignorados no se '
                    'añaden al directorio enlazado simbólicamente '
                    '(DRS_DATA_RAW).')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TRIGGER_WAIT_HELP
# =============================================================================
item = langlist.create('TRIGGER_WAIT_HELP', kind='HELP')
item.value['ENG'] = '[INTEGER] Number of second to wait between processing runs. Should not be too low (below 10s its too fast) unless testing, or too high (above 3600s)'
item.value['FR'] = ('[INTEGER] Nombre de secondes à attendre entre les '
                    'exécutions de traitement. Ne devrait être ni trop bas '
                    "(moins de 10 s c'est trop rapide) sauf pour des tests, "
                    'ni trop haut (plus de 3600 s)')
item.value['ES'] = ('[INTEGER] Número de segundos a esperar entre ejecuciones '
                    'de procesamiento. No debería ser demasiado bajo (menos '
                    'de 10 s es demasiado rápido) salvo para pruebas, ni '
                    'demasiado alto (más de 3600 s)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TRIGGER_CALIB_HELP
# =============================================================================
item = langlist.create('TRIGGER_CALIB_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The run.ini file to use for calibration trigger run'
item.value['FR'] = ("[STRING] Le fichier run.ini à utiliser pour l'exécution "
                    'déclenchée de calibration')
item.value['ES'] = ('[STRING] El archivo run.ini a usar para la ejecución '
                    'disparada de calibración')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TRIGGER_SCI_HELP
# =============================================================================
item = langlist.create('TRIGGER_SCI_HELP', kind='HELP')
item.value['ENG'] = '[STRING] The run.ini file to use for science trigger run'
item.value['FR'] = ("[STRING] Le fichier run.ini à utiliser pour l'exécution "
                    'déclenchée science')
item.value['ES'] = ('[STRING] El archivo run.ini a usar para la ejecución '
                    'disparada de ciencia')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# TRIGGER_TEST_HELP
# =============================================================================
item = langlist.create('TRIGGER_TEST_HELP', kind='HELP')
item.value['ENG'] = 'Active test mode (does not run recipes)'
item.value['FR'] = "Active le mode test (n'exécute pas les recettes)"
item.value['ES'] = 'Activa el modo de prueba (no ejecuta recetas)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LOGSTAT_MODE_HELP
# =============================================================================
item = langlist.create('LOGSTAT_MODE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Stats mode. Any combination of the following (separated by a comma, no white spaces). For all use “all”. For timing statistics use \"timing\". For quality control statistics use \"qc\". For error statistics use \"error\". For memory statistics use \"memory\". For file index use “findex”.  I.e. --mode=qc,memory  runs the qc and memory stats.'
item.value['FR'] = ('[STRING] Mode des statistiques. Toute combinaison des '
                    'suivants (séparés par une virgule, sans espaces). Pour '
                    'tout utilisez “all”. Pour les durées "timing". Pour le '
                    'contrôle qualité "qc". Pour les erreurs "error". Pour la '
                    'mémoire "memory". Pour l\'index de fichiers “findex”.  '
                    'Ex. --mode=qc,memory  exécute les statistiques qc et '
                    'mémoire.')
item.value['ES'] = ('[STRING] Modo de estadísticas. Cualquier combinación de '
                    'los siguientes (separados por comas, sin espacios). Para '
                    'todo use “all”. Para tiempos "timing". Para control de '
                    'calidad "qc". Para errores "error". Para memoria '
                    '"memory". Para el índice de archivos “findex”.  P. ej. '
                    '--mode=qc,memory  ejecuta las estadísticas de qc y '
                    'memoria.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LOGSTAT_PLOG_HELP
# =============================================================================
item = langlist.create('LOGSTAT_PLOG_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Specify a certain log file (full path)'
item.value['FR'] = '[STRING] Spécifier un fichier journal (chemin complet)'
item.value['ES'] = ('[STRING] Especificar un archivo de registro concreto '
                    '(ruta completa)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LOGSTAT_SQL_HELP
# =============================================================================
item = langlist.create('LOGSTAT_SQL_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Specify a SQL WHERE clause to narrow the stats'
item.value['FR'] = ('[STRING] Spécifier une clause SQL WHERE pour restreindre '
                    'les statistiques')
item.value['ES'] = ('[STRING] Especificar una cláusula SQL WHERE para acotar '
                    'las estadísticas')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RUN_INI_DESCRIPTION
# =============================================================================
item = langlist.create('RUN_INI_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Create default run.ini files for APERO instrument(s)'
item.value['FR'] = ('Créer les fichiers run.ini par défaut pour le(s) '
                    'instrument(s) APERO')
item.value['ES'] = ('Crear los archivos run.ini por defecto para el/los '
                    'instrumento(s) APERO')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RUN_INI_INSTRUMENT_HELP
# =============================================================================
item = langlist.create('RUN_INI_INSTRUMENT_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Instrument or instruments to create run.ini files for'
item.value['FR'] = ('[STRING] Instrument(s) pour lesquels créer les fichiers '
                    'run.ini')
item.value['ES'] = '[STRING] Instrumento(s) para los que crear archivos run.ini'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# STATIC_DESCRIPTION
# =============================================================================
item = langlist.create('STATIC_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Create static files for APERO instrument(s)'
item.value['FR'] = 'Créer les fichiers statiques pour le(s) instrument(s) APERO'
item.value['ES'] = ('Crear los archivos estáticos para el/los instrumento(s) '
                    'APERO')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# STATIC_MODE_HELP
# =============================================================================
item = langlist.create('STATIC_MODE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Chooses the static file to create'
item.value['FR'] = '[STRING] Choisit le fichier statique à créer'
item.value['ES'] = '[STRING] Elige el archivo estático a crear'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# VISU_DESCRIPTION
# =============================================================================
item = langlist.create('VISU_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'APERO visualizer'
item.value['FR'] = 'Visualiseur APERO'
item.value['ES'] = 'Visualizador APERO'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# VISU_MODE_HELP
# =============================================================================
item = langlist.create('VISU_MODE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Which type of graph to plot'
item.value['FR'] = '[STRING] Type de graphique à tracer'
item.value['ES'] = '[STRING] Tipo de gráfico a dibujar'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FAILEDQC_HELP
# =============================================================================
item = langlist.create('GET_FAILEDQC_HELP', kind='HELP')
item.value['ENG'] = 'Include files that failed QC. Highly unrecommended.'
item.value['FR'] = ('Inclure les fichiers ayant échoué au QC. Fortement '
                    'déconseillé.')
item.value['ES'] = 'Incluir archivos que fallaron el QC. Muy poco recomendable.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_DESCRIPTION
# =============================================================================
item = langlist.create('GET_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Use database to search and copy any files quickly'
item.value['FR'] = ('Utiliser la base de données pour rechercher et copier '
                    'rapidement les fichiers')
item.value['ES'] = ('Usar la base de datos para buscar y copiar archivos '
                    'rápidamente')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXPLORER_RECIPE
# =============================================================================
item = langlist.create('EXPLORER_RECIPE', kind='HELP')
item.value['ENG'] = '[STRING] Recipe or shortname for recipe (must be used in combination with –flagnum)'
item.value['FR'] = ('[STRING] Recette ou nom court de recette (à utiliser '
                    'avec –flagnum)')
item.value['ES'] = ('[STRING] Receta o nombre corto de receta (debe usarse '
                    'junto con –flagnum)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# EXPLORER_FLAGNUM
# =============================================================================
item = langlist.create('EXPLORER_FLAGNUM', kind='HELP')
item.value['ENG'] = '[INTEGER] Instead of running explorer converts a binary flagg to a set of binary flags for a recipe (must be used in combination with –recipe)'
item.value['FR'] = ("[INTEGER] Au lieu de lancer l'explorateur, convertit un "
                    'drapeau binaire en un ensemble de drapeaux binaires pour '
                    'une recette (à utiliser avec –recipe)')
item.value['ES'] = ('[INTEGER] En lugar de ejecutar el explorador convierte '
                    'una bandera binaria en un conjunto de banderas binarias '
                    'para una receta (debe usarse junto con –recipe)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_MODE_HELP
# =============================================================================
item = langlist.create('REMAKE_MODE_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Which mode to output in \"html\", \"latex\" or \"both\". Default is \"both\".'
item.value['FR'] = ('[STRING] Mode de sortie "html", "latex" ou "both". Par '
                    'défaut "both".')
item.value['ES'] = ('[STRING] Modo de salida "html", "latex" o "both". Por '
                    'defecto "both".')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_INSTRUMENT_HELP
# =============================================================================
item = langlist.create('REMAKE_INSTRUMENT_HELP', kind='HELP')
item.value['ENG'] = '[STRING] Which instrument(s) to run this for (default is current instrument) can also write ALL to get all instruments or list instruments separated by a comma'
item.value['FR'] = ('[STRING] Instrument(s) pour lesquels exécuter ceci (par '
                    "défaut l'instrument actuel) ; ALL pour tous les "
                    "instruments ou liste d'instruments séparés par une "
                    'virgule')
item.value['ES'] = ('[STRING] Instrumento(s) para los que ejecutar esto (por '
                    'defecto el instrumento actual); también puede escribir '
                    'ALL para todos o una lista de instrumentos separados por '
                    'comas')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_DELETE_HELP
# =============================================================================
item = langlist.create('DBMGR_DELETE_HELP', kind='HELP')
item.value['ENG'] = 'Load up the delete table GUI (MySQL only)'
item.value['FR'] = ("Charger l'interface de suppression de table (MySQL "
                    'uniquement)')
item.value['ES'] = 'Cargar la interfaz de borrado de tablas (solo MySQL)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_RESET_HELP
# =============================================================================
item = langlist.create('DBMGR_RESET_HELP', kind='HELP')
item.value['ENG'] = 'Reset current databases'
item.value['FR'] = 'Réinitialiser les bases de données actuelles'
item.value['ES'] = 'Reiniciar las bases de datos actuales'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_CALIBDB_HELP
# =============================================================================
item = langlist.create('DBMGR_CALIBDB_HELP', kind='HELP')
item.value['ENG'] = 'Update calibration database'
item.value['FR'] = 'Mettre à jour la base de données de calibration'
item.value['ES'] = 'Actualizar la base de datos de calibración'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_TELLUDB_HELP
# =============================================================================
item = langlist.create('DBMGR_TELLUDB_HELP', kind='HELP')
item.value['ENG'] = 'Update telluric database'
item.value['FR'] = 'Mettre à jour la base de données tellurique'
item.value['ES'] = 'Actualizar la base de datos telúrica'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_LOGDB_HELP
# =============================================================================
item = langlist.create('DBMGR_LOGDB_HELP', kind='HELP')
item.value['ENG'] = 'Update log database'
item.value['FR'] = 'Mettre à jour la base de données du journal'
item.value['ES'] = 'Actualizar la base de datos del registro'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_FINDEXDB_HELP
# =============================================================================
item = langlist.create('DBMGR_FINDEXDB_HELP', kind='HELP')
item.value['ENG'] = 'Update file index database'
item.value['FR'] = "Mettre à jour la base de données d'index de fichiers"
item.value['ES'] = 'Actualizar la base de datos de índice de archivos'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_ASTROMDB_HELP
# =============================================================================
item = langlist.create('DBMGR_ASTROMDB_HELP', kind='HELP')
item.value['ENG'] = 'Update astrometric database'
item.value['FR'] = 'Mettre à jour la base de données astrométrique'
item.value['ES'] = 'Actualizar la base de datos astrométrica'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DBMGR_REJECTDB_HELP
# =============================================================================
item = langlist.create('DBMGR_REJECTDB_HELP', kind='HELP')
item.value['ENG'] = 'Update rejection database'
item.value['FR'] = 'Mettre à jour la base de données de rejet'
item.value['ES'] = 'Actualizar la base de datos de rechazo'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ASTROMETRIC_OVERWRITE_HELP
# =============================================================================
item = langlist.create('ASTROMETRIC_OVERWRITE_HELP', kind='HELP')
item.value['ENG'] = 'Do not check if object is currently in database. Overwrite old value.'
item.value['FR'] = ("Ne pas vérifier si l'objet est déjà dans la base de "
                    "données. Écraser l'ancienne valeur.")
item.value['ES'] = ('No comprobar si el objeto está actualmente en la base de '
                    'datos. Sobrescribir el valor anterior.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ASTROMETRIC_GETTEFF_HELP
# =============================================================================
item = langlist.create('ASTROMETRIC_GETTEFF_HELP', kind='HELP')
item.value['ENG'] = 'Attempt to get Teff from header value. Requires a raw file of this object and the index database to be up-to-date'
item.value['FR'] = ("Tenter d'obtenir Teff depuis la valeur d'en-tête. "
                    'Nécessite un fichier brut de cet objet et une base de '
                    "données d'index à jour")
item.value['ES'] = ('Intentar obtener Teff del valor de la cabecera. Requiere '
                    'un archivo bruto de este objeto y que la base de datos '
                    'de índice esté actualizada')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ASTROMETRIC_NOPM_REQ_HELP
# =============================================================================
item = langlist.create('ASTROMETRIC_NOPM_REQ_HELP', kind='HELP')
item.value['ENG'] = 'Do not require proper motion (not recommended)'
item.value['FR'] = 'Ne pas exiger de mouvement propre (non recommandé)'
item.value['ES'] = 'No requerir movimiento propio (no recomendado)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ASTROMETRIC_TEST_HELP
# =============================================================================
item = langlist.create('ASTROMETRIC_TEST_HELP', kind='HELP')
item.value['ENG'] = 'Run in test mode (do not add to database)'
item.value['FR'] = 'Exécuter en mode test (ne pas ajouter à la base de données)'
item.value['ES'] = 'Ejecutar en modo de prueba (no añadir a la base de datos)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_RUNFILE_HELP
# =============================================================================
item = langlist.create('SET_RUNFILE_HELP', kind='HELP')
item.value['ENG'] = 'Set a run file to override default arguments'
item.value['FR'] = ("Définir un fichier d'exécution pour remplacer les "
                    'arguments par défaut')
item.value['ES'] = ('Definir un archivo de ejecución para reemplazar los '
                    'argumentos por defecto')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# SET_NOSAVE_HELP
# =============================================================================
item = langlist.create('SET_NOSAVE_HELP', kind='HELP')
item.value['ENG'] = 'Do not save any outputs (debug/information run). Note some recipes require other recipesto be run. Only use --nosave after previous recipe runs have been run successfully at least once.'
item.value['FR'] = ('Ne sauvegarder aucune sortie (exécution de '
                    'débogage/information). Notez que certaines recettes '
                    "nécessitent l'exécution d'autres recettes. N'utilisez "
                    "--nosave qu'après avoir exécuté avec succès au moins une "
                    'fois les recettes précédentes.')
item.value['ES'] = ('No guardar ninguna salida (ejecución de '
                    'depuración/información). Tenga en cuenta que algunas '
                    'recetas requieren que se ejecuten otras recetas. Use '
                    '--nosave solo después de que las recetas previas se '
                    'hayan ejecutado con éxito al menos una vez.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_EXTRACT_COMBINE_METHOD_HELP
# =============================================================================
item = langlist.create('APERO_EXTRACT_COMBINE_METHOD_HELP', kind='HELP')
item.value['ENG'] = 'Method to combine files (if --combine=True)'
item.value['FR'] = 'Méthode de combinaison des fichiers (si --combine=True)'
item.value['ES'] = 'Método para combinar archivos (si --combine=True)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_EXTRACT_FORCE_REF_WAVE_HELP
# =============================================================================
item = langlist.create('APERO_EXTRACT_FORCE_REF_WAVE_HELP', kind='HELP')
item.value['ENG'] = 'Force using the reference wave solution'
item.value['FR'] = ("Forcer l'utilisation de la solution en longueur d'onde "
                    'de référence')
item.value['ES'] = ('Forzar el uso de la solución de longitud de onda de '
                    'referencia')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_FIT_TELLU_FINITERES_HELP
# =============================================================================
item = langlist.create('APERO_FIT_TELLU_FINITERES_HELP', kind='HELP')
item.value['ENG'] = ('Whether to do the finite resolution correction (Always '
                     'false if no template)')
item.value['FR'] = ('Faire ou non la correction de résolution finie (toujours '
                    'faux sans modèle)')
item.value['ES'] = ('Si hacer la corrección de resolución finita (siempre '
                    'falso si no hay plantilla)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# FTELLU_ONLYPRECLEAN_HELP
# =============================================================================
item = langlist.create('FTELLU_ONLYPRECLEAN_HELP', kind='HELP')
item.value['ENG'] = ('Only run the precleaning steps (not recommended - for '
                     'debugging ONLY)')
item.value['FR'] = ('Exécuter uniquement les étapes de pré-nettoyage (non '
                    'recommandé - pour le débogage UNIQUEMENT)')
item.value['ES'] = ('Ejecutar solo los pasos de pre-limpieza (no recomendado '
                    '- SOLO para depuración)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_FLAT_FORCEEXT_HELP
# =============================================================================
item = langlist.create('APERO_FLAT_FORCEEXT_HELP', kind='HELP')
item.value['ENG'] = ('If True, always re-extract the flat even if the output '
                     'already exists (overrides CAL.FLAT.ALWAYS_EXTRACT)')
item.value['FR'] = ('Si True, toujours ré-extraire le flat même si la sortie '
                    'existe déjà (remplace CAL.FLAT.ALWAYS_EXTRACT)')
item.value['ES'] = ('Si es True, siempre volver a extraer el flat aunque la '
                    'salida ya exista (anula CAL.FLAT.ALWAYS_EXTRACT)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_LBL_COMPILE_DESCRIPTION
# =============================================================================
item = langlist.create('APERO_LBL_COMPILE_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Run LBL compute'
item.value['FR'] = 'Exécuter le calcul LBL'
item.value['ES'] = 'Ejecutar el cálculo LBL'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_LBL_COMPUTE_DESCRIPTION
# =============================================================================
item = langlist.create('APERO_LBL_COMPUTE_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Run LBL compute'
item.value['FR'] = 'Exécuter le calcul LBL'
item.value['ES'] = 'Ejecutar el cálculo LBL'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# LBL_COMPUTE_ITER_HELP
# =============================================================================
item = langlist.create('LBL_COMPUTE_ITER_HELP', kind='HELP')
item.value['ENG'] = 'Iteration number (for multiprocessing)'
item.value['FR'] = "Numéro d'itération (pour le multiprocessus)"
item.value['ES'] = 'Número de iteración (para multiproceso)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_LBL_COMPUTE_TOTAL_HELP
# =============================================================================
item = langlist.create('APERO_LBL_COMPUTE_TOTAL_HELP', kind='HELP')
item.value['ENG'] = 'Total number of iterations (for multiprocessing)'
item.value['FR'] = "Nombre total d'itérations (pour le multiprocessus)"
item.value['ES'] = 'Número total de iteraciones (para multiproceso)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_LBL_MASK_DESCRIPTION
# =============================================================================
item = langlist.create('APERO_LBL_MASK_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Create LBL mask'
item.value['FR'] = 'Créer le masque LBL'
item.value['ES'] = 'Crear máscara LBL'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_LBL_REF_DESCRIPTION
# =============================================================================
item = langlist.create('APERO_LBL_REF_DESCRIPTION', kind='HELP')
item.value['ENG'] = ('LBL Setup and reference recipe (Run before any other '
                     'LBL steps)')
item.value['FR'] = ('Recette de configuration et de référence LBL (à exécuter '
                    'avant toute autre étape LBL)')
item.value['ES'] = ('Receta de configuración y referencia de LBL (ejecutar '
                    'antes de cualquier otro paso de LBL)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_LBL_REF_OBJNAMES_HELP
# =============================================================================
item = langlist.create('APERO_LBL_REF_OBJNAMES_HELP', kind='HELP')
item.value['ENG'] = ('Name of the objects to copy, if None copies all objects '
                     'available.')
item.value['FR'] = ('Nom des objets à copier ; si None, copie tous les objets '
                    'disponibles.')
item.value['ES'] = ('Nombre de los objetos a copiar; si es None copia todos '
                    'los objetos disponibles.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_LBL_REF_TEST_HELP
# =============================================================================
item = langlist.create('APERO_LBL_REF_TEST_HELP', kind='HELP')
item.value['ENG'] = 'Run in test mode'
item.value['FR'] = 'Exécuter en mode test'
item.value['ES'] = 'Ejecutar en modo de prueba'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_LEAK_REF_FORCEEXT_HELP
# =============================================================================
item = langlist.create('APERO_LEAK_REF_FORCEEXT_HELP', kind='HELP')
item.value['ENG'] = ('If True, always re-extract the leak reference even if '
                     'the output already exists (overrides '
                     'CAL.LEAK.ALWAYS_EXTRACT)')
item.value['FR'] = ('Si True, toujours ré-extraire la référence de fuite même '
                    'si la sortie existe déjà (remplace '
                    'CAL.LEAK.ALWAYS_EXTRACT)')
item.value['ES'] = ('Si es True, siempre volver a extraer la referencia de '
                    'fuga aunque la salida ya exista (anula '
                    'CAL.LEAK.ALWAYS_EXTRACT)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_MK_TELLU_FINITERES_HELP
# =============================================================================
item = langlist.create('APERO_MK_TELLU_FINITERES_HELP', kind='HELP')
item.value['ENG'] = ('Whether to do the finite resolution correction (Always '
                     'false if no template)')
item.value['FR'] = ('Faire ou non la correction de résolution finie (toujours '
                    'faux sans modèle)')
item.value['ES'] = ('Si hacer la corrección de resolución finita (siempre '
                    'falso si no hay plantilla)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_POL_EXP1_HELP
# =============================================================================
item = langlist.create('APERO_POL_EXP1_HELP', kind='HELP')
item.value['ENG'] = 'Override input exposure 1'
item.value['FR'] = "Remplacer l'exposition d'entrée 1"
item.value['ES'] = 'Reemplazar la exposición de entrada 1'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_POL_EXP2_HELP
# =============================================================================
item = langlist.create('APERO_POL_EXP2_HELP', kind='HELP')
item.value['ENG'] = 'Override input exposure 2'
item.value['FR'] = "Remplacer l'exposition d'entrée 2"
item.value['ES'] = 'Reemplazar la exposición de entrada 2'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_POL_EXP3_HELP
# =============================================================================
item = langlist.create('APERO_POL_EXP3_HELP', kind='HELP')
item.value['ENG'] = 'Override input exposure 3'
item.value['FR'] = "Remplacer l'exposition d'entrée 3"
item.value['ES'] = 'Reemplazar la exposición de entrada 3'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_POL_EXP4_HELP
# =============================================================================
item = langlist.create('APERO_POL_EXP4_HELP', kind='HELP')
item.value['ENG'] = 'Override input exposure 4'
item.value['FR'] = "Remplacer l'exposition d'entrée 4"
item.value['ES'] = 'Reemplazar la exposición de entrada 4'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_POL_EXPOSURES_HELP
# =============================================================================
item = langlist.create('APERO_POL_EXPOSURES_HELP', kind='HELP')
item.value['ENG'] = 'List of exposures to add (order determined by recipe)'
item.value['FR'] = ('Liste des expositions à ajouter (ordre déterminé par la '
                    'recette)')
item.value['ES'] = ('Lista de exposiciones a añadir (orden determinado por la '
                    'receta)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_POL_LSDMASK_HELP
# =============================================================================
item = langlist.create('APERO_POL_LSDMASK_HELP', kind='HELP')
item.value['ENG'] = 'LSD mask'
item.value['FR'] = 'Masque LSD'
item.value['ES'] = 'Máscara LSD'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_POL_LSD_HELP
# =============================================================================
item = langlist.create('APERO_POL_LSD_HELP', kind='HELP')
item.value['ENG'] = 'Run LSD analysis'
item.value['FR'] = "Exécuter l'analyse LSD"
item.value['ES'] = 'Ejecutar el análisis LSD'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_POL_NOQCCHECK_HELP
# =============================================================================
item = langlist.create('APERO_POL_NOQCCHECK_HELP', kind='HELP')
item.value['ENG'] = 'Do not check quality control of inputs'
item.value['FR'] = 'Ne pas vérifier le contrôle qualité des entrées'
item.value['ES'] = 'No comprobar el control de calidad de las entradas'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_POL_OBJRV_HELP
# =============================================================================
item = langlist.create('APERO_POL_OBJRV_HELP', kind='HELP')
item.value['ENG'] = 'Object radial velocity [km/s]'
item.value['FR'] = "Vitesse radiale de l'objet [km/s]"
item.value['ES'] = 'Velocidad radial del objeto [km/s]'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_POL_OUTPUT_HELP
# =============================================================================
item = langlist.create('APERO_POL_OUTPUT_HELP', kind='HELP')
item.value['ENG'] = 'Output file'
item.value['FR'] = 'Fichier de sortie'
item.value['ES'] = 'Archivo de salida'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_POL_OUTPUT_LSD_HELP
# =============================================================================
item = langlist.create('APERO_POL_OUTPUT_LSD_HELP', kind='HELP')
item.value['ENG'] = 'Output LSD file'
item.value['FR'] = 'Fichier LSD de sortie'
item.value['ES'] = 'Archivo LSD de salida'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_STATIC_YAMLFILE_HELP
# =============================================================================
item = langlist.create('APERO_STATIC_YAMLFILE_HELP', kind='HELP')
item.value['ENG'] = 'Static YAML definition file'
item.value['FR'] = 'Fichier YAML de définition statique'
item.value['ES'] = 'Archivo YAML de definición estática'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_WAVE_NIGHT_FORCEEXT_HELP
# =============================================================================
item = langlist.create('APERO_WAVE_NIGHT_FORCEEXT_HELP', kind='HELP')
item.value['ENG'] = 'WAVE_EXTRACT_HELP'
item.value['FR'] = 'WAVE_EXTRACT_HELP'
item.value['ES'] = 'WAVE_EXTRACT_HELP'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# APERO_WAVE_REF_FORCEEXT_HELP
# =============================================================================
item = langlist.create('APERO_WAVE_REF_FORCEEXT_HELP', kind='HELP')
item.value['ENG'] = 'WAVE_EXTRACT_HELP'
item.value['FR'] = 'WAVE_EXTRACT_HELP'
item.value['ES'] = 'WAVE_EXTRACT_HELP'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ARI_CORES_HELP
# =============================================================================
item = langlist.create('ARI_CORES_HELP', kind='HELP')
item.value['ENG'] = ('Number of cores to use (default is 0, which uses value '
                     'from yaml file)')
item.value['FR'] = ('Nombre de cœurs à utiliser (par défaut 0, qui utilise la '
                    'valeur du fichier yaml)')
item.value['ES'] = ('Número de núcleos a usar (por defecto 0, que usa el '
                    'valor del archivo yaml)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ARI_DESCRIPTION
# =============================================================================
item = langlist.create('ARI_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'Run the ARI (APERO reduction interface)'
item.value['FR'] = "Lancer l'ARI (interface de réduction APERO)"
item.value['ES'] = 'Ejecutar el ARI (interfaz de reducción APERO)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ARI_FILTEROBJS_HELP
# =============================================================================
item = langlist.create('ARI_FILTEROBJS_HELP', kind='HELP')
item.value['ENG'] = ('Only process these objects (should only be used for '
                     'debugging). List of comma separated objects (named as '
                     'in astrometric database) ')
item.value['FR'] = ('Traiter uniquement ces objets (pour le débogage '
                    "uniquement). Liste d'objets séparés par des virgules "
                    '(nommés comme dans la base astrométrique) ')
item.value['ES'] = ('Procesar solo estos objetos (solo debe usarse para '
                    'depuración). Lista de objetos separados por comas (con '
                    'el nombre de la base astrométrica) ')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ARI_FINDER_CREATE_HELP
# =============================================================================
item = langlist.create('ARI_FINDER_CREATE_HELP', kind='HELP')
item.value['ENG'] = 'Overwrites the profile setting to create finder charts'
item.value['FR'] = ('Remplace le paramètre du profil pour créer les cartes de '
                    'champ')
item.value['ES'] = ('Sobrescribe la configuración del perfil para crear '
                    'cartas de campo')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ARI_FINDER_RESET_HELP
# =============================================================================
item = langlist.create('ARI_FINDER_RESET_HELP', kind='HELP')
item.value['ENG'] = 'Overwrites the profile setting to reset finder charts'
item.value['FR'] = ('Remplace le paramètre du profil pour réinitialiser les '
                    'cartes de champ')
item.value['ES'] = ('Sobrescribe la configuración del perfil para reiniciar '
                    'cartas de campo')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ARI_PROFILES_HELP
# =============================================================================
item = langlist.create('ARI_PROFILES_HELP', kind='HELP')
item.value['ENG'] = ('List allowed profiles (and path to profiles), as '
                     'profile is usually required any invalid profile yaml '
                     'also displays this and exits.')
item.value['FR'] = ('Lister les profils autorisés (et le chemin des profils) '
                    '; comme un profil est généralement requis, tout yaml de '
                    'profil invalide affiche aussi ceci et quitte.')
item.value['ES'] = ('Listar los perfiles permitidos (y la ruta a los '
                    'perfiles); como normalmente se requiere un perfil, '
                    'cualquier yaml de perfil no válido también muestra esto '
                    'y sale.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ARI_PROFILE_HELP
# =============================================================================
item = langlist.create('ARI_PROFILE_HELP', kind='HELP')
item.value['ENG'] = 'ARI yaml file to use'
item.value['FR'] = 'Fichier yaml ARI à utiliser'
item.value['ES'] = 'Archivo yaml de ARI a utilizar'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ARI_REDO_OBJS_HELP
# =============================================================================
item = langlist.create('ARI_REDO_OBJS_HELP', kind='HELP')
item.value['ENG'] = ('List of comma separated objects (named as in '
                     'astrometric database) to redo. All others will be taken '
                     'from storage unless not currently processed.')
item.value['FR'] = ("Liste d'objets séparés par des virgules (nommés comme "
                    'dans la base astrométrique) à refaire. Tous les autres '
                    "seront repris du stockage sauf s'ils ne sont pas encore "
                    'traités.')
item.value['ES'] = ('Lista de objetos separados por comas (con el nombre de '
                    'la base astrométrica) a rehacer. Todos los demás se '
                    'tomarán del almacenamiento salvo que no estén procesados '
                    'actualmente.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ARI_RESET_HELP
# =============================================================================
item = langlist.create('ARI_RESET_HELP', kind='HELP')
item.value['ENG'] = 'Reset ARI'
item.value['FR'] = 'Réinitialiser ARI'
item.value['ES'] = 'Reiniciar ARI'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ASTROMETRIC_ALIASES_HELP
# =============================================================================
item = langlist.create('ASTROMETRIC_ALIASES_HELP', kind='HELP')
item.value['ENG'] = ('Aliases to add to the database for this object. Note '
                     'this should only be used with a single object name.')
item.value['FR'] = ('Alias à ajouter à la base de données pour cet objet. À '
                    "utiliser uniquement avec un seul nom d'objet.")
item.value['ES'] = ('Alias a añadir a la base de datos para este objeto. Solo '
                    'debe usarse con un único nombre de objeto.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ASTROMETRIC_CHECK_HELP
# =============================================================================
item = langlist.create('ASTROMETRIC_CHECK_HELP', kind='HELP')
item.value['ENG'] = 'Check object database for basic errors'
item.value['FR'] = ("Vérifier la base de données d'objets pour les erreurs de "
                    'base')
item.value['ES'] = ('Comprobar la base de datos de objetos en busca de '
                    'errores básicos')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# ASTROMETRIC_FILEOPTION_HELP
# =============================================================================
item = langlist.create('ASTROMETRIC_FILEOPTION_HELP', kind='HELP')
item.value['ENG'] = ('Use a absolute filepath to identy an object (i.e. from '
                     'RA/Dec). Note this overrides "OBJECTS", however OBJECT '
                     'must be set to something to run astrometrics.')
item.value['FR'] = ('Utiliser un chemin absolu pour identifier un objet (ex. '
                    'depuis RA/Dec). Notez que ceci remplace "OBJECTS", mais '
                    "OBJECT doit être défini pour lancer l'astrométrie.")
item.value['ES'] = ('Usar una ruta absoluta para identificar un objeto (p. '
                    'ej. desde RA/Dec). Tenga en cuenta que esto anula '
                    '"OBJECTS", aunque OBJECT debe estar definido para '
                    'ejecutar la astrometría.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATABASE_MGR_BEFORE_HELP
# =============================================================================
item = langlist.create('DATABASE_MGR_BEFORE_HELP', kind='HELP')
item.value['ENG'] = ('Date to remove entries before (used in combination with '
                     '--telludb or --calibdb) format is YYYY-MM-DD or '
                     'YYYY-MM-DD hh:mm:ss')
item.value['FR'] = ('Date avant laquelle supprimer les entrées (avec '
                    '--telludb ou --calibdb), format YYYY-MM-DD ou YYYY-MM-DD '
                    'hh:mm:ss')
item.value['ES'] = ('Fecha antes de la cual eliminar entradas (junto con '
                    '--telludb o --calibdb), formato YYYY-MM-DD o YYYY-MM-DD '
                    'hh:mm:ss')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATABASE_MGR_BLOCK_KIND_HELP
# =============================================================================
item = langlist.create('DATABASE_MGR_BLOCK_KIND_HELP', kind='HELP')
item.value['ENG'] = 'Block kind filter (not always used)'
item.value['FR'] = 'Filtre sur le type de bloc (pas toujours utilisé)'
item.value['ES'] = 'Filtro por tipo de bloque (no siempre se usa)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATABASE_MGR_CORES_HELP
# =============================================================================
item = langlist.create('DATABASE_MGR_CORES_HELP', kind='HELP')
item.value['ENG'] = ('Number of cores to use for parallel database updates '
                     '(default is 0, which uses value from yaml file). Use '
                     'with --update to enable parallel processing for calib, '
                     'tellu, log, and index databases.')
item.value['FR'] = ('Nombre de cœurs pour les mises à jour parallèles des '
                    'bases de données (par défaut 0, qui utilise la valeur du '
                    'fichier yaml). À utiliser avec --update pour activer le '
                    'traitement parallèle des bases calib, tellu, log et '
                    'index.')
item.value['ES'] = ('Número de núcleos para actualizaciones paralelas de '
                    'bases de datos (por defecto 0, que usa el valor del '
                    'archivo yaml). Úselo con --update para activar el '
                    'procesamiento paralelo de las bases calib, tellu, log e '
                    'index.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATABASE_MGR_DBKIND_HELP
# =============================================================================
item = langlist.create('DATABASE_MGR_DBKIND_HELP', kind='HELP')
item.value['ENG'] = ('Database kind to update or reset. Must use inconjuction '
                     'with --update or --reset')
item.value['FR'] = ('Type de base de données à mettre à jour ou '
                    'réinitialiser. À utiliser avec --update ou --reset')
item.value['ES'] = ('Tipo de base de datos a actualizar o reiniciar. Debe '
                    'usarse junto con --update o --reset')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATABASE_MGR_DELETEFILES_HELP
# =============================================================================
item = langlist.create('DATABASE_MGR_DELETEFILES_HELP', kind='HELP')
item.value['ENG'] = ('Whether to delete files from disk when removing entries '
                     '(using in combination with --telludb or --calibdb and '
                     '--since / --keys)')
item.value['FR'] = ('Supprimer ou non les fichiers du disque lors de la '
                    'suppression des entrées (avec --telludb ou --calibdb et '
                    '--since / --keys)')
item.value['ES'] = ('Si eliminar archivos del disco al eliminar entradas '
                    '(junto con --telludb o --calibdb y --since / --keys)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATABASE_MGR_KEYS_HELP
# =============================================================================
item = langlist.create('DATABASE_MGR_KEYS_HELP', kind='HELP')
item.value['ENG'] = ('Keyname of entries to remove (used in combination with '
                     '--telludb or --calibdb)')
item.value['FR'] = ('Nom de clé des entrées à supprimer (avec --telludb ou '
                    '--calibdb)')
item.value['ES'] = ('Nombre de clave de las entradas a eliminar (junto con '
                    '--telludb o --calibdb)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATABASE_MGR_PUSHNAME_HELP
# =============================================================================
item = langlist.create('DATABASE_MGR_PUSHNAME_HELP', kind='HELP')
item.value['ENG'] = 'Shortname of the pending database entries to push'
item.value['FR'] = ('Nom court des entrées de base de données en attente à '
                    'envoyer')
item.value['ES'] = ('Nombre corto de las entradas de base de datos pendientes '
                    'a enviar')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATABASE_MGR_PUSH_HELP
# =============================================================================
item = langlist.create('DATABASE_MGR_PUSH_HELP', kind='HELP')
item.value['ENG'] = 'Push pending database entries to the database'
item.value['FR'] = 'Envoyer les entrées en attente vers la base de données'
item.value['ES'] = 'Enviar las entradas pendientes a la base de datos'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATABASE_MGR_SINCE_HELP
# =============================================================================
item = langlist.create('DATABASE_MGR_SINCE_HELP', kind='HELP')
item.value['ENG'] = ('Date to remove entries since (used in combination with '
                     '--telludb or --calibdb) format is YYYY-MM-DD or '
                     'YYYY-MM-DD hh:mm:ss')
item.value['FR'] = ('Date depuis laquelle supprimer les entrées (avec '
                    '--telludb ou --calibdb), format YYYY-MM-DD ou YYYY-MM-DD '
                    'hh:mm:ss')
item.value['ES'] = ('Fecha desde la cual eliminar entradas (junto con '
                    '--telludb o --calibdb), formato YYYY-MM-DD o YYYY-MM-DD '
                    'hh:mm:ss')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DATABASE_MGR_TEST_HELP
# =============================================================================
item = langlist.create('DATABASE_MGR_TEST_HELP', kind='HELP')
item.value['ENG'] = 'Run the removal of entries in test mode'
item.value['FR'] = 'Exécuter la suppression des entrées en mode test'
item.value['ES'] = 'Ejecutar la eliminación de entradas en modo de prueba'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# DB_PUSH_DESCRIPTION
# =============================================================================
item = langlist.create('DB_PUSH_DESCRIPTION', kind='HELP')
item.value['ENG'] = ('Push all pending database entries into the databases. '
                     'apero_processing (queue mode) adds one run after every '
                     'queue group so the next group can use the outputs of '
                     'the previous group')
item.value['FR'] = ('Envoyer toutes les entrées de base de données en attente '
                    'dans les bases. apero_processing (mode file) ajoute une '
                    'exécution après chaque groupe de la file pour que le '
                    'groupe suivant puisse utiliser les sorties du précédent')
item.value['ES'] = ('Enviar todas las entradas de base de datos pendientes a '
                    'las bases. apero_processing (modo cola) añade una '
                    'ejecución tras cada grupo de la cola para que el '
                    'siguiente grupo pueda usar las salidas del anterior')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_ASSETS_HELP
# =============================================================================
item = langlist.create('GET_FILES_ASSETS_HELP', kind='HELP')
item.value['ENG'] = 'Download the assets to the github directory'
item.value['FR'] = 'Télécharger les ressources dans le répertoire github'
item.value['ES'] = 'Descargar los recursos al directorio de github'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_BLOCK_KIND_HELP
# =============================================================================
item = langlist.create('GET_FILES_BLOCK_KIND_HELP', kind='HELP')
item.value['ENG'] = ('The APERO file block this file belongs to e.g. raw, '
                     'tmp, red, out, lbl')
item.value['FR'] = ('Le bloc de fichiers APERO auquel appartient ce fichier '
                    'ex. raw, tmp, red, out, lbl')
item.value['ES'] = ('El bloque de archivos APERO al que pertenece este '
                    'archivo p. ej. raw, tmp, red, out, lbl')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_CORES_HELP
# =============================================================================
item = langlist.create('GET_FILES_CORES_HELP', kind='HELP')
item.value['ENG'] = ('How many cores to use for certain steps (will '
                     'multiprocess when possible)')
item.value['FR'] = ('Nombre de cœurs à utiliser pour certaines étapes '
                    '(multiprocessus si possible)')
item.value['ES'] = ('Número de núcleos a usar en ciertos pasos (usará '
                    'multiproceso cuando sea posible)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_GROUP_SERVER_HELP
# =============================================================================
item = langlist.create('GET_FILES_GROUP_SERVER_HELP', kind='HELP')
item.value['ENG'] = ('Group server to use with --group_yaml and '
                     '--permission_yaml.')
item.value['FR'] = ('Serveur de groupes à utiliser avec --group_yaml et '
                    '--permission_yaml.')
item.value['ES'] = ('Servidor de grupos a usar con --group_yaml y '
                    '--permission_yaml.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_GROUP_YAML_HELP
# =============================================================================
item = langlist.create('GET_FILES_GROUP_YAML_HELP', kind='HELP')
item.value['ENG'] = 'Group yaml file. For use with --permission_yaml.'
item.value['FR'] = 'Fichier yaml de groupes. À utiliser avec --permission_yaml.'
item.value['ES'] = 'Archivo yaml de grupos. Para usar con --permission_yaml.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_KEYNAMES_HELP
# =============================================================================
item = langlist.create('GET_FILES_KEYNAMES_HELP', kind='HELP')
item.value['ENG'] = ('For dbkind=calib or dbkind=tellu this is required, and '
                     'sets the type of calibration/telluric required (used '
                     'instead of --outtypes)')
item.value['FR'] = ('Requis pour dbkind=calib ou dbkind=tellu, définit le '
                    'type de calibration/tellurique requis (utilisé à la '
                    'place de --outtypes)')
item.value['ES'] = ('Requerido para dbkind=calib o dbkind=tellu, define el '
                    'tipo de calibración/telúrico requerido (se usa en lugar '
                    'de --outtypes)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_LATEST_HELP
# =============================================================================
item = langlist.create('GET_FILES_LATEST_HELP', kind='HELP')
item.value['ENG'] = ('Only get files processed since a certain date '
                     'YYYY-MM-DD hh:mm:ss')
item.value['FR'] = ('Obtenir uniquement les fichiers traités depuis une date '
                    'YYYY-MM-DD hh:mm:ss')
item.value['ES'] = ('Obtener solo archivos procesados desde una fecha '
                    'YYYY-MM-DD hh:mm:ss')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_MP_MODE_HELP
# =============================================================================
item = langlist.create('GET_FILES_MP_MODE_HELP', kind='HELP')
item.value['ENG'] = 'The multiprocessing mode to use when using --cores'
item.value['FR'] = 'Le mode multiprocessus à utiliser avec --cores'
item.value['ES'] = 'El modo de multiproceso a usar con --cores'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_NODB_HELP
# =============================================================================
item = langlist.create('GET_FILES_NODB_HELP', kind='HELP')
item.value['ENG'] = ('Use filesystem to search for files [very slow] usually '
                     'just for debugging')
item.value['FR'] = ('Utiliser le système de fichiers pour rechercher les '
                    'fichiers [très lent], généralement pour le débogage')
item.value['ES'] = ('Usar el sistema de archivos para buscar archivos [muy '
                    'lento] normalmente solo para depuración')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_NODB_WILDCARD_HELP
# =============================================================================
item = langlist.create('GET_FILES_NODB_WILDCARD_HELP', kind='HELP')
item.value['ENG'] = ('When --nodb is used use --nodb_wildcard to only target '
                     'specific files')
item.value['FR'] = ('Avec --nodb, utilisez --nodb_wildcard pour ne cibler que '
                    'certains fichiers')
item.value['ES'] = ('Cuando se usa --nodb use --nodb_wildcard para apuntar '
                    'solo a archivos específicos')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_NOSUBDIR_HELP
# =============================================================================
item = langlist.create('GET_FILES_NOSUBDIR_HELP', kind='HELP')
item.value['ENG'] = ('Do not put files into a sub-directory. Only use thes '
                     'outpath')
item.value['FR'] = ('Ne pas placer les fichiers dans un sous-répertoire. '
                    'Utiliser uniquement ce chemin de sortie')
item.value['ES'] = ('No colocar los archivos en un subdirectorio. Usar solo '
                    'esta ruta de salida')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_OBSDIR_HELP
# =============================================================================
item = langlist.create('GET_FILES_OBSDIR_HELP', kind='HELP')
item.value['ENG'] = 'Only get files from a certain observation directory'
item.value['FR'] = ("Obtenir uniquement les fichiers d'un répertoire "
                    "d'observation donné")
item.value['ES'] = ('Obtener solo archivos de un directorio de observación '
                    'determinado')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_OUT_PREFIX_HELP
# =============================================================================
item = langlist.create('GET_FILES_OUT_PREFIX_HELP', kind='HELP')
item.value['ENG'] = 'All output files have this prefix added'
item.value['FR'] = 'Ce préfixe est ajouté à tous les fichiers de sortie'
item.value['ES'] = 'Todos los archivos de salida tienen este prefijo añadido'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_OUT_SUFFIX_HELP
# =============================================================================
item = langlist.create('GET_FILES_OUT_SUFFIX_HELP', kind='HELP')
item.value['ENG'] = 'All output files have this suffix added'
item.value['FR'] = 'Ce suffixe est ajouté à tous les fichiers de sortie'
item.value['ES'] = 'Todos los archivos de salida tienen este sufijo añadido'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_PERMISSION_YAML_HELP
# =============================================================================
item = langlist.create('GET_FILES_PERMISSION_YAML_HELP', kind='HELP')
item.value['ENG'] = ('Sort files based on permissions in this yaml file. Must '
                     'also define --group_yaml.')
item.value['FR'] = ('Trier les fichiers selon les permissions de ce fichier '
                    'yaml. Il faut aussi définir --group_yaml.')
item.value['ES'] = ('Ordenar los archivos según los permisos de este archivo '
                    'yaml. También debe definirse --group_yaml.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_PI_NAME_HELP
# =============================================================================
item = langlist.create('GET_FILES_PI_NAME_HELP', kind='HELP')
item.value['ENG'] = 'Only get files from a certain PI'
item.value['FR'] = "Obtenir uniquement les fichiers d'un PI donné"
item.value['ES'] = 'Obtener solo archivos de un PI determinado'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_RUNID_HELP
# =============================================================================
item = langlist.create('GET_FILES_RUNID_HELP', kind='HELP')
item.value['ENG'] = 'Only get files from certain run ids'
item.value['FR'] = 'Obtenir uniquement les fichiers de certains run ids'
item.value['ES'] = 'Obtener solo archivos de ciertos run ids'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_SINCE_HELP
# =============================================================================
item = langlist.create('GET_FILES_SINCE_HELP', kind='HELP')
item.value['ENG'] = ('Only get files processed since a certain date '
                     'YYYY-MM-DD hh:mm:ss')
item.value['FR'] = ('Obtenir uniquement les fichiers traités depuis une date '
                    'YYYY-MM-DD hh:mm:ss')
item.value['ES'] = ('Obtener solo archivos procesados desde una fecha '
                    'YYYY-MM-DD hh:mm:ss')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_SIZELIMIT_HELP
# =============================================================================
item = langlist.create('GET_FILES_SIZELIMIT_HELP', kind='HELP')
item.value['ENG'] = 'Limit the size of output tarfile (in GB)'
item.value['FR'] = 'Limiter la taille du fichier tar de sortie (en Go)'
item.value['ES'] = 'Limitar el tamaño del archivo tar de salida (en GB)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_TARFILE_HELP
# =============================================================================
item = langlist.create('GET_FILES_TARFILE_HELP', kind='HELP')
item.value['ENG'] = ('The name of the tar file to create. Must also provide '
                     'the --tar argument')
item.value['FR'] = ('Le nom du fichier tar à créer. Il faut aussi fournir '
                    "l'argument --tar")
item.value['ES'] = ('El nombre del archivo tar a crear. También debe '
                    'proporcionarse el argumento --tar')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_TAR_HELP
# =============================================================================
item = langlist.create('GET_FILES_TAR_HELP', kind='HELP')
item.value['ENG'] = ('Whether to create a tar instead of copying files.Must '
                     'also provide the --tarfile argument')
item.value['FR'] = ('Créer un tar au lieu de copier les fichiers. Il faut '
                    "aussi fournir l'argument --tarfile")
item.value['ES'] = ('Si crear un tar en lugar de copiar archivos. También '
                    'debe proporcionarse el argumento --tarfile')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GET_FILES_TIMEKEY_HELP
# =============================================================================
item = langlist.create('GET_FILES_TIMEKEY_HELP', kind='HELP')
item.value['ENG'] = ('Whether to use the processed or observed time in the '
                     'since and latest arguments (applies to both)')
item.value['FR'] = ("Utiliser le temps de traitement ou d'observation dans "
                    "les arguments since et latest (s'applique aux deux)")
item.value['ES'] = ('Si usar el tiempo de procesamiento u observación en los '
                    'argumentos since y latest (se aplica a ambos)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GO_RECIPE_ALL_HELP
# =============================================================================
item = langlist.create('GO_RECIPE_ALL_HELP', kind='HELP')
item.value['ENG'] = 'Display all relevant paths'
item.value['FR'] = 'Afficher tous les chemins pertinents'
item.value['ES'] = 'Mostrar todas las rutas relevantes'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GO_RECIPE_MYSQL_HELP
# =============================================================================
item = langlist.create('GO_RECIPE_MYSQL_HELP', kind='HELP')
item.value['ENG'] = 'Display MySQL parameters'
item.value['FR'] = 'Afficher les paramètres MySQL'
item.value['ES'] = 'Mostrar los parámetros de MySQL'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# GO_RECIPE_SETUP_HELP
# =============================================================================
item = langlist.create('GO_RECIPE_SETUP_HELP', kind='HELP')
item.value['ENG'] = 'Display DRS_UCONFIG path'
item.value['FR'] = 'Afficher le chemin DRS_UCONFIG'
item.value['ES'] = 'Mostrar la ruta DRS_UCONFIG'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# NO_IN_QC_HELP
# =============================================================================
item = langlist.create('NO_IN_QC_HELP', kind='HELP')
item.value['ENG'] = 'Disable checking the quality control of input files'
item.value['FR'] = ('Désactiver la vérification du contrôle qualité des '
                    "fichiers d'entrée")
item.value['ES'] = ('Desactivar la comprobación del control de calidad de los '
                    'archivos de entrada')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# PROCESSING_QUEUE_MODE_HELP
# =============================================================================
item = langlist.create('PROCESSING_QUEUE_MODE_HELP', kind='HELP')
item.value['ENG'] = ('Run in queue mode: add jobs to the queue instead of '
                     'processing them directly')
item.value['FR'] = ('Exécuter en mode file : ajouter les tâches à la file au '
                    'lieu de les traiter directement')
item.value['ES'] = ('Ejecutar en modo cola: añadir los trabajos a la cola en '
                    'lugar de procesarlos directamente')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_CORES_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_CORES_HELP', kind='HELP')
item.value['ENG'] = ('Number of tasks to run at once in run mode (same rules '
                     'as apero_processing --cores)')
item.value['FR'] = ('Nombre de tâches à exécuter simultanément en mode run '
                    '(mêmes règles que apero_processing --cores)')
item.value['ES'] = ('Número de tareas a ejecutar a la vez en modo run (mismas '
                    'reglas que apero_processing --cores)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_DESCRIPTION
# =============================================================================
item = langlist.create('QUEUE_RECIPE_DESCRIPTION', kind='HELP')
item.value['ENG'] = ('The APERO queue management tool - run, batch, monitor '
                     'and reset the processing queue (created by '
                     'apero_processing in queue mode)')
item.value['FR'] = ("L'outil de gestion de la file APERO - exécuter, mettre "
                    'en batch, surveiller et réinitialiser la file de '
                    'traitement (créée par apero_processing en mode file)')
item.value['ES'] = ('La herramienta de gestión de la cola de APERO - '
                    'ejecutar, procesar en batch, monitorizar y reiniciar la '
                    'cola de procesamiento (creada por apero_processing en '
                    'modo cola)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_DRY_RUN_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_DRY_RUN_HELP', kind='HELP')
item.value['ENG'] = ('Dry-run behavior by mode: batch/chain write scripts '
                     'that print "Would have run ..." instead of executing '
                     'recipes; reset reports what would be removed without '
                     'deleting')
item.value['FR'] = ('Comportement en simulation selon le mode : batch/chain '
                    'écrivent des scripts qui affichent "Would have run ..." '
                    "au lieu d'exécuter les recettes ; reset indique ce qui "
                    'serait supprimé sans rien supprimer')
item.value['ES'] = ('Comportamiento de simulación según el modo: batch/chain '
                    'escriben scripts que muestran "Would have run ..." en '
                    'lugar de ejecutar recetas; reset informa de lo que se '
                    'eliminaría sin borrar nada')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_HOST_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_HOST_HELP', kind='HELP')
item.value['ENG'] = ('The host address for the gui dashboard server (gui mode '
                     'only, default 127.0.0.1 i.e. localhost only)')
item.value['FR'] = ("L'adresse hôte du serveur du tableau de bord (mode gui "
                    'uniquement, par défaut 127.0.0.1 c.-à-d. localhost '
                    'uniquement)')
item.value['ES'] = ('La dirección del servidor del panel (solo modo gui, por '
                    'defecto 127.0.0.1 es decir solo localhost)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_MODE_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_MODE_HELP', kind='HELP')
item.value['ENG'] = ('The queue mode: "run" runs the next task(s) in the '
                     'queue, "batch" creates (and submits) sbatch scripts for '
                     'the next group, "chain" creates dependency-chained '
                     'Slurm arrays, "status" shows an interactive terminal '
                     'view of the queue, "gui" starts a browser dashboard '
                     '(status view + action buttons), "reset" removes entries '
                     'from the queue, "init" creates the batch template, '
                     '"action" runs an explicit queue action and "system" '
                     '(internal) moves a task from running to complete/failed')
item.value['FR'] = ('Le mode de la file : "run" exécute la/les prochaine(s) '
                    'tâche(s) de la file, "batch" crée (et soumet) des '
                    'scripts sbatch pour le groupe suivant, "chain" crée des '
                    'tableaux Slurm chaînés par dépendances, "status" affiche '
                    'une vue terminal interactive de la file, "gui" lance un '
                    'tableau de bord dans le navigateur (vue status + boutons '
                    'd\'action), "reset" supprime des entrées de la file, '
                    '"init" crée le modèle batch, "action" exécute une action '
                    'explicite sur la file et "system" (interne) déplace une '
                    'tâche de running vers complete/failed')
item.value['ES'] = ('El modo de la cola: "run" ejecuta la(s) siguiente(s) '
                    'tarea(s) de la cola, "batch" crea (y envía) scripts '
                    'sbatch para el siguiente grupo, "chain" crea arrays de '
                    'Slurm encadenados por dependencias, "status" muestra una '
                    'vista interactiva de la cola en la terminal, "gui" '
                    'inicia un panel en el navegador (vista status + botones '
                    'de acción), "reset" elimina entradas de la cola, "init" '
                    'crea la plantilla batch, "action" ejecuta una acción '
                    'explícita de la cola y "system" (interno) mueve una '
                    'tarea de running a complete/failed')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_MPMODE_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_MPMODE_HELP', kind='HELP')
item.value['ENG'] = ('The multiprocessing mode for run mode (defaults to the '
                     'TOOLS.REPROCESS.MP_TYPE constant, same as '
                     'apero_processing)')
item.value['FR'] = ('Le mode multiprocessus pour le mode run (par défaut la '
                    'constante TOOLS.REPROCESS.MP_TYPE, comme '
                    'apero_processing)')
item.value['ES'] = ('El modo de multiproceso para el modo run (por defecto la '
                    'constante TOOLS.REPROCESS.MP_TYPE, igual que '
                    'apero_processing)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_NTASKS_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_NTASKS_HELP', kind='HELP')
item.value['ENG'] = ('Total number of queue tasks to run in run mode. Default '
                     'is one cycle (up to --cores). Use "all" to keep running '
                     'until blocked or the queue is empty')
item.value['FR'] = ('Nombre total de tâches de la file à exécuter en mode '
                    "run. Par défaut un cycle (jusqu'à --cores). Utilisez "
                    '"all" pour continuer jusqu\'au blocage ou jusqu\'à ce '
                    'que la file soit vide')
item.value['ES'] = ('Número total de tareas de la cola a ejecutar en modo '
                    'run. Por defecto un ciclo (hasta --cores). Use "all" '
                    'para seguir ejecutando hasta que se bloquee o la cola '
                    'esté vacía')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_N_BATCHES_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_N_BATCHES_HELP', kind='HELP')
item.value['ENG'] = ('Number of batch scripts to create (batch mode) - if '
                     'given, skips the interactive question')
item.value['FR'] = ('Nombre de scripts batch à créer (mode batch) - si '
                    'fourni, la question interactive est ignorée')
item.value['ES'] = ('Número de scripts batch a crear (modo batch) - si se da, '
                    'se omite la pregunta interactiva')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_PER_BATCH_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_PER_BATCH_HELP', kind='HELP')
item.value['ENG'] = ('Number of tasks per batch script (batch mode) - if '
                     'given, skips the interactive question')
item.value['FR'] = ('Nombre de tâches par script batch (mode batch) - si '
                    'fourni, la question interactive est ignorée')
item.value['ES'] = ('Número de tareas por script batch (modo batch) - si se '
                    'da, se omite la pregunta interactiva')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_PORT_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_PORT_HELP', kind='HELP')
item.value['ENG'] = ('The port for the gui dashboard server (gui mode only, '
                     'default 8090 - tries the next ports if taken)')
item.value['FR'] = ('Le port du serveur du tableau de bord (mode gui '
                    'uniquement, par défaut 8090 - essaie les ports suivants '
                    'si occupé)')
item.value['ES'] = ('El puerto del servidor del panel (solo modo gui, por '
                    'defecto 8090 - prueba los siguientes puertos si está '
                    'ocupado)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_QACTION_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_QACTION_HELP', kind='HELP')
item.value['ENG'] = ('Explicit queue action for action mode. Use --qid for '
                     'per-run actions')
item.value['FR'] = ("Action explicite de file d'attente pour le mode action. "
                    'Utilisez --qid pour les actions par exécution')
item.value['ES'] = ('Acción de cola explícita para el modo acción. Use --qid '
                    'para acciones por ejecución')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_QID_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_QID_HELP', kind='HELP')
item.value['ENG'] = ('The queue id of a task, i.e. "{group}/{run_file}" '
                     '(action mode per-run actions and system mode)')
item.value['FR'] = ("L'identifiant de file d'une tâche, c.-à-d. "
                    '"{group}/{run_file}" (actions par exécution du mode '
                    'action et mode system)')
item.value['ES'] = ('El id de cola de una tarea, es decir '
                    '"{group}/{run_file}" (acciones por ejecución del modo '
                    'action y modo system)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_QPATH_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_QPATH_HELP', kind='HELP')
item.value['ENG'] = ('The absolute path to the queue directory (system mode '
                     'only - allows the fast path to avoid loading the APERO '
                     'runtime)')
item.value['FR'] = ('Le chemin absolu du répertoire de la file (mode system '
                    "uniquement - permet au chemin rapide d'éviter de charger "
                    'APERO)')
item.value['ES'] = ('La ruta absoluta al directorio de la cola (solo modo '
                    'system - permite que la ruta rápida evite cargar APERO)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_QRESULT_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_QRESULT_HELP', kind='HELP')
item.value['ENG'] = 'The result of a task (system mode only)'
item.value['FR'] = "Le résultat d'une tâche (mode system uniquement)"
item.value['ES'] = 'El resultado de una tarea (solo modo system)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_QSTATE_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_QSTATE_HELP', kind='HELP')
item.value['ENG'] = ('Only act on this queue state (for status and reset '
                     'modes) - default is all states')
item.value['FR'] = ('Agir seulement sur cet état de la file (pour les modes '
                    'status et reset) - par défaut tous les états')
item.value['ES'] = ('Actuar solo sobre este estado de la cola (para los modos '
                    'status y reset) - por defecto todos los estados')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_ROWS_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_ROWS_HELP', kind='HELP')
item.value['ENG'] = ('Number of rows to show per page in status mode (cli '
                     'pager page size) and gui mode (table page size, default '
                     '100)')
item.value['FR'] = ('Nombre de lignes à afficher par page en mode status '
                    '(taille de page du pager cli) et en mode gui (taille de '
                    'page de la table, par défaut 100)')
item.value['ES'] = ('Número de filas a mostrar por página en modo status '
                    '(tamaño de página del paginador cli) y en modo gui '
                    '(tamaño de página de la tabla, por defecto 100)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_SUBMIT_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_SUBMIT_HELP', kind='HELP')
item.value['ENG'] = ('Whether to submit the batch script(s) via sbatch (batch '
                     'mode) - if given, skips the interactive question')
item.value['FR'] = ('Soumettre ou non le(s) script(s) batch via sbatch (mode '
                    'batch) - si fourni, la question interactive est ignorée')
item.value['ES'] = ('Si enviar el/los script(s) batch con sbatch (modo batch) '
                    '- si se da, se omite la pregunta interactiva')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# QUEUE_RECIPE_TEMPLATE_HELP
# =============================================================================
item = langlist.create('QUEUE_RECIPE_TEMPLATE_HELP', kind='HELP')
item.value['ENG'] = ('The name of the batch template to use (init and batch '
                     'modes) - default is "default". Use "apero_queue.py '
                     'init" to create named templates')
item.value['FR'] = ('Le nom du modèle batch à utiliser (modes init et batch) '
                    '- par défaut "default". Utilisez "apero_queue.py init" '
                    'pour créer des modèles nommés')
item.value['ES'] = ('El nombre de la plantilla batch a usar (modos init y '
                    'batch) - por defecto "default". Use "apero_queue.py '
                    'init" para crear plantillas con nombre')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REJECT_AUTOFILL_HELP
# =============================================================================
item = langlist.create('REJECT_AUTOFILL_HELP', kind='HELP')
item.value['ENG'] = ('Autofill the questions asked. For identifier this is '
                     'PP,TEL,RV,COMMENT e.g. "1,1,1,bad target" For objname '
                     'this is ALIASES,BAD_ASTRO,NOTES e.g. '
                     '"alias1|alias2|alias3,0,Not a real target"      or      '
                     'e.g. "alias1|alias2|alias3,1,No proper motion"')
item.value['FR'] = ('Remplir automatiquement les questions posées. Pour '
                    'identifier : PP,TEL,RV,COMMENT ex. "1,1,1,bad target" '
                    'Pour objname : ALIASES,BAD_ASTRO,NOTES ex. '
                    '"alias1|alias2|alias3,0,Not a real target"      ou      '
                    'ex. "alias1|alias2|alias3,1,No proper motion"')
item.value['ES'] = ('Autocompletar las preguntas. Para identifier: '
                    'PP,TEL,RV,COMMENT p. ej. "1,1,1,bad target" Para '
                    'objname: ALIASES,BAD_ASTRO,NOTES p. ej. '
                    '"alias1|alias2|alias3,0,Not a real target"      o      '
                    'p. ej. "alias1|alias2|alias3,1,No proper motion"')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REJECT_DESCRIPTION
# =============================================================================
item = langlist.create('REJECT_DESCRIPTION', kind='HELP')
item.value['ENG'] = ('Add a object or file to the object or file reject list '
                     'online.')
item.value['FR'] = ('Ajouter un objet ou un fichier à la liste de rejet en '
                    'ligne.')
item.value['ES'] = 'Añadir un objeto o archivo a la lista de rechazo en línea.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REJECT_IDENTIFIER_HELP
# =============================================================================
item = langlist.create('REJECT_IDENTIFIER_HELP', kind='HELP')
item.value['ENG'] = ('Add a specific file identifier to the file reject list. '
                     'E.g. for spirou this is the odocode, for nirps this is '
                     'raw the filename (Can add multiple as comma separated '
                     'list)')
item.value['FR'] = ('Ajouter un identifiant de fichier spécifique à la liste '
                    "de rejet de fichiers. Ex. pour spirou c'est l'odocode, "
                    "pour nirps c'est le nom du fichier brut (plusieurs "
                    'possibles, séparés par des virgules)')
item.value['ES'] = ('Añadir un identificador de archivo específico a la lista '
                    'de rechazo de archivos. P. ej. para spirou es el '
                    'odocode, para nirps es el nombre del archivo bruto (se '
                    'pueden añadir varios separados por comas)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REJECT_OBJNAME_HELP
# =============================================================================
item = langlist.create('REJECT_OBJNAME_HELP', kind='HELP')
item.value['ENG'] = ('Add a specific object name to the object reject list '
                     '(Can add multiple as comma separated list)')
item.value['FR'] = ("Ajouter un nom d'objet spécifique à la liste de rejet "
                    "d'objets (plusieurs possibles, séparés par des virgules)")
item.value['ES'] = ('Añadir un nombre de objeto específico a la lista de '
                    'rechazo de objetos (se pueden añadir varios separados '
                    'por comas)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REJECT_OBSDIR_HELP
# =============================================================================
item = langlist.create('REJECT_OBSDIR_HELP', kind='HELP')
item.value['ENG'] = ('Add all files from a certain observation directory to '
                     'the file reject list (excludes science observations). '
                     'You may only select one obsdir at once. Note this '
                     'overrides --identifier')
item.value['FR'] = ("Ajouter tous les fichiers d'un répertoire d'observation "
                    'à la liste de rejet de fichiers (hors observations '
                    'science). Un seul obsdir à la fois. Notez que ceci '
                    'remplace --identifier')
item.value['ES'] = ('Añadir todos los archivos de un directorio de '
                    'observación a la lista de rechazo de archivos (excluye '
                    'observaciones de ciencia). Solo puede seleccionar un '
                    'obsdir a la vez. Tenga en cuenta que esto anula '
                    '--identifier')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REJECT_TEST_HELP
# =============================================================================
item = langlist.create('REJECT_TEST_HELP', kind='HELP')
item.value['ENG'] = 'Whether to run in test mode (recommended first time)'
item.value['FR'] = 'Exécuter ou non en mode test (recommandé la première fois)'
item.value['ES'] = 'Si ejecutar en modo de prueba (recomendado la primera vez)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DOC_ALL_HELP
# =============================================================================
item = langlist.create('REMAKE_DOC_ALL_HELP', kind='HELP')
item.value['ENG'] = '--filedef --recipedef and --recipeseq'
item.value['FR'] = '--filedef --recipedef et --recipeseq'
item.value['ES'] = '--filedef --recipedef y --recipeseq'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DOC_ARI_HELP
# =============================================================================
item = langlist.create('REMAKE_DOC_ARI_HELP', kind='HELP')
item.value['ENG'] = ('Generate the apero-ri markdown documentation tree '
                     '(documentation/ari/{docversion}/home/docs/apero) from '
                     'the recipe and file definitions')
item.value['FR'] = ("Générer l'arborescence de documentation markdown "
                    'apero-ri '
                    '(documentation/ari/{docversion}/home/docs/apero) à '
                    'partir des définitions de recettes et de fichiers')
item.value['ES'] = ('Generar el árbol de documentación markdown de apero-ri '
                    '(documentation/ari/{docversion}/home/docs/apero) a '
                    'partir de las definiciones de recetas y archivos')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMAKE_DOC_DOCVERSION_HELP
# =============================================================================
item = langlist.create('REMAKE_DOC_DOCVERSION_HELP', kind='HELP')
item.value['ENG'] = ('[STRING] Documentation version directory to write to '
                     'with --ari (e.g. 0.8.XXX). Defaults to the major '
                     'version of the running APERO.')
item.value['FR'] = ('[STRING] Répertoire de version de documentation où '
                    'écrire avec --ari (ex. 0.8.XXX). Par défaut la version '
                    "majeure d'APERO en cours.")
item.value['ES'] = ('[STRING] Directorio de versión de documentación donde '
                    'escribir con --ari (p. ej. 0.8.XXX). Por defecto la '
                    'versión mayor de APERO en ejecución.')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMOVE_BLOCKS_HELP
# =============================================================================
item = langlist.create('REMOVE_BLOCKS_HELP', kind='HELP')
item.value['ENG'] = ('Delete all instances of tmp/red/out/calib/tellu from '
                     'disk and database (multiple blocks should be separated '
                     'by a comma)')
item.value['FR'] = ('Supprimer toutes les occurrences de '
                    'tmp/red/out/calib/tellu du disque et de la base de '
                    'données (plusieurs blocs séparés par une virgule)')
item.value['ES'] = ('Eliminar todas las instancias de tmp/red/out/calib/tellu '
                    'del disco y de la base de datos (varios bloques '
                    'separados por coma)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMOVE_DESCRIPTION
# =============================================================================
item = langlist.create('REMOVE_DESCRIPTION', kind='HELP')
item.value['ENG'] = 'The APERO file/directory remove tool'
item.value['FR'] = "L'outil de suppression de fichiers/répertoires APERO"
item.value['ES'] = ('La herramienta de eliminación de archivos/directorios de '
                    'APERO')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMOVE_FILE_PREFIX_HELP
# =============================================================================
item = langlist.create('REMOVE_FILE_PREFIX_HELP', kind='HELP')
item.value['ENG'] = ('Delete all instances of a certain file prefix from disk '
                     'and databases')
item.value['FR'] = ("Supprimer toutes les occurrences d'un préfixe de fichier "
                    'du disque et des bases de données')
item.value['ES'] = ('Eliminar todas las instancias de un prefijo de archivo '
                    'del disco y de las bases de datos')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMOVE_FILE_SUFFIX_HELP
# =============================================================================
item = langlist.create('REMOVE_FILE_SUFFIX_HELP', kind='HELP')
item.value['ENG'] = ('Delete all instances of a certain file suffix from disk '
                     'and databases')
item.value['FR'] = ("Supprimer toutes les occurrences d'un suffixe de fichier "
                    'du disque et des bases de données')
item.value['ES'] = ('Eliminar todas las instancias de un sufijo de archivo '
                    'del disco y de las bases de datos')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMOVE_NOWARN_HELP
# =============================================================================
item = langlist.create('REMOVE_NOWARN_HELP', kind='HELP')
item.value['ENG'] = 'Whether to warn the user we are not in test mode.'
item.value['FR'] = ("Avertir ou non l'utilisateur que nous ne sommes pas en "
                    'mode test.')
item.value['ES'] = 'Si advertir al usuario de que no estamos en modo de prueba.'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMOVE_OBJNAMES_HELP
# =============================================================================
item = langlist.create('REMOVE_OBJNAMES_HELP', kind='HELP')
item.value['ENG'] = ('Delete all instances of a certain object name (DRSOBJN) '
                     'from disk and databases')
item.value['FR'] = ("Supprimer toutes les occurrences d'un nom d'objet "
                    '(DRSOBJN) du disque et des bases de données')
item.value['ES'] = ('Eliminar todas las instancias de un nombre de objeto '
                    '(DRSOBJN) del disco y de las bases de datos')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMOVE_OBSDIR_HELP
# =============================================================================
item = langlist.create('REMOVE_OBSDIR_HELP', kind='HELP')
item.value['ENG'] = ('Delete all instances of a certain observation directory '
                     'from disk and databases')
item.value['FR'] = ("Supprimer toutes les occurrences d'un répertoire "
                    "d'observation du disque et des bases de données")
item.value['ES'] = ('Eliminar todas las instancias de un directorio de '
                    'observación del disco y de las bases de datos')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMOVE_RAWDB_HELP
# =============================================================================
item = langlist.create('REMOVE_RAWDB_HELP', kind='HELP')
item.value['ENG'] = 'Whether to remove raw database entries'
item.value['FR'] = 'Supprimer ou non les entrées brutes de la base de données'
item.value['ES'] = 'Si eliminar las entradas brutas de la base de datos'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# REMOVE_TEST_HELP
# =============================================================================
item = langlist.create('REMOVE_TEST_HELP', kind='HELP')
item.value['ENG'] = 'Whether to run in test mode (recommended first time)'
item.value['FR'] = 'Exécuter ou non en mode test (recommandé la première fois)'
item.value['ES'] = 'Si ejecutar en modo de prueba (recomendado la primera vez)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_ONLY_ASSETS_HELP
# =============================================================================
item = langlist.create('RESET_ONLY_ASSETS_HELP', kind='HELP')
item.value['ENG'] = 'Reset only the assets directory'
item.value['FR'] = 'Réinitialiser uniquement le répertoire des ressources'
item.value['ES'] = 'Reiniciar solo el directorio de recursos'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_ONLY_CALIB_HELP
# =============================================================================
item = langlist.create('RESET_ONLY_CALIB_HELP', kind='HELP')
item.value['ENG'] = 'Reset only the calibration directory'
item.value['FR'] = 'Réinitialiser uniquement le répertoire de calibration'
item.value['ES'] = 'Reiniciar solo el directorio de calibración'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_ONLY_LBL_HELP
# =============================================================================
item = langlist.create('RESET_ONLY_LBL_HELP', kind='HELP')
item.value['ENG'] = 'Reset only the lbl directory'
item.value['FR'] = 'Réinitialiser uniquement le répertoire lbl'
item.value['ES'] = 'Reiniciar solo el directorio lbl'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_ONLY_LOG_HELP
# =============================================================================
item = langlist.create('RESET_ONLY_LOG_HELP', kind='HELP')
item.value['ENG'] = 'Reset only the log directory'
item.value['FR'] = 'Réinitialiser uniquement le répertoire des journaux'
item.value['ES'] = 'Reiniciar solo el directorio de registros'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_ONLY_OTHER_HELP
# =============================================================================
item = langlist.create('RESET_ONLY_OTHER_HELP', kind='HELP')
item.value['ENG'] = 'Reset only the other directory'
item.value['FR'] = 'Réinitialiser uniquement le répertoire other'
item.value['ES'] = 'Reiniciar solo el directorio other'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_ONLY_OUT_HELP
# =============================================================================
item = langlist.create('RESET_ONLY_OUT_HELP', kind='HELP')
item.value['ENG'] = 'Reset only the out directory'
item.value['FR'] = 'Réinitialiser uniquement le répertoire out'
item.value['ES'] = 'Reiniciar solo el directorio out'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_ONLY_PLOT_HELP
# =============================================================================
item = langlist.create('RESET_ONLY_PLOT_HELP', kind='HELP')
item.value['ENG'] = 'Reset only the plot directory'
item.value['FR'] = 'Réinitialiser uniquement le répertoire des graphiques'
item.value['ES'] = 'Reiniciar solo el directorio de gráficos'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_ONLY_QUEUE_HELP
# =============================================================================
item = langlist.create('RESET_ONLY_QUEUE_HELP', kind='HELP')
item.value['ENG'] = ('Reset only the processing queue (all queue entries, '
                     'queue output and chain scripts - batch templates are '
                     'kept)')
item.value['FR'] = ('Réinitialiser uniquement la file de traitement (toutes '
                    'les entrées de la file, les sorties de la file et les '
                    'scripts chain - les modèles batch sont conservés)')
item.value['ES'] = ('Reiniciar solo la cola de procesamiento (todas las '
                    'entradas de la cola, las salidas de la cola y los '
                    'scripts chain - se conservan las plantillas batch)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_ONLY_RED_HELP
# =============================================================================
item = langlist.create('RESET_ONLY_RED_HELP', kind='HELP')
item.value['ENG'] = 'Reset only the reduced directory'
item.value['FR'] = 'Réinitialiser uniquement le répertoire reduced'
item.value['ES'] = 'Reiniciar solo el directorio reduced'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_ONLY_RUN_HELP
# =============================================================================
item = langlist.create('RESET_ONLY_RUN_HELP', kind='HELP')
item.value['ENG'] = 'Reset only the run directory'
item.value['FR'] = 'Réinitialiser uniquement le répertoire run'
item.value['ES'] = 'Reiniciar solo el directorio run'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_ONLY_TELLU_HELP
# =============================================================================
item = langlist.create('RESET_ONLY_TELLU_HELP', kind='HELP')
item.value['ENG'] = 'Reset only the telluric directory'
item.value['FR'] = 'Réinitialiser uniquement le répertoire tellurique'
item.value['ES'] = 'Reiniciar solo el directorio telúrico'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RESET_ONLY_TMP_HELP
# =============================================================================
item = langlist.create('RESET_ONLY_TMP_HELP', kind='HELP')
item.value['ENG'] = 'Reset only the tmp directory'
item.value['FR'] = 'Réinitialiser uniquement le répertoire tmp'
item.value['ES'] = 'Reiniciar solo el directorio tmp'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# RUN_INI_RUNFILE_HELP
# =============================================================================
item = langlist.create('RUN_INI_RUNFILE_HELP', kind='HELP')
item.value['ENG'] = 'Only create a single run file (for debugging)'
item.value['FR'] = "Créer un seul fichier d'exécution (pour le débogage)"
item.value['ES'] = 'Crear un único archivo de ejecución (para depuración)'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# STATS_LIMIT_HELP
# =============================================================================
item = langlist.create('STATS_LIMIT_HELP', kind='HELP')
item.value['ENG'] = ('Limit the number of entries in memory plot (any recipe '
                     'with more than this limit is left out of stats)')
item.value['FR'] = ("Limiter le nombre d'entrées dans le graphique mémoire "
                    '(toute recette au-delà de cette limite est exclue des '
                    'statistiques)')
item.value['ES'] = ('Limitar el número de entradas en el gráfico de memoria '
                    '(cualquier receta por encima de este límite se excluye '
                    'de las estadísticas)')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# VISULISE_CORE_HELP
# =============================================================================
item = langlist.create('VISULISE_CORE_HELP', kind='HELP')
item.value['ENG'] = 'Number of cores to use'
item.value['FR'] = 'Nombre de cœurs à utiliser'
item.value['ES'] = 'Número de núcleos a usar'
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# VISULISE_INFOPATH_HELP
# =============================================================================
item = langlist.create('VISULISE_INFOPATH_HELP', kind='HELP')
item.value['ENG'] = ('Path to save info plots to (only for mode=info). Note '
                     'this will flatten any file structure under --path. If '
                     '--infopath is not plots will save to --path/{path to '
                     'file} (i.e. where the files are found).')
item.value['FR'] = ("Chemin où enregistrer les graphiques d'information "
                    '(seulement pour mode=info). Notez que cela aplatit toute '
                    "structure de fichiers sous --path. Si --infopath n'est "
                    'pas défini, les graphiques seront enregistrés dans '
                    '--path/{path to file} (c.-à-d. là où se trouvent les '
                    'fichiers).')
item.value['ES'] = ('Ruta donde guardar los gráficos de información (solo '
                    'para mode=info). Tenga en cuenta que esto aplana '
                    'cualquier estructura de archivos bajo --path. Si '
                    '--infopath no se define, los gráficos se guardarán en '
                    '--path/{path to file} (es decir, donde se encuentran los '
                    'archivos).')
item.arguments = 'None'
item.comment = ''
langlist.add(item)

# =============================================================================
# VISULISE_PATH_HELP
# =============================================================================
item = langlist.create('VISULISE_PATH_HELP', kind='HELP')
item.value['ENG'] = ('Some modes require a path. For mode=info this is the '
                     'path to the files to create info graphics for '
                     '(recursive)')
item.value['FR'] = ('Certains modes nécessitent un chemin. Pour mode=info '
                    "c'est le chemin des fichiers pour lesquels créer des "
                    "graphiques d'information (récursif)")
item.value['ES'] = ('Algunos modos requieren una ruta. Para mode=info es la '
                    'ruta de los archivos para los que crear gráficos de '
                    'información (recursivo)')
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
