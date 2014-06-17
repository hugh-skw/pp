import numpy as np
from matplotlib import pyplot


def decodeDH11Data(data):
    prev = 0
    count = 0
    bits = ''
    for i in range(len(data)):
        # low to high transition
        if prev == 0 and data[i] == 1:
            count = 1
        # high to low transition
        elif prev == 1 and data[i] == 0:
            if count > 3:
                bits += '1'
            else:
                bits += '0'
        # count
        else:
            count += 1
        prev = data[i]

    print len(bits)
    print bits
    
    x = []
    for i in range(0, 40, 8):
        x.append(int(bits[i:i+8], 2))
    if (sum(x[:4]) == x[4]):
        print('checksum verified')

    strRH = str(x[0]) + '.' + str(x[1])
    strT = str(x[2]) + '.' + str(x[3])
    print("RH = %s, T = %s" % (strRH, strT))

f = open('samples.txt')
vals = [int(i) for i in f.read().split()]
f.close()
# convert
data = vals[1::2]
decodeDH11Data(data)

# plot
x = np.array(vals[::2])
y = np.array(vals[1::2])
pyplot.axis([-1, 1.01*np.max(x), 0, 1.5])
pyplot.plot(x, y, 'o-')

# show plot
pyplot.show()