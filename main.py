import streamlit as st
import pandas as pd
import time
import os
import json
import tkinter as tk
from tkinter import filedialog
from pdf_extractor import extract_txt_list  # Daniel's script
# from extract_fields import main as extract  #Austin's script
from export_data import main as export_td




# function to show native file system - completed
def select_folder():
    root = tk.Tk()
    root.wm_attributes('-topmost', 1)
    root.withdraw()
    folder_path = filedialog.askdirectory(master=root)
    root.destroy()
    return folder_path
    
# function to list all folders and files (file tree)
def list_files(startpath):
    
    # initialise unique key for checkboxes
    unique_key = 0
    selected = []

    for root, dirs, files in os.walk(startpath):    # os.walk returns tuple(str parent path, list of subdirs, list of filenames only)

        # indicates file level (root, subfolder, subsubfolder, ......); returns int
        level = root.replace(startpath, '').count(os.sep)

        # folder indents based on level
        indent = ' ─ ' * (level)

        # file indents
        subindent = ' ─ ' * (level)


        # print parent folder
        if level == 0:  # level 0 is the parent dir
            st.write(":file_folder: " + os.path.basename(root))

        else:
            # st.write("|" + indent + " :file_folder: " + os.path.basename(root))
            st.write(f"├{indent} :file_folder: {os.path.basename(root)}")


        # print files
        for f in files:
            unique_key += 1

            # check to ensure that file ends with .pdf
            if f.endswith(".pdf") or f.endswith(".docx"):
                # select = st.checkbox(subindent + ":page_facing_up: " + f, key=unique_key)
                # select = st.checkbox("└──" + subindent + f, key=unique_key)
                select = st.checkbox(f"└{subindent} :page_facing_up: {f}", key=unique_key)

                if select:
                    file_path = os.path.join(root, f)   # get full file path
                    normalised = os.path.normpath(file_path)    # standardise backslashes since os.walk() slashes are inconsistent
                    selected.append(normalised)

    return selected

# load data into Pandas DataFrame --> takes in dictionary retrieved from json file
def show_td_table():

    # retrieve values from json file
    def get_json_output():

        output = {}

        # Opening JSON file
        f = open('./output.json')
        
        # returns JSON object as a dictionary
        data = json.load(f)
        
        # key - field name; value - field value
        for i in range(len(data)):
            output[data[i]["column_name"]] = data[i]["answer"]
        
        # Closing file
        f.close()

        return output   # returns dict
    
    output = get_json_output()



    subsection = list(output.keys())     # col 1
    extracted_info = list(output.values())   # col 2
    selection = []      # col3
    for i in enumerate(subsection):
        selection.append(False)
    file_location = ""
    

    # column : values
    d = {"Sub-Section": subsection, 
         "Extracted Data Points": extracted_info, 
         "Selection": selection, 
         "File Location": file_location}
    df = (pd.DataFrame(data=d)).explode("Extracted Data Points")    # allows file to output lists

    return df





def run_sidebar():

    try:

        # open css file
        with open(r'./styles/style.css') as f:
            css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

    # =======================================================================================

        # Inside sidebar
        with st.sidebar:

            # initialise session states
            selected_folder_path = st.session_state.get("folder_path", None)
            if 'show' not in st.session_state:
                st.session_state.show = False
            if 'checked' not in st.session_state:
                st.session_state.checked = False

            # set project name
            if selected_folder_path == None:
                project_name = "New Project"
            else:
                project_name = os.path.basename(selected_folder_path)
                
            # project name display
            st.markdown(f'''
                        <div class='margin-bottom bg_blue border'>
                            <h3 class='margin-top bg_blue'>{project_name}</h3>
                        </div>
                        ''', unsafe_allow_html=True)

            # layout columns
            buttoncol1, buttoncol2, buttoncol3 = st.columns([0.5, 0.5, 0.5], gap="small")

            # Button - Select folder
            with buttoncol1:    

                # initialise button
                folder_select_button = st.button(":heavy_plus_sign: Select folder")
                
                if folder_select_button:
                    selected_folder_path = select_folder()      # folder popup
                    st.session_state.folder_path = selected_folder_path     # save folder path in session state
                    st.rerun()      # ensures that project name is populated
                

            # display file tree
            if selected_folder_path != None:

                # get list of selected files for processing
                selected_files = list_files(selected_folder_path)

                if selected_files:
                    st.session_state.checked = True
                
                else:
                    st.session_state.checked = False


            # Button - Filter files
            with buttoncol2:
                st.button(":arrow_down_small: Filter files")


            # Button - Extract details
            with buttoncol3:
                extract_details = st.button(":outbox_tray: Extract details")

                if extract_details:
                    st.session_state.show = True

                    if st.session_state.checked == False:
                        st.session_state.show = False
                        st.toast("Please open a folder and select files you want to process.")

            
    # =======================================================================================

        # check if files are selected and Extract button is clicked
        if st.session_state.checked and st.session_state.show:


            # pass list of files to main to extract text files - output txt files generated, returns list of txt files in curdir
            extract_txt_list(selected_files)

            # pass list of txt files for field extraction - outputs json
            # fields_extract = extract()
            # if fields_extract:
            #     print("- question ans finished -")
            

            header = "TD ASSESSMENT [Tool Ver.]"
            st.markdown(f'''
                        <div class='margin-bottom bg_blue border'>
                            <h5>{header}</h5>
                        </div>
                        ''', unsafe_allow_html=True)
            


            with st.container(border=True):
                # show Pandas DF with fields
                df = show_td_table()
                edited_df = st.data_editor(
                                df, 
                                column_config={
                                "Selection": st.column_config.CheckboxColumn(
                                    "Selection",
                                    default=False
                                )},
                                hide_index=True, 
                                disabled=["Sub-Section"], 
                                use_container_width=True)  # can be edited
            
            subcol1, subcol3, subcol4 = st.columns([0.3, 1, 0.2])
            with subcol1:
                st.write("Progress bar: ")
            
                progress = "37%"
                progress_text = f"Progress: {progress}"
                my_bar = st.progress(0, text=progress_text)

                for percent_complete in range(37):
                    time.sleep(0.01)
                    my_bar.progress(percent_complete + 1, text=progress_text)

            # with subcol2:

            with subcol3:
                st.empty()

            with subcol4:

                # Specify the file name
                filename = 'edited_data.json'
                
                if st.button("Next Section"):
                    # Save the edited DataFrame to JSON automatically
                    edited_df.to_json(filename, orient="records")

                    # Export JSON data to TD docx
                    export_td()


    except TypeError:
        pass




# page config
st.set_page_config(
    page_title="TDA",
    page_icon="🧊",
    layout="wide",
    menu_items={
        # 'Get Help': 'https://www.extremelycoolapp.com/help',
        # 'Report a bug': "https://www.extremelycoolapp.com/bug",
        # 'About': "# This is a header. This is an *extremely* cool app!"
    }
)

if __name__ == "__main__":
    run_sidebar()