#! /usr/bin/env python3
import dearpygui.dearpygui as dpg
#import UltraDict.UltraDict as udict

from multiprocessing import Queue
from multiprocessing import Process
from time import sleep

global workloads
global wl_idx
global wl_settings

workloads = 0
wl_idx = 0
wl_settings = {}

def debugprint():
    print(f"button pressed!")

def debugmsg():
    q_command.put({'action': None, 'msg': 'Hi from the DPG!'})

def add_workload():
    global workloads
    global wl_idx
    global wl_settings

    workloads += 1
    wl_idx += 1
    wl_settings[f"workload-{wl_idx}"] = {"D": 0, "P": 0, "R": 0}

    with dpg.table_row(parent="table", tag=f"workload-{wl_idx}"):

        # Row column 1
        with dpg.table_cell():
            with dpg.group(horizontal=True):
                dpg.add_text(f"workload {wl_idx}")
                dpg.add_button(label="-",
                               width=30,
                               user_data=wl_idx,
                               callback=del_pod)
                dpg.add_input_text(default_value="0",
                                   width=30,
                                   tag=f"wl-{wl_idx}-desired",
                                   decimal=True,
                                   user_data=wl_idx,
                                   on_enter=True,
                                   callback=set_pod)
                dpg.add_button(label="+", width=30,
                               user_data=wl_idx,
                               callback=add_pod)

        # Row column 2
        with dpg.table_cell():
            dpg.add_text(wl_settings[f"workload-{wl_idx}"]["P"], tag=f"wl-{wl_idx}-pending")

        # Row column 3
        with dpg.table_cell():
            dpg.add_text(wl_settings[f"workload-{wl_idx}"]["R"], tag=f"wl-{wl_idx}-running")
    # TODO: kubernetes add deployment

def del_workload():
    global workloads
    global wl_idx
    global wl_settings

    if workloads == 0:
        return

    wl_del = int(list(wl_settings)[-1].split('-')[-1])
    dpg.delete_item(f"workload-{wl_del}")
    del(wl_settings[f"workload-{wl_del}"])
    workloads -= 1
    # TODO: kubernetes remove deployment

def add_pod(sender, app_data, user_data):
    global wl_settings
    wl_settings[f"workload-{user_data}"]["D"] += 1
    dpg.set_value(f"wl-{user_data}-desired", wl_settings[f"workload-{user_data}"]["D"])
    # TODO: kubernetes scale workload

def del_pod(sender, app_data, user_data):
    global wl_settings
    if wl_settings[f"workload-{user_data}"]["D"] == 0:
        return
    wl_settings[f"workload-{user_data}"]["D"] -= 1
    dpg.set_value(f"wl-{user_data}-desired", wl_settings[f"workload-{user_data}"]["D"])
    # TODO: kubernetes scale workload

def set_pod(sender, app_data, user_data):
    global wl_settings
    wl_settings[f"workload-{user_data}"]["D"] = int(app_data)
    # TODO: kubernetes scale workload

def process_message(msg):
    print(msg)

def gui_main(q_gui, q_command):
    # Vertical sync (limit FPS)
    # Commented due to segfault in dev environment
    #dpg.set_viewport_vsync(True)

    #shm_gui = udict({'msgs': [], 'queued': False}, auto_unlink=True)
    #shm_worker = udict({'msgs': [], 'queued': False}, auto_unlink=True)
    dpg.create_context()

    with dpg.window(tag="primary", no_saved_settings=True):
        dpg.set_primary_window("primary", True)

        # Window menu
        with dpg.menu_bar():
            with dpg.menu(label='Workers'):
                dpg.add_menu_item(label='Start')
                dpg.add_menu_item(label='Stop')

            with dpg.menu(label='Workloads'):
                dpg.add_menu_item(label='Load...')

        # Workloads table
        with dpg.group(horizontal=True):

            with dpg.table(tag="table",
                           header_row=True,
                           borders_outerH=False,
                           borders_outerV=False,
                           borders_innerV=True,
                           borders_innerH=True,
                           row_background=True,
                           resizable=False,
                           width=400):

                dpg.add_table_column(label="WORKLOADS (DESIRED)", init_width_or_weight=336)
                dpg.add_table_column(label="PEN", init_width_or_weight=32)
                dpg.add_table_column(label="RUN", init_width_or_weight=32)

                with dpg.table_row(height=30):
                    with dpg.table_cell():
                        with dpg.group(horizontal=True):
                            workloads = 0
                            dpg.add_button(label="-", width=90, height=30,
                                           callback=del_workload, user_data=workloads)
                            dpg.add_button(label="+", width=90, height=30,
                                           callback=add_workload, user_data=workloads)

            dpg.add_button(label="I'm a button", callback=debugmsg)

    dpg.create_viewport()
    dpg.setup_dearpygui()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        # Loop tasks
        while not q_gui.empty():
            process_message(q_gui.get_nowait())
        # Render
        dpg.render_dearpygui_frame()

    dpg.destroy_context()

class K8sWorker(object):
    def init_client(self):
        self.core = kubernetes.client.CoreV1Api()

class PollWorker(Process, K8sWorker):
    def __init__(self, q_gui):
        self.q_gui = q_gui
        super().__init__()

    def run(self):
        __run = True

        while __run:
            try:
                q_gui.put({'msg': 'Hello, world!', 'src': 'poll'})
                sleep(5)
            except Exception as e:
                print(e, e.reason)
                break

class EventWorker(Process, K8sWorker):
    def __init__(self, q_gui):
        self.q_gui = q_gui
        super().__init__()

    def run(self):
        __run = True

        while __run:
            try:
                q_gui.put({'msg': 'Hello, world!', 'src': 'event'})
                sleep(5)
            except Exception as e:
                print(e, e.reason)
                break

class CommandWorker(Process, K8sWorker):
    def __init__(self, q_command, q_gui):
        self.q_command = q_command
        self.q_gui = q_gui
        super().__init__()

    def run(self):
        __run = True

        while __run:
            try:
                msg = q_command.get()
                if msg['action'] == 'stop':
                    __run == False
                else:
                    q_gui.put({'t': 'log', 'lvl': 'info', 'msg': msg, 'src': 'command'})

            except Exception as e:
                print(e, e.reason)


class Main(object):
    def __init__(self):
        self.q_gui = Queue()
        self.q_command = Queue()

        self.evt_worker = EventWorker(self.q_gui)
        self.cmd_worker = CommandWorker(self.q_command, self.q_gui)
        self.pll_worker = PollWorker(self.q_gui)

        gui_main(self.q_gui, self.q_command)

    def start(self):
        evt_worker.start()
        cmd_worker.start()
        pll_worker.start()

    def stop(self):
        q_command.put({'action': 'stop'})
        sleep(0.2)

        q_command.close()
        q_command.join_thread()
        q_gui.close()
        q_gui.join_thread()

        cmd_worker.terminate()
        cmd_worker.join()
        cmd_worker.close()

        evt_worker.terminate()
        evt_worker.join()
        evt_worker.close()

        pll_worker.terminate()
        pll_worker.join()
        pll_worker.close()

if __name__ == '__main__':
    Main()
