WebSDR Network Setup
=============

## IP Addresses

* 192.168.100.1 - WR1043ND
* 192.168.100.100 - WebSDR
  * port 80 (http)
* 192.168.100.101 - HVPi
  * port 123 (ntp)
* 192.168.100.201 - HVPC
  * port 4001
  * port 5925
* 192.168.100.202 - Netiom
  * port 81
* 192.168.100.203 - PowerBlock (static)
  * port 80

## Switch Ports

### TP-Link WR1043ND on Shelf

WAN: PPPoE (IPv4/IPv6)

1. -> Netgear Prosafe in Rack
2. WebSDR
3. PowerBlock
4. HVpi

### Netgear Prosafe in Rack

1. -> TP-Link WR1043ND on Shelf
4. HVPC
6. Netiom
