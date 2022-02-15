import os
import pandas as pd
import numpy as np
import shutil
from data_handling_functions import get_article_row, m_j_dict
import math

this_path = 'Bilbokning/'

#PARAMETERS
EUR_PALLET_VOLUME = 1.20*0.80*1.00
NUM_OF_ZONES = 9

def calculate_dij_mj(degree_of_filling, date):

    #Remove /csv/... if it exists, then create a new
    if os.path.exists(this_path+"csv"):
        shutil.rmtree(this_path+"csv")
    os.mkdir(this_path+"csv")

    df_utlev = pd.read_csv(this_path+'data/df_utleveranser_TATA62.csv', sep=';')
    df_prod = pd.read_csv(this_path+'data/df_artiklar_TATA62.csv', sep=';')

    #Select only todays orders
    todays_date = df_utlev[df_utlev.Datum == date]


    #---------------------------Augmenting todays_date-------------------------

    #Augment todays_date with Zone, Volumes, Type and Quantities)
    zone_list=[]
    article_volume_list=[]
    pack_volume_list=[]
    pallet_volume_list=[]
    pickup_type_list=[]
    pack_quantity_list=[]
    pallet_quantity_list=[]

    for i in todays_date["Artikelnr"]:
        zone_list.append(df_prod.loc[get_article_row(i, df_prod), "PlockOmråde"])
    for i in todays_date["Artikelnr"]:
        article_volume_list.append(df_prod.loc[get_article_row(i, df_prod), "ArtikelVolym"])
    for i in todays_date["Artikelnr"]:
        pack_volume_list.append(df_prod.loc[get_article_row(i, df_prod), "FörpVolym"])
    for i in todays_date["Artikelnr"]:
        pallet_volume_list.append(df_prod.loc[get_article_row(i, df_prod), "PallVolym"])
    for i in todays_date["Artikelnr"]:
        pickup_type_list.append(df_prod.loc[get_article_row(i, df_prod), "PlockTyp"])
    for i in todays_date["Artikelnr"]:
        pack_quantity_list.append(df_prod.loc[get_article_row(i, df_prod), "FörpQ"])
    for i in todays_date["Artikelnr"]:
        pallet_quantity_list.append(df_prod.loc[get_article_row(i, df_prod), "PallQ"])

    todays_date.loc[:,"PlockOmråde"] = zone_list
    todays_date.loc[:,"ArtikelVolym"] = article_volume_list
    todays_date.loc[:,"FörpVolym"] = pack_volume_list
    todays_date.loc[:,"PallVolym"] = pallet_volume_list
    todays_date.loc[:,"PlockTyp"] = pickup_type_list
    todays_date.loc[:,"FörpQ"] = pack_quantity_list
    todays_date.loc[:,"PallQ"] = pallet_quantity_list

    #--------------------------------------------------------------------------


    todays_date.to_csv(this_path+"csv/"+date+".csv", index=False)

    #List with shop_ids
    shop_ids = set(todays_date["Butiksnr"].tolist())

    #Create directories and sorted csv-files (shop-ids, product_types)
    os.mkdir(this_path+"csv/stores")

    dij = np.array([])
    dij.shape=(NUM_OF_ZONES,0)
    m_j = []

    for shop in shop_ids:
        os.mkdir(this_path+"csv/stores/"+str(shop))
        specific_shop = todays_date[todays_date.Butiksnr == shop]
        specific_shop.to_csv(this_path+"csv/stores/"+str(shop)+"/"+str(shop)+".csv", index=False)

        product_types = set(specific_shop["Varugrupp"].tolist())
        Dij = np.array([])
        Dij.shape=(NUM_OF_ZONES,0)

        for product_type in product_types:
            os.mkdir(this_path+"csv/stores/"+str(shop)+"/"+str(product_type))
            specific_product = specific_shop[specific_shop.Varugrupp == product_type]
            specific_product.to_csv(this_path+"csv/stores/"+str(shop)+"/"+str(product_type)+"/"+str(product_type)+".csv", index=False)


            #----------------------------Packing problem----------------------------

            num_of_rows = range(specific_product.shape[0])
            zone_volume_article = np.zeros((NUM_OF_ZONES,1))
            zone_volume_pack = np.zeros((NUM_OF_ZONES,1))
            zone_pallet_pallets = np.zeros((NUM_OF_ZONES,1))

            for i in num_of_rows:
                item = specific_product.iloc[i,:]

                #Decide the real zone (The order is important!!)
                if item.PlockOmråde == "Tält":
                    real_zone = 0
                elif item.PlockOmråde == "Fristapling" or item.PlockOmråde == "Udda":
                    real_zone = 1
                elif item.PlockOmråde == "Helpall" or item.PlockTyp == "Pall":
                    real_zone = 5
                elif item.PlockOmråde == "ADR":
                    real_zone = 6
                elif product_type == "2 El & belysning":
                    real_zone = 7
                elif item.PlockOmråde == "Entresol":
                    real_zone = 8
                elif product_type == "6 Trädgård" or product_type == "5 Färg":
                    real_zone = 2
                elif product_type == "3 VVS & Bad" or product_type == "4 Bygg":
                    real_zone = 3
                elif product_type == "1 Järn":
                    real_zone = 4

                #Sort pallets after zone for each product_type
                if item.PlockTyp == "Styck":
                    zone_volume_article[real_zone] += item.Kvantitet * float(item.ArtikelVolym.replace(',', '.'))
                elif item.PlockTyp == "Förpackning" or item.PlockTyp == "":
                    zone_volume_pack[real_zone] += (item.Kvantitet / item.FörpQ) * float(item.FörpVolym.replace(',', '.'))
                elif item.PlockTyp == "Pall":
                    zone_pallet_pallets[real_zone] += math.ceil(item.Kvantitet / item.PallQ)

            zone_article_pallets = np.ceil(zone_volume_article / (degree_of_filling * EUR_PALLET_VOLUME))
            zone_pack_pallets = np.ceil(zone_volume_pack / (degree_of_filling * EUR_PALLET_VOLUME))
            
            #Number of pallets from a zone for a specific product_type for a specific shop
            pallets_from_zone = zone_article_pallets + zone_pack_pallets + zone_pallet_pallets

            #One failsafe. It is now okay to send 96 pallets from one zone for one product type.
            if np.any((pallets_from_zone > 48) == True) or pallets_from_zone[0] > 30:
                tmp = np.floor(pallets_from_zone / 2)
                pallets_from_zone -= tmp
                Dij = np.append(Dij, tmp, axis=1)
                
            #Control to check if any zone sends more than 48 pallets for one product type
            if np.any((pallets_from_zone > 48) == True):
                print(str(shop)+" "+str(product_type)+" "+ str(real_zone) + " greater than 48 will generate error, or tent greater than 30")
            
            Dij = np.append(Dij, pallets_from_zone, axis=1)

            #-----------------------------------------------------------------------


        #----------------------------Combination problem---------------------------

        #Every initial order is set to less than 48 (Split large product_types) 
        col = 0
        while col < Dij.shape[1]:
            max_pallets = 0
            new_column = np.zeros((NUM_OF_ZONES,1))
            for i in range(Dij.shape[0]):
                if Dij[i,col] + max_pallets <= 48:
                    max_pallets += Dij[i,col]
                    new_column[i,:] = 0
                else:
                    new_column[i,:] = Dij[i,col]
                    Dij[i,col] = 0
            if sum(new_column[:,:]) != 0:
                Dij = np.append(Dij,new_column,axis=1)
            col += 1

        #Combine orders
        fixed_Dij = np.zeros((NUM_OF_ZONES,Dij.shape[1]))
        deleted = []
        for j in range(fixed_Dij.shape[1]):
            test_range = range(Dij.shape[1])
            for k in test_range:
                if k in deleted:
                    continue
                if sum(fixed_Dij[:,j]) + sum(Dij[:,k]) <= 48 and (fixed_Dij[0,j] + Dij[0,k]) <= 30:
                    fixed_Dij[:,j] = fixed_Dij[:,j] + Dij[:,k]
                    deleted.append(k)

        #Delete empty columns
        delete_col = []
        for j in range(fixed_Dij.shape[1]):
            if sum(fixed_Dij[:,j]) == 0:
                delete_col.append(j)
        fixed_Dij = np.delete(fixed_Dij,delete_col,axis=1)

        #Generate m_j
        for n in range(fixed_Dij.shape[1]):
            m_j = np.append(m_j,m_j_dict[str(shop)])

        #Append Dij for specific shop to total dij
        dij = np.append(dij,fixed_Dij,axis=1)

        #--------------------------------------------------------------------------


    return dij, m_j

#Real_zones
#0 - Tält - Allt från tält
#1 - Fristapling - Allt från Fristapling och Udda
#2 - Dropzon (Trädgård+Färg) - Styck, förp och "" från Trädgård och Färg
#3 - Dropzon (VVS&Bad+Bygg) - Styck, förp och "" från VVS & Bad och Bygg
#4 - Dropzon (Järn) - Styck, förp och "" från Järn
#5 - Helpall (inkl. Pushback) - Allt från Helpall samt PlockTyp == "Pall" för Trädgård, Färg, VVS & Bad, Bygg, Järn och El&Bel
#6 - ADR - Styck, förp och "" från ADR
#7 - Entresol (El&Bel) - Styck, Förp och "" från El&Bel
#8 - Entresol (Styckplock) - Styckplock från Entresol (Inte El&Bel)
