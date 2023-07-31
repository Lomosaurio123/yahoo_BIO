import yfinance as yf
import csv

acciones_mexicanas = [
    "AC.MX",
    "ALFAA.MX",
    "ALPEKA.MX",
    "ALSEA.MX",
    "AMXL.MX",
    "ASURB.MX",
    "BIMBOA.MX",
    "BOLSAA.MX",
    "CEMEXCPO.MX",
    "COMEUBC.MX",
    "ELEKTRA.MX",
    "FMSAUBD.MX",
    "GAPB.MX",
    "GCARSOA1.MX",
    "GENTERA.MX",
    "GFINBURO.MX",
    "GFNORTEO.MX",
    "GFREGIOO.MX",
    "GMEXICOB.MX",
    "GRUMAB.MX",
    "ICA.MX",
    "ICHB.MX",
    "IENOVA.MX",
    "KIMBERA.MX",
    "KOFL.MX",
    "LABB.MX",
    "LALAB.MX",
    "LIVEPOLC1.MX",
    "MEXCHEM.MX",
    "OHLMEX.MX",
    "PENOLES.MX",
    "PINFRA.MX",
    "SANMEXB.MX",
    "TLVACPO.MX",
    "WALMEXV.MX"
]

acciones_existentes =  []
nombres=[]

for accion in acciones_mexicanas:
    try:
        info = yf.Ticker(accion).info
        nombre_completo = info.get('longName', None)
        if len(nombre_completo )>0:
            nombres.append(nombre_completo)
            acciones_existentes.append(accion)  # Si la acción existe, la agregamos a la lista de acciones existentes
        
    except:
        pass  # Si no existe, simplemente pasamos al siguiente símbolo

print(len(acciones_existentes),"\n",acciones_existentes)

with open('acciones.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Abreviacion', 'Nombre Completo'])
    for i in range(len(acciones_existentes)):
        writer.writerow([acciones_existentes[i], nombres[i]])