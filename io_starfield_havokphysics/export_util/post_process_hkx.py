import ctypes
import os
import sys


def post_process_hkx(input_hkx, output_hkx, meshconverter_dll_path):

    # Verify file exists
    if not os.path.exists(input_hkx):
        print(f"Error: File '{input_hkx}' not found")
        return False
    
    this_script_file = os.path.realpath(__file__)
    this_script_file_directory = os.path.dirname(this_script_file)   
    hktypetranscriptpath = os.path.join(this_script_file_directory, "hkTypeTranscript.json")


    # Load DLL and process file
    try:
        pd = ctypes.CDLL(meshconverter_dll_path)
        result = pd.extractPhysicsData(input_hkx.encode('utf-8'), output_hkx.encode('utf-8'), hktypetranscriptpath.encode('utf-8'))
        print(f"Processed {input_hkx} successfully")
        return True
    except Exception as e:
        print(f"Error processing {input_hkx}: {str(e)}")
        return False