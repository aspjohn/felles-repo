
import math

class Kalkulator:

    def __init__(self, kjøpesum, felleskost, maks_per_mnd, rate = 0, ek = 0.1, år = 30, ppå = 12):
        
        self.kjøpesum       = kjøpesum
        self.felleskost     = felleskost
        self.maks_per_mnd   = maks_per_mnd
        self.ek_prct        = ek
        self.gjeld_prct     = 1 - ek
        self.annuitet_beløp = self.kalkuler_nedbetaling(r = rate, år = år, ppå = ppå)
        self.rente           = rate
        self.år             = år
        self.ppå            = ppå

    def vakre_tall(self, tall, tekst = ''):
        
        n = 0
        tall = str(float(tall))
        tall, dec = tall.split('.')
        for symb in reversed(tall):
            
            tekst = symb + tekst
            n += 1
            
            if n == 3:
                tekst = ' ' + tekst
                n = 0

        return 'kr. ' + tekst + '.' + dec
            
    def kalkuler_nedbetaling(self, kjøpesum = None, r = 0, år = 30, ppå = 12):
        
        if kjøpesum is None:
            gjeld = self.kjøpesum * self.gjeld_prct

        else:
            gjeld = kjøpesum * self.gjeld_prct

        if r != 0:
            annuitet = float((r / ppå) / (1 - (1 + (r / ppå))**(-år * ppå)))
            annuitet_beløp = int(annuitet * gjeld)
        
        else:
            annuitet = 0
            annuitet_beløp = float(gjeld / (år * ppå))

        # print(f'         Gjeld: {self.vakre_tall(tall = gjeld)}')
        # print(f'    Annuiteten: {round(annuitet * 100, 2)} %')
        # print(f'Annuitet beløp: {self.vakre_tall(tall = annuitet_beløp)}')
        
        return annuitet_beløp
    
    def chagne_factor(self, factor = None, max_fac = 8):

        if factor is None:
            return 0.01

        lenght = len(str(factor))

        if lenght >= max_fac:
            return factor

        return float(factor / 10)

    def endre_rente(self, kjøpesum = None):

        if kjøpesum is None:
            kjøpesum = self.kjøpesum

        rente = self.rente
        factor = 0.01

        while True:
            
            annuitet_beløp = self.kalkuler_nedbetaling(r = rente, kjøpesum = kjøpesum)

            if annuitet_beløp == self.maks_per_mnd:
                return rente
            
            elif annuitet_beløp > self.maks_per_mnd:
                rente -= factor
                factor = self.chagne_factor(factor = factor)
            
            elif annuitet_beløp < self.maks_per_mnd:
                rente += factor
                factor = self.chagne_factor(factor = factor)

    def endre_varighet(self, kjøpesum):
        
        år = self.år
        factor = 1

        while True:
            
            annuitet = self.kalkuler_nedbetaling(kjøpesum = kjøpesum, år = år)

            if annuitet <= self.maks_per_mnd + 1 and annuitet >= self.maks_per_mnd -1:
                return år

            elif annuitet > self.maks_per_mnd:
                år += factor
                factor = self.chagne_factor(factor=factor, max_fac=4)

            elif annuitet < self.maks_per_mnd:
                år -= factor
                factor = self.chagne_factor(factor=factor, max_fac=4)


    def møte_krit(self, kjøpesum = None):

        # test endre rente
        endre_rente = self.endre_rente(kjøpesum = kjøpesum)
        print('Rente:\t', round(endre_rente * 100, 2), '%')

        # test endre periode,
        endre_perio = self.endre_varighet(kjøpesum = kjøpesum)
        print('År:\t', endre_perio)

        # test endre kjøpesum

        return 0



if __name__ == '__main__':
    kalk = Kalkulator(kjøpesum      = 3500000,
                      felleskost    = 4535,
                      maks_per_mnd  = 15000,
                      ek            = 0.1,
                      rate          = 0.02
                    )


    kalk.møte_krit(kjøpesum = 4000000)
