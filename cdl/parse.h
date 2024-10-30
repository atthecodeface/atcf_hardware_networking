typedef struct {
    bit is_bcast;
    bit[48] dmac;
    bit[48] smac;
    bit[16] proto;
} t_eth_hdr;

typedef struct {
    bit[4] version; // must be 4
    bit[4] hdr_len; // must be 5
    bit[8] dscp;
    bit[16] len;
    bit[16] id;
    bit[16] frag;
    bit[8] ttl;
    bit[8] proto;
    bit[16] csum;
    bit[32] src;
    bit[32] dst;
    
    bit valid_vh;
    bit valid_frag;
    bit valid_ttl;
} t_ipv4_hdr;

typedef struct {
    bit[16] len;
    bit[16] csum;
    bit[16] src;
    bit[16] dst;
} t_udp_hdr;

