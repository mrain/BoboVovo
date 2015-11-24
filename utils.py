from os.path import join

def matchfile(s):
    webpage = s.webpage.replace('/', '$')
    return open(join('matches', webpage), 'a')


