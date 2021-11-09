

def autoTitle(pieces):
    """ takes a list of pieces, e.g. ['2000m', '2000m', '1000m']
        and converts it to a pretty title -> '2x2000m, 1000m']
    """
    if len(pieces) == 1: return pieces[0]

    count = 0
    out = ''
    last = pieces[0]
    for i in range(len(pieces)):
        if pieces[i] == last:
            count += 1
            last = pieces[i]
        else:
            if count == 1:
                out += last + ', '
                last = pieces[i]
            else:
                out += str(count)+'x'+ last + ', '
                count = 0
                last = pieces[i]

    if count == 1:
        out += str(count)+'x'
        final = ', '.join((out + last).split(',')[:-1])
    else:
        final =  str(count) + 'x'+last

    return final

if __name__ == "__main__":
    p1 = ['2000m']
    p2 = ['2000m','2000m','2000m']
    p3 = ['4000m', '3000m','2000m', '2000m']

    print(autoTitle(p1))
    print(autoTitle(p2))
    print(autoTitle(p3))