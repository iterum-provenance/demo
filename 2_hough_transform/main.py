import time
import os

from pyterum.transformation_step import TransformationStepInput, TransformationStepOutput
from pyterum.local_fragment_desc import LocalFragmentDesc, LocalFileDesc

from pyterum import env

import cv2
import numpy as np

if __name__ == "__main__":
    # Setup
    ts_in = TransformationStepInput()
    ts_out = TransformationStepOutput()

    passed_fragments = 0
    starting_time = time.time_ns()

    output_folder = os.path.join(env.DATA_VOLUME_PATH, "output")
    os.mkdir(output_folder)

    # For each message inbound from the sidecar
    for input_msg in ts_in.consumer():
        # If it is the kill message, finalize the process here
        if input_msg == None:
            print(f"Transformation step received kill message, stopping...", flush=True)
            ts_out.produce_done()
            ts_out.close()
            break

        # Print some general information and make some assertions
        print(f"Transformation step received fragment message")
        print(f"\tFragment contains:")
        print(f"\t\t{len(input_msg.files)} data files and")
        print(f"\t\t{input_msg.metadata}\n", flush=True)

        # Process the actual message
        assert(len(input_msg.files) == 1)
        file_desc = input_msg.files[0]
        photo_name = file_desc.name
        photo_path = file_desc.path

        # Read file
        print(photo_path, flush=True)
        img = cv2.imread(photo_path, 1)

        # Perform edge detection

        cimg = img
        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 20, 
            param1=50, param2=30, minRadius=10, maxRadius=75)
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for circle in circles:
                cv2.circle(cimg,(circle[0],circle[1]),2,(255,0,0),3) # Draw the center
                cv2.circle(cimg,(circle[0],circle[1]),circle[2],(255,0,0),2) # Draw the radius

        # Save file
        new_file_path = os.path.join(output_folder, photo_name)
        print(f"Storing new file in : {new_file_path}")
        cv2.imwrite(new_file_path, cimg)

        # Create, and send out new fragment
        file_desc = LocalFileDesc(name="_".join(["hough_transform", photo_name]), path=new_file_path)
        new_fragment = LocalFragmentDesc(files=[file_desc], predecessors=[input_msg.metadata.fragment_id])
        ts_out.produce(new_fragment)
        ts_out.done_with(input_msg)

        # Setup for next iteration
        passed_fragments += 1

        stopping_time = time.time_ns()
        seconds = (stopping_time - starting_time) // 1000000000
        minutes = seconds // 60
        hours = minutes // 60
        minutes -= hours * 60
        seconds -= ((hours * 60 + minutes) * 60)

        print(f"Transformation step finished processing fragment...")
        print(f"Processed a total of {passed_fragments} fragments")
        print(f"Ran for {hours} hours, {minutes} minutes and {seconds} seconds")
        print(f"Waiting for next fragment..")

    # Finalize the transformation step by doing some final assertions and generating some statistics
    stopping_time = time.time_ns()
    seconds = (stopping_time - starting_time) // 1000000000
    minutes = seconds // 60
    hours = minutes // 60
    minutes -= hours * 60
    seconds -= ((hours * 60 + minutes) * 60)

    print(f"Transformation step finishing up...")
    print(f"Processed a total of {passed_fragments} fragments")
    print(f"Ran for {hours} hours, {minutes} minutes and {seconds} seconds")

    if seconds+hours+minutes == 0:
        milliseconds = (stopping_time - starting_time) // 1000000
        print(f"Ran for {milliseconds} milliseconds")
