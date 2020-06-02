# Transmit

The transmit side operates with a transmit SRAM read pointer, pointing
in to the transmit SRAM at the address of the current transmit block.

A transmit block is structured as a packet status word followed by a
user word, followed by data for the packet.

The transmit packet status word has a 16-bit transmit byte count in
its bottom 16 bits; the rest of the word is unused. This byte count
must include the (not transmitted) user word; so if the packet data is
17 bytes, then the transmit packet status word must be 21.

## Initialization

The transmit starts in reset, and enters reset on
apb_state.global_config.tx_reset

It has to receive an apb_state.global_config.tx_init to move to the
idle state

## Idle

When the transmit side is idle, it will poll the transmit SRAM every
10 cycles (defined by tx_poll_count_restart_value).

This polling is performed by reading the tx packet status at the
current transmit SRAM read pointer. If this is non-zero, then the
transmitter assumes it is a valid packet status word, and will
continue to transmit the packet following.

## Packet transmission

A packet is transmitted by first reading the user word (which follows
the transmit packet status word). This is presented with every AXI4S
data word on the bus.

Then the packet data is read word-by-word; this is presented to the
AXI4S bus, with the constant user data, along with strobes indicating
which bytes are valid - this will be all bytes except in the last word
of a packet, when it will be the bottom N bytes as required.

There is a delay in reading from the transmit SRAM and getting the
data to the AXI4S bus; the transmitter thus includes a 4-element FIFO
to decouple the two systems (SRAM and AXI4S) somewhat. The transmitter
reads the SRAM if it has any uncommitted room in the 4-element FIFO.

