import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Connecting with database
conn = sqlite3.connect("database.db")
cur = conn.cursor()

# Grabing data from tables
data = pd.read_sql("SELECT * FROM data",conn)
connection = pd.read_sql("SELECT * FROM connection",conn)
additional_data = pd.read_sql("SELECT * FROM additional_data",conn)

# Changing indexes, so merge won't generate extra columns
data = data.set_index('id')
connection = connection.set_index('id')

# Merging tables
df = data.merge(connection,how='left',left_on='connection_id',right_index=True)
df = df.merge(additional_data,how='inner',left_on='name',right_on='color_name')

# Ensuring that values types are correct
df['x'] = pd.to_numeric(df['x'])
df['y'] = pd.to_numeric(df['y'])
df['z'] = pd.to_numeric(df['z'])
df['color_id'] = pd.to_numeric(df['color_id'])

# Few more drops 
df = df.drop(['name', 'connection_id'],axis=1)
df = df.dropna()
df.columns = ['x', 'y', 'z', 'color_id', 'color']

# Printing unique values from 'color' column
unique_color = df['color'].unique()
print(unique_color)

# Dropping all points, but those with z = 100
df = df.where(df['z'] == 100).dropna()



# Method to find red points that are not far from 'avrage red'.
def avrg_red(df,sigma):
    
    # Prepering DataFrame with red points
    reds = df[['x','y','z']].where(df['color'] == 'red').dropna()
    
    # Calculating "avrage red point" (ARP)
    avrg = reds[['x','y','z']].mean(axis=0).values
    print(avrg)
    #Calculating distance from ARP for each point
    reds['dist'] = np.linalg.norm(reds[['x','y','z']].values - avrg, axis=1)

    # Collecting indexes of points that are closer from ARP then sigma
    indexes = reds.where(reds['dist'] > sigma).dropna().index
    
    return indexes


# Calling out method
sigma = 5
indexes = avrg_red(df,sigma)
df = df.drop(index=indexes)

# Changing index
df.index = np.arange(0, len(df))

# Saving to HDF5
ns1 = df.drop(columns=['z','color_id'])
ns1.to_hdf('ns1.h5',key='ns1')

# Plotting Mr. Smile
plt.scatter(pd.read_hdf('ns1.h5',key='ns1').values[:,0],
            pd.read_hdf('ns1.h5',key='ns1').values[:,1],
            c=pd.read_hdf('ns1.h5',key='ns1').values[:,2])
plt.show()
