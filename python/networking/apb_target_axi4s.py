#a Copyright
#  
#  This file 'apb_target_jtag.py' copyright Gavin J Stark 2020
#  
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#a Imports
from cdl.utils.csr   import Csr, CsrField, CsrFieldZero, Map, MapCsr, CsrFieldResvd

#a CSRs
class CommitCsr(Csr):
    _fields = { 0:   CsrFieldResvd(width=32),
              }

class TxPtrCsr(Csr):
    _fields = { 0:   CsrField(width=16, name="buffer_addr", brief="bufadr", doc="Address for transmit data accesses through tx data CSRs"),
                16:  CsrField(width=16, name="axi_addr",    brief="axiadr", doc="Address of SRAM being used by AXI transmitter; read-only"),
              }

class RxPtrCsr(Csr):
    _fields = { 0:   CsrField(width=16, name="buffer_addr", brief="bufadr", doc="Address for receive data accesses through rx data CSRs"),
                16:  CsrField(width=16, name="axi_addr",    brief="axiadr", doc="Address of SRAM being used by AXI receiver; read-only"),
              }

class DataCsr(Csr):
    _fields = { 0:   CsrField(width=32, name="data", brief="data", doc=""),
              }

class ConfigBufferCsr(Csr):
    _fields = { 0:   CsrField(width=16, name="buffer_end", brief="bufend", doc=""),
                16:  CsrFieldResvd(width=16),
              }

class ConfigCsr(Csr):
    _fields = { 0:  CsrField(width=1, name="rx_reset", brief="rxrst", doc=""),
                1:  CsrField(width=1, name="rx_init", brief="rxrst", doc=""),
                2:  CsrField(width=1, name="tx_reset", brief="txrst", doc=""),
                3:  CsrField(width=1, name="tx_init", brief="txinit", doc=""),
                4: CsrFieldZero(width=28),
              }

class Axi4sAddressMap(Map):
    _map = [ MapCsr(reg=0,  name="config",       brief="cfg",    csr=ConfigCsr, doc=""),
             MapCsr(reg=2,  name="rx_config",    brief="rxcfg",  csr=ConfigBufferCsr, doc=""),
             MapCsr(reg=3,  name="rx_ptr",       brief="rxptr",  csr=RxPtrCsr, doc=""),
             MapCsr(reg=4,  name="rx_data",      brief="rxd",    csr=DataCsr, doc=""),
             MapCsr(reg=5,  name="rx_data_inc",  brief="rxdinc", csr=DataCsr, doc=""),
             MapCsr(reg=8,  name="tx_config",    brief="txcfg",  csr=ConfigBufferCsr, doc=""),
             MapCsr(reg=9,  name="tx_ptr",       brief="txptr",  csr=TxPtrCsr, doc=""),
             MapCsr(reg=10, name="tx_data",      brief="txd",    csr=DataCsr, doc=""),
             MapCsr(reg=11, name="tx_data_inc",  brief="txdinc", csr=DataCsr, doc=""),
             ]
