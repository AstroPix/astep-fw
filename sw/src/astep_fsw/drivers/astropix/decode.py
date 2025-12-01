import pandas as pd
import logging
logger = logging.getLogger(__name__)

def decode_readout(self, logger, readout:bytearray, i:int, printer: bool = True):
    #Decodes readout
    #Required argument:
    #readout: Bytearray - readout from sensor, not the printed Hex values
    #i: int - Readout number
    #Optional:
    #printer: bool - Print decoded output to terminal
    #Returns dataframe
    #!!! Warning, richard 11/10/23 -> The Astep FW returns all bits properly ordered, don't reverse bits when using this firmware!

    list_hits =[]
    hit_list = []

    #Break full readout into separate data packets as defined by how many bytes are contained in each hit from the FW, use to fill array 'list_hits'
    b=0
    while b<len(readout):
        packet_len = int(readout[b])
        if packet_len>16:
            logger.debug("Probably didn't find a hit here - go to next byte")
            b+=1
        else: #got a hit
            list_hits.append(readout[b:b+packet_len+1])
            #logger.debug(f"found hit {binascii.hexlify(readout[b:b+packet_len+1])}")
            b += packet_len+1

    #decode hit contents
    for hit in list_hits:
        # Generates the values from the bitstream
        try:
            pack_len  = int(hit[0])
            layer       = int(hit[1])
            id          = int(hit[2]) >> 3
            payload     = int(hit[2]) & 0b111
            location    = int(hit[3])  & 0b111111
            col         = 1 if (int(hit[3]) >> 7 ) & 1 else 0
            timestamp   = int(hit[4])
            tot_msb     = int(hit[5]) & 0b1111
            tot_lsb     = int(hit[6])   
            tot_total   = (tot_msb << 8) + tot_lsb
            tot_us      = (tot_total * self.sampleclock_period_ns)/1000.0
            fpga_ts     = int.from_bytes(hit[7:11], 'little')
        except IndexError: #hit cut off at end of stream
            packet_len, layer, id, payload, location, col = -1, -1, -1, -1, -1, -1
            timestamp, tot_msb, tot_lsb, tot_total = -1, -1, -1, -1
            tot_us, fpga_ts = -1, -1
        
        # print decoded info in terminal if desiered
        if printer:
            try:
                print(
                f"{i} Packet len: {pack_len}\t Layer ID: {layer}\n"
                f"ChipId: {id}\tPayload: {payload}\t"
                f"Location: {location}\tRow/Col: {'Col' if col else 'Row'}\t"
                f"TS: {timestamp}\t"
                f"ToT: MSB: {tot_msb}\tLSB: {tot_lsb} Total: {tot_total} ({tot_us} us) \n"
                f"FPGA TS: {fpga_ts}\n"           
                )
            except IndexError:
                print(f"HIT TOO SHORT TO BE DECODED - {binascii.hexlify(hit)}")
            except UnboundLocalError:
                print(f"Hit could not be decoded - likely missing a header\n\n"
                f"{i} Packet len: {pack_len}\t Layer ID: {layer}\n"
                f"ChipId: {id}\tPayload: {payload}\t"
                f"Location: {location}\tRow/Col: {'Col' if col else 'Row'}\t"
                f"TS: {timestamp}\t"
                f"ToT: MSB: {tot_msb}\tLSB: {tot_lsb} \n"
                )

        # hits are sored in dictionary form
        hits = {
            'readout': i,
            'layer': layer,
            'chipID': id,
            'payload': payload,
            'location': location,
            'isCol': (True if col else False),
            'timestamp': timestamp,
            'tot_msb': tot_msb,
            'tot_lsb': tot_lsb,
            'tot_total': tot_total,
            'tot_us': tot_us,
            'fpga_ts': fpga_ts
            }
        hit_list.append(hits)

    # Much simpler to convert to df in the return statement vs df.concat
    return pd.DataFrame(hit_list)