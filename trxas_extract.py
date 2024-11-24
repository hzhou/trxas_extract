import re
import os, os.path
import os
import math
import numpy as np

class RE:
    m = None
    def match(pat, str, flags=0):
        RE.m = re.match(pat, str, flags)
        return RE.m
    def search(pat, str, flags=0):
        RE.m = re.search(pat, str, flags)
        return RE.m

class Extract:
    def is_sample_data(file):
        f = open(file, 'r')
        line = f.readline()
        if re.match(r'#F \S+$', line):
            return True
        else:
            return False

    def average_output(folder, idx_min, idx_max):
        def get_header(file):
            f = open(file, 'r')
            header = f.readline()
            f.close()
            return header.rstrip()

        header_line = None
        data = []
        for filename in os.listdir(folder):
            if filename.startswith('avg'):
                continue
            m = re.match(r'.*-(\d+)\.txt$', filename)
            if m and int(m.group(1)) >= idx_min and int(m.group(1)) <= idx_max:
                file = os.path.join(folder, filename)
                if not header_line:
                    header_line = get_header(file)
                data.append(np.loadtxt(file, skiprows=1))
        t = np.mean(data, axis=0)
        file_out = os.path.join(folder, "avg-%d-%d.txt" % (idx_min, idx_max))
        np.savetxt(file_out, t, header=header_line, fmt='%.6f', comments='')

        return (len(data), file_out)
        return "Averaging %d data files -> %s" % (len(data), file_out)

    def read(self, file):
        print("reading %s ..." % file)
        self.type = None
        header = None
        rows = []
        with open(file) as f:
            for line in f:
                if line.startswith('#L '):
                    header = line[3:]
                    if re.match(r'#L .* Energy ', line):
                        self.type = "Energy"
                    elif re.match(r'#L .* laserd ', line):
                        self.type = "laserd"
                    else:
                        print("  file unrecognized: %s, header: %s..." % (file, line[0:20]))
                        return False
                elif re.match(r'\d.*', line) and header:
                    rows.append(line)
        if not rows:
            print("  file empty")
            return False
        self.cols = header.split()
        self.idxs = {}
        self.c_min = 999
        self.c_max = 0
        self.o_min = 999
        self.o_max = 0
        self.b_min = 999
        self.b_max = 0

        for i, col in enumerate(self.cols):
            if RE.match(r'c(\d+)o(\d+)b(\d+)', col):
                self.c_max = max(self.c_max, int(RE.m.group(1)))
                self.c_min = min(self.c_min, int(RE.m.group(1)))
                self.o_max = max(self.o_max, int(RE.m.group(2)))
                self.o_min = min(self.o_min, int(RE.m.group(2)))
                self.b_max = max(self.b_max, int(RE.m.group(3)))
                self.b_min = min(self.b_min, int(RE.m.group(3)))
            self.idxs[col] = i

        self.c_jump = self.idxs['c1o0b0'] - self.idxs['c0o0b0']
        self.o_jump = self.b_max+1
        self.num_channel = self.c_max + 1
        self.num_bunches = self.b_max + 1
        self.num_orbital = self.o_max
        if not (self.c_min==0):
            print(" check failed for file for self.c_min==0 file: %s" % file)
            return False
        if not (self.o_min==0):
            print(" check failed for file for self.o_min==0 file: %s" % file)
            return False
        if not (self.b_min==0):
            print(" check failed for file for self.b_min==0 file: %s" % file)
            return False
        if not (self.c_max>=2):
            print(" check failed for file for self.c_max>=2 file: %s" % file)
            return False
        if not (self.idxs['c0o0b0']):
            print(" check failed for file for self.idxs['c0o0b0'] file: %s" % file)
            return False
        if not (self.idxs['c1o0b0']):
            print(" check failed for file for self.idxs['c1o0b0'] file: %s" % file)
            return False
        self.num_cols = len(rows[0].split())
        self.num_rows = len(rows)
        self.data = np.empty([self.num_rows, self.num_cols], dtype = np.float64)
        for i, l in enumerate(rows):
            for j, t in enumerate(l.split()):
                self.data[i, j] = float(t)
        return True

    def normalize(self, max_count=0, do_avg_bg=True):
        i0 = self.idxs['c0o0b0']
        i1 = self.idxs['c1o0b0']
        i2 = self.idxs['c2o0b0']
        if max_count > 0:
            for i in range(self.num_rows):
                i_sec = self.idxs['Seconds']
                for j in range(i0,self.num_cols):
                    P1 = self.data[i,j] / (max_count * self.data[i,i_sec])
                    self.data[i,j] = -math.log(1.0 - P1)
        for i in range(1,self.num_rows):
            if do_avg_bg:
                avgs = []
                for j in range(self.num_bunches):
                    sum = 0.0
                    for k in range(self.num_orbital):
                        sum += self.data[i, i0 + k * self.num_bunches + j]
                    avgs.append(sum / self.num_orbital)
                for j in range(self.num_bunches * self.num_orbital):
                    self.data[i, i1 + j] /= avgs[j % self.num_bunches]
                    self.data[i, i2 + j] /= avgs[j % self.num_bunches]
            else:
                for j in range(self.num_bunches * self.num_orbital):
                    self.data[i, i1 + j] /= self.data[i, i0 + j]
                    self.data[i, i2 + j] /= self.data[i, i0 + j]
        self.normalized = True

    def process_energy(self, fileout, trig, pre_n_avg, aft_n_avg, n_pnt, do_perbunch=True):
        header_cols = []
        if self.type != "Energy":
            raise Exception("Expect Energy scan, but the file is %s scan." % self.type)

        extra_cols = []
        extra_cols.append("Energy")
        header_cols.extend(extra_cols)

        for j in range(n_pnt):
            header_cols.append("b%d" % j)
            header_cols.append("b%d-diff" % j)
        data_out = np.empty([self.num_rows, len(header_cols)])

        num_extra = len(extra_cols)
        for i, col in enumerate(extra_cols):
            data_out[:, i] = self.data[:, self.idxs[col]]

        for i_row in range(self.num_rows):
            row_in = self.data[i_row,:]
            back12 = []

            for i in range(self.o_jump):
                (t1, t2, t12) = (0, 0, 0)
                i0 = self.idxs['c0o0b0'] + trig + i
                for j in range(pre_n_avg):
                    t1+=row_in[i0 - (j+1) * self.o_jump+self.c_jump]
                    t2+=row_in[i0 - (j+1) * self.o_jump+self.c_jump*2]
                t1 /= pre_n_avg
                t2 /= pre_n_avg
                t12=(t1+t2)/2

                back12.append(t12)

            if not do_perbunch:
                back12_avg = np.mean(back12)

            row_out = data_out[i_row,num_extra:]
            for j in range(n_pnt):
                a12 = 0
                adiff = 0
                i0 = self.idxs['c0o0b0'] + trig + j*aft_n_avg
                for i in range(aft_n_avg):
                    t1=row_in[i0 + i+self.c_jump]
                    t2=row_in[i0 + i+self.c_jump*2]
                    t12=(t1+t2)/2
                    if do_perbunch:
                        diff = t12 - back12[(j * aft_n_avg + i) % self.o_jump]
                    else:
                        diff = t12 - back12_avg
                    a12+=t12
                    adiff+=diff

                a12/=aft_n_avg
                adiff/=aft_n_avg

                row_out[j*2] = a12
                row_out[j*2 + 1] = adiff

        self.data_out = data_out
        if fileout:
            np.savetxt(fileout, data_out, header=' '.join(header_cols), fmt='%.6f', comments='')

    def process_laserd(self, fileout, trig, pre_n_avg, n_bunch, n_pre_bunch=1, do_perbunch=True):
        header_cols = []
        if self.type != "laserd":
            raise Exception("Expect laserd scan, but the file is %s scan." % self.type)

        header_cols.append("diff")
        N = self.num_rows * n_pre_bunch + n_bunch - n_pre_bunch
        data_out = np.empty([N, len(header_cols)])

        for i_row in range(self.num_rows):
            row_in = self.data[i_row,:]
            back12 = []

            for i in range(self.o_jump):
                (t1, t2, t12) = (0, 0, 0)
                i0 = self.idxs['c0o0b0'] + trig + i
                for j in range(pre_n_avg):
                    t1+=row_in[i0 - (j+1) * self.o_jump+self.c_jump]
                    t2+=row_in[i0 - (j+1) * self.o_jump+self.c_jump*2]
                t1 /= pre_n_avg
                t2 /= pre_n_avg
                t12=(t1+t2)/2

                back12.append(t12)

            if not do_perbunch:
                back12_avg = np.mean(back12)
            bunch_spacing = 3681.23 / self.o_jump
            i_d = self.idxs['laserd']
            i0 = self.idxs['c0o0b0'] + trig
            for j in range(n_pre_bunch):
                t1=row_in[i0+j+self.c_jump]
                t2=row_in[i0+j+self.c_jump*2]
                t12=(t1+t2)/2
                if do_perbunch:
                    diff = t12 - back12[j % self.o_jump]
                else:
                    diff = t12 - back12_avg
                t = -(row_in[i_d] - j * bunch_spacing)
                i2 = self.num_rows * j + i_row
                data_out[i2, 0] = t
                data_out[i2, 1] = diff
            for j in range(n_pre_bunch,n_bunch):
                t1=row_in[i0+j+self.c_jump]
                t2=row_in[i0+j+self.c_jump*2]
                t12=(t1+t2)/2
                if do_perbunch:
                    diff = t12 - back12[j % self.o_jump]
                else:
                    diff = t12 - back12_avg
                t = -(row_in[i_d] - j * bunch_spacing)
                i2 = self.num_rows * n_pre_bunch + (j - n_pre_bunch)
                if i_row == 0:
                    data_out[i2, 0] = t / self.num_rows
                    data_out[i2, 1] = diff / self.num_rows
                else:
                    data_out[i2, 0] += t / self.num_rows
                    data_out[i2, 1] += diff / self.num_rows

        self.data_out = data_out
        if fileout:
            np.savetxt(fileout, data_out, header=' '.join(header_cols), fmt='%.6f', comments='')

def main():
    t = Extract()
    t.read("laserd/11022024-full-00237")
    print("  %s cols, %s rows, %s channels, %s bunches, %s orbitals" % (t.num_cols, t.num_rows, t.num_channel, t.num_bunches, t.num_orbital))
    t.process_simple('data/simple.out')

# ---------------------------------------------------------
if __name__ == "__main__":
    main()
