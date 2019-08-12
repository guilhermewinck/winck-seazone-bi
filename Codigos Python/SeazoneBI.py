#!/usr/bin/env python
# coding: utf-8

# # Import libraries 

from sqlalchemy import create_engine, exc
from DBtools import read_sql_tmpfile, df_price_info
import time

# # Read DB
#### DB connection ####
db_engine = create_engine('postgresql+psycopg2://rootfernando:ferjigsaw!2018@seazone.casczodtym3u.us-west-2.rds.amazonaws.com:5432/jigsaw')

try: 
    
	conn = db_engine.connect()
	print("You are connected to PostgresSQL - AWS RDS - Seazone Scraping DB... Getting started to import listings and price-info DB")

	## runs main code ##
	start_time = time.time()

	sql_listings = "select * from listing_airbnblisting order by id"
	listings = read_sql_tmpfile(sql_listings, db_engine)

	sql_price_info = "select * from listing_airbnbavailabilityandprice order by date"
	price_info = read_sql_tmpfile(sql_price_info, db_engine)

except exc.SQLAlchemyError:
    conn = None # by default
    print("Error while connecting to PostgreSQL")

finally:
    if conn is not None:
    	conn.close()
    	print("PostgreSQL connection is closed, elapsed time: " +  str(time.time() - start_time))
    	runPricing = True
    else:
    	print("Unsuccessful execution caused by server connection error")
    	runPricing = False

if runPricing:

	# # Data Pre-Processing for Price_Info DataFrame

	### DB imports are done #### 
	# now it is possible to work with them as DataFrame
	start_time2 = time.time()
	price_info_asDF, price_info_asDF_color = df_price_info(price_info)   
	print("Elapsed time to transform listing_airbnbavailabilityandprice into price_info: " +  str(time.time() - start_time2))

	start_time3 = time.time()

	# # Data Transformations
	import pandas as pd

	# Listings Update - create new columns

	listings['ad_id'] = listings['ad_id'].astype(str)

	# Defines 'auxiliar' sheet

	auxiliar = 'auxiliar.xlsx' 

	# Jurere Geo Coordenates

	LatLon = pd.read_excel(auxiliar, sheet_name = 'Bairro') # Jurere Geo Coord
	Bairro = LatLon.iloc[:,1:]  

	# Ads defined by Seazone

	Anuncios = pd.read_excel(auxiliar, sheet_name = 'Anuncios') # Ads manuais
	Anuncios['ID'] = Anuncios['ID'].astype(str)

	# Import function that updates the listings DataFrame

	from funcTools import modsToListing

	updated_airbnb_listings = pd.concat(modsToListing(listings, Bairro,'Jurere', Anuncios), axis=1, sort=False)

	# Working with price_info DataFrame

	# Write 'price_info_asDF' and 'price_info_asDF_color' into Excel files

	# Create a copy of 'price_info_asDF' and 'price_info_asDF_color'

	price_info_COPY = price_info_asDF.copy()
	price_info_color_COPY = price_info_asDF_color.copy()

	# Transpose both copies

	price_info_COPY = price_info_COPY.T
	price_info_color_COPY = price_info_color_COPY.T

	calendar = pd.DataFrame(price_info_COPY.index)
	calendar.columns = ['Airbnb Calendar']

	calendar['Airbnb Calendar'] = pd.to_datetime(calendar['Airbnb Calendar'])
	calendar['Week Day'] = calendar['Airbnb Calendar'].dt.weekday_name
	calendar['Month'] = calendar['Airbnb Calendar'].dt.month_name()
	calendar['Week Day'] = calendar['Week Day'].astype(str)
	calendar['Month'] = calendar['Month'].astype(str)
	calendar['Airbnb Calendar'] = calendar['Airbnb Calendar'].dt.date
	calendar['Airbnb Calendar'] = calendar['Airbnb Calendar'].astype(str)

	from funcTools import weekendDetailedDescription

	calendar['Weekend Type'] = weekendDetailedDescription(calendar)
	calendar['Weekend Type'] = calendar['Weekend Type'].astype(str)

	# Holidays sheet

	Holidays = pd.read_excel(auxiliar, sheet_name = 'Feriados')  
	Holidays['Data'] = pd.DataFrame(pd.to_datetime(Holidays['Data']).dt.date)
	Holidays['Data'] = Holidays['Data'].astype(str)
	Holidays['Inicio'] = pd.DataFrame(pd.to_datetime(Holidays['Inicio']).dt.date)
	Holidays['Inicio'] = Holidays['Inicio'].astype(str)
	Holidays['Fim'] = pd.DataFrame(pd.to_datetime(Holidays['Fim']).dt.date)
	Holidays['Fim'] = Holidays['Fim'].astype(str)

	from funcTools import dateHolidays

	calendar['Holiday Type'] = dateHolidays(calendar, Holidays)
	calendar['Holiday Type'] = calendar['Holiday Type'].astype(str)

	# Concat Calendar Detailed Description with Price_Info

	price_info_COPY = pd.concat([calendar.reset_index(drop=True), price_info_COPY.reset_index(drop=True)], axis=1, sort=False)
	price_info_color_COPY = pd.concat([calendar.reset_index(drop=True), price_info_color_COPY.reset_index(drop=True)], axis=1, sort=False)

	# Filtering price_info per date

	from datetime import date
	from dateutil.relativedelta import relativedelta
	report_date = (date.today() - relativedelta(days=+10)).strftime("%Y-%m-%d") # to get current date
	# report_date = '2018-10-28' # based on the Excel Dashboard
	end_date = calendar['Airbnb Calendar'].iloc[-1]

	for_calendar_mask = pd.DataFrame(calendar['Airbnb Calendar'])      
	mask_calendar = (for_calendar_mask >= report_date) & (for_calendar_mask <= end_date)       
	price_info_COPY = price_info_COPY.loc[mask_calendar['Airbnb Calendar'].values.tolist()]
	price_info_color_COPY = price_info_color_COPY.loc[mask_calendar['Airbnb Calendar'].values.tolist()]

	# Filter Anuncios by 'is Jurere ?' flag

	mask_Jurere = updated_airbnb_listings['is Jurere?']

	Anuncios_Jurere = updated_airbnb_listings[mask_Jurere]

	# Filter Anuncios by 'ILC' flag

	from funcTools import getMaskHotel

	Anuncios_ILC = updated_airbnb_listings.loc[getMaskHotel(updated_airbnb_listings, 'ILC')]

	# Filter by Owner 

	Anuncios_ILC_Fernando_or_Seazone = Anuncios_ILC.loc[((Anuncios_ILC['Categoria Dono'] == 'Fernando') | (Anuncios_ILC['Categoria Dono'] == 'Seazone'))]

	# Getting an ILC Calendar 

	Header_Calendar = calendar.columns


	from funcTools import getMaskID

	mask_filt_ILC = getMaskID(list(price_info_asDF.index.astype(str)), list(Anuncios_ILC['ad_id']))

	Calendar_ILC = price_info_asDF.loc[mask_filt_ILC].T
	Calendar_ILC_color = price_info_asDF_color.loc[mask_filt_ILC].T

	Calendar_ILC = pd.concat([calendar.reset_index(drop=True), Calendar_ILC.reset_index(drop=True)], axis=1, sort=False)
	Calendar_ILC_color = pd.concat([calendar.reset_index(drop=True), Calendar_ILC_color.reset_index(drop=True)], axis=1, sort=False)

	# Filtering per date the tables

	Calendar_ILC = Calendar_ILC.loc[mask_calendar['Airbnb Calendar'].values.tolist()]
	Calendar_ILC_color = Calendar_ILC_color.loc[mask_calendar['Airbnb Calendar'].values.tolist()]

	# Getting an ILC Fernando or Seazone Calendar

	mask_filt_ILC_Fernando_Seazone = getMaskID(list(price_info_asDF.index.astype(str)), list(Anuncios_ILC_Fernando_or_Seazone['ad_id']))

	Calendar_ILC_Fernando_Seazone = price_info_asDF.loc[mask_filt_ILC_Fernando_Seazone].T
	Calendar_ILC_Fernando_Seazone_color = price_info_asDF_color.loc[mask_filt_ILC_Fernando_Seazone].T

	Calendar_ILC_Fernando_Seazone = pd.concat([calendar.reset_index(drop=True), Calendar_ILC_Fernando_Seazone.reset_index(drop=True)], axis=1, sort=False)
	Calendar_ILC_Fernando_Seazone_color = pd.concat([calendar.reset_index(drop=True), Calendar_ILC_Fernando_Seazone_color.reset_index(drop=True)], axis=1, sort=False)

	# Filtering per date the tables

	Calendar_ILC_Fernando_Seazone = Calendar_ILC_Fernando_Seazone.loc[mask_calendar['Airbnb Calendar'].values.tolist()]
	Calendar_ILC_Fernando_Seazone_color = Calendar_ILC_Fernando_Seazone_color.loc[mask_calendar['Airbnb Calendar'].values.tolist()]

	# Show 'Calendar_ILC_Fernando_Seazone' and 'Calendar_ILC_Fernando_Seazone_color, now filtered

	# Rename columns to a Seazone ID

	Calendar_ILC_Fernando_Seazone.columns = Calendar_ILC_Fernando_Seazone.columns[:5].tolist() + Anuncios_ILC_Fernando_or_Seazone['Categoria ID Seazone'].tolist()
	Calendar_ILC_Fernando_Seazone_color.columns = Calendar_ILC_Fernando_Seazone_color.columns[:5].tolist() + Anuncios_ILC_Fernando_or_Seazone['Categoria ID Seazone'].tolist()

	# Corrections  ???

	from funcTools import inputDataCorrections

	Corrections = inputDataCorrections(Calendar_ILC, Calendar_ILC_color, 5) 

	# # Analysis Procedure

	for_analysis_mask = pd.DataFrame((Anuncios_ILC['Categoria Dono'] == 'Fernando') | (Anuncios_ILC['Categoria Dono'] == 'Seazone'))
	for_analysis_mask = for_analysis_mask.T  
	for_analysis_mask.columns = Anuncios_ILC['ad_id'].tolist()

	from funcTools import getDataAnalysis

	# Creates the Analysis_ILC DataFrame for further procedures

	Analysis_ILC = getDataAnalysis(Calendar_ILC, Calendar_ILC_color, for_analysis_mask) 

	# # Pricing

	# Interested columns for Seazone

	Seazone_Header = ['Airbnb Calendar','Week Day','Month','Weekend Type','Holiday Type','totalAds','freeApts','AnalAvgRatPed','MinRatePed'] 
	Seazone_Header_add = ['PosMin', 'PosMax', 'Fat Rate', 'LT Rate']

	from funcTools import getAnalysisCols, priceFunction1

	ILC_pricing = pd.concat([(getAnalysisCols(Analysis_ILC, Seazone_Header + Seazone_Header_add)).reset_index(drop=True),priceFunction1(Calendar_ILC_Fernando_Seazone.iloc[:,5:], Calendar_ILC_Fernando_Seazone_color.iloc[:,5:]).reset_index(drop=True)], axis=1)

	planilha_geral = 'PlanilhaGeral.xlsx'

	PG_sheets_dictionary = pd.read_excel(planilha_geral, sheet_name=None)

	# Read 'ILC Summary'

	ILC_Summary = pd.read_excel(auxiliar, sheet_name = 'ILC Sumario')
	ILC_Summary = ILC_Summary.loc[ILC_Summary.index[0]:ILC_Summary.index[ILC_Summary.shape[0]-2],:] # arrumar o excel tbm eh uma solucao

	from funcTools import priceFunction2

	ILC_pricing2 = priceFunction2(PG_sheets_dictionary, ILC_pricing)

	from funcTools import priceFunction3

	ILC_pricing3 = priceFunction3(ILC_pricing2, ILC_Summary, Holidays)

	Price_Season_Pos = pd.read_excel(auxiliar, sheet_name = 'Price Season Position')
	Price_Season_Pos.index = list(Price_Season_Pos['Price Position'])
	Price_Season_Pos = Price_Season_Pos.loc[:,Price_Season_Pos.columns[1]:]

	from funcTools import priceFunction2a

	from funcTools import priceFunction4

	# if the last value = to False then it will return only one DataFrame
	ILC_pricing4F, ILC_bookingUpdateF = priceFunction4(ILC_pricing3.copy(), len(Seazone_Header+Seazone_Header_add),priceFunction2a(Analysis_ILC), Price_Season_Pos, key = False)

	# if the last value = to False then it will return only one DataFrame
	ILC_pricing4T, ILC_bookingUpdateT, ILC_bookingUpdate_INFO = priceFunction4(ILC_pricing3.copy(), len(Seazone_Header+Seazone_Header_add),priceFunction2a(Analysis_ILC), Price_Season_Pos, key = True)

	# pricing is done

	print("Elapsed time to complete pricing: " +  str(time.time() - start_time3))

	start_time4 = time.time()

	from datetime import date

	## defines output excel file ###
	# Create a Pandas Excel writer using XlsxWriter as the engine.
	with pd.ExcelWriter('excel_output_SEAZONE_BI.xlsx', engine='xlsxwriter') as writer:
		updated_airbnb_listings.to_excel(writer, sheet_name= "updated_airbnb_listings")
		price_info_asDF.to_excel(writer, sheet_name= "price_info_filtered")
		price_info_asDF_color.to_excel(writer, sheet_name= "price_info_color_filtered")
		Calendar_ILC.to_excel(writer, sheet_name= "CalendarILC")
		Calendar_ILC_color.to_excel(writer, sheet_name= "CalendarILC__")
		Calendar_ILC_Fernando_Seazone.to_excel(writer, sheet_name= "CalendarILC_S")
		Calendar_ILC_Fernando_Seazone_color.to_excel(writer, sheet_name= "CalendarILC_Sc")
		Analysis_ILC.to_excel(writer, sheet_name= "AnaliseILC")
		ILC_pricing4T.to_excel(writer, sheet_name= "PricingILC")
		ILC_bookingUpdateT.to_excel(writer, sheet_name= "PriceUp")
		ILC_bookingUpdate_INFO.to_excel(writer, sheet_name= "PriceUp__")

	# Close the Pandas Excel writer and output the Excel file.
	writer.save()
	writer.close()

	# Create a .txt log message
	file = open('testfile_SEAZONE_BI.txt',	'w+') 
	 
	file.write('log message '+ (date.today()).strftime("%Y-%m-%d"))

	file.close()

	print("Elapsed time to complete Excel writing: " +  str(time.time() - start_time4))