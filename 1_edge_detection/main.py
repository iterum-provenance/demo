import time
import os

from pyterum.transformation_step import TransformationStepInput, TransformationStepOutput
from pyterum.local_fragment_desc import LocalFragmentDesc, LocalFileDesc
from pyterum import env
import pyterum

import cv2
import numpy as np

def timing(previous_time:int, message:str):
    stopping_time = time.time_ns()
    seconds = (stopping_time - previous_time) // 1000000000
    minutes = seconds // 60
    hours = minutes // 60
    minutes -= hours * 60
    seconds -= ((hours * 60 + minutes) * 60)
    print(message)
    print(f"{hours} hours, {minutes} minutes and {seconds} seconds")
    if seconds+hours+minutes == 0:
        milliseconds = (stopping_time - starting_time) // 1000000
        print(f"and {milliseconds} milliseconds")
    return stopping_time

if __name__ == "__main__":
    ### Setup
    ts_in = TransformationStepInput()
    ts_out = TransformationStepOutput()

    passed_fragments = 0
    starting_time = time.time_ns()
    output_folder = os.path.join(env.DATA_VOLUME_PATH, "output")
    os.mkdir(output_folder)

    hthreshold1 = pyterum.config.get("H_THRESHOLD1")
    hthreshold2 = pyterum.config.get("H_THRESHOLD2")

    ########## For each message inbound from the sidecar ##########
    for input_msg in ts_in.consumer():
        fragment_start_time = time.time_ns()
       
        # If it is the kill message, finalize the process here
        if input_msg == None:
            print(f"Transformation step received kill message, stopping...", flush=True)
            ts_out.produce_done()
            ts_out.close()
            break

        ########## Print some general information and make some assertions ##########
        print(f"Transformation step received fragment message")
        print(f"\tFragment contains:")
        print(f"\t\t{len(input_msg.files)} data files and")
        print(f"\t\t{input_msg.metadata}\n", flush=True)
        assert(len(input_msg.files) == 1)


        ########## Process the actual message ##########
        # Destructure message
        file_desc = input_msg.files[0]
        photo_name = file_desc.name
        photo_path = file_desc.path

        # Process image
        img = cv2.imread(photo_path, 0)
        edges = cv2.Canny(img, hthreshold1, hthreshold2)

        # Save file
        new_file_path = os.path.join(output_folder, photo_name)
        cv2.imwrite(new_file_path, edges)
        print(f"Stored new file in : {new_file_path}")

        # Create, and send out new fragment
        file_desc = LocalFileDesc(name="_".join(["edges", photo_name]), path=new_file_path)
        new_fragment = LocalFragmentDesc(files=[file_desc], predecessors=[input_msg.metadata.fragment_id])
        ts_out.produce(new_fragment)
        ts_out.done_with(input_msg)

        # Setup for next iteration
        passed_fragments += 1

        fragment_end_time = timing(fragment_start_time, "Transformation step finished processing fragment...")
        print(f"Processed a {passed_fragments} fragments so far")
        print(f"Waiting for next fragment..")

    # Finalize the transformation step by doing some final assertions and generating some statistics
    stopping_time = timing(starting_time, "Transformation step finishing up...")
    print(f"Processed a total of {passed_fragments} fragments")
