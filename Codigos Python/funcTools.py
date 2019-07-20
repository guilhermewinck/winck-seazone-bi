import pandas as pd
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta

def is_nan(x):
    return (x is np.nan or x != x)

def modsToListing(dataset,Bairro,Jurere,Anuncios):
    
	isICLaux = []
	aux = []
	    
	CategoryAP = np.full((dataset.shape[0], 1),None)
	CategoryHotel = np.full((dataset.shape[0], 1),None)
	CategoryDono = np.full((dataset.shape[0], 1),None)
	CategorySeazoneID = np.full((dataset.shape[0], 1),None)
	CategoryTipo = np.full((dataset.shape[0], 1),None)
	    
	for row_index, row in dataset.iterrows(): # check each row
	
		# isILC procedure

		if row['latitude'] < Bairro.at[0,'Ponto 1 Lat']:    

			aux.append(1)

		else:

			aux.append(0)

		if row['latitude'] > Bairro.at[0,'Ponto 2 Lat']:

			aux.append(1)

		else:

			aux.append(0)

		if row['latitude'] > Bairro.at[0,'Ponto 3 Lat']:

			aux.append(1)

		else:

			aux.append(0)
		  
		if row['latitude'] < Bairro.at[0,'Ponto 4 Lat']:

			aux.append(1)

		else:

			aux.append(0)

		if row['longitude'] > Bairro.at[0,'Ponto 1 Lon']:

			aux.append(1)

		else:

			aux.append(0)

		if row['longitude'] > Bairro.at[0,'Ponto 2 Lon']:

			aux.append(1)

		else:

			aux.append(0)
		                  
		if row['longitude'] < Bairro.at[0,'Ponto 3 Lon']:

			aux.append(1)

		else:

			aux.append(0)
		                      
		if row['longitude'] < Bairro.at[0,'Ponto 4 Lon']:

			aux.append(1)

		else:

			aux.append(0)
		       
		if min(aux) == 0:

			isICLaux.append(False)

		else:

			isICLaux.append(True)

		aux = []
	          
		# getCategories procedure

		for row_index2, row2 in Anuncios.iterrows(): # check each row

		    if str(row['ad_id']) == str(row2['ID']): 

		        CategoryAP[row_index] = str(row2['Hotel']) + str(row2['Tipo'])
		        CategoryHotel[row_index] = str(row2['Hotel'])
		        
		        if str(row2['Hotel']) != 'Incorrect Listed':
		        
		            if (str(row2['Dono']) == 'Fernando') or (str(row2['Dono']) == 'Seazone'):
		                
		                CategoryDono[row_index] = str(row2['Dono'])
		                CategorySeazoneID[row_index] = str(row2['ID Seazone'])
		                CategoryTipo[row_index] = str(row2['Tipo'])  
		                        
		        else:
		            
		            CategoryAP[row_index] = 'Incorrect Listed'
	    
	    
	CategoryAP = pd.DataFrame(CategoryAP)
	CategoryAP.columns = ['Categoria AP']
	CategoryHotel = pd.DataFrame(CategoryHotel)
	CategoryHotel.columns = ['Categoria Hotel']
	CategoryDono = pd.DataFrame(CategoryDono)
	CategoryDono.columns = ['Categoria Dono']
	CategorySeazoneID = pd.DataFrame(CategorySeazoneID)
	CategorySeazoneID.columns = ['Categoria ID Seazone']
	CategoryTipo = pd.DataFrame(CategoryTipo)
	CategoryTipo.columns = ['Categoria Seazone Tipo']
	      
	isICLaux = pd.DataFrame(isICLaux)
	isICLaux.columns = ['is Jurere?']    

	return [dataset, isICLaux, CategoryAP, CategoryHotel, CategoryDono, CategorySeazoneID, CategoryTipo]

def weekendDetailedDescription(Only_Calendar):
    
    Type_Weekend = np.full((Only_Calendar.shape[0], 1),None)
    
    for row_index, row in Only_Calendar.iterrows():
        
        if ((str(row['Week Day']) == 'Friday') | (str(row['Week Day']) == 'Saturday')):
            
            if ((str(row['Month']) == 'December') | (str(row['Month']) == 'January') | (str(row['Month']) == 'February')):
                
                Type_Weekend[row_index] = 'Hard Weekend'
                            
            else:
                
                Type_Weekend[row_index] = 'Soft Weekend'
     
    Type_Weekend = pd.DataFrame(Type_Weekend)
                       
    return Type_Weekend

def getMaskHotel(dataset, hotel_interesse):
    
    Mask = [False] * dataset.shape[0] 

    for row_index, row in dataset.iterrows(): # check each line of dataset
                  
        if str(row['Categoria Hotel']) == hotel_interesse:
                      
            Mask[row_index] = True
    
    return Mask

def getMaskID(Content, Anuncios):
        
    Mask = [False] * len(Content)
    
    for i, element in enumerate(Content):
                
        if element in Anuncios: 
            
            Mask[i] = True
                        
    return Mask

# based on a manual data filtering         
def dateHolidays(Only_Calendar, Holidays):
    
    isHoliday = [None] * Only_Calendar.shape[0]
    
    for i in range(Holidays.shape[0]): # check each line of Holidays
        
        for j in range(Only_Calendar.shape[0]): # then check each line of Airbnb Calendar
            
            if (str(Holidays.at[Holidays.index[i], 'Data']) == str(Only_Calendar.at[Only_Calendar.index[j], 'Airbnb Calendar'])): # use to get holiday month as well ***
                
                # check holiday overlaping
                if (i != 0) and not (str(Holidays.at[Holidays.index[i-1], 'Data']) >= str(Holidays.at[Holidays.index[i], 'Inicio']) and str(Holidays.at[Holidays.index[i-1], 'Data']) <= str(Holidays.at[Holidays.index[i], 'Fim']) and str(Holidays.at[Holidays.index[i-1], 'Categoria']) < str(Holidays.at[Holidays.index[i], 'Categoria'])):
                    
                    # check how long is the holiday
                    if str(Holidays.at[Holidays.index[i], 'Duracao']) == 'Padrao':
                        
                        # check if the holiday is on Saturday or Sunday
                        if str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Sunday' or str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Saturday': 
                    
                            # *** check if the holiday is on December, January or February - create a flag to identify it
                            if ((str(Only_Calendar.at[Only_Calendar.index[j],'Month']) == 'December') | (str(Only_Calendar.at[Only_Calendar.index[j],'Month']) == 'January') | (str(Only_Calendar.at[Only_Calendar.index[j],'Month']) == 'February')):
                                
                                isHoliday[j] = '252'
                                
                            else:
                                
                                isHoliday[j] = '252'
                                
                        else:
                            
                            # check Diaria Tipo
                            if str(Holidays.at[Holidays.index[i], 'Diaria']) == 'Diaria Padrao':
                                
                                # check if it is on Friday
                                if str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Fri':
                                    
                                    isHoliday[j] = '252'
                                    if j <= Only_Calendar.shape[0]-1:
                                        isHoliday[j+1] = '252'
                                    isHoliday[j-1] = '252' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                
                                # check if it is on Monday    
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Mon':
                                    
                                    isHoliday[j-1] = '252' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j >= 2: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-2] = '252'
                                    if j >= 3: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-3] = '252'
                                
                                # check if it is on Thursday
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Thu':
                                    
                                    isHoliday[j] = '252'
                                    isHoliday[j-1] = '252' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+1] = '252'
                                    if j <= Only_Calendar.shape[0]-2: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+2] = '252'          
                            
                                # check if it is on Thuesday
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Tue': 
                                    
                                    isHoliday[j-1] = '252' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j >= 2: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-2] = '252'
                                    if j >= 3: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-3] = '252'
                                    if j >= 4: # garantir que i-3 seja no minimo 0
                                        isHoliday[j-4] = '252'
                                    
                                # check if it is on Wednesday
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Wed': 
                                   
                                    isHoliday[j-1] = '252' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    isHoliday[j] = '252'
                                   
                            else:
                                
                                # check if it is on Friday
                                if str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Fri':
                                    
                                    isHoliday[j] = '192'
                                    if j <= Only_Calendar.shape[0]-1:
                                        isHoliday[j+1] = 'vbRed'
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                
                                # check if it is on Monday    
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Mon':
                                    
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j >= 2: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-2] = 'vbRed'
                                    if j >= 3: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-3] = 'vbRed'
                                
                                # check if it is on Thursday
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Thu':
                                    
                                    isHoliday[j] = '192'
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+1] = 'vbRed'
                                    if j <= Only_Calendar.shape[0]-2: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+2] = 'vbRed'          
                            
                                # check if it is on Thuesday
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Tue': 
                                    
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j >= 2: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-2] = 'vbRed'
                                    if j >= 3: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-3] = 'vbRed'
                                    if j >= 4: # garantir que i-3 seja no minimo 0
                                        isHoliday[j-4] = 'vbRed'
                                    
                                # check if it is on Wednesday
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Wed': 
                                   
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    isHoliday[j] = '192'
                    
                    else:
                        
                        if str(Holidays.at[Holidays.index[i], 'Diaria']) == 'Diaria Padrao':
                            
                            if str(Holidays.at[Holidays.index[i], 'Descricao']) == 'Dia das Maes' or str(Holidays.at[Holidays.index[i], 'Descricao']) == 'Dia dos Pais' or str(Holidays.at[Holidays.index[i], 'Descricao']) == 'Dia dos Namorados':
                                
                                isHoliday[j] = '252'
                            
                        else: 
                            
                            if str(Holidays.at[Holidays.index[i], 'Descricao']) == 'Semana Guga Kuerten':
                                
                                isHoliday[j] = '192'
                                if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                    isHoliday[j+1] = 'vbRed'
                                if j <= Only_Calendar.shape[0]-2: # garante que nao ultrapasse o valor maximo
                                    isHoliday[j+2] = 'vbRed'
                                if j <= Only_Calendar.shape[0]-3: # garante que nao ultrapasse o valor maximo
                                    isHoliday[j+3] = 'vbRed'
                                if j <= Only_Calendar.shape[0]-4: # garante que nao ultrapasse o valor maximo
                                    isHoliday[j+4] = 'vbRed'
                                if j <= Only_Calendar.shape[0]-5: # garante que nao ultrapasse o valor maximo
                                    isHoliday[j+5] = 'vbRed'
                                if j <= Only_Calendar.shape[0]-6: # garante que nao ultrapasse o valor maximo
                                    isHoliday[j+6] = 'vbRed' 
                            
                            elif str(Holidays.at[Holidays.index[i], 'Descricao']) == 'Ano novo':
                                
                                # check if it is on Friday
                                if str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Fri': 
                                
                                    isHoliday[j] = '192'
                                    if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+1] = 'vbRed'
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j >= 2: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-2] = '255'  
                                    if j >= 3: # garantir que i-3 seja no minimo 0
                                        isHoliday[j-3] = '255' 
                                    if j >= 4: # garantir que i-4 seja no minimo 0
                                        isHoliday[j-4] = '255' 
                                    if j >= 5: # garantir que i-5 seja no minimo 0
                                        isHoliday[j-5] = '255'
                                # check if it is on Monday 
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Mon':

                                    isHoliday[j] = '192'
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j >= 2: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-2] = 'vbRed'  
                                    if j >= 3: # garantir que i-3 seja no minimo 0
                                        isHoliday[j-3] = 'vbRed' 
                                    if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+1] = '255'
                                    if j <= Only_Calendar.shape[0]-2: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+2] = '255'
                                    if j <= Only_Calendar.shape[0]-3: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+3] = '255'
                                    if j <= Only_Calendar.shape[0]-4: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+4] = '255'
                                    if j <= Only_Calendar.shape[0]-5: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+5] = '255'

                                # check if it is on Thursday 
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Thu':

                                    isHoliday[j] = '192'
                                    if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+1] = 'vbRed'
                                    if j <= Only_Calendar.shape[0]-2: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+2] = 'vbRed'
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j >= 2: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-2] = '255'  
                                    if j >= 3: # garantir que i-3 seja no minimo 0
                                        isHoliday[j-3] = '255'
                                    if j >= 4: # garantir que i-4 seja no minimo 0
                                        isHoliday[j-4] = '255'

                                # check if it is on Tuesday
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Tue': 

                                    isHoliday[j] = '192'
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j >= 2: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-2] = 'vbRed'  
                                    if j >= 3: # garantir que i-3 seja no minimo 0
                                        isHoliday[j-3] = 'vbRed'
                                    if j >= 4: # garantir que i-4 seja no minimo 0
                                        isHoliday[j-4] = 'vbRed'     
                                    if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+1] = '255'
                                    if j <= Only_Calendar.shape[0]-2: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+2] = '255'
                                    if j <= Only_Calendar.shape[0]-3: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+3] = '255'
                                    if j <= Only_Calendar.shape[0]-4: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+4] = '255'

                                # check if it is on Wednesday
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Wed':

                                    isHoliday[j] = '192'
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j >= 2: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-2] = 'vbRed'  
                                    if j >= 3: # garantir que i-3 seja no minimo 0
                                        isHoliday[j-3] = 'vbRed'
                                    if j >= 4: # garantir que i-4 seja no minimo 0
                                        isHoliday[j-4] = 'vbRed'
                                    if j >= 5: # garantir que i-4 seja no minimo 0
                                        isHoliday[j-5] = 'vbRed'
                                    if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+1] = '255'
                                    if j <= Only_Calendar.shape[0]-2: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+2] = '255'
                                    if j <= Only_Calendar.shape[0]-3: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+3] = '255'
                                      
                                # check if it is on Saturday
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Sat':

                                    isHoliday[j] = '192'
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+1] = '255'
                                    if j <= Only_Calendar.shape[0]-2: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+2] = '255'
                                    if j <= Only_Calendar.shape[0]-3: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+3] = '255'
                                    if j <= Only_Calendar.shape[0]-4: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+4] = '255'
                                    if j <= Only_Calendar.shape[0]-5: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+5] = '255'
                                    if j <= Only_Calendar.shape[0]-6: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+6] = '255'
                                    if j <= Only_Calendar.shape[0]-7: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+7] = '255'

                                # check if it is on Sunday
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Sun':

                                    isHoliday[j] = '192'
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j >= 2: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-2] = 'vbRed'  
                                    if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+1] = '255'
                                    if j <= Only_Calendar.shape[0]-2: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+2] = '255'
                                    if j <= Only_Calendar.shape[0]-3: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+3] = '255'
                                    if j <= Only_Calendar.shape[0]-4: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+4] = '255'
                                    if j <= Only_Calendar.shape[0]-5: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+5] = '255'
                                    if j <= Only_Calendar.shape[0]-6: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+6] = '255'

                            elif str(Holidays.at[Holidays.index[i], 'Descricao']) == 'Natal':

                                # check if it is on Friday
                                if str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Fri': 
                                    
                                    isHoliday[j] = '192'
                                    if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+1] = 'vbRed'
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j >= 2: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-2] = '255'  
                                    if j >= 3: # garantir que i-3 seja no minimo 0
                                        isHoliday[j-3] = '255'
                                    if j >= 4: # garantir que i-4 seja no minimo 0
                                        isHoliday[j-4] = '255'
                                    if j >= 5: # garantir que i-5 seja no minimo 0
                                        isHoliday[j-5] = '255'
                                    if j >= 6: # garantir que i-6 seja no minimo 0
                                        isHoliday[j-6] = '255'  
                                    if j >= 7: # garantir que i-7 seja no minimo 0
                                        isHoliday[j-7] = '255'

                                # check if it is on Monday
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Mon':

                                    isHoliday[j] = '192'
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j >= 2: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-2] = 'vbRed'  
                                    if j >= 3: # garantir que i-3 seja no minimo 0
                                        isHoliday[j-3] = 'vbRed'
                                    if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+1] = '255'
                                    if j <= Only_Calendar.shape[0]-2: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+2] = '255'
                                    if j <= Only_Calendar.shape[0]-3: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+3] = '255'
                                
                                # check if it is on Thursday
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Thu':

                                    isHoliday[j] = '192'
                                    if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+1] = 'vbRed'
                                    if j <= Only_Calendar.shape[0]-2: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+2] = 'vbRed'
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j >= 2: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-2] = '255'  
                                    if j >= 3: # garantir que i-3 seja no minimo 0
                                        isHoliday[j-3] = '255'
                                    if j >= 4: # garantir que i-4 seja no minimo 0
                                        isHoliday[j-4] = '255'
                                    if j >= 5: # garantir que i-5 seja no minimo 0
                                        isHoliday[j-5] = '255'
                                    if j >= 6: # garantir que i-6 seja no minimo 0
                                        isHoliday[j-6] = '255'

                                # check if it is on Tuesday
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Tue':

                                    isHoliday[j] = '192'
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j >= 2: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-2] = 'vbRed'  
                                    if j >= 3: # garantir que i-3 seja no minimo 0
                                        isHoliday[j-3] = 'vbRed'
                                    if j >= 4: # garantir que i-4 seja no minimo 0
                                        isHoliday[j-4] = 'vbRed'
                                    if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+1] = '255'
                                    if j <= Only_Calendar.shape[0]-2: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+2] = '255'

                                # check if it is on Wednesday
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Wed':

                                    isHoliday[j] = '192'
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j >= 2: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-2] = 'vbRed'  
                                    if j >= 3: # garantir que i-3 seja no minimo 0
                                        isHoliday[j-3] = 'vbRed'
                                    if j >= 4: # garantir que i-4 seja no minimo 0
                                        isHoliday[j-4] = 'vbRed'
                                    if j >= 5: # garantir que i-5 seja no minimo 0
                                        isHoliday[j-5] = 'vbRed'
                                    if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+1] = '255'

                                # check if it is on Saturday
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Sat':

                                    isHoliday[j] = '192'
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+1] = '255'
                                    if j <= Only_Calendar.shape[0]-2: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+2] = '255'
                                    if j <= Only_Calendar.shape[0]-3: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+3] = '255'
                                    if j <= Only_Calendar.shape[0]-4: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+4] = '255'
                                    if j <= Only_Calendar.shape[0]-5: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+5] = '255'

                                # check if it is on Sunday
                                elif str(Holidays.at[Holidays.index[i], 'Dia da Semana']) == 'Sun':

                                    isHoliday[j] = '192'
                                    isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                    if j >= 2: # garantir que i-2 seja no minimo 0
                                        isHoliday[j-2] = 'vbRed'  
                                    if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+1] = '255'
                                    if j <= Only_Calendar.shape[0]-2: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+2] = '255'
                                    if j <= Only_Calendar.shape[0]-3: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+3] = '255'
                                    if j <= Only_Calendar.shape[0]-4: # garante que nao ultrapasse o valor maximo
                                        isHoliday[j+4] = '255'

                            elif str(Holidays.at[Holidays.index[i], 'Descricao']) == 'Winter Play':

                                isHoliday[j] = '192'
                                if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                    isHoliday[j+1] = 'vbRed'

                            elif str(Holidays.at[Holidays.index[i], 'Descricao']) == 'Iron Man Ingleses': 

                                isHoliday[j] = '192'
                                isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                if j >= 2: # garantir que i-2 seja no minimo 0
                                    isHoliday[j-2] = 'vbRed'  
                                if j >= 3: # garantir que i-3 seja no minimo 0
                                    isHoliday[j-3] = 'vbRed'
                                if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                    isHoliday[j+1] = 'vbRed'

                            elif str(Holidays.at[Holidays.index[i], 'Descricao']) == 'Iron Man Jurere':

                                isHoliday[j] = '192'
                                isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                if j >= 2: # garantir que i-2 seja no minimo 0
                                    isHoliday[j-2] = 'vbRed'  
                                if j >= 3: # garantir que i-3 seja no minimo 0
                                    isHoliday[j-3] = 'vbRed'
                                if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                    isHoliday[j+1] = 'vbRed'


                            elif str(Holidays.at[Holidays.index[i], 'Descricao']) == 'Carnaval':

                                isHoliday[j] = '192'
                                isHoliday[j-1] = 'vbRed' # ja ta garantido que i aqui ja vai ser diferente de 0, logo ok
                                if j >= 2: # garantir que i-2 seja no minimo 0
                                    isHoliday[j-2] = 'vbRed'  
                                if j >= 3: # garantir que i-3 seja no minimo 0
                                    isHoliday[j-3] = 'vbRed'
                                if j >= 4: # garantir que i-4 seja no minimo 0
                                    isHoliday[j-4] = 'vbRed'

                            elif str(Holidays.at[Holidays.index[i], 'Descricao']) == 'Pos Carnaval':

                                isHoliday[j] = '192'
                                if j <= Only_Calendar.shape[0]-1: # garante que nao ultrapasse o valor maximo
                                    isHoliday[j+1] = '255'
                                if j <= Only_Calendar.shape[0]-2: # garante que nao ultrapasse o valor maximo
                                    isHoliday[j+2] = '255'
                                if j <= Only_Calendar.shape[0]-3: # garante que nao ultrapasse o valor maximo
                                    isHoliday[j+3] = '255'

                            else:

                                isHoliday[j] = 'vbBlue'
                                
    isHoliday = pd.DataFrame(isHoliday)
    
    return isHoliday

def inputDataCorrections(hotel_IDs, hotel_IDs_colors, cte): # pensar sobre utilizar o DB e como fazer essa function

    dateInfo = hotel_IDs.iloc[:,0:2]
    dateContent = hotel_IDs.iloc[:,2:]
    dateContent_colors = hotel_IDs_colors.iloc[:,2:]

    ncols = dateContent.shape[1]
    nrows = dateContent.shape[0]

    cellsRep = 0
    newChain = False
    iniLine = 1
    Mask =  np.zeros((nrows, ncols))
    Mask = pd.DataFrame(Mask)
    for i in range(ncols): # check each ID of the Hotel label

          for j in range(nrows): # check each date of the ID of the Hotel
                
                if str(dateInfo.at[dateInfo.index[j],'Airbnb Calendar']) > (date.today() + relativedelta(months=+5)).strftime("%Y-%m-%d"):

                    if str(dateContent_colors.at[dateContent_colors.index[j],dateContent_colors.columns[i]]) == 'GREEN':

                        cellsRep = cellsRep + 1
                        newChain = False

                    else:

                        newChain = True
                        totalrep = cellsRep
                        cellsRep = 0
                else:

                    if j != 0:

                        if str(dateContent.at[dateContent.index[j-1],dateContent.columns[i]]) == str(dateContent.at[dateContent.index[j],dateContent.columns[i]]) and str(dateContent_colors.at[dateContent_colors.index[j],dateContent_colors.columns[i]]) == 'GREEN':

                            cellsRep = cellsRep + 1
                            newChain = False

                        else:

                            newChain = True
                            totalrep = cellsRep
                            cellsRep = 0

                # flag and counter are already defined
                if newChain:

                    if totalrep >= cte:
                      
                        Mask.iloc[iniLine:iniLine+totalrep,i] = 'Darkgrey'

                    iniLine = j

    return Mask

# for each Hotel or any category this procedure creates a dataframe 
def getDataAnalysis(hotel_IDs, hotel_IDs_colors, hotel_IDs_Managers): # pensar sobre utilizar o DB e como fazer essa function

    dateInfo = hotel_IDs.iloc[:,0:5] # after all concat with the final dataframe
    dateContent = hotel_IDs.iloc[:,5:]
    dateContent_colors = hotel_IDs_colors.iloc[:,5:]

    ncols = dateContent.shape[1]
    nrows = dateContent.shape[0]

    totalSea = 0
    count_totalAds = 0
    count_bookApts = 0
    count_freeApts = 0
    count_blockApts = 0
    count_totalRateBooked = 0
    count_totalNotRateBooked = 0
    aptBelowAvg = 0
    rateRed_collection = []
    rateGreen_collection = []

    Out = pd.DataFrame(np.zeros((nrows,17)))
    Out.columns = ['totalAds','bookApts','freeApts','blockApts','totalRateBooked','totalNotRateBooked','MinRatePed','MaxRatePed', 'MinRateRes', 'MaxRateRes','AnalAvgRatPed', 'AnalAvgRatRes','AnalToWBlo','AnalToNBlo', 'AptBelowAvg','totalSea','auxiliarColor']
    LastColToAdd = Out.shape[1]

    for i in range(nrows):

        # calculates 
        for j in range(ncols):

            if not hotel_IDs_Managers.at[hotel_IDs_Managers.index[0],hotel_IDs_Managers.columns[j]]: # it is not Seazone

                    # Count the number of Ads
                    count_totalAds = count_totalAds + 1

                    # Count the number of booked Ads
                    if str(dateContent_colors.at[dateContent_colors.index[i],dateContent_colors.columns[j]]) == 'GREEN':

                        count_bookApts = count_bookApts + 1

                    # Count the number of free Ads
                    if str(dateContent_colors.at[dateContent_colors.index[i],dateContent_colors.columns[j]]) == 'RED':

                        count_freeApts = count_freeApts + 1

                    # Count the number of blocked Ads
                    if str(dateContent_colors.at[dateContent_colors.index[i],dateContent_colors.columns[j]]) == 'YELLOW' or str(dateContent_colors.at[dateContent_colors.index[i],dateContent_colors.columns[j]]) == 'GREY' or str(dateContent.at[dateContent.index[i],dateContent.columns[j]]) == '__N/A__':

                        count_blockApts = count_blockApts + 1

                    # Soma de todas as diarias com reserva confirmada e numero de aptos
                    if str(dateContent_colors.at[dateContent_colors.index[i],dateContent_colors.columns[j]]) == 'GREEN':
                        
                        if dateContent.at[dateContent.index[i],dateContent.columns[j]] != '__N/A__' and dateContent.at[dateContent.index[i],dateContent.columns[j]] != 'Booked': # is numeric

                            count_totalRateBooked = count_totalRateBooked + float(dateContent.at[dateContent.index[i],dateContent.columns[j]])

                            # Collection Green
                            rateGreen_collection.append(float(dateContent.at[dateContent.index[i],dateContent.columns[j]]))

                    # Soma de todas as diarias sem reserva confirmada e numero de aptos
                    if str(dateContent_colors.at[dateContent_colors.index[i],dateContent_colors.columns[j]]) == 'RED':

                        if dateContent.at[dateContent.index[i],dateContent.columns[j]] != '__N/A__' and dateContent.at[dateContent.index[i],dateContent.columns[j]] != 'Booked': # is numeric
                            
                            count_totalNotRateBooked = count_totalNotRateBooked + float(dateContent.at[dateContent.index[i],dateContent.columns[j]])
                            
                            # Collection Red
                            rateRed_collection.append(float(dateContent.at[dateContent.index[i],dateContent.columns[j]]))

            else: # it is Seazone

                    totalSea = totalSea + 1        

        # updates output arrays after finishing all columns of a row
        Out.at[Out.index[i],'totalSea'] = totalSea
        totalSea = 0

        Out.at[Out.index[i],'totalAds'] = count_totalAds
        count_totalAds = 0

        Out.at[Out.index[i],'bookApts'] = count_bookApts
        count_bookApts = 0

        Out.at[Out.index[i],'freeApts'] = count_freeApts
        count_freeApts = 0

        Out.at[Out.index[i],'blockApts'] = count_blockApts
        count_blockApts = 0

        Out.at[Out.index[i],'totalRateBooked'] = count_totalRateBooked
        count_totalRateBooked = 0

        Out.at[Out.index[i],'totalNotRateBooked'] = count_totalNotRateBooked
        count_totalNotRateBooked = 0

        if rateRed_collection:
            
            #rateRed_collection = QuickSort(rateRed_collection, 0, len(rateRed_collection) - 1)
            #rateRed_collection = quicksort(rateRed_collection)
            rateRed_collection.sort()
            Out.at[Out.index[i],'MinRatePed'] = rateRed_collection[0] 
            Out.at[Out.index[i],'MaxRatePed'] = rateRed_collection[len(rateRed_collection)-1] 

        if rateGreen_collection:

            #rateGreen_collection = QuickSort(rateGreen_collection, 0, len(rateGreen_collection) - 1)
            #rateGreen_collection = quicksort(rateGreen_collection)
            rateGreen_collection.sort()
            Out.at[Out.index[i],'MinRateRes'] = rateGreen_collection[0] 
            Out.at[Out.index[i],'MaxRateRes'] = rateGreen_collection[len(rateGreen_collection)-1] 

        # Some extra analysis
        if Out.at[Out.index[i],'freeApts'] != 0:

            Out.at[Out.index[i],'AnalAvgRatPed'] = Out.at[Out.index[i],'totalNotRateBooked'] / Out.at[Out.index[i],'freeApts']

        else:
                    
            Out.at[Out.index[i],'AnalAvgRatPed'] = 0

        ######################################################################

        if Out.at[Out.index[i],'bookApts'] != 0:

             Out.at[Out.index[i],'AnalAvgRatRes'] = Out.at[Out.index[i],'totalRateBooked'] / Out.at[Out.index[i],'bookApts']

        else:

             Out.at[Out.index[i],'AnalAvgRatRes'] = 0

        ######################################################################

        if Out.at[Out.index[i],'totalAds'] != 0:

             Out.at[Out.index[i],'AnalToWBlo'] = 100 * Out.at[Out.index[i],'bookApts'] / Out.at[Out.index[i],'totalAds']

        else:

             Out.at[Out.index[i],'AnalToWBlo'] = 0 

        ######################################################################

        if (Out.at[Out.index[i],'freeApts'] + Out.at[Out.index[i],'bookApts']) != 0:

              Out.at[Out.index[i],'AnalToNBlo'] = 100 * Out.at[Out.index[i],'bookApts'] / (Out.at[Out.index[i],'freeApts'] + Out.at[Out.index[i],'bookApts'])

        else: 

              Out.at[Out.index[i],'AnalToNBlo'] = 0

        ######################################################################

        if rateRed_collection:
            
            cont = LastColToAdd 

            # tests each element of the Red Collection to find out if the rule is satisfied and to create auxiliar cols
            for k in range(len(rateRed_collection)):
 
                    if rateRed_collection[k] < Out.at[Out.index[i],'AnalAvgRatPed']:

                        aptBelowAvg = aptBelowAvg + 1

                    Out.at[Out.index[i],str(cont)] = rateRed_collection[k]
                    cont = cont + 1

            Out.at[Out.index[i],'AptBelowAvg'] = aptBelowAvg 
            aptBelowAvg = 0 

            if Out.at[Out.index[i],Out.columns[LastColToAdd]] < 0.5 * Out.at[Out.index[i],'AnalAvgRatPed'] and str(dateInfo.at[dateInfo.index[i], 'Airbnb Calendar']) > (date.today()).strftime("%Y-%m-%d"):


                        if str(dateInfo.at[dateInfo.index[i],'Holiday Type']) == '192' or str(dateInfo.at[dateInfo.index[i],'Holiday Type']) == '255' or str(dateInfo.at[dateInfo.index[i],'Holiday Type']) == '192' or str(dateInfo.at[dateInfo.index[i],'Holiday Type']) == 'vbRed':

                                Out.at[Out.index[i],'auxiliarColor'] = 100000000000000.0 # 'vbGreen'
                                        
        rateRed_collection.clear()
        rateGreen_collection.clear()

    Out_final = pd.concat([dateInfo.reset_index(drop=True),Out.reset_index(drop=True)], axis=1)

    return Out_final

def getAnalysisCols(Analysis, inter_header):

    Analysis_header = list(Analysis)
    nrows = Analysis.shape[0]

    Out = pd.DataFrame(np.zeros((nrows,len(inter_header))))
    Out.columns = inter_header
    
    for i, element in enumerate(Analysis_header):

        for j, item in enumerate(inter_header):

            if element == item:

                Out[item] = Analysis[element]

    return Out

def priceFunction1(dataset, dataset_color):
    
    dataset_out = dataset.copy()

    nrows = dataset.shape[0]
    ncols = dataset.shape[1]

    for i in range(nrows):

        for j in range(ncols):
            
            if dataset_color.at[dataset_color.index[i],dataset_color.columns[j]] != 'RED':
                
                dataset_out.at[dataset_out.index[i],dataset_out.columns[j]] = 'O'               

    return dataset_out

def priceFunction2(PG_sheets_dictionary, datasetComplete):

    # get worksheet names as a list
    PG_sheet_names = list(PG_sheets_dictionary.keys())

    dataset_header = list(datasetComplete.head()) # it has ncols 
      
    col = 0

    for i in range(len(dataset_header)): # i is running through all the cols

          for j in range(len(PG_sheet_names)): # for all WorkSheets from PG

                if str(PG_sheet_names[j]) == str(dataset_header[i]): # to compare Ids

                    col = i
              
                    currentSheetContent, dateSheet = priceFunction2b(PG_sheets_dictionary[dataset_header[i]].iloc[3:,:]) # get Information of 2 days ago

                    datasetComplete = priceFunction2a(datasetComplete) # get Information of 2 days ago and go 
                                                   
                    for lin in range(datasetComplete.shape[0]):

                        for cc in range(currentSheetContent.shape[0]):

                            if str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) == str(dateSheet.at[dateSheet.index[cc],'Data']):
                                  
                                    if str(datasetComplete.at[datasetComplete.index[lin],datasetComplete.columns[col]]) == 'O':
                                     
                                        if is_nan(currentSheetContent.at[currentSheetContent.index[cc],'Pessoa']):  
                                            
                                                datasetComplete.at[datasetComplete.index[lin],datasetComplete.columns[col]] = 'O-grey-O'
                                    else:

                                        if not is_nan(currentSheetContent.at[currentSheetContent.index[cc],'Valor alugado']):
                                               
                                                datasetComplete.at[datasetComplete.index[lin],datasetComplete.columns[col]] = 'O-vbYellow-O'

                                    if str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) <= (date.today() + relativedelta(days=+14)).strftime("%Y-%m-%d") and str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) >= (date.today() - relativedelta(days=+2)).strftime("%Y-%m-%d") and not is_nan(currentSheetContent.at[currentSheetContent.index[cc],'Pessoa']) and not is_nan(currentSheetContent.at[currentSheetContent.index[cc],'Status']):
                                
                                        if not is_nan(currentSheetContent.at[currentSheetContent.index[cc],'Meio']) and str(currentSheetContent.at[currentSheetContent.index[cc],'Meio']) != 'Código de reserva enviado para hóspede':

                                              datasetComplete.at[datasetComplete.index[lin],datasetComplete.columns[col]] = 'O-vbRed-O'

                                    if str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) <= (date.today() + relativedelta(days=+60)).strftime("%Y-%m-%d") and str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) >= (date.today() - relativedelta(days=+2)).strftime("%Y-%m-%d") and not is_nan(currentSheetContent.at[currentSheetContent.index[cc],'Pessoa']) and not is_nan(currentSheetContent.at[currentSheetContent.index[cc],'Pagamento']):
                    
                                        if str(currentSheetContent.at[currentSheetContent.index[cc],'Meio']) == 'Contrato':

                                                if str(currentSheetContent.at[currentSheetContent.index[cc],'Pagamento']) == 'A PAGAR' or str(currentSheetContent.at[currentSheetContent.index[cc],'Pagamento']) == 'AP - AVISADO AO RESPONSAVEL':

                                                    datasetComplete.at[datasetComplete.index[lin],datasetComplete.columns[col]] += 'box'

                                                elif str(currentSheetContent.at[currentSheetContent.index[cc],'Pagamento']) == 'PARCIALMENTE PAGO' or str(currentSheetContent.at[currentSheetContent.index[cc],'Pagamento']) == 'PP - AVISADO AO RESPONSAVEL':
                                              
                                                    datasetComplete.at[datasetComplete.index[lin],datasetComplete.columns[col]] += 'boxANDdiag1'

                                                elif str(currentSheetContent.at[currentSheetContent.index[cc],'Pagamento']) == 'PAGO':

                                                    datasetComplete.at[datasetComplete.index[lin],datasetComplete.columns[col]] += 'boxANDdiag2'
      
    return datasetComplete

def priceFunction2a(dataset):
      
    mask_calendar = pd.DataFrame(dataset['Airbnb Calendar']) >= (date.today() - relativedelta(days=+2)).strftime("%Y-%m-%d")
      
    dataset_out = dataset.loc[mask_calendar['Airbnb Calendar'].values.tolist()]

    return dataset_out


def priceFunction2b(currentSheet):

    current_SheetHeader = currentSheet.loc[currentSheet.index[0],:] 
    currentSheetContent = currentSheet.loc[currentSheet.index[1]:,:]

    currentSheetContent.columns = current_SheetHeader.tolist() 
      
    dateSheet = pd.DataFrame(pd.to_datetime(currentSheetContent['Data']).dt.date)

    mask_calendar = pd.DataFrame(dateSheet['Data']) >= pd.to_datetime((date.today() - relativedelta(days=+2)).strftime("%Y-%m-%d")).date()

    currentSheetContent_out = currentSheetContent[mask_calendar]
      
    currentSheetContent_out = currentSheetContent.loc[mask_calendar['Data'].values.tolist()]

    dateSheet_out = dateSheet[mask_calendar]
      
    dateSheet_out = dateSheet.loc[mask_calendar['Data'].values.tolist()]
                
    return currentSheetContent_out, dateSheet_out

def priceFunction3(datasetComplete, Summary, Holidays):

    nrows = datasetComplete.shape[0]
    ncols = datasetComplete.shape[1] 

    dataset_header = list(datasetComplete.head()) # it has ncols 

    nrowSummary = Summary.shape[0]
    ncolSummary = Summary.shape[1]

    Summary_header = list(Summary.head()) # it has ncolSummary

    dateSummary = priceFunction3a(Summary)

    nrowHolidays = Holidays.shape[0]

    for SumCol in range(ncolSummary): # SumCol is running through all the cols of the Summary

            for col in range(ncols):  # col is running through all the cols of the ILC pricing dataset

                  if str(dataset_header[col]) == str(Summary_header[SumCol]):

                        for lin in range(nrows): 

                              for zz in range(nrowSummary):

                                      if str(datasetComplete.at[datasetComplete.index[lin],'Month']) == str(dateSummary.at[dateSummary.index[zz],'Month']):

                                            if str(datasetComplete.at[datasetComplete.index[lin],'Holiday Type']) == '192' or str(datasetComplete.at[datasetComplete.index[lin],'Holiday Type']) == 'vbRed':

                                                    for cont in range(nrowHolidays):

                                                          if str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) >= str(Holidays.at[Holidays.index[cont],'Inicio']) and str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) <= str(Holidays.at[Holidays.index[cont],'Fim']):

                                                                if not isinstance(Holidays.at[Holidays.index[cont],'Diaria'],str):
                                                                      datasetComplete.at[datasetComplete.index[lin],datasetComplete.columns[col]] = Holidays.at[Holidays.index[cont],'Diaria']
                                                                    

                                            elif str(datasetComplete.at[datasetComplete.index[lin],'Holiday Type']) == '255':

                                                    datasetComplete.at[datasetComplete.index[lin],datasetComplete.columns[col]] = Summary.at[Summary.index[zz],Summary.columns[SumCol]]

                                            else:

                                                    datasetComplete.at[datasetComplete.index[lin],datasetComplete.columns[col]] = Summary.at[Summary.index[zz],Summary.columns[SumCol]]

    return datasetComplete

def priceFunction3a(Summary):

    date = pd.DataFrame(pd.to_datetime(Summary['Mes']).dt.date)

    date['Month'] = pd.to_datetime(date['Mes']).dt.month_name()

    return date

def priceFunction4(datasetComplete, DataPosToInsert, Analysis, Price, key):

    SeazoneDataToInsert = datasetComplete.loc[:,datasetComplete.columns[DataPosToInsert]:]
    nrows = SeazoneDataToInsert.shape[0]
    ncols = SeazoneDataToInsert.shape[1] 

    AnalysisDataToRead = Analysis.loc[:,Analysis.columns[22]:]

    for lin in range(nrows):

            pricePos = []

            for col in range(ncols):
                
                try:
                    rule = float(SeazoneDataToInsert.at[SeazoneDataToInsert.index[lin],SeazoneDataToInsert.columns[col]])
                except ValueError:
                    rule = str('any')
                    
                if not isinstance(rule, str): # different of 'O' and colors
                    
                    pos = 0

                    foundData = False

                    cc = 0
                    while not is_nan(AnalysisDataToRead.at[AnalysisDataToRead.index[lin],AnalysisDataToRead.columns[cc]]):
                        
                        foundData = True

                        if rule < float(AnalysisDataToRead.at[AnalysisDataToRead.index[lin],AnalysisDataToRead.columns[cc]]):

                              break # stops the while even if the while condition is true

                        else:

                              pos = pos + 1

                        cc = cc + 1

                    # Defines Seasons    
                    if str(datasetComplete.at[datasetComplete.index[lin],'Month']) == 'May' or str(datasetComplete.at[datasetComplete.index[lin],'Month']) == 'June' or str(datasetComplete.at[datasetComplete.index[lin],'Month']) == 'August' or str(datasetComplete.at[datasetComplete.index[lin],'Month']) == 'September':

                            pos0to3Days = Price.at['0 to 3 Days','Low Season']
                            pos3to7Days = Price.at['3 to 7 Days','Low Season']
                            pos7to14Days = Price.at['7 to 14 Days','Low Season']
                            pos14to60Days = Price.at['14 to 60 Days','Low Season']
                            posOver60Days = Price.at['+ 60 Days','Low Season']

                    elif str(datasetComplete.at[datasetComplete.index[lin],'Month']) == 'October' or str(datasetComplete.at[datasetComplete.index[lin],'Month']) == 'November' or str(datasetComplete.at[datasetComplete.index[lin],'Month']) == 'March' or str(datasetComplete.at[datasetComplete.index[lin],'Month']) == 'April' or str(datasetComplete.at[datasetComplete.index[lin],'Month']) == 'July':

                            pos0to3Days = Price.at['0 to 3 Days','Mid Season']
                            pos3to7Days = Price.at['3 to 7 Days','Mid Season']
                            pos7to14Days = Price.at['7 to 14 Days','Mid Season']
                            pos14to60Days = Price.at['14 to 60 Days','Mid Season']
                            posOver60Days = Price.at['+ 60 Days','Mid Season']

                    elif str(datasetComplete.at[datasetComplete.index[lin],'Month']) == 'December' or str(datasetComplete.at[datasetComplete.index[lin],'Month']) == 'January' or str(datasetComplete.at[datasetComplete.index[lin],'Month']) == 'February':

                            pos0to3Days = Price.at['0 to 3 Days','High Season']
                            pos3to7Days = Price.at['3 to 7 Days','High Season']
                            pos7to14Days = Price.at['7 to 14 Days','High Season']
                            pos14to60Days = Price.at['14 to 60 Days','High Season']
                            posOver60Days = Price.at['+ 60 Days','High Season']

                    if key:

                            if lin == 0: # creates it at the first iteration

                                # creates Color Info and Comment Info as well as VBA Excel
                                datasetCompleteColor = precificacaoAux(datasetComplete.copy(), DataPosToInsert, 'WHITE')
                                datasetCompleteInfo = precificacaoAux(datasetComplete.copy(), DataPosToInsert, np.nan)

                            if str(datasetComplete.at[datasetComplete.index[lin],'Holiday Type']) != '192' and str(datasetComplete.at[datasetComplete.index[lin],'Holiday Type']) != 'vbRed':
                                
                                if str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) >= (date.today()).strftime("%Y-%m-%d") and str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) <= (date.today() + relativedelta(days=+3)).strftime("%Y-%m-%d"):
                                        datasetCompleteInfo.at[datasetCompleteInfo.index[lin], datasetCompleteInfo.columns[col+DataPosToInsert]], datasetCompleteColor.at[datasetCompleteColor.index[lin], datasetCompleteColor.columns[col+DataPosToInsert]] = precificacao(AnalysisDataToRead, SeazoneDataToInsert, datasetComplete, pos0to3Days, pos, lin, col)

                                elif str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) > (date.today() + relativedelta(days=+3)).strftime("%Y-%m-%d") and str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) <= (date.today() + relativedelta(days=+10)).strftime("%Y-%m-%d"): 

                                        datasetCompleteInfo.at[datasetCompleteInfo.index[lin], datasetCompleteInfo.columns[col+DataPosToInsert]], datasetCompleteColor.at[datasetCompleteColor.index[lin], datasetCompleteColor.columns[col+DataPosToInsert]] = precificacao(AnalysisDataToRead, SeazoneDataToInsert, datasetComplete, pos3to7Days, pos, lin, col)

                                elif str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) > (date.today() + relativedelta(days=+10)).strftime("%Y-%m-%d") and str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) <= (date.today() + relativedelta(days=+17)).strftime("%Y-%m-%d"): 

                                        datasetCompleteInfo.at[datasetCompleteInfo.index[lin], datasetCompleteInfo.columns[col+DataPosToInsert]], datasetCompleteColor.at[datasetCompleteColor.index[lin], datasetCompleteColor.columns[col+DataPosToInsert]] = precificacao(AnalysisDataToRead, SeazoneDataToInsert, datasetComplete, pos7to14Days, pos, lin, col)

                                elif  str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) > (date.today() + relativedelta(days=+17)).strftime("%Y-%m-%d") and str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) <= (date.today() + relativedelta(days=+60)).strftime("%Y-%m-%d"):

                                        datasetCompleteInfo.at[datasetCompleteInfo.index[lin], datasetCompleteInfo.columns[col+DataPosToInsert]], datasetCompleteColor.at[datasetCompleteColor.index[lin], datasetCompleteColor.columns[col+DataPosToInsert]] = precificacao(AnalysisDataToRead, SeazoneDataToInsert, datasetComplete, pos14to60Days, pos, lin, col)
                                
                                elif str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) > (date.today() + relativedelta(days=+60)).strftime("%Y-%m-%d"):  

                                        datasetCompleteInfo.at[datasetCompleteInfo.index[lin], datasetCompleteInfo.columns[col+DataPosToInsert]], datasetCompleteColor.at[datasetCompleteColor.index[lin], datasetCompleteColor.columns[col+DataPosToInsert]] = precificacao(AnalysisDataToRead, SeazoneDataToInsert, datasetComplete, posOver60Days, pos, lin, col)
                                
                      
                    if foundData:
                        
                        pricePos.append(pos)

                # updating Booking prices
                if not key:
                    
                    if lin == 0: # creates it at the first iteration
                        
                        bookingUpdate = precificacaoAux(datasetComplete.copy(), DataPosToInsert, np.nan) # makes a blank DataFrame with the same columns as datasetCompletE

                    if str(datasetComplete.at[datasetComplete.index[lin],'Airbnb Calendar']) > (date.today()).strftime("%Y-%m-%d"):
                            
                            if not isinstance(rule, str): # different of 'O' and colors
                                
                                bookingUpdate.at[bookingUpdate.index[lin],bookingUpdate.columns[col+DataPosToInsert]] = rule * 1.5
                                

            if pricePos:

                pricePos.sort()
                datasetComplete.at[datasetComplete.index[lin],'PosMin'] = pricePos[0] 
                datasetComplete.at[datasetComplete.index[lin],'PosMax'] = pricePos[len(pricePos)-1]  

    if key:
        
        return datasetComplete, datasetCompleteColor, datasetCompleteInfo

    else:  
        
        return datasetComplete, bookingUpdate  
        
def precificacaoAux(datasetComplete, DataPosToInsert, blank_str):

    nrows = datasetComplete.loc[:,datasetComplete.columns[DataPosToInsert]:].shape[0]
    ncols = datasetComplete.loc[:,datasetComplete.columns[DataPosToInsert]:].shape[1]

    for lin in range(nrows):

          for col in range(ncols):

                datasetComplete.loc[datasetComplete.index[lin],datasetComplete.columns[col+DataPosToInsert]] = blank_str

    return datasetComplete

def precificacao(Analysis, dataset, datasetComplete, posDesired, posCurrent, lin, col):

    Color = 'WHITE'
    Info = np.nan
    
    try:
        rule = float(dataset.at[dataset.index[lin],dataset.columns[col]])
    except ValueErro:
        rule = str('any')

    if str(datasetComplete.at[datasetComplete.index[lin],'Holiday Type']) != 'vbRed' and str(datasetComplete.at[datasetComplete.index[lin],'Holiday Type']) != '192' and not isinstance(rule,str):
        
            try:
                rule2 = float(dataset.at[dataset.index[lin-1],dataset.columns[col]])
            except ValueError:
                rul2 = str('any')
            try:
                rule3 = float(dataset.at[dataset.index[lin+1],dataset.columns[col]])
            except (ValueError, IndexError):
                rule3 = str('any')

            if isinstance(rule, str) and isinstance(rule3, str) and str(datasetComplete.at[datasetComplete.index[lin],'Week Day']) != 'Satudary':

                  if posCurrent != 0:

                        if round(Analysis.at[Analysis.index[lin],Analysis.columns[0]] / 1.1, 0) < datasetComplete.at[datasetComplete.index[lin],'Fat Rate']:

                                Color = 'vbBlue'

                                sugRate = round(Analysis.loc[Analysis.index[lin],Analysis.columns[0]] / 1.1, 0)
                                discRate8 = (sugRate - (sugRate * Const().desHigMidSea7()))
                                discRate14 = (sugRate - (sugRate * Const().desHigMidea14()))

                                Info = 'Move pos 0, It will be below Fat, suggested Rate R$:    ' + str(sugRate) + '     Disc Rate 8%:' + str(discRate8) + '     Disc Rate 17%:' + str(discRate14)

                        else: 

                                Color = 'vbBlue'

                                sugRate = round(Analysis.loc[Analysis.index[lin],Analysis.columns[0]] / 1.1, 0)
                                discRate8 = (sugRate - (sugRate * Const().desHigMidSea7()))
                                discRate14 = (sugRate - (sugRate * Const().desHigMidea14()))

                                Info = 'Move pos 0, suggested Rate R$:    ' + str(sugRate) + '     Disc Rate 8%:' + str(discRate8) + '     Disc Rate 17%:' + str(discRate14)

            elif posCurrent > posDesired:

                    if round(Analysis.at[Analysis.index[lin],Analysis.columns[posDesired]] / 1.1, 0) < datasetComplete.at[datasetComplete.index[lin],'Fat Rate']:
                        
                        Color = 'vbBlue'

                        sugRate = round(Analysis.loc[Analysis.index[lin],Analysis.columns[posDesired]] / 1.1, 0)
                        discRate8 = (sugRate - (sugRate * Const().desHigMidSea7()))
                        discRate14 = (sugRate - (sugRate * Const().desHigMidea14()))

                        Info = 'Move pos 0, It will be below Fat, suggested Rate R$:    ' + str(sugRate) + '     Disc Rate 8%:' + str(discRate8) + '     Disc Rate 17%:' + str(discRate14)

                    else:

                        Color = 'vbBlue'

                        sugRate = round(Analysis.loc[Analysis.index[lin],Analysis.columns[posDesired]] / 1.1, 0)
                        discRate8 = (sugRate - (sugRate * Const().desHigMidSea7()))
                        discRate14 = (sugRate - (sugRate * Const().desHigMidea14()))

                        Info = 'Move pos 0, suggested Rate R$:    ' + str(sugRate) + '     Disc Rate 8%:' + str(discRate8) + '     Disc Rate 17%:' + str(discRate14)

      #    elif posCurrent < posDesired:

                        # Deixa em branco ???

          #       # nao faz nada por enquanto
          #       if dataset.loc[dataset.index[lin], dataset.columns[col]] == datasetComplete.loc[datasetComplete.index[lin],'LT Rate']:

          #               #######
          #       else:

          #               ######

            if posCurrent == 0:

                  if Analysis.at[Analysis.index[lin],Analysis.columns[0]] == dataset.at[dataset.index[lin], dataset.columns[col]]:

                        Color = '255orange'

                        sugRate = round(Analysis.loc[Analysis.index[lin],Analysis.columns[posDesired]] / 1.1, 0)
                        discRate8 = (sugRate - (sugRate * Const().desHigMidSea7()))
                        discRate14 = (sugRate - (sugRate * Const().desHigMidea14()))

                        Info = 'Move pos 0, suggested Rate R$:    ' + str(sugRate) + '     Disc Rate 8%:' + str(discRate8) + '     Disc Rate 17%:' + str(discRate14)

    return Info, Color


# defines some constants to be used 
class Const:
  
  def desHigMidSea7(self):
    return 0.08

  def desHigMidea14(self):
    return 0.17  