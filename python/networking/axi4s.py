#a Copyright
#  
#  This file 'axi4s.py' copyright Gavin J Stark 2020
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

from typing import List, Tuple, Dict, Optional, Any

t_axi4s32 = {"valid":1, "t":{"data":32, "last":1, "user":64, "strb":4, "keep":4, "id":64, "dest":64}}
t_axi4s64 = {"valid":1, "t":{"data":64, "last":1, "user":64, "strb":8, "keep":8, "id":64, "dest":64}}

#c Axi4sT
class Axi4sT(object):
    data:int
    strb:int
    last:bool
    keep:int
    _meta: Any=None

    def __init__(self, data, strb, last, keep=None):
        if keep is None: keep=strb
        self.data = data
        self.keep = keep
        self.strb = strb
        self.last = last
        pass

    @classmethod
    def of_bytes(cls, data:bytes, last:bool):
        n = len(data)
        mask = (1<<n)-1
        return cls(data = int.from_bytes(data, byteorder='little'),
                   strb = mask,
                   keep = mask,
                   last = last)

    @property
    def meta(self):
        """Metadata for the flit"""
        return self._meta

    @meta.setter
    def meta(self, value: Any):
        self._meta = value
        pass

    def get_axi4s(self, axi4s):
        self.data = axi4s.get("data")
        self.last = axi4s.get("last")
        self.keep = axi4s.get("keep")
        self.strb = axi4s.get("strb")
        pass
    
    def set_axi4s(self, axi4s):
        axi4s.set("data", self.data)
        axi4s.set("last", self.last)
        axi4s.set("keep", self.keep)
        axi4s.set("strb", self.strb)
        pass
    
    def compare(self, th, axi4s):
        th.compare_expected("axi4s data %s / %08x"%(str(self),axi4s.get("data")), self.data, axi4s.get("data"))
        th.compare_expected("axi4s last %s"%(str(self)), self.last, axi4s.get("last"))
        th.compare_expected("axi4s strb %s"%(str(self)), self.strb, axi4s.get("strb"))
        th.compare_expected("axi4s keep %s"%(str(self)), self.keep, axi4s.get("keep"))
        return
    
    def __str__(self):
        r = "%08x:%x:%x:%d"%(self.data,self.strb,self.keep,int(self.last))
        return r

    def __repr__(self):
        r = "%08x:%x:%x:%d"%(self.data,self.strb,self.keep,int(self.last))
        return r

    pass

class Pkt(object):
    data: bytearray
    _initial_meta: Any
    _last_meta: Any
    _index : int
    def __init__(self, data=None):
        if data is None:
            data = bytearray()
            pass
        if type(data) == bytes: data = bytearray(data)
        self.data = data
        self._initial_meta = None
        self._last_meta = None
        self._index = 0
        pass
    
    def __len__(self) -> int:
        return len(self.data)

    @property
    def index(self):
        """Metadata for a first cycle of packet"""
        return self._index

    @index.setter
    def index(self, value: Any):
        self._index = value
        pass
    
    @property
    def initial_meta(self):
        """Metadata for a first cycle of packet"""
        return self._initial_meta

    @initial_meta.setter
    def initial_meta(self, value: Any):
        self._initial_meta = value
        pass
    
    @property
    def last_meta(self):
        """Metadata for a first cycle of packet"""
        return self._last_meta

    @last_meta.setter
    def last_meta(self, value: Any):
        self._last_meta = value
        pass

    def clone(self):
        pkt = Pkt(self.data[:])
        pkt._initial_meta = self._initial_meta
        pkt._last_meta = self._last_meta
        pkt.index = self._index
        pass
    
    def next(self, n:int) -> Tuple[bytes, bool, bool, Optional[Any]]:
        is_start = self._index == 0
        index = self._index
        if index >= len(self.data):
            index = len(self.data)
            pass
        if index + n > len(self.data):
            n = len(self.data) - index
            pass
        self._index += n
        is_last = self._index >= len(self.data)
        meta = None
        if is_start: meta = self._initial_meta
        if is_last: meta = self._last_meta
        return (self.data[index:index+n], is_start, is_last, meta)

    def push(self, data:bytes):
        self.data += data
        return self

    def push_be(self, data:int, n:int):
        for i in range(n):
            self.data.append((data>>(8*(n-1-i))) & 0xff)
            pass
        return self

    def push_le(self, data:int, n:int):
        for i in range(n):
            self.data.append((data>>(8*i)) & 0xff)
            pass
        return self

    def push_axi4s(self, flit:Axi4sT):
        for i in range(8):
            if (flit.keep>>i)&1 != 0: # This copes witth 4- or 8- byte AXI4S
                self.data.append((flit.data>>(8*i))&0xff)
                pass
            pass
        return self

    def csum16(self, s:int, n:int) -> int:
        csum = 0
        for i in range(n//2):
            csum += self.data[s+i*2+1]
            csum += self.data[s+i*2]<<8
            if csum > 0xffff: csum -= 0xffff
            pass
        return csum

    def fix_ipv4_csum(self, s:int, n:int, d:int):
        csum = 0xffff - self.csum16(s, n)
        self.data[d+1] = csum&0xff
        self.data[d]   = (csum>>8)&0xff
        return self
    
    def as_axi4s(self, bpf:int) -> List[Axi4sT]:
        result = []
        self.index = 0
        while True:
            (data, start, last, meta) = self.next(bpf)
            if len(data)==0: break
            flit = Axi4sT.of_bytes(data, last)
            flit.meta = meta
            result.append(flit)
            pass
        return result

    def add_eth_hdr(self, smac:int, dmac:int, proto:int):
        self.push_be(dmac,6)
        self.push_be(smac,6)
        self.push_be(proto,2)
        return self

    def add_ipv4_hdr(self, plen:int, src:int, dst:int, proto:int, ttl:int=64):
        n = len(self.data)
        self.data.append(0x45)
        self.data.append(0x2) # dscp, ECN
        self.push_be(plen+20,2)
        self.push_be(0,2) # id
        self.push_be(0x4000,2) # frag
        self.data.append(ttl)
        self.data.append(proto)
        self.push_be(0,2) # csum
        self.push_be(src,4)
        self.push_be(dst,4)
        self.fix_ipv4_csum(n, 20, n+10)
        return self

    def add_udp_hdr(self, plen:int, src:int, dst:int):
        self.push_be(src,2)
        self.push_be(dst,2)
        self.push_be(plen+8,2)
        self.push_be(0,2)
        return self

    pass
