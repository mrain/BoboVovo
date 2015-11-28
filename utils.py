from os.path import join

def matchfile(s, mode='a'):
    webpage = s.webpage.replace('/', '$')
    return open(join('matches', webpage), mode)

def domain(s):
    return s.webpage.split('/')[2]


