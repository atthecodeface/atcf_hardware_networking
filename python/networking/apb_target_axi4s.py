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
class ConfigCsr(Csr):
    _fields = { 0:  CsrField(width=1, name="rx_reset", brief="rxrst", doc=""),
                1:  CsrField(width=1, name="rx_init", brief="rxrst", doc=""),
                2:  CsrField(width=1, name="tx_reset", brief="txrst", doc=""),
                3:  CsrField(width=1, name="tx_init", brief="txinit", doc=""),
                4: CsrFieldZero(width=28),
              }

class Axi4sAddressMap(Map):
    _map = [ MapCsr(reg=0, name="config",    brief="cfg",  csr=ConfigCsr, doc=""),
             ]
#    apb_address_config      = 0   "Global configuration",
#    apb_address_debug       = 1   "Global configuration",
#    apb_address_rx_config      = 2   "Receive configuration",
#    apb_address_rx_data_ptr    = 3   "Receive data pointer",
#    apb_address_rx_data        = 4   "Receive data",
#    apb_address_rx_data_next   = 5   "Receive data and move on",
#    apb_address_rx_commit      = 6   "Mark current receive data pointer as head of read",
#    apb_address_tx_config      = 8   "Transmit configuration",
#    apb_address_tx_data_ptr    = 9   "Transmit data pointer",
#    apb_address_tx_data        = 10  "Transmit data",
#    apb_address_tx_data_next   = 11  "Transmit data and move on",
#             
