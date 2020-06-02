import cdl_desc
from cdl_desc import CdlModule, CdlSimVerilatedModule, CModel, CSrc

class Library(cdl_desc.Library):
    name="networking"
    pass

class Axi4sModules(cdl_desc.Modules):
    name = "axi4s"
    src_dir      = "cdl"
    tb_src_dir   = "tb_cdl"
    libraries = {"std":True, "utils":True}
    cdl_include_dirs = ["cdl"]
    export_dirs = cdl_include_dirs + [ src_dir ]
    modules = []
    modules += [ CdlModule("axi4s32_fifo_4",
                           force_includes=["axi4s.h"],
                           types={"gt_generic_valid_req":"t_axi4s32"},
                           cdl_module_name="generic_valid_ack_fifo",
                           instance_types={"fifo_status":"fifo_status_7"},
    ) ]
    modules += [ CdlModule("apb_target_axi4s") ]
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
    modules += [ CModel("axi4s32_master_slave", src_dir="cmodel") ]
    # modules += [ Csrc("axi_master", src_dir="csrc") ]
    pass

