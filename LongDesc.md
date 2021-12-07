## Requirements

1. Have a local mongo db server installed and running. The program uses this to create a local db instance.
2. Install wireshark and tshark
3. Install suricata and modify `suricata.yaml` to export pcap file
   - Default Locations:
     - Windows: C:\Program Files\Suricata\suricata.yaml
     - Linux: /etc/suricata/suricata/yaml
```commandline
- pcap-log:
  - enabled: yes
  - filename: log.pcap
```
## Run
Once your changes are done and need to run the package as if you were a user of it. 
Follow these steps:
1. Run *pip install packetvisualization*
2. Run *python*
3. Type
    ``` 
    from packetvisualization import run
    run()
    ```


