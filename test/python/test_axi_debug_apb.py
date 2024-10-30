#a Copyright
#  
#  This file 'test_axi_debug_apb.py' copyright Gavin J Stark 2020
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
Tests using the AXi to APB debugger
"""

#a Imports
from random import Random
from regress.apb import Script
from regress.apb import target_timer, target_gpio, target_sram_interface
from regress.apb.structs import t_apb_request, t_apb_response
from regress.apb.bfm     import ApbMaster
from regress.networking  import apb_target_axi4s, axi4s
from regress.networking.axi4s import Axi4sT, Pkt, t_axi4s32, t_axi4s64
from cdl.sim     import ThExecFile
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from cdl.utils   import csr

from typing import List, Tuple, Dict, Optional, Any

#a Test classes
#c ApbAddressMap
class ApbAddressMap(csr.Map):
    _width=32
    _select=0
    _address=0
    _shift=0
    _address_size=0
    _map=[csr.MapMap(offset=0<<16, name="sram", map=target_sram_interface.SramInterfaceAddressMap),
         ]
    pass

#c Axi4sTestBase
class Axi4sTestBase(ThExecFile):
    """
    """
    axi4s_byte_width = 4
    tx_random_seed = "some tx random seed"
    rx_random_seed = "some rx random seed"
    tx_buffer_end = 0x100
    rx_buffer_end = 0x100

    dut_mac = 0x123456789abc
    dut_ipv4 = 0xac10f078
    dut_udp = 0x1234
    rx_end_wait = 1000

    #c scripts
    apb = ApbAddressMap()
    scripts = {}
    scripts["sram"] = ([
        Script.op_set("addr1",apb.sram.address.Address()>>8),
        Script.op_set("addr2",apb.sram.address.Address()>>16),
        Script.op_set("addr3",apb.sram.address.Address()>>24),
        Script.op_write(apb.sram.address.Address(),32,[0]),
        Script.op_write(apb.sram.data_inc.Address(),32,[0x1234567, 0x2345678]),
        Script.op_write(apb.sram.address.Address(),32,[0]),
        Script.op_read(apb.sram.data_inc.Address(),32,2),
        ],0,[(0x1234567,4),
             (0x2345678,4)])
    scripts["sram_long"] = ([
        Script.op_set("addr1",apb.sram.address.Address()>>8),
        Script.op_set("addr2",apb.sram.address.Address()>>16),
        Script.op_set("addr3",apb.sram.address.Address()>>24),
        Script.op_write(apb.sram.address.Address(),32,[0]),
        Script.op_write(apb.sram.data_window.Address()+0,32,[0x1, 0x2, 0x3, 0x4, 0x5], True),
        Script.op_write(apb.sram.data_window.Address()+4,32,[0x1234567, 0x2345678], True),
        Script.op_write(apb.sram.data_window.Address()+8,32,[0x9, 0xa, 0xb], True),
        Script.op_read(apb.sram.data_window.Address()+4,32,2,True),        
        Script.op_read(apb.sram.data_window.Address()+1,32,4,True),        
        ],0,[(0x1234567,4),
                (0x2345678,4),
                (2,4),
                (3,4),
                (4,4),
                (0x1234567,4),
                ])
    scripts["sram_prep"] = ([
        Script.op_set("poll_delay",14),
        Script.op_set("poll_count",3),
        Script.op_set("addr1",apb.sram.address.Address()>>8),
        Script.op_set("addr2",apb.sram.address.Address()>>16),
        Script.op_set("addr3",apb.sram.address.Address()>>24),
        Script.op_write(apb.sram.address.Address(),32,[0]),
        ],0,[])
    scripts["sram_wr_data"] = ([
        Script.op_write(apb.sram.data_inc.Address(),32,[1,2,3,4,5,6,7,8]),
        Script.op_write(apb.sram.data_inc.Address(),32,[9,10,11,12,13,14,15,16]),
        Script.op_write(apb.sram.data_inc.Address(),32,[17,18,19,20,21,22,23,24]),
        Script.op_write(apb.sram.data_inc.Address(),32,[25,26,27,28,29,30,31]),
        ],0,[])
    scripts["sram_rd_all"] = ([
        Script.op_read(apb.sram.data_inc.Address(),32,8), # no inc address
        Script.op_read(apb.sram.data_inc.Address(),32,8),
        Script.op_read(apb.sram.data_inc.Address(),32,8),
        Script.op_read(apb.sram.data_inc.Address(),32,7),
        ],0,[
            (1,4),(2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),
            (9,4),(10,4),(11,4),(12,4),(13,4),(14,4),(15,4),(16,4),( 17,4),(18,4),(19,4),(20,4),(21,4),(22,4),(23,4),(24,4),( 25,4),(26,4),(27,4),(28,4),(29,4),(30,4),(31,4)])
    scripts["sram_rd_all_bytes"] = ([
        Script.op_read(apb.sram.data_inc.Address(),8,8), # no inc address
        Script.op_read(apb.sram.data_inc.Address(),8,8),
        Script.op_read(apb.sram.data_inc.Address(),8,8),
        Script.op_read(apb.sram.data_inc.Address(),8,7),
        ],0,[
            (1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),
            (9,1),(10,1),(11,1),(12,1),(13,1),(14,1),(15,1),(16,1),( 17,1),(18,1),(19,1),(20,1),(21,1),(22,1),(23,1),(24,1),( 25,1),(26,1),(27,1),(28,1),(29,1),(30,1),(31,1)])
    scripts["sram_rd_all_16"] = ([
        Script.op_read(apb.sram.data_inc.Address(),16,8), # no inc address
        Script.op_read(apb.sram.data_inc.Address(),16,8),
        Script.op_read(apb.sram.data_inc.Address(),16,8),
        Script.op_read(apb.sram.data_inc.Address(),16,7),
        ],0,[
            (1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),
            (9,2),(10,2),(11,2),(12,2),(13,2),(14,2),(15,2),(16,2),( 17,2),(18,2),(19,2),(20,2),(21,2),(22,2),(23,2),(24,2),( 25,2),(26,2),(27,2),(28,2),(29,2),(30,2),(31,2)])
    scripts["sram_rd_poll_faill"] = ([
        Script.op_read(apb.sram.data_inc.Address(),16,8), # no inc address
        Script.op_poll_set(apb.sram.data_inc.Address(),31), # Poll will fail
        Script.op_read(apb.sram.data_inc.Address(),16,8), # no inc address - this does not happen
        ],3,[
            (1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),
        ])
    
    #f __init__
    def __init__(self, **kwargs):
        super(Axi4sTestBase,self).__init__(**kwargs)
        pass
    #f exec_init
    def exec_init(self) -> None:
        self.die_event         = self.sim_event()
        super(Axi4sTestBase,self).exec_init()
        pass
    #f run__init - invoked by submodules
    def run__init(self):
        self.bfm_wait(10)
        self.sim_msg = self.sim_message()
        self.tx_random = Random()
        self.tx_random.seed(self.tx_random_seed)
        self.rx_random = Random()
        self.rx_random.seed(self.rx_random_seed)
        self.configure()
        self.axi_bfm.axi4s("rx_axi")
        self.spawn(self.tx_checker)
        pass

    #f tx_checker
    def tx_checker(self):
        self.axi_bfm.axi4s("tx_checker_axi")
        pkt = Pkt()
        flit = Axi4sT.of_bytes([], True)
        while not self.die_event.fired():
            self.bfm_wait(40)
            self.tx_checker_axi.slave_wait_for_data(400) # timeout in global_cycle() ticks
            while not self.tx_checker_axi.slave_empty():
                self.tx_checker_axi.slave_dequeue()
                flit.get_axi4s(self.tx_checker_axi)
                pkt.push_axi4s(flit)
                if flit.last == 1:
                    if len(self.expected) == 0:
                        self.failtest("Received a packet that was not expected")
                        return
                    exp = self.expected.pop(0)
                    self.compare_expected("Eth portion of pack",
                                          exp.data[0:14],
                                          pkt.data[0:14],
                                          ) 
                    self.compare_expected("IPv4 portion of pack",
                                          exp.data[14:34],
                                          pkt.data[14:34],
                                          )
                    self.compare_expected("UDP portion of pack",
                                          exp.data[34:42],
                                          pkt.data[34:42],
                                          )
                    self.compare_expected("Payload portion of pack",
                                          exp.data[42:],
                                          pkt.data[42:],
                                          )
                    pkt = Pkt()
                    pass
                pass
            pass
        pass

    #f rx_packet
    def rx_packet(self, pkt):
        flits = pkt.as_axi4s(self.axi4s_byte_width)
        for f in flits:
            f.set_axi4s(self.rx_axi)
            while self.rx_axi.master_full():
                self.bfm_wait(10)
                pass
            self.rx_axi.master_enqueue()
            pass
        self.bfm_wait(100)
        pass
    #f script_req_pkt
    def script_req_pkt(self, mac:int, ip:int, udp:int, id:int, resvd:int, script:Any) -> Pkt:
        script = script.as_bytes()
        dlen = 4 + len(script)
        pkt = (Pkt().add_eth_hdr(mac, self.dut_mac, 0x0800)
                    .add_ipv4_hdr(dlen+8, ip, self.dut_ipv4, 0x11, 0x40)
                    .add_udp_hdr(dlen, udp, 0x1234)
                    .push_le(id,1)
                    .push_le(resvd,3)
                    .push(script)
               )
        return pkt
    #f script_resp_pkt
    def script_resp_pkt(self, mac:int, ip:int, udp:int, id:int, comp:int, data:List[Tuple[int,int]]) -> Pkt:
        dlen = 4
        for (x,n) in data: dlen += n
        pkt = (Pkt().add_eth_hdr(self.dut_mac, mac, 0x0800)
                    .add_ipv4_hdr(dlen+8, self.dut_ipv4, ip, 0x11, 0x40)
                    .add_udp_hdr(dlen, 0x1234, udp)
                    .push_le(id,1)
                    .push_le(comp,1)
                    .push_le(dlen,2))
        for (x,n) in data:
            pkt.push_le(x,n)
            pass
        return pkt
                                      
    #f configure
    def configure(self):
        pass

    #f run
    def run(self):
        pass
    #f run__finalize
    def run__finalize(self):
        self.bfm_wait_until_test_done(1000)
        self.die_event.fire()
        self.bfm_wait_until_test_done(100)
        # rx_ptr = self.apb.read(self.axi4s_map.rx_ptr.Address())
        # self.verbose.error("Rx ptr %08x"%rx_ptr)
        self.passtest("Test completed")
        # self.verbose.error("%s"%(self.global_cycle()))
        pass
    #f All done
    pass

#c DebugApbTest_0
class DebugApbTest_0(Axi4sTestBase):
    #f run
    scripts_to_run = ["sram", "sram_long",
                      "sram",
                      "sram_prep", "sram_wr_data",
                      "sram_prep", "sram_rd_all",
                      "sram_prep", "sram_rd_all_bytes",
                      "sram_prep", "sram_rd_all_16",
                      "sram_prep", "sram_rd_poll_faill",
                      ]
    def run(self):
        self.to_deliver = []
        self.expected = []
        self.compiled_scripts = {}
        for (n,s) in self.scripts.items():
            self.verbose.info("Compile script %s"%n)
            self.compiled_scripts[n] = (
                Script.compile_script(s[0]),
                s[1],
                s[2])
            pass
        mac = 0xa00ab00bc00c
        ip = 0x0a011002
        udp = 0x0450
        id = 0x34
        for n in self.scripts_to_run:
            mac += 1
            ip += 7
            udp += 3
            id += 2
            (s, c, d) = self.compiled_scripts[n]
            self.to_deliver.append(self.script_req_pkt(mac,
                                                       ip,
                                                       udp,
                                                       id,
                                                       0,
                                                       s))
            self.expected.append( self.script_resp_pkt( mac,
                                                        ip,
                                                        udp,
                                                        id,
                                                        c,
                                                        d
                              ))
            pass
        while len(self.to_deliver) != 0:
            self.rx_packet(self.to_deliver.pop(0))
            pass
        self.bfm_wait(self.rx_end_wait)
        if len(self.expected) != 0:
            self.failtest("Had outstanding expected packets at end of test")
            pass
        pass

    pass
#c DebugApbTest_0_64
class DebugApbTest_0_64(DebugApbTest_0):
    axi4s_byte_width = 8

#a Hardware classes
#c AxiDebugApbHw
class AxiDebugApbHw(HardwareThDut):
    clock_desc = [("clk",(0,1,1)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    th_module_type = "axi4s_th"
    th_options = {"master_fifo_size":16,
                  "slave_fifo_size":128,
                  "data_width":32,
                  }
    module_name    = "tb_axi_debug_apb"
    dut_inputs  = {"apb_request":t_apb_request,
                   "dut_axi4s_tready":1,
                   "th_axi4s":t_axi4s32,
    }
    dut_outputs = {"apb_response":t_apb_response,
                   "th_axi4s_tready":1,
                   "dut_axi4s":t_axi4s32,
    }
    th_bfm_connections = ["th_axi4s_tready",
                          "dut_axi4s_tready",
                          "th_axi4s",
                          "dut_axi4s"]
    pass
#c AxiDebugApbSimpleHw
class AxiDebugApbSimpleHw(HardwareThDut):
    clock_desc = [("clk",(0,1,1)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    th_module_type = "axi4s_th"
    th_options = {"master_fifo_size":16,
                  "slave_fifo_size":128,
                  "data_width":64,
                  }
    module_name    = "tb_axi_debug_apb_simple"
    dut_inputs  = {"dut_axi4s_tready":1,
                   "th_axi4s":t_axi4s64,
    }
    dut_outputs = {"th_axi4s_tready":1,
                   "dut_axi4s":t_axi4s64,
    }
    th_bfm_connections = ["th_axi4s_tready",
                          "dut_axi4s_tready",
                          "th_axi4s",
                          "dut_axi4s"]
    pass

#a Simulation test classes
#c 
class ApbTargetAxi4s(TestCase):
    """
    Run scripts with widen/narrow of AXI module
    """
    hw = AxiDebugApbHw
    kwargs = {
    # "verbosity":0,
        #"th_args":{"tx_sram_write":Axi4sTestBase.tx_sram_write_axi},
        #"th_args":{"tx_sram_write":Axi4sTestBase.tx_sram_write_msg},
    }
    _tests = {
        # "smoke"        :  (DebugApbTest_0,40*1000,  kwargs),
        "tx_0"        :  (DebugApbTest_0,40*1000,  kwargs),
    }
    pass

class ApbTargetAxi4s_Simple(TestCase):
    """
    Run scripts with simple module
    """
    hw = AxiDebugApbSimpleHw
    kwargs = {
    # "verbosity":0,
        #"th_args":{"tx_sram_write":Axi4sTestBase.tx_sram_write_axi},
        #"th_args":{"tx_sram_write":Axi4sTestBase.tx_sram_write_msg},
    }
    _tests = {
        "tx_0"        :  (DebugApbTest_0_64,40*1000,  kwargs),
        "smoke"        :  (DebugApbTest_0_64,40*1000,  kwargs),
    }
    pass
