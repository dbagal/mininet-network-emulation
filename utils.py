def get_network_addr(cidr):
    ip, subnet = cidr.split("/")
    subnet = int(subnet)
    subnet_mask_bits= [1,]*subnet + [0,]*(32-subnet)
    ip_bin = [format(int(quad), "b") for quad in ip.split(".")]
    ip_bin = [list('0'*(8-len(x))+x) for x in ip_bin]
    ip_bits = []
    for quad in ip_bin:
        ip_bits+= [int(bit) for bit in quad]

    nw_addr_bits = [x*y for x,y in zip(ip_bits, subnet_mask_bits )]
    nw_addr = []
    for i in range(0,32,8):
        nw_addr += [str(int("".join(str(i) for i in nw_addr_bits[i:i+8]), 2))]
    
    return ".".join(nw_addr)+"/"+str(subnet)

#x = get_network_addr("64.0.123.2/22")
#print(x)
    
    

