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
from random import Random
from regress.apb.structs import t_apb_request, t_apb_response
from regress.apb.bfm     import ApbMaster
from regress.apb         import target_sram_interface
from regress.networking  import apb_target_axi4s
from cdl.sim     import ThExecFile
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from cdl.utils   import csr

from typing import List, Tuple, Dict, Optional

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
#c Axi4sT
class Axi4sT(object):
    data:int
    strb:int
    last:bool
    keep:Optional[int]=None
    user:Optional[int]=None
    id  :Optional[int]=None
    dest:Optional[int]=None
    def __init__(self, data, strb, last):
        self.data = data
        self.strb = strb
        self.last = last
        pass
    def compare(self, th, axi4s):
        th.compare_expected("axi4s data %s"%(str(self)), self.data, axi4s.get("data"))
        th.compare_expected("axi4s last %s"%(str(self)), self.last, axi4s.get("last"))
        th.compare_expected("axi4s strb %s"%(str(self)), self.strb, axi4s.get("strb"))
        return
    
    def __str__(self):
        r = "%08x:%x:%d"%(self.data,self.strb,int(self.last))
        return r

    pass
#f rand_int32
def rand_int32(random):
    v0 = random.randrange(0,0x10000)
    v1 = random.randrange(0,0x10000)
    return (v0<<16) + v1
    
#c Axi4sTestBase
class Axi4sTestBase(ThExecFile):
    """
    """
    tx_random_seed = "some tx random seed"
    rx_random_seed = "some rx random seed"
    tx_buffer_end = 0x100
    rx_buffer_end = 0x100
    #f __init__
    def __init__(self, tx_sram_write=None, **kwargs):
        super(Axi4sTestBase,self).__init__(**kwargs)
        if tx_sram_write is None: tx_sram_write = self.__class__.tx_sram_write_msg
        def tx_sram_write_fn(data:int, address:Optional[int]=None):
            return tx_sram_write(self, data=data, address=address)
        self.tx_sram_write = tx_sram_write_fn
        pass
    #f exec_init
    def exec_init(self) -> None:
        self.die_event         = self.sim_event()
        super(Axi4sTestBase,self).exec_init()
        pass
    #f run__init - invoked by submodules
    def run__init(self):
        self.bfm_wait(10)
        self.apb = ApbMaster(self, "apb_request",  "apb_response")
        self.apb_map = ApbAddressMap()
        self.axi4s_map  = self.apb_map.axi4s # This is an ApbAddressMap()
        self.tx_sram_map  = self.apb_map.tx_sram # This is an ApbAddressMap()
        self.rx_sram_map  = self.apb_map.rx_sram # This is an ApbAddressMap()
        self.expected_tx_axi4s = []
        self.tx_sram_address = 0xffff
        self.tx_sram_addr     = self.apb.reg(self.tx_sram_map.address)
        self.tx_sram_data     = self.apb.reg(self.tx_sram_map.data)
        self.tx_sram_data_inc = self.apb.reg(self.tx_sram_map.data_inc)
        self.rx_sram_addr     = self.apb.reg(self.rx_sram_map.address)
        self.rx_sram_data     = self.apb.reg(self.rx_sram_map.data)
        self.rx_sram_data_inc = self.apb.reg(self.rx_sram_map.data_inc)
        self.tx_pkt_ptr = 0
        self.last_tx_pkt_axi_addr = 0
        self.sim_msg = self.sim_message()
        self.tx_random = Random()
        self.tx_random.seed(self.tx_random_seed)
        self.rx_random = Random()
        self.rx_random.seed(self.rx_random_seed)
        self.configure()
        self.spawn(self.tx_checker)
        pass

    #f tx_sram_write_msg
    def tx_sram_write_msg(self, data:int, address:Optional[int]=None):
        if address is not None:
            self.tx_sram_address = address
            pass
        self.sim_msg.send_value("dut.tx_sram",9,0,self.tx_sram_address,data)
        # print("%08x:%08x"%(self.tx_sram_address,data))
        self.tx_sram_address = (self.tx_sram_address+1) % self.tx_buffer_end
        pass
    #f tx_sram_write_axi
    def tx_sram_write_axi(self, data:int, address:Optional[int]=None):
        if address is not None:
            if self.tx_sram_address != address:
                self.apb.write(address=self.axi4s_map.tx_ptr.Address(),data=address)
                self.tx_sram_address = address
                pass
            pass
        self.apb.write(address=self.axi4s_map.tx_data_inc.Address(),data=data)
        self.tx_sram_address = self.tx_sram_address+1
        pass
    #f tx_sram_write_apb
    def tx_sram_write_apb(self, data:int, address:Optional[int]=None):
        if address is not None:
            if self.tx_sram_address != address:
                self.tx_sram_addr.write(address)
                self.tx_sram_address = address
                pass
            pass
        self.tx_sram_data_inc.write(data)
        self.tx_sram_address = (self.tx_sram_address+1) % self.tx_buffer_end
        pass
    #f tx_update_pkt_axi_addr
    def tx_update_pkt_axi_addr(self):
        v = self.apb.read(address=self.axi4s_map.tx_ptr.Address())
        self.last_tx_pkt_axi_addr = (v>>16)&0xffff
        pass
        
    #f tx_wait_for_room
    def tx_wait_for_room(self, num_words):
        while True:
            space_available = self.last_tx_pkt_axi_addr - self.tx_pkt_ptr
            if space_available<=0: space_available = space_available + self.tx_buffer_end
            if space_available >= num_words: break
            self.bfm_wait(100)
            self.tx_update_pkt_axi_addr()
            pass
        pass
            
    #f tx_packet
    def tx_packet(self, user:int, data:List[int], last_bytes=4):
        self.tx_wait_for_room(len(data)+4)
        tx_data_ptr = (self.tx_pkt_ptr+1) % self.tx_buffer_end
        self.tx_sram_write(address=tx_data_ptr, data=user)
        tx_data_ptr = (tx_data_ptr+1) % self.tx_buffer_end
        dn = 0
        for d in data:
            s = 15
            last = False
            if dn==len(data)-1:
                s=(1<<last_bytes)-1
                last=True
                pass
            dn=dn+1
            e = Axi4sT(data=d, strb=s, last=last)
            self.expected_tx_axi4s.append(e)
            self.tx_sram_write(data=d)
            tx_data_ptr = (tx_data_ptr+1) % self.tx_buffer_end
            pass
        self.tx_sram_write(data=0)
        self.tx_sram_write(address=self.tx_pkt_ptr, data=(len(data)*4-4+last_bytes))
        self.tx_pkt_ptr = tx_data_ptr
        pass
    #f tx_packet_random
    def tx_packet_random(self, random):
        user = rand_int32(random)
        num_bytes = 4+random.randrange(100)
        num_words = (num_bytes+3) // 4
        last_bytes = num_bytes - 4*(num_words-1)
        data = [rand_int32(random) for i in range(num_words)]
        self.tx_packet(user=user, data=data, last_bytes=last_bytes)
        pass
    #f tx_checker
    def tx_checker(self):
        self.axi_bfm.axi4s("tx_checker_axi")
        while not self.die_event.fired():
            self.bfm_wait(40)
            self.tx_checker_axi.slave_wait_for_data(400) # timeout in global_cycle() ticks
            while not self.tx_checker_axi.slave_empty():
                self.tx_checker_axi.slave_dequeue()
                if self.expected_tx_axi4s == []:
                    self.failtest("AXI4S slave got tx data, but nothing was expected")
                    pass
                e = self.expected_tx_axi4s.pop(0)
                e.compare(self,self.tx_checker_axi)
                pass
            pass
        tx_ptr = self.apb.read(self.axi4s_map.tx_ptr.Address())
        self.verbose.message("tx ptrs %08x : %08x"%(self.tx_pkt_ptr, tx_ptr))
        self.compare_expected("Transmit packet pointer on completion", self.tx_pkt_ptr<<16, (tx_ptr &~ 0xffff))
        pass
    #f configure
    def configure(self):
        cfg = self.apb.reg(self.axi4s_map.config)
        tx_cfg = self.apb.reg(self.axi4s_map.tx_config)
        rx_cfg = self.apb.reg(self.axi4s_map.rx_config)
        tx_cfg.write(self.tx_buffer_end)
        rx_cfg.write(self.rx_buffer_end)
        cfg.write(0x5)
        self.bfm_wait(10)
        cfg.write(0x0)
        self.bfm_wait(10)
        cfg.write(0x0a)
        self.bfm_wait(10)
        cfg.write(0x0)
        pass

    #f run
    def run(self):
        pass
    #f run__finalize
    def run__finalize(self):
        self.bfm_wait_until_test_done(1000)
        self.die_event.fire()
        self.bfm_wait_until_test_done(100)
        rx_ptr = self.apb.read(self.axi4s_map.rx_ptr.Address())
        self.verbose.error("Rx ptr %08x"%rx_ptr)
        self.passtest("Test completed")
        # self.verbose.error("%s"%(self.global_cycle()))
        pass
    #f All done
    pass

#c Axi4sTest_Tx_0
class Axi4sTest_Tx_0(Axi4sTestBase):
    #f run
    def run(self):
        self.tx_packet(0x12345678, [0,1,2,3,4,5,6],3)
        self.tx_packet(0x12345678, [0,1,2,3,4,5,6],3)
        pass
    pass

#c Axi4sTest_Tx_1
class Axi4sTest_Tx_1(Axi4sTestBase):
    #f run
    def run(self):
        for i in range(100):
            self.tx_packet((i*0xfec12364d) & 0xffffffff,
                               [0,1,2,3,4,5,6], 1+(i&3))
            pass
        pass
    pass

#c Axi4sTest_Tx_Random_0
class Axi4sTest_Tx_Random_0(Axi4sTestBase):
    num_pkts = 1000 # 100 packets takes about 4k cycles with msg to write sram
    #f run
    def run(self):
        for i in range(self.num_pkts):
            self.tx_packet_random(self.tx_random)
            pass
        pass
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
#c ApbTargetAxi4s_Msg
class ApbTargetAxi4s_Msg(TestCase):
    hw = ApbTargetAxi4sHw
    kwargs = {
    # "verbosity":0,
        #"th_args":{"tx_sram_write":Axi4sTestBase.tx_sram_write_axi},
        "th_args":{"tx_sram_write":Axi4sTestBase.tx_sram_write_msg},
    }
    _tests = {
        "tx_0"        :  (Axi4sTest_Tx_0,40*1000,  kwargs),
        "tx_1"        :  (Axi4sTest_Tx_1,40*1000,  kwargs),
        "tx_random_0" :  (Axi4sTest_Tx_Random_0,43*1000,  kwargs),
    }
    pass

#c ApbTargetAxi4s_Axi
class ApbTargetAxi4s_Axi(ApbTargetAxi4s_Msg):
    hw = ApbTargetAxi4sHw
    kwargs = {
        "th_args":{"tx_sram_write":Axi4sTestBase.tx_sram_write_axi},
    }
    _tests = {
        "tx_0"        :  (Axi4sTest_Tx_0,40*1000,  kwargs),
        "tx_1"        :  (Axi4sTest_Tx_1,40*1000,  kwargs),
        "tx_random_0" :  (Axi4sTest_Tx_Random_0,43*1000,  kwargs),
    }
    pass

#c ApbTargetAxi4s_Apb
class ApbTargetAxi4s_Apb(ApbTargetAxi4s_Msg):
    hw = ApbTargetAxi4sHw
    kwargs = {
        "th_args":{"tx_sram_write":Axi4sTestBase.tx_sram_write_apb},
    }
    _tests = {
        "tx_0"        :  (Axi4sTest_Tx_0,40*1000,  kwargs),
        "tx_1"        :  (Axi4sTest_Tx_1,40*1000,  kwargs),
        "tx_random_0" :  (Axi4sTest_Tx_Random_0,43*1000,  kwargs),
        "smoke"       :  (Axi4sTest_Tx_Random_0,43*1000,  kwargs),
    }
    pass

