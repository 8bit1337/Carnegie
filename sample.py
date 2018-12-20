# written by Jason Gruetzmacher

import pandas as pd
import numpy as np
from sys import exit as errorMsg, argv as sys_argv
import matplotlib.pyplot as plt

def main(argv):
  #Variable Assumptions
  samples=200   #the total number of samples I want in the export
  minsamples=3  #the minimum number of samples I think I should take, regardless of population size
  sampled_df=pd.DataFrame(columns=['sensorid','sensortype'])  #dataframe to contain our sampled sensors
  
  #Open the file and get the data into a dataframe
  try:  
    input_file = argv[1]
    input_df=pd.read_csv(input_file, sep=',', header=0)
  except:
    errorMsg('Could not open provided file. ')
      
  #Group the data by sensorid, creating a new field that indicates which type(s) a sensor is
  #I also want to know how many unique IDs there are
  sensors_df=input_df.groupby('sensorid')['sensortype'].apply(' '.join).reset_index()
  numsensors=sensors_df.count()[0]
  
  
  #Here we randomize the index, so that we can add a minimum number of sensors to our final dataframe
  sensors_df.reindex(index=np.random.permutation(sensors_df.index))
  
  #if there are less than 200 sensors in the file, just return everything
  if numsensors== 200:
    sampled_df=sampled_df.append(sensors_df)
  else:
    #Group by sensor type, so we can get a sense of what our sample population should look like
    #In this dataframe, 'sensorid' actuall contains a count of sensor, not actual IDs
    #After I've calculated the weights I don't need the counts any longer
    types_df=sensors_df.groupby('sensortype').count().reset_index()
    types_df['weights']=types_df['sensorid']/numsensors
    
    for types in types_df['sensortype']:
      min_df=sensors_df.query("sensortype=='"+types+"'").sample(n=minsamples)
      sampled_df=sampled_df.append(min_df, ignore_index=True)
      samples-=min_df.size  #we need to reduce the number of overall samples we require as we take minimums
      
    #Removing unnecessary column for this next step
    del types_df['sensorid']

    #Now we merge the two dataframes, to give me a weighting for each sensortype
    merged_df=sensors_df.set_index('sensortype').join(types_df.set_index('sensortype')).reset_index()
  
    #Using the weights above, sample the remaining sensors and add to our sampled_df
    sampled_df=sampled_df.append(merged_df.sample(n=samples, weights=merged_df.weights))
  
  #Final data presentation:
  #  - print a graph showing what %s we have of each combination of type
  #  - split the sensortype field back into it's own rows, to match input file
  #  - remove unnecessary columns
  #  - make the sensorid the index so that the to_csv function gives us a clean csv
  
  #Create the graph before we switch the data to it's final format
  
  report_df=sampled_df.groupby(['sensortype']).size().reset_index(name='counts')
  labels=tuple(report_df['sensortype'].tolist())
  counts=tuple(report_df['counts'].tolist())
  n=len(labels)
  index=np.arange(n)
  
  fig, ax = plt.subplots()
  plt.bar(index, counts)
  plt.xticks(index, labels, rotation='vertical')
  plt.xlabel('Types')
  plt.ylabel('Count')
  for i in range(n):
    plt.text(i-.1, counts[i]+.5, "{0:0}".format(counts[i]))
  plt.show()
  
  #Now create our csv for export
  split_df=sampled_df['sensortype'].str.split(' ').apply(pd.Series, 1).stack()
  split_df.index = split_df.index.droplevel(-1)
  split_df.name='sensortype'
  del sampled_df['sensortype']
  del sampled_df['weights']
  final_df=sampled_df.join(split_df).set_index('sensorid')
  final_df.to_csv('output.csv')

  return True
    
  
if __name__ == '__main__':
  main(sys_argv)