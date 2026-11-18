
import copy
import getpass
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# =============================================================================
# Define variables
# =============================================================================
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


# =============================================================================
# Define classes
# =============================================================================
class AperoCheckContactList:
    """Class to represent a list of contacts for a check."""

    def __init__(self) -> None:
        """Initialize an empty contact list and its starred names."""
        self.starred: List[str] = []
        self.contact_names: List[str] = []
        self.contact_emails: List[str] = []

    def add(
        self,
        contact: 'AperoCheckContact',
        starred: bool = False,
    ) -> None:
        """Add a contact once, optionally marking it as starred.

        :param contact: Contact to add.
        :param starred: Whether to include the contact name in ``starred``.
        """
        if contact.name not in self.contact_names:
            self.contact_names.append(contact.name)
            self.contact_emails.append(contact.email)
            if starred:
                self.starred.append(contact.name)

class AperoCheckContact:
    """Class to represent a contact for a check."""

    def __init__(self, name: str, email: str) -> None:
        """Store a contact's display name and email address.

        :param name: Contact display name.
        :param email: Contact email address or contact instructions.
        """
        self.name = name
        self.email = email



# =============================================================================
# Define contacts
# =============================================================================

NJC = AperoCheckContact('Neil Cook', 'neil.cook@umontreal.ca')

LM = AperoCheckContact('Lison Malo', 'lison.malo@umontreal.ca')

EA = AperoCheckContact('Etienne Artigau',
                       'etienne.artigau@umontreal.ca')

FB = AperoCheckContact('Frederique Baron',
                       'frederique.baron@umontreal.ca')

CC = AperoCheckContact('Charles Cadieux',
                       'charles.cadieux.1@umontreal.ca')

TV = AperoCheckContact('Thomas Vandal',
                       'thomas.vandal@umontreal.ca')

PV = AperoCheckContact('Philippe Vallee',
                       'philippe.vallee@umontreal.ca')

LMI = AperoCheckContact('Lucile Mignon',
                        'lucile.mignon@univ-grenoble-alpes.fr')

RA = AperoCheckContact('Romain Allart',
                       'romain.allart@umontreal.ca')

UMAIL = AperoCheckContact('UdeM NIRPS mailing list',
                          'nirps_mtl@listes.umontreal.ca')

NIRPS_SUPPORT = AperoCheckContact('NIRPS Support',
                                  'nirps_support@listes.umontreal.ca')

CURRENT_OBSERVER = AperoCheckContact('The current observer',
                                     'See observer guide: sec:how_to:find_observer')

CL_SERVICE_DESK = AperoCheckContact('ESO CL Service Desk',
                                    'cl-servicedesk@eso.org')

TELESCOPE_3P6 = AperoCheckContact('3.6m Telescope', '3P6@eso.org')

TELESCOPE_DNOS = AperoCheckContact('La Silla Day and Night Staff',
                                   'ls-dnos@eso.org')

GLC = AperoCheckContact('Gaspare Lo Curto', 'glocurto@eso.org')

XD = AperoCheckContact('Xavier Dumusque', 'xavier.dumusque@unige.ch')