#############
# python udpserver.py
# usage: python udpserver.py <Port number>
#############

import socket
import sys
from datetime import datetime
import time

def printData (dnsList):
    listNum = 0
    print >> sys.stderr, '\t#: host name : ip address : time'
    for name in dnsList:
        print >> sys.stderr, '\t%s: %s : %s : %s %s%s' % (listNum + 1, name[0], name[1], name[2], name[3], name[4])
        listNum += 1

if (len(sys.argv) < 2):
    print('usage: python udpserver.py <Port number>')
    sys.exit()

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', int(sys.argv[1]))
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

#empty local DNS
dnsList = []
#Empty Response
response = ""

while True:
    print >>sys.stderr, '\nwaiting to receive message\n'
    data, address = sock.recvfrom(4096)

    host = (socket.gethostbyaddr(address[0])[0])

    currentTime = time.localtime()
    #Time in seconds for comparison later on, not shown to client
    checkTime = int(round(time.time()))

    date = time.strftime("%a %b %d ", currentTime)
    hour = int(time.strftime("%I", currentTime))
    #Subtracting 5 from hours to convert from UCT to CDT
    hour -= 5
    restOfTime = time.strftime(":%M:%S CDT %Y", currentTime)
    #IP address of the host name entered
    ipAddress = socket.gethostbyname(data)
    
    timeStmt = "[Time: " + date + str(hour) + restOfTime + "]"
    dataStmtList = [data, ipAddress, date, hour, restOfTime, checkTime]

    # 'x' is a counter variable; current DNS entry in list
    x = 0
    found = False

    print >> sys.stderr, '%s Server recieved datagram from %s (%s)' % (timeStmt, host, address[0])    
    print >>sys.stderr, '%s Server recieved %s/%s bytes: %s' % (timeStmt, len(data), len(data), data)
    #If the local DNS is empty
    if (not dnsList):
        print >> sys.stderr, '%s Server has no %s in cache' % (timeStmt, data)
        printData(dnsList)
        print >> sys.stderr, '%s Server requests to the DNS server' % (timeStmt)
        print '%s Server gets IP address (%s)' % (timeStmt, ipAddress)
        print '%s Server saves %s %s in cache' % (timeStmt, data, ipAddress)
        dnsList.append(dataStmtList)
        printData(dnsList)
        response = (dnsList[x])[1]
    
    else:
        while (x < len(dnsList)):
            #If the DNS list contains the host name entered
            if ((dnsList[x])[0] == data):
                response = (dnsList[x])[1]
                #Compare the saved DNS listing time to the new time; TTL = 10 seconds
                #If so, it deletes the old entry and replaces it with the newer one
                if ((checkTime - (dnsList[x])[5]) > 10):
                    print >> sys.stderr, '%s Server has %s in cache, but invalid' % (timeStmt, data)
                    printData(dnsList)
                    print >> sys.stderr, '%s Server requests to the DNS server' % (timeStmt)
                    print '%s Server gets IP address (%s)' % (timeStmt, ipAddress)
                    print '%s Server saves %s %s in cache' % (timeStmt, data, ipAddress)
                    del dnsList[x]
                    dnsList.append(dataStmtList)
                    printData(dnsList)
                    found = True
                    break
                else:
                    print >> sys.stderr, '%s Server has %s in cache, valid' % (timeStmt, data)
                    printData(dnsList)
                    response = (dnsList[x])[1]
                    found = True
                    break
            x += 1
        #Incoming Host was not in the local DNS server, lookup IP for caching
        if (found == False):
            print >> sys.stderr, '%s Server has no %s in cache' % (timeStmt, data)
            printData(dnsList)
            print >> sys.stderr, '%s Server requests to the DNS server' % (timeStmt)
            print '%s Server gets IP address (%s)' % (timeStmt, ipAddress)
            print '%s Server saves %s %s in cache' % (timeStmt, data, ipAddress)
            dnsList.append(dataStmtList)
            response = (dnsList[x])[1]
            #If the local DNS cache has 3 entries, delete the earliest entry
            if (len(dnsList) == 4):
                del dnsList[0]
            printData(dnsList)
    #Send IP address back to client
    if data:
        print >> sys.stderr, '%s Server sends %s to the client' % (timeStmt, response)
        sent = sock.sendto(response, address)
        #print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)

