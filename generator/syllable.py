class Syllable:
    def __init__(self, onset, nucleus, coda):
        self.onset = onset
        self.nucleus = nucleus
        self.coda = coda


    def str_debug(self):
        return str(self.onset) + str(self.nucleus) + str(self.coda)


    def __str__(self):
        onset = ''.join(self.onset)
        coda = ''.join(self.coda)
        return f'{onset + self.nucleus + coda}'