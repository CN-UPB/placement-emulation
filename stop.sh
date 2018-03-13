#!/bin/bash

# find the pids and stop the process (will automatically clean up)
pgrep -f "python emu" | sudo xargs kill

