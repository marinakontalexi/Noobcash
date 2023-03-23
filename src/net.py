import netifaces as ni

def test_network():
    interfaces = ni.interfaces()

    for i in interfaces: #Will cycle through all available interfaces and check each one.
        if i != "lo": #This will remove lo from the interfaces it checks.
            try:
                ni.ifaddresses(i)
                gws = ni.gateways()
                gateway = gws['default'][ni.AF_INET][0]
                ip = ni.ifaddresses(i)[ni.AF_INET][0]['addr']
                sm = ni.ifaddresses(i)[ni.AF_INET][0]['netmask']
                print ("Network information for " + i + ":")
                print ("IP address: " + ip)
                print ("Subnet Mask: " + sm)
                print ("Gateway: " + gateway)
                print ()
            except: #Error case for a disconnected Wi-Fi or trying to test a network with no DHCP
                print (i + " is not connected or DHCP is not available. Try setting a static IP address.")
test_network()