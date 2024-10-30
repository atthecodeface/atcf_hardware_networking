import cdl_desc
from cdl_desc import CdlModule, CdlSimVerilatedModule, CModel, CSrc

class Library(cdl_desc.Library):
    name="networking"
    pass

class Axi4sModules(cdl_desc.Modules):
    name = "axi4s"
    src_dir      = "cdl"
    tb_src_dir   = "tb_cdl"
    libraries = {"std":True, "utils":True, "apb":True}
    cdl_include_dirs = ["cdl"]
    export_dirs = cdl_include_dirs + [ src_dir ]
    modules = []
    for axi in ["axi4s32", "axi4s64", "axi4s128"]:
        t_axi = "t_"+axi;
        modules += [ CdlModule(axi+"_fifo_4",
                           force_includes=["axi4s.h"],
                           types={"gt_generic_valid_req":t_axi},
                           cdl_module_name="generic_valid_ack_fifo",
                           instance_types={"fifo_status":"fifo_status_7"},
                               ) ]
        modules += [ CdlModule(axi+"_double_buffer",
                           force_includes=["axi4s.h"],
                           types={"gt_generic_valid_req":t_axi},
                           cdl_module_name="generic_valid_ack_double_buffer",
                           instance_types={"fifo_status":"fifo_status_3"},
                               ) ]
        modules += [ CdlModule(axi+"_insertion_buffer_8",
                           force_includes=["axi4s.h"],
                           types={"gt_generic_valid_req":t_axi},
                           constants={"fifo_depth":8},
                           instance_types={"fifo_status":"fifo_status_7"},
                           cdl_module_name="generic_valid_ack_insertion_buffer",
                               ) ]

        pass
    modules += [ CdlModule("apb_target_axi4s") ]
    modules += [ CdlModule("axi4s64_to_axi4s32") ]
    modules += [ CdlModule("axi4s32_to_axi4s64") ]
    modules += [ CdlModule("axi4s64_to_axi4s128") ]
    modules += [ CdlModule("axi4s128_to_axi4s64") ]
    modules += [ CdlModule("axi4s64_apb_master") ]
    modules += [ CdlModule("axi4s64_initiator_sram") ]
    modules += [ CdlModule("axi4s_process") ]
    modules += [ CdlModule("axi4s_process8_map_udp") ]
    modules += [ CdlModule("tb_apb_target_axi4s", src_dir="tb_cdl") ]
    pass

class Axi4sBFM(cdl_desc.Modules):
    name = "axi4s_bfm"
    src_dir      = "cmodel"
    cpp_include_dirs=["csrc", "cmodel"]    
    libraries = {"std":True, "utils":True}
    modules = []
    modules += [ CSrc("ef_object", src_dir="csrc") ]
    modules += [ CSrc("axi_types", src_dir="csrc") ]
    modules += [ CModel("axi4s_th", src_dir="cmodel") ]
    # modules += [ Csrc("axi_master", src_dir="csrc") ]
    pass

