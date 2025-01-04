/** Copyright (C) 2016-2018,  Gavin J Stark.  All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * @file   axi4s_modules.h
 * @brief  AXI4s modules header file for CDL modules
 *
 * Header file for the types and CDL modules for AXI4S modules
 *
 */

/*a Includes */
include "apb::apb.h"
include "utils::fifo_status.h"
include "utils::sram_access.h"
include "utils::debug.h"
include "parse.h"
include "axi4s.h"

/*a AXI4S 32 modules */
/*m apb_target_axi4s */
extern module apb_target_axi4s( clock clk         "System clock",
                         input bit reset_n "Active low reset",

                         input  t_apb_request  apb_request  "APB request",
                         output t_apb_response apb_response "APB response",

                         output t_sram_access_req  tx_sram_access_req  "SRAM access request",
                         input  t_sram_access_resp tx_sram_access_resp "SRAM access response",

                         output t_sram_access_req  rx_sram_access_req  "SRAM access request",
                         input  t_sram_access_resp rx_sram_access_resp "SRAM access response",

                         input bit        tx_axi4s_tready,
                         output t_axi4s32 tx_axi4s,
                         input t_axi4s32  rx_axi4s,
                         output bit       rx_axi4s_tready
    )
{
    timing to   rising clock clk tx_axi4s_tready;
    timing from rising clock clk tx_axi4s;
    timing from rising clock clk rx_axi4s_tready;
    timing to   rising clock clk rx_axi4s;
    timing from rising clock clk apb_response;
    timing to   rising clock clk apb_request;
    timing from rising clock clk rx_sram_access_req, tx_sram_access_req;
    timing to   rising clock clk rx_sram_access_resp, tx_sram_access_resp;
}

/*m axi4s_pcap */
extern module axi4s_pcap( clock clk         "System clock",

                         input bit        master_axi4s_tready,
                         output t_axi4s32 master_axi4s,
                         input t_axi4s32  slave_axi4s,
                         output bit       slave_axi4s_tready
    )
{
    timing to   rising clock clk master_axi4s_tready;
    timing from rising clock clk master_axi4s;
    timing from rising clock clk slave_axi4s_tready;
    timing to   rising clock clk slave_axi4s;
}

/*m axi4s32_double_buffer */
// 2-entry FIFO
extern
module axi4s32_double_buffer( clock clk                      "Clock for the FIFO",
                       input bit reset_n              "Asynchronous reset",
                       input t_axi4s32 req_in         "AXI4S input side master data",
                       output bit ack_in              "AXI4S input side slave 'tready' signal",
                       output t_axi4s32 req_out       "AXI4S output side master data",
                       input bit ack_out              "AXI4S output side slave 'tready' signal",
                       output t_fifo_status fifo_status "Standard FIFO status"
    )
{
    timing to    rising clock clk req_in;
    timing from  rising clock clk ack_in;

    timing from  rising clock clk req_out;
    timing to    rising clock clk ack_out;

    timing from  rising clock clk fifo_status;
}

/*m axi4s32_insertion_buffer_8 */
// 8-entry FIFO, with whole contents visible, oldest at data 0, valid from data0 upwards
extern
module axi4s32_insertion_buffer_8( clock clk                      "Clock for the FIFO",
                              input bit reset_n              "Asynchronous reset",
                              input t_axi4s32 req_in         "AXI4S input side master data",
                              output bit ack_in              "AXI4S input side slave 'tready' signal",
                              output t_axi4s32 req_out       "AXI4S output side master data",
                              input bit ack_out              "AXI4S output side slave 'tready' signal",

                              output t_axi4s32 data0         "AXI4S FIFO contents (oldest)",
                              output t_axi4s32 data1         "AXI4S FIFO contents",
                              output t_axi4s32 data2         "AXI4S FIFO contents",
                              output t_axi4s32 data3         "AXI4S FIFO contents",
                              output t_axi4s32 data4         "AXI4S FIFO contents",
                              output t_axi4s32 data5         "AXI4S FIFO contents",
                              output t_axi4s32 data6         "AXI4S FIFO contents",
                              output t_axi4s32 data7         "AXI4S FIFO contents",

                              output t_fifo_status fifo_status     "Fifo status, that need not be used"
    )
{
    timing to    rising clock clk req_in;
    timing from  rising clock clk ack_in;

    timing from  rising clock clk req_out;
    timing to    rising clock clk ack_out;

    timing from  rising clock clk data0, data1, data2, data3, data4, data5, data6, data7;

    timing from  rising clock clk fifo_status;
}

/*m axi4s32_fifo_4 */
// 4-entry FIFO
extern
module axi4s32_fifo_4( clock clk                      "Clock for the FIFO",
                       input bit reset_n              "Asynchronous reset",
                       input t_axi4s32 req_in         "AXI4S input side master data",
                       output bit ack_in              "AXI4S input side slave 'tready' signal",
                       output t_axi4s32 req_out       "AXI4S output side master data",
                       input bit ack_out              "AXI4S output side slave 'tready' signal",
                       output t_fifo_status fifo_status "Standard FIFO status"
    )
{
    timing to    rising clock clk req_in;
    timing from  rising clock clk ack_in;

    timing from  rising clock clk req_out;
    timing to    rising clock clk ack_out;

    timing from  rising clock clk fifo_status;
}

/*m axi4s32_to_axi4s64 */
// 2-entry FIFO in 32-bit and 64-bit double buffer out
extern
module axi4s32_to_axi4s64( clock clk                      "Clock for the FIFO",
                              input bit reset_n              "Asynchronous reset",
                              input t_axi4s32 rx_axi4s       "AXI4S input side master data",
                              output bit rx_axi4s_tready     "AXI4S input side slave 'tready' signal",
                              output t_axi4s64 tx_axi4s      "AXI4S output side master data",
                              input bit tx_axi4s_tready      "AXI4S output side slave 'tready' signal"
    )
{
    timing to    rising clock clk rx_axi4s;
    timing from  rising clock clk rx_axi4s_tready;

    timing to    rising clock clk tx_axi4s_tready;
    timing from  rising clock clk tx_axi4s;
}

/*a AXI4S 64 modules */
/*m axi4s64_double_buffer */
// 2-entry FIFO
extern
module axi4s64_double_buffer( clock clk                      "Clock for the FIFO",
                       input bit reset_n              "Asynchronous reset",
                       input t_axi4s64 req_in         "AXI4S input side master data",
                       output bit ack_in              "AXI4S input side slave 'tready' signal",
                       output t_axi4s64 req_out       "AXI4S output side master data",
                       input bit ack_out              "AXI4S output side slave 'tready' signal",
                       output t_fifo_status fifo_status "Standard FIFO status"
    )
{
    timing to    rising clock clk req_in;
    timing from  rising clock clk ack_in;

    timing from  rising clock clk req_out;
    timing to    rising clock clk ack_out;

    timing from  rising clock clk fifo_status;
}

/*m axi4s64_insertion_buffer_8 */
// 8-entry FIFO, with whole contents visible, oldest at data 0, valid from data0 upwards
extern
module axi4s64_insertion_buffer_8( clock clk                      "Clock for the FIFO",
                              input bit reset_n              "Asynchronous reset",
                              input t_axi4s64 req_in         "AXI4S input side master data",
                              output bit ack_in              "AXI4S input side slave 'tready' signal",
                              output t_axi4s64 req_out       "AXI4S output side master data",
                              input bit ack_out              "AXI4S output side slave 'tready' signal",

                              output t_axi4s64 data0         "AXI4S FIFO contents (oldest)",
                              output t_axi4s64 data1         "AXI4S FIFO contents",
                              output t_axi4s64 data2         "AXI4S FIFO contents",
                              output t_axi4s64 data3         "AXI4S FIFO contents",
                              output t_axi4s64 data4         "AXI4S FIFO contents",
                              output t_axi4s64 data5         "AXI4S FIFO contents",
                              output t_axi4s64 data6         "AXI4S FIFO contents",
                              output t_axi4s64 data7         "AXI4S FIFO contents",

                              output t_fifo_status fifo_status     "Fifo status, that need not be used"
    )
{
    timing to    rising clock clk req_in;
    timing from  rising clock clk ack_in;

    timing from  rising clock clk req_out;
    timing to    rising clock clk ack_out;

    timing from  rising clock clk data0, data1, data2, data3, data4, data5, data6, data7;

    timing from  rising clock clk fifo_status;
}

/*m axi4s64_fifo_4 */
// 4-entry FIFO
extern
module axi4s64_fifo_4( clock clk                      "Clock for the FIFO",
                       input bit reset_n              "Asynchronous reset",
                       input t_axi4s64 req_in         "AXI4S input side master data",
                       output bit ack_in              "AXI4S input side slave 'tready' signal",
                       output t_axi4s64 req_out       "AXI4S output side master data",
                       input bit ack_out              "AXI4S output side slave 'tready' signal",
                       output t_fifo_status fifo_status "Standard FIFO status"
    )
{
    timing to    rising clock clk req_in;
    timing from  rising clock clk ack_in;

    timing from  rising clock clk req_out;
    timing to    rising clock clk ack_out;

    timing from  rising clock clk fifo_status;
}

/*m axi4s64_to_axi4s128 */
// 2-entry FIFO in 64-bit and 128-bit double buffer out
extern
module axi4s64_to_axi4s128( clock clk                      "Clock for the FIFO",
                              input bit reset_n              "Asynchronous reset",
                              input t_axi4s64 rx_axi4s       "AXI4S input side master data",
                              output bit rx_axi4s_tready     "AXI4S input side slave 'tready' signal",
                              output t_axi4s128 tx_axi4s      "AXI4S output side master data",
                              input bit tx_axi4s_tready      "AXI4S output side slave 'tready' signal"
    )
{
    timing to    rising clock clk rx_axi4s;
    timing from  rising clock clk rx_axi4s_tready;

    timing to    rising clock clk tx_axi4s_tready;
    timing from  rising clock clk tx_axi4s;
}

/*m axi4s64_to_axi4s32 */
// 64-bit double buffer and 32-bit double buffer
extern
module axi4s64_to_axi4s32( clock clk                      "Clock for the FIFO",
                              input bit reset_n              "Asynchronous reset",
                              input t_axi4s64 rx_axi4s       "AXI4S input side master data",
                              output bit rx_axi4s_tready     "AXI4S input side slave 'tready' signal",
                              output t_axi4s32 tx_axi4s      "AXI4S output side master data",
                              input bit tx_axi4s_tready      "AXI4S output side slave 'tready' signal"
    )
{
    timing to    rising clock clk rx_axi4s;
    timing from  rising clock clk rx_axi4s_tready;

    timing to    rising clock clk tx_axi4s_tready;
    timing from  rising clock clk tx_axi4s;
}

/*m axi4s128_to_axi4s64 */
// 128-bit double buffer and 64-bit double buffer
extern
module axi4s128_to_axi4s64( clock clk                      "Clock for the FIFO",
                              input bit reset_n              "Asynchronous reset",
                              input t_axi4s128 rx_axi4s       "AXI4S input side master data",
                              output bit rx_axi4s_tready     "AXI4S input side slave 'tready' signal",
                              output t_axi4s64 tx_axi4s      "AXI4S output side master data",
                              input bit tx_axi4s_tready      "AXI4S output side slave 'tready' signal"
    )
{
    timing to    rising clock clk rx_axi4s;
    timing from  rising clock clk rx_axi4s_tready;

    timing to    rising clock clk tx_axi4s_tready;
    timing from  rising clock clk tx_axi4s;
}

/*m axi4s64_initiator_sram
 */
extern module axi4s64_initiator_sram( clock clk         "System clock",
                             input bit reset_n "Active low reset",

                             input bit force_reset "If asserted, reset all ptrs",
   
                             input  t_ais_request  ais_request  "Axi4s initiator request",
                             output bit  ais_ready "Asserted if a valid AIS request would be taken",

                             output t_sram_access_req  sram_access_req  "SRAM access request",
                             input  t_sram_access_resp sram_access_resp "SRAM access response",

                             input bit        tx_axi4s_tready,
                             output t_axi4s64 tx_axi4s,

                                      input t_ais_cfg ais_cfg,
                                      output t_fifo_status fifo_status "FIFO status for *uncommitted* packet data"
    )
{
    timing to    rising clock clk ais_cfg;
    timing to    rising clock clk ais_request;
    timing from  rising clock clk ais_ready;

    timing from  rising clock clk sram_access_req;
    timing to    rising clock clk sram_access_resp;

    timing from  rising clock clk tx_axi4s;
    timing to    rising clock clk tx_axi4s_tready;

    timing from  rising clock clk fifo_status;
}

/*a AXI4S 128 modules */
/*m axi4s128_double_buffer */
// 2-entry FIFO
extern
module axi4s128_double_buffer( clock clk                      "Clock for the FIFO",
                       input bit reset_n              "Asynchronous reset",
                       input t_axi4s128 req_in         "AXI4S input side master data",
                       output bit ack_in              "AXI4S input side slave 'tready' signal",
                       output t_axi4s128 req_out       "AXI4S output side master data",
                       input bit ack_out              "AXI4S output side slave 'tready' signal",
                       output t_fifo_status fifo_status "Standard FIFO status"
    )
{
    timing to    rising clock clk req_in;
    timing from  rising clock clk ack_in;

    timing from  rising clock clk req_out;
    timing to    rising clock clk ack_out;

    timing from  rising clock clk fifo_status;
}

/*m axi4s128_insertion_buffer_8 */
// 8-entry FIFO, with whole contents visible, oldest at data 0, valid from data0 upwards
extern
module axi4s128_insertion_buffer_8( clock clk                      "Clock for the FIFO",
                              input bit reset_n              "Asynchronous reset",
                              input t_axi4s128 req_in         "AXI4S input side master data",
                              output bit ack_in              "AXI4S input side slave 'tready' signal",
                              output t_axi4s128 req_out       "AXI4S output side master data",
                              input bit ack_out              "AXI4S output side slave 'tready' signal",

                              output t_axi4s128 data0         "AXI4S FIFO contents (oldest)",
                              output t_axi4s128 data1         "AXI4S FIFO contents",
                              output t_axi4s128 data2         "AXI4S FIFO contents",
                              output t_axi4s128 data3         "AXI4S FIFO contents",
                              output t_axi4s128 data4         "AXI4S FIFO contents",
                              output t_axi4s128 data5         "AXI4S FIFO contents",
                              output t_axi4s128 data6         "AXI4S FIFO contents",
                              output t_axi4s128 data7         "AXI4S FIFO contents",

                              output t_fifo_status fifo_status     "Fifo status, that need not be used"
    )
{
    timing to    rising clock clk req_in;
    timing from  rising clock clk ack_in;

    timing from  rising clock clk req_out;
    timing to    rising clock clk ack_out;

    timing from  rising clock clk data0, data1, data2, data3, data4, data5, data6, data7;

    timing from  rising clock clk fifo_status;
}

/*m axi4s128_fifo_4 */
// 4-entry FIFO
extern
module axi4s128_fifo_4( clock clk                      "Clock for the FIFO",
                       input bit reset_n              "Asynchronous reset",
                       input t_axi4s128 req_in         "AXI4S input side master data",
                       output bit ack_in              "AXI4S input side slave 'tready' signal",
                       output t_axi4s128 req_out       "AXI4S output side master data",
                       input bit ack_out              "AXI4S output side slave 'tready' signal",
                       output t_fifo_status fifo_status "Standard FIFO status"
    )
{
    timing to    rising clock clk req_in;
    timing from  rising clock clk ack_in;

    timing from  rising clock clk req_out;
    timing to    rising clock clk ack_out;

    timing from  rising clock clk fifo_status;
}

/*m APB master */
/*m axi4s64_dbg_master */
extern
module axi4s64_dbg_master( clock clk                      "Clock for the FIFO",
                          input bit reset_n              "Asynchronous reset",
                          input t_axi4s64 rx_axi4s       "AXI4S input side master data",
                          output bit rx_axi4s_tready     "AXI4S input side slave 'tready' signal",
                          output t_axi4s64 tx_axi4s      "AXI4S output side master data",
                          input bit tx_axi4s_tready      "AXI4S output side slave 'tready' signal",
                           output t_dbg_master_request dbg_master_req,
                           input t_dbg_master_response dbg_master_resp
    )
{
    timing to    rising clock clk rx_axi4s;
    timing from  rising clock clk rx_axi4s_tready;

    timing to    rising clock clk tx_axi4s_tready;
    timing from  rising clock clk tx_axi4s;

    timing from rising clock clk dbg_master_req;
    timing to   rising clock clk dbg_master_resp;
}

/*a AXI4S processing */
/*m axi4s_process_map */
extern module axi4s_process_map( clock clk                      "Clock for the FIFO",
                                 input bit reset_n              "Asynchronous reset",
                                 input bit output_ready         "Output ready; use only for state transitions, not for outputs",

                                 input bit start,

                                 input t_axi4s128 data0         "AXI4S FIFO contents (oldest)",
                                 input t_axi4s128 data1         "AXI4S FIFO contents",
                                 input t_axi4s128 data2         "AXI4S FIFO contents",
                                 input t_axi4s128 data3         "AXI4S FIFO contents",
                                 input t_axi4s128 data4         "AXI4S FIFO contents",
                                 input t_axi4s128 data5         "AXI4S FIFO contents",
                                 input t_axi4s128 data6         "AXI4S FIFO contents",
                                 input t_axi4s128 data7         "AXI4S FIFO contents",

                                 output t_map_result map_result,
                                 output t_axi4s128 mapped_data         "Mapped data0, if result is 'map'"
    )
{
    timing to    rising clock clk output_ready, start; 
    timing to  rising clock clk data0, data1, data2, data3, data4, data5, data6, data7;
    timing from  rising clock clk map_result, mapped_data;

    timing comb input start, data0, data1, data2, data3, data4, data5, data6, data7;
    timing comb output mapped_data;
}

/*a Network parsing */
extern module net_parse_eth(
    input bit[64] data0,
    input bit[64] data1,

    output t_eth_hdr eth_hdr

    )
{
    timing comb input data0, data1;
    timing comb output eth_hdr;
}

extern module net_parse_ipv4(
    input bit[64] data0,
    input bit[64] data1,
    input bit[64] data2,

    output t_ipv4_hdr ipv4_hdr

    )
{
    timing comb input data0, data1, data2;
    timing comb output ipv4_hdr;
}

extern module net_parse_udp(
    input bit[64] data0,

    output t_udp_hdr udp_hdr

    )
{
    timing comb input data0;
    timing comb output udp_hdr;
}

/*a Network parsing */
extern module net_pack_eth(
    output bit[64] data0,
    output bit[48] data1,

    input t_eth_hdr eth_hdr

    )
{
    timing comb output data0, data1;
    timing comb input eth_hdr;
}

extern module net_pack_ipv4(
    output bit[64] data0,
    output bit[64] data1,
    output bit[32] data2,

    input t_ipv4_hdr ipv4_hdr

    )
{
    timing comb output data0, data1, data2;
    timing comb input ipv4_hdr;
}

extern module net_pack_udp(
    output bit[64] data0,

    input t_udp_hdr udp_hdr

    )
{
    timing comb output data0;
    timing comb input udp_hdr;
}
