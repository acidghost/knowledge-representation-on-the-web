import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import csv

classes = []
count = []

with open('dataset_frequency.csv', 'rb') as csvfile:
	classreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	for row in classreader:
		classes.append(row[0])
		count.append(row[1])


plt.plot(count, 'b-',linestyle='None', marker='.')
plt.title(("Frequencies by class"))
plt.ylabel("frequency")
plt.xlabel("class")
plt.show()