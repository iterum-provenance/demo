import os

from pyterum.transformation_step import TransformationStepInput, TransformationStepOutput
from pyterum.local_fragment_desc import LocalFragmentDesc, LocalFileDesc
from pyterum import env
import pyterum

import cv2
import numpy as np

if __name__ == "__main__":
    ### Setup
    ts_in = TransformationStepInput()
    ts_out = TransformationStepOutput()

    passed_fragments = 0

    output_folder = os.path.join(env.DATA_VOLUME_PATH, "output")
    os.mkdir(output_folder)

    h_threshold1 = pyterum.config.get("H_THRESHOLD1")
    h_threshold2 = pyterum.config.get("H_THRESHOLD2")
    blur_kernel_size = pyterum.config.get("BLUR_KERNEL_SIZE")

    ########## For each message inbound from the sidecar ##########
    for input_msg in ts_in.consumer():      
        # If it is the kill message, finalize the process here
        if input_msg == None:
            print(f"Transformation step received kill message, stopping...", flush=True)
            ts_out.produce_done()
            ts_out.close()
            break

        ########## Print some general information and make some assertions ##########
        print(f"Transformation step received fragment message")
        print(f"\tFragment contains:")
        print(f"\t\t{len(input_msg.files)} data files", flush=True)
        assert(len(input_msg.files) == 1)


        ########## Process the actual message ##########
        # Destructure message
        file_desc = input_msg.files[0]
        photo_name = file_desc.name
        photo_path = file_desc.path

        # Process image
        img = cv2.imread(photo_path, cv2.IMREAD_GRAYSCALE)
        blurred = cv2.medianBlur(img, blur_kernel_size)
        edges = cv2.Canny(blurred, h_threshold1, h_threshold2)

        # Save file
        new_file_path = os.path.join(output_folder, photo_name)
        cv2.imwrite(new_file_path, edges)
        print(f"Stored new file in : {new_file_path}")

        # Create, and send out new fragment
        file_desc = LocalFileDesc(name="_".join(["edges", photo_name]), path=new_file_path)
        new_fragment = LocalFragmentDesc(files=[file_desc], predecessors=[input_msg.metadata.fragment_id])
        ts_out.produce(new_fragment)
        ts_out.done_with(input_msg)
