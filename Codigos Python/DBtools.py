import pandas as pd
import numpy as np
from datetime import date, timedelta
import tempfile
from funcTools import is_nan

### For DB ###
def read_sql_tmpfile(query, db_engine):
    with tempfile.TemporaryFile() as tmpfile:
        copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(
           query=query, head="HEADER"
        )
        conn = db_engine.raw_connection()
        cur = conn.cursor()
        cur.copy_expert(copy_sql, tmpfile)
        tmpfile.seek(0)
        df = pd.read_csv(tmpfile)
        return df

def df_price_info(price_info):
      
    start = pd.to_datetime(price_info.at[price_info.index[0],'date'])
    end = pd.to_datetime(price_info.at[price_info.index[price_info.shape[0]-1],'date'])
    date_generated = [start + timedelta(days=x) for x in range((end-start).days+1)]    
    date_strings = [d.strftime('%Y-%m-%d') for d in date_generated]

    grouped_price_info = price_info.groupby(['airbnb_listing_id'])

    content = np.full((len(grouped_price_info), len(date_strings)),'__N/A__')
    content_color = np.full((len(grouped_price_info), len(date_strings)),'__WHITE__')

    price_info_indexer = []

    for name, group in grouped_price_info:
        
        price_info_indexer.append(name)

        results = []

        for row_index, row in group.iterrows():

            if not is_nan(row['price']):

                content[len(price_info_indexer)-1,date_strings.index(row['date'])] = row['price']

                if row['available'] == 't':

                    content_color[len(price_info_indexer)-1,date_strings.index(row['date'])] = 'RED'

                else:

                    content_color[len(price_info_indexer)-1,date_strings.index(row['date'])] = 'GREEN'
            else:

                content[len(price_info_indexer)-1,date_strings.index(row['date'])] = 'Booked'
                content_color[len(price_info_indexer)-1,date_strings.index(row['date'])] = 'YELLOW'

            # after this it will find the consecutive blocked days (and make all them grey)               
            if row['date'] > (date.today()).strftime("%Y-%m-%d"):

                if content_color[len(price_info_indexer)-1,date_strings.index(row['date'])] == 'RED':

                    if len(results) >= 25:

                        content_color[len(price_info_indexer)-1,results] = 'GREY'

                    results = []

                else:

                    results.append(date_strings.index(row['date']))

        if len(results) >= 25:

            content_color[len(price_info_indexer)-1,results] = 'GREY'

    price_info_asDF = pd.DataFrame(data=content,index=price_info_indexer,columns=date_strings)
    price_info_asDF = price_info_asDF.astype(str)
    price_info_asDF_color = pd.DataFrame(data=content_color,index=price_info_indexer,columns=date_strings)
    price_info_asDF_color = price_info_asDF_color.astype(str)

    return price_info_asDF, price_info_asDF_color 