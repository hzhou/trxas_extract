from trxas_extract import *
import os.path
import os

class G:
    opts = {}

G.file_type = ""
def main():
    pass

# ---- subroutines --------------------------------------------
def check_file(file):
    if not file or not os.path.exists(file):
        print("File not found? [%s]" % file)
        return
    trxas = Extract()
    trxas.read(file)
    assert trxas.c_min == 0
    assert trxas.o_min == 0
    assert trxas.b_min == 0
    G.type = trxas.type
    G.num_channel = trxas.num_channel
    G.num_bunches = trxas.num_bunches
    G.num_orbital = trxas.num_orbital
    G.num_rows = trxas.num_rows

    if RE.match(r'(.*)-\d+$', os.path.basename(file)):
        G.folder = os.path.dirname(file)
        G.name = RE.m.group(1)

        load_files(G.folder)

def extract_all():
    if not G.folder or not os.path.exists(G.folder):
        print("Run check_file() first.")
        return

    folder_out = G.output_folder
    if not os.path.exists(folder_out):
        os.makedirs(folder_out)

    count = 0
    for file_in in G.files:
        if RE.match(r'(.*)-(\d+)$', file_in):
            idx = int(RE.m.group(2))
            if idx < G.idx_min or idx > G.idx_max:
                continue
        file_out = os.path.join(folder_out, os.path.basename(file_in) + '.txt')

        trxas = Extract()
        if trxas.read(file_in):
            if G.opts['do_poission']:
                trxas.normalize(float(G.opts['rep_rate']))
            else:
                trxas.normalize()
            if G.type == "Energy" and trxas.type == "Energy":
                do_perbunch = not (G.opts['gs_method'] == 'avg bunch GS')
                trxas.process_energy(file_out, int(G.opts['trigger']), int(G.opts['pre_n_avg']), int(G.opts['aft_n_avg']), int(G.opts['aft_npnt']), do_perbunch)
            elif G.type == "laserd" and trxas.type == "laserd":
                do_perbunch = not (G.opts['gs_method'] == 'avg bunch GS')
                trxas.process_laserd(file_out, int(G.opts['trigger']), int(G.opts['pre_n_avg']), int(G.opts['num_bunch']), int(G.opts['n_pre_bunch']), do_perbunch)
            else:
                print("ignoring %s, type mismatch: %s != %s" % (G.type, trxas.type))
        count+=1
    print("Processed %d data files in %s\n" % (count, folder_out))

def load_files(folder_in):
    G.idx_min = 99999
    G.idx_max = 0
    G.files = []
    for root, dirs, files in os.walk(folder_in):
        for name in files:
            if RE.match(r'(.*)-(\d+)$', name):
                filepath = os.path.join(root, name)
                idx = int(RE.m.group(2))

                G.files.append(filepath)
                if G.idx_min > idx:
                    G.idx_min = idx
                if G.idx_max < idx:
                    G.idx_max = idx

# ---------------------------------------------------------
if __name__ == "__main__":
    main()
