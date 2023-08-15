import yfinance as yf
import csv

acciones_mexicanas = [
    "AMXL.MX","WALMEX.MX","FEMSAUBD.MX","ALFAA.MX","CEMEXCPO.MX","BIMBOA.MX","GFNORTEO.MX","SORIANAB.MX","ALPEKA.MX","GCARSOA1.MX","LIVEPOL1.MX","TLEVICPO.MX","SANMEXB.MX","MEXCHEM*.MX","ELEKTRA.MX","CHEDRAUIB.MX","AC*.MX","PE&OLES.MX","GFINBURO.MX","GRUMAB.MX","COMERUBC.MX","LALAB.MX","AHMSA.MX","AEROMEX*.MX","BACHOCOB.MX","GSANBOB1.MX","ICA.MX","CULTIBAB.MX","GMODELOC.MX","GNP.MX","FRAGUAB.MX","ICHB.MX","KIMBERA.MX","SIMECB.MX","ALSEA.MX","GPH1.MX","VITROA.MX","GIGANTE.MX","KUOB.MX","SAB.MX","OHLMEX.MX","QCCPO.MX","GENTERA.MX","MASECAB.MX","GFAMSAA.MX","IDEALB1.MX","HERDEZ.MX","VOLARA.MX","GFINTERO.MX","AZTECACP.MX","MFRISCOA.MX","PAPPEL.MX","RASSINIA.MX","LABB.MX","MEGACPO.MX","BEVIDESA.MX","IENOVA.MX","AXTELCPO.MX","GCC.MX","GISSAA.MX","CMOCTEZ.MX","BAFARB.MX","GPROFUT.MX","LAMOSA.MX","GFREGIO.MX","CABLECPO.MX","CERAMICB.MX","PINFRA*.MX","AGUA.MX","CIEB.MX","INCARSOB.MX","ARA.MX","POCHTECB.MX","ASURB.MX","FINDEP.MX","POSADASA.MX","MINSAB.MX","GAPB.MX","INVEXA.MX","GCYDSASAA.MX","MONEXB.MX","COLLADO.MX","UNIFINA.MX","ACTINVRB.MX","GFMULTIO.MX","ACCELSAB.MX","AUTLANB.MX","PASAB.MX","OMAB.MX","PINFRA.MX","GBMO.MX","PV.MX","CREAL.MX","TMMA.MX","MAXCOMCP.MX","VASCONI.MX","FIBRAMQ.MX","GMD.MX","CMRB.MX","BOLSAA.MX","VALUEGFO.MX","MEDICAB.MX","TERRA13.MX","FINAMEXO.MX","DANHOS13.MX","GENSEG.MX","FIHO12.MX","CIDMEGA.MX","HCITY.MX","FIBRAPL.MX","ARISTOSA.MX","SPORTS.MX","DINEB.MX","CONVERA.MX","VESTA.MX","RCENTROA.MX","FINN13.MX","HOGARB.MX","HOTEL.MX","FSHOP13.MX","TEAKCPO.MX","HILASALA.MX","LASEG.MX","SAREB.MX","FMTY14.MX","INGEALB.MX","EDOARDOB.MX","FHIPO.MX","GEOB.MX","GOMO.MX","HOMEX.MX","RCOA.MX","URBI.MX"
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

with open('acciones.csv', mode='w', newline='',encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Abreviacion', 'Nombre Completo'])
    for i in range(len(acciones_existentes)):
        writer.writerow([acciones_existentes[i], nombres[i]])