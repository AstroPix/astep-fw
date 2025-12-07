import pandas as pd
import logging
import binascii

logger = logging.getLogger(__name__)

def gray_to_dec(gray: int) -> int:
    """
    Decode Gray code to decimal

    :param gray: Gray code

    :returns: Decoded decimal
    """
    bits = gray >> 1
    while bits:
        gray ^= bits
        bits >>= 1
    return gray


def prepare_readout(readout: bytearray) -> list:
    list_hits = []
    b = 0
    packet_len = 0
    while b < len(readout):
        packet_len = int(readout[b])
        if packet_len > 16:
            logger.debug("Probably didn't find a hit here - go to next byte")
            b += 1
        else:  # got a hit
            list_hits.append(readout[b:b+packet_len+1])
            logger.debug("found hit %s", binascii.hexlify(readout[b:b+packet_len+1]))
            b += packet_len+1
    return list_hits, packet_len

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

    list_hits, packet_len = prepare_readout(readout)

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
            pack_len, layer, id, payload, location, col = -1, -1, -1, -1, -1, -1
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


def decode_readout_v4(self, logger, readout: bytearray, i: int, printer: bool = True, use_negedge_ts: bool = True) -> pd.DataFrame:
    """
    Decode 8byte Frames from AstroPix 4

    :param list_hists: List with all hits

    :returns: Dataframe with decoded hits
    """

    list_hits = []
    hit_list = []

    list_hits, packet_len = prepare_readout(readout)

    for hit in list_hits:
        try:
            pack_len  = int(hit[0])
            layer       = int(hit[1])
            id          = int(hit[2]) >> 3
            payload     = int(hit[2]) & 0b111
            row         = int(hit[3]) >> 3
            col         = ((int(hit[3]) & 0b111) << 2) + (int(hit[4]) >> 6)
            tsneg1      = (int(hit[4]) >> 5) & 0b1
            ts1         = ((int(hit[4]) & 0b11111) << 9) + (int(hit[5]) << 1) + (int(hit[6]) >> 7)
            tsfine1     = (int(hit[6]) >> 4) & 0b111
            tstdc1      = ((int(hit[6]) & 0b1111) << 1) + (int(hit[7]) >> 7)

            tsneg2      = (int(hit[7]) >> 6) & 0b1
            ts2         = ((int(hit[7]) & 0b111111) << 8) + int(hit[8])
            tsfine2     = (int(hit[9]) >> 5) & 0b111
            tstdc2      = int(hit[9]) & 0b11111

            ts1_dec = gray_to_dec((ts1 << 3) + tsfine1) << 1 | (tsneg1 & use_negedge_ts)
            ts2_dec = gray_to_dec((ts2 << 3) + tsfine2) << 1 | (tsneg2 & use_negedge_ts)

            if ts2_dec > ts1_dec:
                tot_total = ts2_dec - ts1_dec
            else:
                tot_total = 2**18 - 1 + ts2_dec - ts1_dec
            tot_us      = (tot_total * self.sampleclock_period_ns)/1000.0
            fpga_ts     = int.from_bytes(hit[10:14], 'little')
        except IndexError:  # hit cut off at end of stream
            pack_len, layer, id, payload, col, row= -1, -1, -1, -1, -1, -1
            ts1, ts2, tsfine1, tsfine2, tsneg1, tsneg2, tstdc1, tstdc2, ts1_dec, ts2_dec, tot_total = -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1
            tot_us, fpga_ts = -1, -1

        # print decoded info in terminal if desiered
        if printer:
            try:
                print(
                    f"{i} Packet len: {pack_len}\t Layer ID: {layer}\n"
                    f"ChipId: {id}\tPayload: {payload}\t"
                    f"Row: {row}\t"
                    f"Col: {col}\t"
                    f"TS1: {ts1_dec}\t"
                    f"TS2: {ts2_dec}\t"
                    f"Total: {tot_total} ({tot_us} us) \n"
                    f"FPGA TS: {fpga_ts}\n"
                )
            except IndexError:
                print(f"HIT TOO SHORT TO BE DECODED - {binascii.hexlify(hit)}")
            except UnboundLocalError:
                print(
                    f"Hit could not be decoded - likely missing a header\n\n"
                    f"{i} Packet len: {pack_len}\t Layer ID: {layer}\n"
                    f"ChipId: {id}\tPayload: {payload}\t"
                    f"Row: {row}\t"
                    f"Col: {col}\t"
                    f"TS1: {ts1_dec}\t"
                    f"TS2: {ts2_dec}\t"
                    f"Total: {tot_total} ({tot_us} us) \n"
                    f"FPGA TS: {fpga_ts}\n"
                )

        # hits are sored in dictionary form
        hits = {
            'readout': i,
            'layer': layer,
            'chipID': id,
            'payload': payload,
            'row': row,
            'col': col,
            'ts1': ts1,
            'ts2': ts2,
            'ts1_fine': tsfine1,
            'ts2_fine': tsfine2,
            'ts1_neg': tsneg1,
            'ts2_neg': tsneg2,
            'ts1_tdc': tstdc1,
            'ts2_tdc': tstdc2,
            'ts1_dec': ts1_dec,
            'ts2_dec': ts2_dec,
            'tot_total': tot_total,
            'tot_us': tot_us,
            'fpga_ts': fpga_ts
        }
        hit_list.append(hits)

    # Much simpler to convert to df in the return statement vs df.concat
    return pd.DataFrame(hit_list)
