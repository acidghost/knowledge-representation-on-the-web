import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import csv

entities = []
indegree = []

with open('dataset_indegree.csv', 'rb') as csvfile:
	classreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	for row in classreader:
		entities.append(row[0])
		indegree.append(row[1])


plt.plot(indegree, 'b-',linestyle='None', marker='.')
plt.title(("In degree by entity"))
plt.ylabel("indegree")
plt.xlabel("entity")
plt.show()