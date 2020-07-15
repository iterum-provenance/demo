import os

from pyterum.transformation_step import TransformationStepInput, TransformationStepOutput
from pyterum.local_fragment_desc import LocalFragmentDesc, LocalFileDesc

from pyterum import env
import pyterum

import cv2
import numpy as np

if __name__ == "__main__":
    # Setup
    ts_in = TransformationStepInput()
    ts_out = TransformationStepOutput()

    output_folder = os.path.join(env.DATA_VOLUME_PATH, "output")
    os.mkdir(output_folder)

    high_threshold = pyterum.config.get("HIGH_THRESHOLD")
    low_threshold = pyterum.config.get("LOW_THRESHOLD")

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
        file_desc = input_msg.files[0]
        photo_name = file_desc.name
        photo_path = file_desc.path

        # Read file
        print(photo_path, flush=True)
        img = cv2.imread(photo_path, cv2.IMREAD_GRAYSCALE)
        img_color = cv2.imread(photo_path, cv2.IMREAD_COLOR)

        # Perform hough transform
        max_radius = int(img.shape[0] / 4)
        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 30,
                param1=high_threshold, param2=low_threshold, minRadius=0, maxRadius=max_radius)
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for circle in circles:
                cv2.circle(img_color,(circle[0],circle[1]),2,(0,0,255),3) # Draw the center
                cv2.circle(img_color,(circle[0],circle[1]),circle[2],(0,255,0),2) # Draw the radius

        # Save file
        new_file_path = os.path.join(output_folder, photo_name)
        print(f"Storing new file in : {new_file_path}")
        cv2.imwrite(new_file_path, img_color)

        # Create, and send out new fragment
        file_desc = LocalFileDesc(name="_".join(["hough_transform", photo_name]), path=new_file_path)
        new_fragment = LocalFragmentDesc(files=[file_desc], predecessors=[input_msg.metadata.fragment_id])
        ts_out.produce(new_fragment)
        ts_out.done_with(input_msg)

