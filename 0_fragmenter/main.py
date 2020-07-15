from pyterum.fragmenter import FragmenterInput, FragmenterOutput
import pyterum
from pyterum import LocalFileDesc

if __name__ == "__main__":
    # Setup
    fragmenter_in = FragmenterInput()
    fragmenter_out = FragmenterOutput()

    # For each message inbound from the sidecar
    for input_msg in fragmenter_in.consumer():
        # If it is the kill message, finalize the process here
        if input_msg == None:
            print(f"Fragmenter received kill message, stopping...", flush=True)
            fragmenter_out.produce_done()
            fragmenter_out.close()
            break

        # Print some general information and make some assertions
        print(f"Fragmenter received input message", flush=True)
        print(f"\tInput contained:", flush=True)
        print(f"\t\t{len(input_msg.data_files)} data files", flush=True)

        # Produce fragments the actual message
        for filename in input_msg.data_files:
            frag = {"files": [filename], "metadata": {}}
            fragmenter_out.produce(frag)

