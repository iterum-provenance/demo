import time

from pyterum.fragmenter import FragmenterInput, FragmenterOutput
import pyterum
from pyterum import LocalFileDesc

def compute_time(time_elapsed):
    seconds = time_elapsed // 1000000000
    minutes = seconds // 60
    hours = minutes // 60
    minutes -= hours * 60
    seconds -= ((hours * 60 + minutes) * 60)
    return hours, minutes, seconds

if __name__ == "__main__":
    # Setup
    fragmenter_in = FragmenterInput()
    fragmenter_out = FragmenterOutput()

    messages_processed = 0
    fragments_produced = 0

    starting_time = time.time_ns()

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
            fragments_produced += 1

                
        # config_path = pyterum.config.get_filepath("CONFIG")
        # config_desc = LocalFileDesc(name="CONFIG", path=config_path)
        # config = parse_config(config_desc)
        # fragments_produced = produce_fragments(
        #     input_msg.data_files, config, fragmenter_out)

        # Setup for next iteration
        messages_processed += 1

        stopping_time = time.time_ns()
        hours, minutes, seconds = compute_time(stopping_time - starting_time)

        print(f"Fragmenter step finished processing fragment...", flush=True)
        print(f"Processed a total of {messages_processed} fragments", flush=True)
        print(f"Ran for {hours} hours, {minutes} minutes and {seconds} seconds", flush=True)
        print(f"Waiting for next fragment..", flush=True)

    # Finalize the fragmenter by doing some final assertions and generating some statistics
    assert(messages_processed == 1)
    stopping_time = time.time_ns()
    hours, minutes, seconds = compute_time(stopping_time - starting_time)

    print(f"Fragmenter finishing up...")
    print(f"Produced a total of {fragments_produced} fragments")
    print(f"Ran for {hours} hours, {minutes} minutes and {seconds} seconds")

    if seconds+hours+minutes == 0:
        milliseconds = (stopping_time - starting_time) // 1000000
        print(f"Ran for {milliseconds} milliseconds")
