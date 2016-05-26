import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import csv

entities = []
outdegree = []

with open('dataset_outdegree.csv', 'rb') as csvfile:
	classreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	for row in classreader:
		entities.append(row[0])
		outdegree.append(row[1])


plt.plot(outdegree, 'b-',linestyle='None', marker='.')
plt.title(("Out degree by entity"))
plt.ylabel("outdegree")
plt.xlabel("entity")
plt.show()