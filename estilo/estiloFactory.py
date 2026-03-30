# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Juan S.G. Castellanos

from estilo import dark
from vista.gui_dictionary import CLASESTEMAS


class EstiloFactory:
    @staticmethod
    def definirEstilo(tipo: str):    
        estilo = CLASESTEMAS.get(tipo, dark.DarkColor)
        return estilo()