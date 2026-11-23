#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: server-to-server synchronisation.

Two ARI servers exchange record-level changes over signed, encrypted HTTP
requests. The pieces are:

- ``crypto``: pairing tokens, request signing and payload encryption
- ``store``: on-disk identity, peers, issued tokens, journals and bases
- ``adapters``: one adapter per syncable data category
- ``engine``: change detection, sync planning and execution

Created on 2026-10-22

@author: cook
"""

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.core.server_sync'
