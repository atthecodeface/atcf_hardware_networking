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
    # modules += [ CdlModule("axi4s32_fifo_4", force_includes=["axi4s.h"], types={"gt_generic_valid_req":"t_axi4s32"}, cdl_filename="generic_valid_ack_fifo") ]
    pass

