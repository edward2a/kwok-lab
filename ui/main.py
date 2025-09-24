#! /usr/bin/env python3
import dearpygui.dearpygui as dpg

global workloads
global wl_idx
global wl_settings

workloads = 0
wl_idx = 0
wl_settings = {}

def debugprint():
    print(f"button pressed!")

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

def main():
    dpg.create_context()

    with dpg.window(tag="primary"):
        dpg.set_primary_window("primary", True)

        with dpg.group(horizontal=True):

            with dpg.table(tag="table",
                           header_row=True,
                           borders_outerH=False,
                           borders_outerV=False,
                           borders_innerV=True,
                           borders_innerH=True,
                           row_background=True,
                           resizable=True,
                           width=600):

                dpg.add_table_column(label="WORKLOADS (DESIRED)", width=200)
                dpg.add_table_column(label="PENDING", width=50)
                dpg.add_table_column(label="RUNNING", width=50)

                with dpg.table_row(height=30):
                    with dpg.table_cell():
                        with dpg.group(horizontal=True):
                            workloads = 0
                            dpg.add_button(label="-", width=90, height=30,
                                           callback=del_workload, user_data=workloads)
                            dpg.add_button(label="+", width=90, height=30,
                                           callback=add_workload, user_data=workloads)

            dpg.add_button(label="I'm a button")

    dpg.create_viewport()
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == '__main__':
    main()
