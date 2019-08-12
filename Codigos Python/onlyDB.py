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

	start_time4 = time.time()

	## defines output excel file ###
	# Create a Pandas Excel writer using XlsxWriter as the engine.
	from pandas import ExcelWriter
	from datetime import date 

	with ExcelWriter('excel_output_ONLY_DB_'+(date.today()).strftime("%Y-%m-%d")+'.xlsx', engine='xlsxwriter') as writer:
		price_info_asDF.to_excel(writer, sheet_name= "price_info")
		price_info_asDF_color.to_excel(writer, sheet_name= "price_infoCOLOR")
		listings.to_excel(writer, sheet_name= "airbnb_listings")
	# Close the Pandas Excel writer and output the Excel file.
	writer.save()
	writer.close()

	# Create a .txt log message
	file = open('testfile_ONLY_DB_'+(date.today()).strftime("%Y-%m-%d")+'.txt',	'w+') 

	file.write('log message '+ (date.today()).strftime("%Y-%m-%d"))

	file.close() 

	print("Elapsed time to complete Excel writing: " +  str(time.time() - start_time4))