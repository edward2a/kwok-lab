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

    with dpg.window(tag="primary", no_saved_settings=True):
        dpg.set_primary_window("primary", True)

        # Window menu
        with dpg.menu_bar():
            with dpg.menu(label='Workloads'):
                dpg.add_menu_item(label='Load...')

            with dpg.menu(label='Kubernetes'):
                dpg.add_menu_item(label='Initialize')
                dpg.add_menu_item(label='Terminate')

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

            dpg.add_button(label="I'm a button")

    dpg.create_viewport()
    dpg.setup_dearpygui()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        # Loop tasks

        # Render
        dpg.render_dearpygui_frame()

    dpg.destroy_context()


if __name__ == '__main__':
    # Vertical sync (limit FPS)
    # Commented due to segfault in dev environment
    #dpg.set_viewport_vsync(True)

    main()
