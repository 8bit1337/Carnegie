# written by Jason Gruetzmacher

import pandas as pd
import numpy as np
from random import shuffle
from sys import exit as errorMsg, argv as sys_argv
import matplotlib.pyplot as plt

def main(argv):
  #Variable Assumptions
  samples=200   #the total number of samples I want in the export
  minsamples=5  #the minimum number of samples I think I should take, regardless of population size
  
  #Open the file and get the data into a dataframe
  try:  
#    inputfile = argv[1]
    input_file='iot-sensors.csv'
    input_df=pd.read_csv(input_file, sep=',', header=0)
  except:
    errorMsg('Could not open provided file. ')
      
  #Group the data by sensorid, creating a new field that indicates which type(s) a sensor is
  #I also want to know how many unique IDs there are
  sensors_df=input_df.groupby('sensorid')['sensortype'].apply(' '.join).reset_index()
  numsensors=sensors_df.count()[0]
  
  
  #Here we randomize the index, so that we can add a minimum number of sensors to our final dataframe
  sensors_df.reindex(index=np.random.permutation(sensors_df.index))
  sensors_df.to_csv('merged_types.csv')
  
  #if there are less than 200 sensors in the file, just return everything
  if numsensors== 200:
    final_df=sensors_df
  else:
    sampled_df=pd.DataFrame(columns=['sensorid','sensortype'])
    
    #Group by sensor type, so we can get a sense of what our sample population should look like
    #In this dataframe, 'sensorid' actuall contains a count of sensor, not actual IDs
    #After I've calculated the weights I don't need the counts any longer
    types_df=sensors_df.groupby('sensortype').count().reset_index()
    types_df['weights']=types_df['sensorid']/numsensors
    
    for types in types_df['sensortype']:
      min_df=sensors_df.query("sensortype=='"+types+"'").sample(n=minsamples)
      sampled_df=sampled_df.append(min_df, ignore_index=True)
      samples-=minsamples
      
    #I'm removing this column for the merged_df join
    del types_df['sensorid']

    #Now we merge the two dataframes, to give me a weighting for each sensortype
    merged_df=sensors_df.set_index('sensortype').join(types_df.set_index('sensortype')).reset_index()
  
    #Using the weights above, sample the remaining sensors and add to our sampled_df
    sampled_df=sampled_df.append(merged_df.sample(n=samples, weights=merged_df.weights))
    sampled_df.to_csv('sampled.csv')
  
    #Final data presentation:
    #  - split the sensortype field back into it's own rows, to match input file
    #  - remove unnecessary columns
    #  - make the sensorid the index so that the to_csv function gives us a clean csv
    split_df=sampled_df['sensortype'].str.split(' ').apply(pd.Series, 1).stack()
    split_df.index = split_df.index.droplevel(-1)
    split_df.name='sensortype'
    del sampled_df['sensortype']
    del sampled_df['weights']
    final_df=sampled_df.join(split_df).set_index('sensorid')
    
  #Now that we've created our final_dataframe, export it
  final_df.to_csv('output.csv')
#
#output results to bar chart
#  plt.bar(x, y, width, color="blue")

#  print(final_df.groupby('sensortype').apply(list))


  return True
    
  
if __name__ == '__main__':
  main(sys_argv)