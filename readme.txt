tda_tool (root)
├─ main.py: Streamlit UI code
├─ pdf_extractor.py: pdf to txt extractor
├─ extract_fields.py: Q&A extraction
├─ export_data.py: edited fields exported to docx (TD)


extracted_output{no.}.txt : txt file output after pdf extraction
output.json: json file output after field extraction
edited_data.json: edited json file output after data is edited by TD Assessor

============================================
- CHANGES -
(pdf_extractor_cmdline.py) changed to (pdf_extractor.py)
(tda_main.py) changed to (extract_fields.py)

============================================
- TO BE IMPLEMENTED -

pdf_temp_dir.py:
- if temp dir should be used

Optimisation of app:
Runs slowly so extract_fields.py will not be included in demo (unless CPU/GPU is used to demo)
