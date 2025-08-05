import ctypes
import os
import sys


def post_process_hkx(input_hkx, output_hkx, meshconverter_dll_path):

    # Verify file exists
    if not os.path.exists(input_hkx):
        print(f"Error: File '{input_hkx}' not found")
        return False
    
    # Load DLL and process file
    try:
        pd = ctypes.CDLL(meshconverter_dll_path)
        result = pd.extractPhysicsData(hkx_file.encode('utf-8'), out_file.encode('utf-8'))
        print(f"Processed {hkx_file} successfully")
        return True
    except Exception as e:
        print(f"Error processing {hkx_file}: {str(e)}")
        return False