#python3 Distance20210723.py 'pred_aug0_EDF 03 - EST-06.txt' 30 beam column
from shapely.ops import nearest_points
from shapely.geometry import Polygon
import sys
import ast
import json
import os
import re


pivotItemsList = []
dependentItemsList = []


def getItemsLists(lines, pivot_element, dependent_element):
    #Convierte cada linea en diccionario y asigna las columnas al listado de pivotes y las vigas al listado de dependientes
    pivot = []
    dependent = []

    index_c = 0
    index_b = 0

    for line in lines:
        dictionary = ast.literal_eval(line)
        if dictionary["elem"] == dependent_element:
            dependent.append(dictionary)
            dictionary["elem"] = dictionary["elem"] + str(index_b)
            index_b = index_b + 1
        elif dictionary["elem"] == pivot_element:
            pivot.append(dictionary)
            dictionary["elem"] = dictionary["elem"] + str(index_c)
            index_c = index_c + 1
    return dependent, pivot


def checkMinimumDistance(path_file, pivotItems, dependentItems):
    filename = path_file.split('/')[len(path_file.split('/')) - 1]
    print(filename)
    filename = filename + "_relacionados" + str(cota) + '.txt' #genero un archivo de texto por cada imagen de test
    txt = open(filename,'w') #abro en modo escritura

    for pivotItem in pivotItems:
        cercanos = []
        pivotPoints = pivotItem['points']
        pivot = Polygon([(int(pivotPoints['x1']), int(pivotPoints['y1'])), (int(pivotPoints['x1']), int(pivotPoints['y2'])),
                        (int(pivotPoints['x2']), int(pivotPoints['y1'])), (int(pivotPoints['x2']), int(pivotPoints['y2']))])

        for dependentItem in dependentItems:
            dependentPoints = dependentItem['points']
            dependent = Polygon([(int(dependentPoints['x1']), int(dependentPoints['y1'])), (int(dependentPoints['x1']), int(dependentPoints['y2'])),
                                 (int(dependentPoints['x2']), int(dependentPoints['y1'])), (int(dependentPoints['x2']), int(dependentPoints['y2']))])
            p1, p2 = nearest_points(pivot, dependent)

            points_distance = p1.distance(p2)
            #print("Beam: " + dependentItem['elem'] +
             #     " - Distancia: " + str(p1.distance(p2)))

            #Si la distancia es menor a una cota determinada, guardo el elemento dependiente como cercano
            if points_distance < cota:
                cercanos.append(dependentItem)


        pivotItem["relItems"] = cercanos

        txt.write((str(pivotItem) + '\n')) #escribo el elemento pivot con sus relacionados


    #Aplico a la salida formato pseudo json
    txt.close()
    return
    

def readAndGet(path_file, pivot_element, dependent_element):
    #Verifico que el archivo exista
    try:
        archivo = open(path_file, 'r')
    except:
        print('El archivo no existe')
        exit(0)

    #Obtengo todas las lineas
    lines = archivo.readlines()

    #Obtengo los listados
    dependentItemsList, pivotItemsList = getItemsLists(lines, pivot_element, dependent_element)

    output = checkMinimumDistance(path_file, pivotItemsList, dependentItemsList)

########################################################

#Verifico cantidad de parametros
if len(sys.argv) < 5:
    print('Falta un argumento --> predictionsFile_path cota pivot dependent')
    exit(0)

#Asigno los parametros
path_file = sys.argv[1]
cota = int(sys.argv[2])

posibles = ['beam', 'column', 'slab']

pivot_element = sys.argv[3]
dependent_element = sys.argv[4]

if pivot_element not in posibles or dependent_element not in posibles:
    print('Elemento pivote o dependiente invalido. Opciones: beam, column, slab')
    exit(0)


if os.path.isdir(path_file):
    for filename in os.listdir(path_file):
        if filename.startswith("pred_") and '_relacionados' not in filename:
            path_file = os.getcwd() + '/' + filename
            print(path_file)
            readAndGet(path_file, pivot_element, dependent_element)
    print('Proceso terminado ... \n')
    exit(0)

readAndGet(path_file, pivot_element, dependent_element)
print('Proceso terminado ... \n')

#Guardo el output en relacionados.json
exit(0)
