from trxas_extract import *
import numpy as np
import sys, os, os.path
import os
import sys
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as msgbox
import os.path
import os, os.path

try:
    import matplotlib
    has_matplotlib=True
except ImportError:
    print('Missing module matplotlib')
    has_matplotlib=False
try:
    from tktooltip import ToolTip
    has_ToolTip=True
except ImportError:
    print('Missing module ToolTip from tktooltip')
    has_ToolTip=False

class G:
    opts = {}

G.file_type=""
def main():
    if not os.path.exists("trxas_extract.py"):
        os.chdir(os.path.dirname(sys.argv[0]))
    if not os.path.exists("trxas_extract.py"):
        print("Missing trxas_extract.py. Run from the script folder.")

    G.window = tk.Tk()
    G.window.title("XTA MXP data process (TRR Group)")
    G.window.resizable(True, True)
    G.window.geometry('800x600')

    frm = tk.Frame(G.window, height=20)
    frm.pack(side=tk.TOP)
    frm1 = tk.Frame(G.window)
    frm1.pack(side=tk.LEFT, padx=10)
    btn_A = tk.Button(frm1, text="Process", command=command_Process)
    btn_A.pack()
    frm = tk.Frame(frm1, height=20)
    frm.pack(side=tk.TOP)
    btn_B = tk.Button(frm1, text="Average", command=command_Average)
    btn_B.pack()

    if has_ToolTip:
        ToolTip(btn_A, msg="Switch to the form to process the data as Energy scan or laserd data")
        ToolTip(btn_B, msg="Switch to the form to average the processed data")

    G.frm_current = None
    frm1 = tk.Frame(G.window, relief='groove', borderwidth=2)
    G.frm_Process = frm1
    frm2 = tk.Frame(frm1)
    frm2.pack(side=tk.TOP, pady=5)
    G.opts['file_in'] = ""
    G.btn_file_in = None
    G.lbl_file_in = None
    G.lbl_file_in_info = None

    def command_file_in():
        G.opts['file_in'] = fd.askopenfilename()
        if G.opts['file_in'] and os.path.exists(G.opts['file_in']):
            G.opts['folder_in'] = os.path.dirname(G.opts['file_in'])
            check_folder(G.opts['folder_in'])
            check_file(G.opts['file_in'])

    frm3 = tk.Frame(frm2, width=30)
    frm3.pack(side=tk.LEFT, padx=20)
    G.btn_file_in = tk.Button(frm3, text="Check Data File", command=command_file_in)
    G.btn_file_in.pack()
    G.lbl_file_in = tk.Label(frm3, text=G.opts['file_in'])
    G.lbl_file_in.pack()
    G.lbl_file_in_info = tk.Label(frm3, text="")
    G.lbl_file_in_info.pack()
    frm2 = tk.Frame(frm1)
    frm2.pack(side=tk.TOP, pady=5)
    G.opts['folder_in'] = ""
    G.btn_folder_in = None
    G.lbl_folder_in = None
    G.lbl_folder_in_info = None

    def command_folder_in():
        G.opts['folder_in'] = fd.askdirectory()
        check_folder(G.opts['folder_in'])
        if G.name:
            check_file(G.opts['file_in'])

    frm3 = tk.Frame(frm2, width=30)
    frm3.pack(side=tk.LEFT, padx=20)
    G.btn_folder_in = tk.Button(frm3, text="Select Input Folder", command=command_folder_in)
    G.btn_folder_in.pack()
    G.lbl_folder_in = tk.Label(frm3, text=G.opts['folder_in'])
    G.lbl_folder_in.pack()
    G.lbl_folder_in_info = tk.Label(frm3, text="")
    G.lbl_folder_in_info.pack()
    frm2 = tk.Frame(frm1)
    frm2.pack(side=tk.TOP, pady=5)
    G.opts['folder_out'] = ""
    G.btn_folder_out = None
    G.lbl_folder_out = None
    G.lbl_folder_out_info = None

    def command_folder_out():
        G.opts['folder_out'] = fd.askdirectory()
        G.lbl_folder_out.config(text=shortname(G.opts['folder_out']))
        G.btn_folder_out.config(text = "Change Output Folder")

    frm3 = tk.Frame(frm2, width=30)
    frm3.pack(side=tk.LEFT, padx=20)
    G.btn_folder_out = tk.Button(frm3, text="Select Output Folder", command=command_folder_out)
    G.btn_folder_out.pack()
    G.lbl_folder_out = tk.Label(frm3, text=G.opts['folder_out'])
    G.lbl_folder_out.pack()
    G.lbl_folder_out_info = tk.Label(frm3, text="")
    G.lbl_folder_out_info.pack()

    frm2 = tk.Frame(frm1)
    frm2.pack(side=tk.TOP, pady=10)
    frm3 = tk.Frame(frm2)
    frm3.pack(side=tk.LEFT, padx=5)
    G.choice_do_poission = tk.IntVar()

    frm4 = tk.Frame(frm3)
    frm4.pack(side=tk.LEFT, padx=20)
    tmp_checkbox = tk.Checkbutton(frm4, variable=G.choice_do_poission, text="Apply Poisson Correction")
    tmp_checkbox.pack()
    G.choice_do_avg_bg = tk.IntVar()

    frm4 = tk.Frame(frm3)
    frm4.pack(side=tk.LEFT, padx=20)
    tmp_checkbox = tk.Checkbutton(frm4, variable=G.choice_do_avg_bg, text="Average C0 Across Orbitals")
    tmp_checkbox.pack()
    G.entry_rep_rate = None
    G.lbl_rep_rate = None

    frm3 = tk.Frame(frm2, width=40)
    frm3.pack(side=tk.LEFT, padx=20)
    G.lbl_rep_rate = tk.Label(frm3, text="Laser Rep-Rate")
    G.lbl_rep_rate.pack()
    G.entry_rep_rate = tk.Entry(frm3, width=15)
    G.entry_rep_rate.pack()
    frm = tk.Frame(frm3, width=20)
    frm.pack(side=tk.LEFT)
    frm2 = tk.Frame(frm1)
    frm2.pack(side=tk.TOP, pady=10)
    G.entry_trigger = None
    G.lbl_trigger = None

    frm3 = tk.Frame(frm2, width=40)
    frm3.pack(side=tk.LEFT, padx=20)
    G.lbl_trigger = tk.Label(frm3, text="Sync bunch number")
    G.lbl_trigger.pack()
    G.entry_trigger = tk.Entry(frm3, width=15)
    G.entry_trigger.pack()
    frm = tk.Frame(frm3, width=20)
    frm.pack(side=tk.LEFT)
    G.entry_range = None
    G.lbl_range = None

    frm3 = tk.Frame(frm2, width=40)
    frm3.pack(side=tk.LEFT, padx=20)
    G.lbl_range = tk.Label(frm3, text="File index range\n(min - max)")
    G.lbl_range.pack()
    G.entry_range = tk.Entry(frm3, width=15)
    G.entry_range.pack()
    frm = tk.Frame(frm3, width=20)
    frm.pack(side=tk.LEFT)
    choices = ['per bunch GS', 'avg bunch GS']
    G.choice_gs_method = tk.StringVar(frm2)
    G.choice_gs_method.set(choices[0])

    frm3 = tk.Frame(frm2, width=40)
    frm3.pack(side=tk.LEFT, padx=20)
    G.lbl_gs_method = tk.Label(frm3, text="Ground State Method\n")
    G.lbl_gs_method.pack()
    tmp_select = tk.OptionMenu(frm3, G.choice_gs_method, *choices)
    tmp_select.pack()
    frm = tk.Frame(frm3, width=20)
    frm.pack(side=tk.LEFT)
    frm2 = tk.Frame(frm1)
    frm2.pack(side=tk.TOP, pady=10)
    G.entry_pre_n_avg = None
    G.lbl_pre_n_avg = None

    frm3 = tk.Frame(frm2, width=40)
    frm3.pack(side=tk.LEFT, padx=20)
    G.lbl_pre_n_avg = tk.Label(frm3, text="Number of orbitals\nfor GS")
    G.lbl_pre_n_avg.pack()
    G.entry_pre_n_avg = tk.Entry(frm3, width=15)
    G.entry_pre_n_avg.pack()
    frm = tk.Frame(frm3, width=20)
    frm.pack(side=tk.LEFT)
    frm3 = tk.Frame(frm2)
    frm3.pack(side=tk.LEFT, padx=2)
    G.subfrm_a = None
    frm4 = tk.Frame(frm3)
    G.subfrm_Energy = frm4
    G.entry_aft_n_avg = None
    G.lbl_aft_n_avg = None

    frm5 = tk.Frame(frm4, width=40)
    frm5.pack(side=tk.LEFT, padx=20)
    G.lbl_aft_n_avg = tk.Label(frm5, text="Number of bunches\nto compress")
    G.lbl_aft_n_avg.pack()
    G.entry_aft_n_avg = tk.Entry(frm5, width=15)
    G.entry_aft_n_avg.pack()
    frm = tk.Frame(frm5, width=20)
    frm.pack(side=tk.LEFT)
    G.entry_aft_npnt = None
    G.lbl_aft_npnt = None

    frm5 = tk.Frame(frm4, width=40)
    frm5.pack(side=tk.LEFT, padx=20)
    G.lbl_aft_npnt = tk.Label(frm5, text="Number of points\nto output")
    G.lbl_aft_npnt.pack()
    G.entry_aft_npnt = tk.Entry(frm5, width=15)
    G.entry_aft_npnt.pack()
    frm = tk.Frame(frm5, width=20)
    frm.pack(side=tk.LEFT)
    frm4 = tk.Frame(frm3)
    G.subfrm_laserd = frm4
    G.entry_num_bunch = None
    G.lbl_num_bunch = None

    frm5 = tk.Frame(frm4, width=40)
    frm5.pack(side=tk.LEFT, padx=20)
    G.lbl_num_bunch = tk.Label(frm5, text="Number of bunches\nto output")
    G.lbl_num_bunch.pack()
    G.entry_num_bunch = tk.Entry(frm5, width=15)
    G.entry_num_bunch.pack()
    frm = tk.Frame(frm5, width=20)
    frm.pack(side=tk.LEFT)
    G.entry_n_pre_bunch = None
    G.lbl_n_pre_bunch = None

    frm5 = tk.Frame(frm4, width=40)
    frm5.pack(side=tk.LEFT, padx=20)
    G.lbl_n_pre_bunch = tk.Label(frm5, text="First num bunches\nnot to compress")
    G.lbl_n_pre_bunch.pack()
    G.entry_n_pre_bunch = tk.Entry(frm5, width=15)
    G.entry_n_pre_bunch.pack()
    frm = tk.Frame(frm5, width=20)
    frm.pack(side=tk.LEFT)

    frm2 = tk.Frame(frm1)
    frm2.pack(side=tk.TOP, pady=10)
    frm3 = tk.Frame(frm2)
    frm3.pack(side=tk.LEFT, padx=20)
    btn = tk.Button(frm3, text="Run", command=command_run)
    btn.pack()
    frm3 = tk.Frame(frm2)
    frm3.pack(side=tk.LEFT, padx=20)
    btn_reset = tk.Button(frm3, text="Reset", command=command_reset)
    btn_reset.pack()
    frm1 = tk.Frame(G.window, relief='groove', borderwidth=2)
    G.frm_Average = frm1

    frm = tk.Frame(frm1, height=20)
    frm.pack(side=tk.TOP)
    frm2 = tk.Frame(frm1)
    frm2.pack(side=tk.TOP, pady=1)
    G.opts['file_avg'] = ""
    G.btn_file_avg = None
    G.lbl_file_avg = None
    G.lbl_file_avg_info = None

    def command_file_avg():
        G.opts['file_avg'] = fd.askopenfilename()
        G.opts['folder_avg'] = os.path.dirname(G.opts['file_avg'])
        G.lbl_folder_avg.config(text=shortname(G.opts['folder_avg']))
        G.btn_folder_avg.config(text = "Change Output Folder")
        str_range = load_txt_range(G.opts['folder_avg'])
        G.entry_avg_range.delete(0, tk.END)
        G.entry_avg_range.insert(0, str_range)

        G.lbl_file_avg.config(text=shortname(G.opts['file_avg']))

    frm3 = tk.Frame(frm2, width=30)
    frm3.pack(side=tk.LEFT, padx=20)
    G.btn_file_avg = tk.Button(frm3, text="Check Data File", command=command_file_avg)
    G.btn_file_avg.pack()
    G.lbl_file_avg = tk.Label(frm3, text=G.opts['file_avg'])
    G.lbl_file_avg.pack()
    G.lbl_file_avg_info = tk.Label(frm3, text="")
    G.lbl_file_avg_info.pack()

    frm2 = tk.Frame(frm1)
    frm2.pack(side=tk.TOP, pady=1)
    G.opts['folder_avg'] = ""
    G.btn_folder_avg = None
    G.lbl_folder_avg = None
    G.lbl_folder_avg_info = None

    def command_folder_avg():
        G.opts['folder_avg'] = fd.askdirectory()
        G.lbl_folder_avg.config(text=shortname(G.opts['folder_avg']))
        G.btn_folder_avg.config(text = "Change Output Folder")
        str_range = load_txt_range(G.opts['folder_avg'])
        G.entry_avg_range.delete(0, tk.END)
        G.entry_avg_range.insert(0, str_range)

    frm3 = tk.Frame(frm2, width=30)
    frm3.pack(side=tk.LEFT, padx=20)
    G.btn_folder_avg = tk.Button(frm3, text="Select Input Folder To Average", command=command_folder_avg)
    G.btn_folder_avg.pack()
    G.lbl_folder_avg = tk.Label(frm3, text=G.opts['folder_avg'])
    G.lbl_folder_avg.pack()
    G.lbl_folder_avg_info = tk.Label(frm3, text="")
    G.lbl_folder_avg_info.pack()

    frm2 = tk.Frame(frm1)
    frm2.pack(side=tk.TOP, pady=1)
    G.entry_avg_range = None
    G.lbl_avg_range = None

    frm3 = tk.Frame(frm2, width=40)
    frm3.pack(side=tk.LEFT, padx=20)
    G.lbl_avg_range = tk.Label(frm3, text="File index range (min - max)")
    G.lbl_avg_range.pack()
    G.entry_avg_range = tk.Entry(frm3, width=15)
    G.entry_avg_range.pack()
    frm = tk.Frame(frm3, width=20)
    frm.pack(side=tk.LEFT)
    btn = tk.Button(frm2, text="Run Average", command=command_avg)
    btn.pack()

    frm = tk.Frame(frm1, height=20)
    frm.pack(side=tk.TOP)
    frm2 = tk.Frame(frm1)
    frm2.pack(side=tk.TOP, pady=1)
    G.opts['file_avg_plot'] = ""
    G.btn_file_avg_plot = None
    G.lbl_file_avg_plot = None
    G.lbl_file_avg_plot_info = None

    def command_file_avg_plot():
        G.opts['file_avg_plot'] = fd.askopenfilename()
        G.lbl_file_avg_plot.config(text = G.opts['file_avg_plot'])

        t = np.loadtxt(G.opts['file_avg_plot'], skiprows=1)
        if t.shape[1] == 2:
            msg = "Laser Delay: %d rows" % t.shape[0]
        else:
            num_bunches = (t.shape[1] - 1) / 2
            msg = "Energy Scan: %d rows, %d bunches" % (t.shape[0], num_bunches)
        G.lbl_file_avg_plot_info.config(text = msg)

    frm3 = tk.Frame(frm2, width=30)
    frm3.pack(side=tk.LEFT, padx=20)
    G.btn_file_avg_plot = tk.Button(frm3, text="Select Avg Data File", command=command_file_avg_plot)
    G.btn_file_avg_plot.pack()
    G.lbl_file_avg_plot = tk.Label(frm3, text=G.opts['file_avg_plot'])
    G.lbl_file_avg_plot.pack()
    G.lbl_file_avg_plot_info = tk.Label(frm3, text="")
    G.lbl_file_avg_plot_info.pack()

    frm2 = tk.Frame(frm1)
    frm2.pack(side=tk.TOP, pady=1)
    G.entry_plot_col = None
    G.lbl_plot_col = None

    frm3 = tk.Frame(frm2, width=40)
    frm3.pack(side=tk.LEFT, padx=20)
    G.lbl_plot_col = tk.Label(frm3, text="Plot Column")
    G.lbl_plot_col.pack()
    G.entry_plot_col = tk.Entry(frm3, width=15)
    G.entry_plot_col.pack()
    frm = tk.Frame(frm3, width=20)
    frm.pack(side=tk.LEFT)
    G.entry_plot_col.delete(0, tk.END)
    G.entry_plot_col.insert(0, "0")
    btn = tk.Button(frm2, text="Plot", command=command_plot)
    btn.pack()

    frm2 = tk.Frame(frm1)
    frm2.pack(side=tk.TOP, pady=1)
    G.frm_Plot = frm2
    G.plt = None

    init_default()
    command_Process()
    G.window.mainloop()

# ---- subroutines --------------------------------------------
def command_Process():
    if G.frm_current:
        G.frm_current.pack_forget()
    G.frm_current = G.frm_Process
    G.frm_current.pack(pady = 5)

def command_Average():
    if G.frm_current:
        G.frm_current.pack_forget()
    G.frm_current = G.frm_Average
    G.frm_current.pack(pady = 5)

def check_folder(folder):
    load_files(folder)
    if G.name:
        G.entry_range.delete(0, tk.END)
        G.entry_range.insert(0, "%s-%s" % (G.idx_min, G.idx_max))
    G.lbl_folder_in.config(text=shortname(folder))
    G.btn_folder_in.config(text = "Change Input Folder")
    G.lbl_folder_in_info.config(text="%d data files" % len(G.files))

def check_file(file):
    G.lbl_file_in.config(text=shortname(file))

    trxas = Extract()
    trxas.read(file)
    msg = "%d channels, %d orbitals, %d bunches, %d rows" % (trxas.c_max-trxas.c_min+1, trxas.o_max-trxas.o_min+1, trxas.b_max-trxas.b_min+1, trxas.num_rows)

    G.lbl_file_in_info.config(text=msg)

    if trxas.type != G.file_type:
        G.file_type = trxas.type
        if G.file_type == "Energy":
            if G.subfrm_a:
                G.subfrm_a.pack_forget()
            G.subfrm_a = G.subfrm_Energy
            G.subfrm_a.pack(side=tk.LEFT)
        else:
            if G.subfrm_a:
                G.subfrm_a.pack_forget()
            G.subfrm_a = G.subfrm_laserd
            G.subfrm_a.pack(side=tk.LEFT)

def shortname(str):
    if len(str) > 100:
        return "..." + str[-100:]
    else:
        return str

def command_run():
    load_form()
    save_opts()

    if RE.match(r'(\d+)-(\d+)', G.opts['range']):
        G.idx_min = int(RE.m.group(1))
        G.idx_max = int(RE.m.group(2))

    if not os.path.exists(G.opts['folder_out']):
        os.makedirs(G.opts['folder_out'])

    count = 0
    for file_in in G.files:
        if RE.match(r'(.*)-(\d+)$', file_in):
            idx = int(RE.m.group(2))
            if idx < G.idx_min or idx > G.idx_max:
                continue
        file_out = get_file_out(file_in)

        trxas = Extract()
        if trxas.read(file_in):
            if G.opts['do_poission']:
                trxas.normalize(float(G.opts['rep_rate']), G.opts['do_avg_bg'])
            else:
                trxas.normalize(0, G.opts['do_avg_bg'])
            if G.file_type == "Energy" and trxas.type == "Energy":
                do_perbunch = not (G.opts['gs_method'] == 'avg bunch GS')
                trxas.process_energy(file_out, int(G.opts['trigger']), int(G.opts['pre_n_avg']), int(G.opts['aft_n_avg']), int(G.opts['aft_npnt']), do_perbunch)
            elif G.file_type == "laserd" and trxas.type == "laserd":
                do_perbunch = not (G.opts['gs_method'] == 'avg bunch GS')
                trxas.process_laserd(file_out, int(G.opts['trigger']), int(G.opts['pre_n_avg']), int(G.opts['num_bunch']), int(G.opts['n_pre_bunch']), do_perbunch)
        count+=1
    msgbox("Processed %d data files in %s\n" % (count, G.opts['folder_out']))

def command_reset():
    reset_default()

def load_txt_range(folder):
    idx_min = '99999'
    idx_max = '00000'
    for file in os.listdir(folder):
        if file.startswith('avg'):
            continue
        if RE.match(r'(.*)-(\d+)\.txt$', file):
            idx = RE.m.group(2)
            if int(idx_min) > int(idx):
                idx_min = idx
            if int(idx_max) < int(idx):
                idx_max = idx
    return "%s-%s" % (idx_min, idx_max)

def command_avg():
    G.opts['avg_range'] = G.entry_avg_range.get()
    if RE.match(r'(\d+)-(\d+)', G.opts['avg_range']):
        idx_min = int(RE.m.group(1))
        idx_max = int(RE.m.group(2))
        count, G.avg_file = Extract.average_output(G.opts['folder_avg'], idx_min, idx_max)
        G.opts['file_avg_plot'] = G.avg_file
        G.lbl_file_avg_plot.config(text = G.opts['file_avg_plot'])

        t = np.loadtxt(G.opts['file_avg_plot'], skiprows=1)
        if t.shape[1] == 2:
            msg = "Laser Delay: %d rows" % t.shape[0]
        else:
            num_bunches = (t.shape[1] - 1) / 2
            msg = "Energy Scan: %d rows, %d bunches" % (t.shape[0], num_bunches)
        G.lbl_file_avg_plot_info.config(text = msg)

def command_plot():
    if has_matplotlib:
        import matplotlib.pyplot as plt
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        matplotlib.use("TkAgg")
    else:
        return

    def get_col():
        col = G.entry_plot_col.get()
        if RE.match(r'b(\d+)-diff', col):
            return int(RE.m.group(1)) * 2 + 2
        elif RE.match(r'b(\d+)$', col):
            return int(RE.m.group(1)) * 2 + 1
        else:
            return 0

    avg_file = G.opts['file_avg_plot']
    t = np.loadtxt(avg_file, skiprows=1)
    figure = Figure(figsize=(5,3), dpi=100)
    G.plt = figure.add_subplot(1, 1, 1)
    G.plt2 = G.plt.twinx()

    G.plot_window = tk.Toplevel(G.window)
    G.plot_window.geometry('1024x768')
    G.plot_window.title("Plot Average Data")

    G.canvas = FigureCanvasTkAgg(figure, G.plot_window)
    G.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=11, pady=10)
    if t.shape[1] == 2:
        G.plot_window.title("Laser Delay - " + avg_file)
        G.plt.set_xlabel('Laser Delay')
        G.plt.set_ylabel('diff', color='tab:blue')
        G.plt2.set_axis_off()

        G.plt.clear()
        G.plt.plot(t[:,0], t[:,1], color='tab:blue')
    else:
        G.plt.set_xlabel('Energy')
        G.plt.set_ylabel('raw', color='tab:blue')
        G.plt2.set_axis_on()
        G.plt2.set_ylabel('diff', color='tab:red')

        col = int(G.entry_plot_col.get())
        G.plot_window.title("Energy Scan - %s - Column %d" % (avg_file, col))

        j = col * 2 + 1
        G.plt.clear()
        G.plt.plot(t[:,0], t[:,j], label='raw', color='tab:blue')
        G.plt2.clear()
        G.plt2.plot(t[:,0], t[:,j+1], label='diff', color='tab:red')

    G.canvas.draw()

def init_default():
    load_opts()
    if 'trigger' in G.opts:
        G.entry_trigger.delete(0, tk.END)
        G.entry_trigger.insert(0, G.opts["trigger"])
    if 'range' in G.opts:
        G.entry_range.delete(0, tk.END)
        G.entry_range.insert(0, G.opts["range"])
    if 'pre_n_avg' in G.opts:
        G.entry_pre_n_avg.delete(0, tk.END)
        G.entry_pre_n_avg.insert(0, G.opts["pre_n_avg"])
    if 'aft_n_avg' in G.opts:
        G.entry_aft_n_avg.delete(0, tk.END)
        G.entry_aft_n_avg.insert(0, G.opts["aft_n_avg"])
    if 'aft_npnt' in G.opts:
        G.entry_aft_npnt.delete(0, tk.END)
        G.entry_aft_npnt.insert(0, G.opts["aft_npnt"])
    if 'num_bunch' in G.opts:
        G.entry_num_bunch.delete(0, tk.END)
        G.entry_num_bunch.insert(0, G.opts["num_bunch"])
    if 'rep_rate' in G.opts:
        G.entry_rep_rate.delete(0, tk.END)
        G.entry_rep_rate.insert(0, G.opts["rep_rate"])
    if 'n_pre_bunch' in G.opts:
        G.entry_n_pre_bunch.delete(0, tk.END)
        G.entry_n_pre_bunch.insert(0, G.opts["n_pre_bunch"])
    if 'do_poission' in G.opts:
        G.choice_do_poission.set(G.opts["do_poission"])
    if 'do_avg_bg' in G.opts:
        G.choice_do_avg_bg.set(G.opts["do_avg_bg"])
    if 'gs_method' in G.opts:
        G.choice_gs_method.set(G.opts["gs_method"])

    if G.opts['folder_in'] and os.path.exists(G.opts['folder_in']):
        check_folder(G.opts['folder_in'])
        if G.name:
            check_file(G.opts['file_in'])

    if G.opts['folder_out'] and os.path.exists(G.opts['folder_out']):
        G.lbl_folder_out.config(text=shortname(G.opts['folder_out']))
        G.btn_folder_out.config(text = "Change Output Folder")

def load_files(folder_in):
    G.idx_min = '99999'
    G.idx_max = '00000'
    G.name = None
    G.files = []
    for root, dirs, files in os.walk(folder_in):
        for name in files:
            if RE.match(r'(.*)-(\d+)$', name):
                filepath = os.path.join(root, name)
                idx = RE.m.group(2)

                if not G.name and Extract.is_sample_data(filepath):
                    if not G.opts['file_in']:
                        G.opts['file_in'] = filepath
                    if RE.match(r'(.*)-\d+$', name):
                        G.name = RE.m.group(1)

                G.files.append(filepath)
                if int(G.idx_min) > int(idx):
                    G.idx_min = idx
                if int(G.idx_max) < int(idx):
                    G.idx_max = idx

def load_form():
    G.opts['trigger'] = G.entry_trigger.get()
    G.opts['range'] = G.entry_range.get()
    G.opts['pre_n_avg'] = G.entry_pre_n_avg.get()
    G.opts['aft_n_avg'] = G.entry_aft_n_avg.get()
    G.opts['aft_npnt'] = G.entry_aft_npnt.get()
    G.opts['num_bunch'] = G.entry_num_bunch.get()
    G.opts['rep_rate'] = G.entry_rep_rate.get()
    G.opts['n_pre_bunch'] = G.entry_n_pre_bunch.get()
    G.opts['do_poission'] = G.choice_do_poission.get()
    G.opts['do_avg_bg'] = G.choice_do_avg_bg.get()
    G.opts['gs_method'] = G.choice_gs_method.get()

def save_opts():
    f = open("config", "w")
    for k in G.opts:
        f.write("%s: %s\n" % (k, G.opts[k]))
    f.close()

def get_file_out(file_in):
    return os.path.join(G.opts['folder_out'], os.path.basename(file_in) + '.txt')

def msgbox(msg):
    tk.messagebox.showinfo(message=msg)

def reset_default():
    G.opts = {'n_pre_bunch':1, 'folder_in':'', 'folder_out':''}
    if os.path.exists("config"):
        os.remove("config")
    if 'trigger' in G.opts:
        G.entry_trigger.delete(0, tk.END)
        G.entry_trigger.insert(0, G.opts["trigger"])
    if 'range' in G.opts:
        G.entry_range.delete(0, tk.END)
        G.entry_range.insert(0, G.opts["range"])
    if 'pre_n_avg' in G.opts:
        G.entry_pre_n_avg.delete(0, tk.END)
        G.entry_pre_n_avg.insert(0, G.opts["pre_n_avg"])
    if 'aft_n_avg' in G.opts:
        G.entry_aft_n_avg.delete(0, tk.END)
        G.entry_aft_n_avg.insert(0, G.opts["aft_n_avg"])
    if 'aft_npnt' in G.opts:
        G.entry_aft_npnt.delete(0, tk.END)
        G.entry_aft_npnt.insert(0, G.opts["aft_npnt"])
    if 'num_bunch' in G.opts:
        G.entry_num_bunch.delete(0, tk.END)
        G.entry_num_bunch.insert(0, G.opts["num_bunch"])
    if 'rep_rate' in G.opts:
        G.entry_rep_rate.delete(0, tk.END)
        G.entry_rep_rate.insert(0, G.opts["rep_rate"])
    if 'n_pre_bunch' in G.opts:
        G.entry_n_pre_bunch.delete(0, tk.END)
        G.entry_n_pre_bunch.insert(0, G.opts["n_pre_bunch"])
    if 'do_poission' in G.opts:
        G.choice_do_poission.set(G.opts["do_poission"])
    if 'do_avg_bg' in G.opts:
        G.choice_do_avg_bg.set(G.opts["do_avg_bg"])
    if 'gs_method' in G.opts:
        G.choice_gs_method.set(G.opts["gs_method"])

    if G.opts['folder_in'] and os.path.exists(G.opts['folder_in']):
        check_folder(G.opts['folder_in'])
        if G.name:
            check_file(G.opts['file_in'])

    if G.opts['folder_out'] and os.path.exists(G.opts['folder_out']):
        G.lbl_folder_out.config(text=shortname(G.opts['folder_out']))
        G.btn_folder_out.config(text = "Change Output Folder")

def load_opts():
    if os.path.exists("config"):
        with open("config") as In:
            for l in In:
                if RE.match(r'(\w+):\s*(.*)', l):
                    G.opts[RE.m.group(1)] = RE.m.group(2)
    if 'n_pre_bunch' not in G.opts:
        G.opts['n_pre_bunch'] = 1

# ---------------------------------------------------------
if __name__ == "__main__":
    main()
