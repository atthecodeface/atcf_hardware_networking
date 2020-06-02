#a Copyright
#  
#  This file 'test_target_axi4s.py' copyright Gavin J Stark 2020
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

#a Documentation
"""
"""

#a Imports
from regress.apb.structs import t_apb_request, t_apb_response
from regress.apb.bfm     import ApbMaster
from regress.apb         import target_sram_interface
from regress.networking  import apb_target_axi4s
from cdl.sim     import ThExecFile
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from cdl.utils   import csr

#a Test classes
#c ApbAddressMap
class ApbAddressMap(csr.Map):
    _width=32
    _select=0
    _address=0
    _shift=0
    _address_size=0
    _map=[csr.MapMap(offset=0, name="axi4s", map=apb_target_axi4s.Axi4sAddressMap),
          csr.MapMap(offset=2<<16, name="tx_sram", map=target_sram_interface.SramInterfaceAddressMap),
          csr.MapMap(offset=3<<16, name="rx_sram", map=target_sram_interface.SramInterfaceAddressMap),
         ]
    pass
#c Axi4sTestBase
class Axi4sTestBase(ThExecFile):
    """
    """
    #f run__init - invoked by submodules
    def run__init(self):
        self.bfm_wait(10)
        self.apb = ApbMaster(self, "apb_request",  "apb_response")
        self.apb_map = ApbAddressMap()
        self.axi_bfm.axi4s("banana")
        print(self.banana)
        self.axi4s_map  = self.apb_map.axi4s # This is an ApbAddressMap()
        self.tx_sram_map  = self.apb_map.tx_sram # This is an ApbAddressMap()
        self.rx_sram_map  = self.apb_map.rx_sram # This is an ApbAddressMap()
        pass

    #f run
    def run(self):
        cfg = self.apb.reg(self.axi4s_map.config)
        tx_addr     = self.apb.reg(self.tx_sram_map.address)
        tx_data     = self.apb.reg(self.tx_sram_map.data)
        tx_data_inc = self.apb.reg(self.tx_sram_map.data_inc)
        rx_addr     = self.apb.reg(self.rx_sram_map.address)
        rx_data     = self.apb.reg(self.rx_sram_map.data)
        rx_data_inc = self.apb.reg(self.rx_sram_map.data_inc)
        cfg.write(0x5)
        self.bfm_wait(10)
        cfg.write(0x0)
        self.bfm_wait(10)
        cfg.write(0x0a)
        self.bfm_wait(10)
        cfg.write(0x0)
        tx_addr.write(1)
        tx_data_inc.write(0x1234567) # User
        for d in range((63+3)//4):
            tx_data_inc.write(0xfedcba98) # d0
            pass
        tx_data_inc.write(0)
        tx_addr.write(0)
        tx_data.write(63) # 63 byte packet!
        self.verbose.error("%d %d"%(self.global_cycle(),self.banana.slave_empty()))
        for i in range(12):
            self.banana.slave_wait_for_data()
            self.banana.slave_dequeue()
            print(self.banana.get("data"))
            pass
        self.verbose.error("%d %d"%(self.global_cycle(),self.banana.slave_empty()))
        self.passtest("Test completed")
        pass
    #f run__finalize
    def run__finalize(self):
        # self.verbose.error("%s"%(self.global_cycle()))
        pass

#a Hardware classes
#c ApbTargetAxi4sHw
t_axi4s32 = {"valid":1, "t":{"data":32, "last":1, "user":64, "strb":4, "keep":4, "id":64, "dest":64}}
class ApbTargetAxi4sHw(HardwareThDut):
    clock_desc = [("aclk",(0,1,1)),
    ]
    reset_desc = {"name":"areset_n", "init_value":0, "wait":5}
    th_module_type = "axi4s32_master_slave"
    module_name    = "tb_apb_target_axi4s"
    dut_inputs  = {"apb_request":t_apb_request,
                   "slave_axi4s_tready":1,
                   "master_axi4s":t_axi4s32,
    }
    dut_outputs = {"apb_response":t_apb_response,
                   "master_axi4s_tready":1,
                   "slave_axi4s":t_axi4s32,
    }
    th_bfm_connections = ["slave_axi4s_tready",
                          "master_axi4s_tready",
                          "slave_axi4s",
                          "master_axi4s"]
    pass

#a Simulation test classes
#c ApbTargetAxi4s
class ApbTargetAxi4s(TestCase):
    hw = ApbTargetAxi4sHw
    # "verbosity":0,
    kwargs = {}
    _tests = {
        "smoke"  : (Axi4sTestBase,40*1000,  kwargs),
    }
    pass

