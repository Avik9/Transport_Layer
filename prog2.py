import random
import sys
"""
/* ******************************************************************
 ALTERNATING BIT AND GO-BACK-N NETWORK EMULATOR: VERSION 1.1  J.F.Kurose

   This code should be used for PA2, unidirectional or bidirectional
   data transfer protocols (from A to B. Bidirectional transfer of data
   is for extra credit and is not required).  Network properties:
   - one way network delay averages five time units (longer if there
     are other messages in the channel for GBN), but can be larger
   - packets can be corrupted (either the header or the data portion)
     or lost, according to user-defined probabilities
   - packets will be delivered in the order in which they were sent
     (although some can be lost).
**********************************************************************/
"""

BIDIRECTIONAL = False # DON'T CHANGE THIS
                      # /* change to 1 if you're doing extra credit */
                      # /* and write a routine called B_output */

# Structures
"""
/* a "msg" is the data unit passed from layer 5 (teachers code) to layer  */
/* 4 (students' code).  It contains the data (characters) to be delivered */
/* to layer 5 via the students transport level protocol entities.         */

 The only instance variable of the Msg class is the data field.  Data is just
 a bytes object that represents the application data being passed to you 
 reliable delivery transport protocol.
"""
class Msg():
    def __init__(self):
        self.data = b""
    # end def __init__()

    def __str__(self):
        return "Message Data: " + str(self.data)
    # end def __str_()
# end class Msg

"""
/* a packet is the data unit passed from layer 4 (students code) to layer */
/* 3 (teachers code).  Note the pre-defined packet structure, which all   */
/* students must follow. */

 The Pkt class represents the transport layer segment used by your relibable
 transport protocol.
 The Pkt class has four attributes.  seqnum is the sequence number assigned to
 the Pkt object, the acknum is the acknowledgement number sent in response, and
 the checksum is the checksum calculated for this segment. Finally, payload is
 where the application layer data is stored--it is a bytes object just like the
 field in a Msg object.
"""
class Pkt():
    def __init__(self):
        self.seqnum = -1
        self.acknum = -1
        self.checksum = -1
        self.payload = b""
    # end def __init__()

    def __str__(self):
        s = ""
        s += "Seqnum: " + str(self.seqnum) + "\n"
        s += "Acknum: " + str(self.acknum) + "\n"
        s += "Checksum: " + str(self.checksum) + "\n"
        s += "Payload: " + str(self.payload)
        return s
    # end def __str__()
# end class Pkt

"""
 The Event class is used by the simulator to construct network events (Pkt
 sending, Pkt receiving, Pkt corruption, timeouts.
 You should not have to deal with this class directly.
"""
class Event():
    def __init__(self):
        self.evtime = None
        self.evtype = None
        self.eventity = None
        self.pktptr = None
        self.prev = None
        self.next = None
    # end def __init__()

    def __str__(self):
        event_types = ("Timer Interrupt", "From Layer 5", "From Layer 3")
        entities = ["Host A", "Host B"]
        s = ""
        s += "Event Type: " + event_types[self.evtype] + "\n"
        s += "Event Time: " + str(self.evtime) + "\n"
        s += "Event Entity: " + entities[self.eventity] + "\n"
        s += "Packet: " + str(self.pktptr)
        return s
    # end def __str__()
# end class Event

# /********* STUDENTS WRITE THE NEXT SEVEN ROUTINES *********/

# PLEASE ALSO SEE THE STUDENT CALLABLE ROUTINES FURTHER DOWN.
# You will use those functions--starttimer, stoptimer, tolayer3, tolayer5--to
# implement your reliable delivery algorithm.

# Keep a check for seq and ack on their respective sides
# Keep a payload for previous sent message/packet
# Keep a check for timer, only 1 should be started at a time

# global A_sequence_num
# global A_prev_packet
# global A_is_timer_running

# global B_Ack_num
# global B_prev_pkt

B_prev_packet = None
B_Ack_num = 0

A_sequence_num = 0
A_prev_packet = None
A_is_timer_running = False

# /* called from layer 5, passed the data to be sent to other side */
# This function will be called when the simulator generates application data for
# Host A to send to Host B. The input is a Msg object, the ouput should be a 
# Pkt object constructed to contain the application data in message, and then
# sent to Layer 3 (the network layer controlled by the simulator.
# Call the tolayer3() function, passing it your new Pkt.

def A_output(message):
    print("A_output Called...", message)
    message_length = len(message.data.decode())
    
    pkt_obj = Pkt()
    pkt_obj.payload = message.data
    pkt_obj.checksum = message_length * 8
    pkt_obj.seqnum = A_sequence_num
    tolayer3(A, pkt_obj)

    if not A_is_timer_running:
        A_is_timer_running = True
        starttimer(A, 1)
        
    A_sequence_num += message_length


# /* called from layer 3, when a packet arrives for layer 4 */
def A_input(packet):
    print("A_input Called:\n" + str(packet))

    if packet.acknum != A_sequence_num or isCorrupt(packet):
       pass
    elif packet.acknum == A_sequence_num or not isCorrupt(packet):
        stoptimer(A)
        msg_obj = Msg()
        msg_obj.data = packet.payload
        tolayer5(A, msg_obj)
    else:
       pass

# /* called when A's timer goes off */
def A_timerinterrupt():
    print("A_timerinterrupt Called...")
    # Send the previous packet again
    tolayer5(A, A_prev_packet)
    starttimer(A, 1)

# /* the following routine will be called once (only) before any other */
# /* entity A routines are called. You can use it to do any initialization */
def A_init():
    print("A_init Called...")
    global A_sequence_num
    global A_prev_packet
    global A_is_timer_running

    A_sequence_num = 0
    A_prev_packet = None
    A_is_timer_running = False


# /* called from layer 3, when a packet arrives for layer 4 at B*/
def B_input(packet):
    print("B_input Called:\n" + str(packet))

    message_length = len(packet.payload.decode())

    if B_Ack_num == packet.seqnum + message_length and not isCorrupt(packet):
        msg_obj = Msg()
        msg_obj.data = packet.payload
        tolayer5(B, packet.payload)

        B_Ack_num += message_length

    ack_pkt = Pkt()
    ack_pkt.acknum = B_Ack_num
    ack_pkt.checksum = 0


# /* the following rouytine will be called once (only) before any other */
# /* entity B routines are called. You can use it to do any initialization */
def B_init():
    print("B_init Called...")
    global B_prev_packet
    global B_Ack_num
    
    B_prev_packet = None
    B_Ack_num = 0


# /* Note that with simplex transfer from a-to-B, there is no B_output() */
# IGNORE THE TWO (2) FUNCTIONS BELOW
# // IGNORE THIS FUNCTION
def B_output(message):
    pass

# /* called when B's timer goes off */
# // IGNORE THIS FUNCTION
def B_timerinterrupt():
    pass
# IGNORE THE TWO (2) FUNCTIONS ABOVE


def isCorrupt(packet):
    return packet.checksum == (len(packet.payload.decode()) * 8)


"""
/*****************************************************************
***************** NETWORK EMULATION CODE STARTS BELOW ***********
The code below emulates the layer 3 and below network environment:
  - emulates the tranmission and delivery (possibly with bit-level corruption
    and packet loss) of packets across the layer 3/4 interface
  - handles the starting/stopping of a timer, and generates timer
    interrupts (resulting in calling students timer handler).
  - generates message to be sent (passed from later 5 to 4)

THERE IS NOT REASON THAT ANY STUDENT SHOULD HAVE TO READ OR UNDERSTAND
THE CODE BELOW.  YOU SHOLD NOT TOUCH, OR REFERENCE (in your code) ANY
OF THE DATA STRUCTURES BELOW.  If you're interested in how I designed
the emulator, you're welcome to look at the code - but again, you shouldn't
have to, and you defeinitely should not have to modify
******************************************************************/
"""

evlist = None # /* the event list */

# Constants
# possible events
TIMER_INTERRUPT = 0
FROM_LAYER5     = 1
FROM_LAYER3     = 2

OFF = 0
ON  = 1
A   = 0
B   = 1

TRACE = 1          # /* for my debugging */
nsim = 0           # /* number of messages from 5 to 4 so far */ 
nsimmax = 0        # /* number of msgs to generate, then stop */
time = 0.0
lossprob = 0.0     # /* probability that a packet is dropped  */
corruptprob = 0.0  # /* probability that one bit is packet is flipped */
lambda_ = 0        # /* arrival rate of messages from layer 5 */   
ntolayer3 = 0      # /* number sent into layer 3 */
nlost = 0          # /* number lost in media */
ncorrupt = 0       # /* number corrupted by media*/



def main():
    global evlist
    global time
    global nsim
    eventptr = None
    msg2give = None
    pkt2give = None
    c = i = j = None

    init()
    A_init()
    B_init()

    while True:
        printevlist()
        eventptr = evlist
        print(eventptr)
        if eventptr == None:
            
            print("Simulator terminated at time " + str(time) + 
                  "\n after sending " + str(nsim) + " msgs from layer5\n")
            return 0
        evlist = evlist.next
        if evlist != None:
            evlist.prev = None
        if TRACE >= 2:
            print("\nEVENT time: %f," % (eventptr.evtime,), end = "")
            print("  type: %d" % (eventptr.evtype,), end = "")
            if eventptr.evtype == 0:
                print(", timerinterrupt ", end = "")
            elif eventptr.evtype == 1:
                print(", fromlayer5 ", end = "")
            else:
                print(", fromlayer3 ", end = "")
            print(" entity: %d\n" % (eventptr.eventity,), end = "")
            print()
        time = eventptr.evtime
        if nsim == nsimmax:
            #break
            pass
        if eventptr.evtype == FROM_LAYER5:
            msg2give = Msg()
            j = (nsim - 1) % 26
            for i in range(20):
                msg2give.data = msg2give.data + bytes([(97 + j)])
            if nsim < nsimmax:
                generate_next_arrival()
                nsim += 1
            if TRACE >= 2:
                print("MAINLOOP: data given to student: ", end = "")
                for i in range(len(msg2give.data)):
                    print("%c" % msg2give.data[i], end="")
                print()
            if eventptr.eventity == A:
                A_output(msg2give)
            else:
                B_output(msg2give)
        elif eventptr.evtype == FROM_LAYER3:
            pkt2give = Pkt()
            pkt2give.seqnum = eventptr.pktptr.seqnum
            pkt2give.acknum = eventptr.pktptr.acknum
            pkt2give.checksum = eventptr.pktptr.checksum
            pkt2give.payload = eventptr.pktptr.payload[:]
            if eventptr.eventity == A:
                A_input(pkt2give)
            else:
                B_input(pkt2give)
        elif eventptr.evtype == TIMER_INTERRUPT:
            if eventptr.eventity == A:
                A_timerinterrupt()
            else:
                B_timerinterrupt()
        else:
            print("INTERNAL PANIC: unknown event type \n")
    print(" Simulator terminated at time %f\n after sending %d msgs from layer5\n" % (time, nsim));
    return
# end def main()

def init():
    global nsim
    global nsimmax
    global lossprob
    global corruptprob
    global lambda_
    global TRACE
    global ntolayer3
    global nlost
    global ncorrupt
    global time
    
    print("-----  Stop and Wait Network Simulator Version 1.1 -------- \n\n")
    nsimmax = int(input("Enter the number of messages to simulate: "))
    lossprob = float(input("Enter packet loss probability [enter 0.0 for no loss]: "))
    corruptprob = float(input("Enter packet corruption probability [0.0 for no corruption]: "))
    lambda_ = float(input("Enter average time between messages from sender's layer5 [ > 0.0]: "))
    TRACE = int(input("Enter TRACE: "))
    print()
    
    #random.seed(a = 9999)
    sum = 0.0
    for i in range(1000):
        sum = sum + random.uniform(0, 1)
    avg = sum/1000.0
    if avg < 0.25 or avg > 0.75:
        print("It is likely that random number generation on your machine" ) 
        print("is different from what this emulator expects.  Please take")
        print("a look at the routine jimsrand() in the emulator code. Sorry. \n")
        sys.exit(-1)
        
    ntolayer3 = 0
    nlost = 0
    ncorrupt = 0
    
    time = 0.0
    generate_next_arrival()
    nsim += 1
# end def init()

"""
/********************* EVENT HANDLINE ROUTINES *******/
/*  The next set of routines handle the event list   */
/*****************************************************/
"""

def generate_next_arrival():
    if TRACE >= 2:
        print("GENERATE NEXT ARRIVAL: creating new arrival")
    x = lambda_ * (random.uniform(0, 1) * 2) # /* x is uniform on [0,2*lambda] */
                                             # /* having mean of lambda        */
    evptr = Event()
    evptr.evtime = time + x
    evptr.evtype = FROM_LAYER5
    if BIDIRECTIONAL and (random.uniform(0, 1) > 5):
        evptr.eventity = B
    else:
        evptr.eventity = A
    insertevent(evptr)
# end def generate_next_arrival()

def insertevent(p):
    global evlist
    
    if TRACE >= 2:
        print("INSERTEVENT: time is %lf" % (time,))
        print("INSERTEVENT: future time will be %lf" % (p.evtime,))
        print()
    
    q = evlist # /* q points to header of list in which p struct inserted */
    if q is None: # /* list is empty */
        evlist = p
        p.next = None
        p.prev = None
    else:
        qold = q
        while q is not None and p.evtime > q.evtime:
            qold = q
            q = q.next
        if q is None:      # /* end of list */
            qold.next = p
            p.prev = qold
            p.next = None
        elif q is evlist:  # /* front of list */
            p.next = evlist
            p.prev = None
            p.next.prev = p
            evlist = p
        else:
            p.next = q
            p.prev = q.prev
            q.prev.next = p
            q.prev = p
# end def insertevent()

def printevlist():
    print("--------------\nEvent List Follows:\n")
    q = evlist
    while q is not None:
        print("Event time: %f, type: %d, entity: %d\n" % (q.evtime, q.evtype, q.eventity))
        q = q.next
    print("--------------\n")

# /********************** Student-callable ROUTINES ***********************/

# /* called by students routine to cancel a previously-started timer */
def stoptimer(AorB): # /* A or B is trying to stop timer */
    global evlist
    if TRACE >= 2:
        print("STOP TIMER: stopping timer at %f\n" % (time,))
    q = evlist
    while q is not None:
        if q.evtype == TIMER_INTERRUPT and q.eventity == AorB:
            # /* remove this event */
            if q.next == None and q.prev == None: # /* remove first and only event on list */
                evlist = None
            elif q.next == None: # /* end of list - there is one in front */
                q.prev.next = None
            elif q is evlist: # /* front of list - there must be event after */
                q.next.prev = None
                evlist = q.next
            else: # /* middle of list */
                q.next.prev = q.prev
                q.prev.next = q.next
            return
        q = q.next
    print("Warning: unable to cancel your timer. It wasn't running.\n")
# end def stoptimer()

def starttimer(AorB, increment): # /* A or B is trying to start timer */
    if TRACE >= 2:
        print("START TIMER: starting timer at %f\n" % (time,))
    # /* be nice: check to see if timer is already started, if so, then  warn */
    q = evlist
    while q is not None:
        if q.evtype == TIMER_INTERRUPT and q.eventity == AorB:
            print("Warning: attempt to start a timer that is already started\n")
            return
        q = q.next
    
    # /* create future event for when timer goes off */
    evptr = Event()
    evptr.evtime = time + increment
    evptr.evtype = TIMER_INTERRUPT
    evptr.eventity = AorB
    insertevent(evptr)
# end def starttimer()

# /************************** TOLAYER3 ***************/

def tolayer3(AorB, packet):
    global ntolayer3
    global nlost
    global ncorrupt
    ntolayer3 += 1
    
    # /* simulate losses: */
    if random.uniform(0, 1) < lossprob:
        nlost += 1
        if TRACE > 0:
            print("TOLAYER3: packet being lost\n")
        return
    
    # /* make a copy of the packet student just gave me since he/she may decide */
    # /* to do something with the packet after we return back to him/her */
    mypktptr = Pkt()
    mypktptr.seqnum = packet.seqnum
    mypktptr.acknum = packet.acknum
    mypktptr.checksum = packet.checksum
    mypktptr.payload = packet.payload[:]
    if TRACE >= 2:
        print("TOLAYER3: seq: %d, ack %d, check: %d " % 
              (mypktptr.seqnum, mypktptr.acknum, mypktptr.checksum))
        print("               ", end="")
        for i in range(len(mypktptr.payload)):
            print(chr(mypktptr.payload[i]), end="")
        print()
        
    # /* create future event for arrival of packet at the other side */
    evptr = Event()
    evptr.evtype = FROM_LAYER3      # /* packet will pop out from layer3 */
    evptr.eventity = (AorB + 1) % 2 # /* event occurs at other entity */
    evptr.pktptr = mypktptr         # /* save ptr to my copy of packet */
    # /* finally, compute the arrival time of packet at the other end.
    # medium can not reorder, so make sure packet arrives between 1 and 10
    # time units after the latest arrival time of packets
    # currently in the medium on their way to the destination */
    lasttime = time
    q = evlist
    while q is not None:
        if q.evtype == FROM_LAYER3 and q.eventity == evptr.eventity:
            lasttime = q.evtime
        q = q.next
    evptr.evtime = lasttime + 1 + (9 * random.uniform(0, 1))
    
    # /* simulate corruption: */
    if random.uniform(0, 1) < corruptprob:
        ncorrupt += 1
        x = random.uniform(0, 1)
        if x < 0.75:
            mypktptr.payload = b'Z' + mypktptr.payload[1::] # /* corrupt payload */
        elif  x < 0.875:
            mypktptr.seqnum = 999999
        else:
            mypktptr.acknum = 999999
        if TRACE > 0:
            print("TOLAYER3: packet being corrupted\n")
    
    if TRACE >= 2:
        print("          TOLAYER3: scheduling arrival on other side\n")
    insertevent(evptr)
# end def tolayer3()

def tolayer5(AorB, datasent):
    """
    AorB identifies the Host
    datasent is a 20 byte message
    """
    datasent = datasent.decode()
    if TRACE >= 2:
        print("TOLAYER5: data received: ")
        print("               ", end="")
        for i in range(len(datasent)):
            print(datasent[i], end="")
        print()
# end def tolayer5()


if __name__ == "__main__":
    main()
