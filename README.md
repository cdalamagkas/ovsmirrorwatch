## Open vSwitch Mirror Monitor tool

The script monitors the state of the mirrors currently configured. It uses the ovs-vsctl cmd tool wrapped as a python script to interact with the ovs-db in the machine running the mirrors. Every 5 seconds the script fetches the current port mirrorings and keeps an internal state of said port mirrors. If in the next poll the states have changed the script attempts to re-establish the failed port mirrors based on the stored mirror state form the previous 5 seconds.

### To build the image run:
```docker build -t mirror_monitor .```

### To run the image:
``` docker run -it --net=host  mirror_monitor ```

# Future Updates
 - Build web app to manage port mirrorings
