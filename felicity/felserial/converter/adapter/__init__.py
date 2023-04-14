# -*- coding: utf-8 -*-
from felicity.felserial.converter.adapter.abbott import AbbotM2000ASTMAdapter
from felicity.felserial.converter.adapter.panther import PantherASTMAdapter
from felicity.felserial.converter.adapter.roche import RocheASTMPlusAdapter, RocheCOBAS68008800Hl7Adapter

astm_adapters = [AbbotM2000ASTMAdapter,
                 PantherASTMAdapter, RocheASTMPlusAdapter]
hl7_adapters = [RocheCOBAS68008800Hl7Adapter]
