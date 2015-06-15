# coding: utf-8

#!/usr/bin/python
import sys, getopt, os


def main(argv):
    usage_text = 'model.py -o <outputfile> -p <paras[]> -ch <choice_var> -w <weight> -c <weight_calibration>'
    weight = "1.0"
    weight_cal = "1.0"
    beta= []
    output = "modell.py"
    choice = "CHOICE"
    
    py = ""
    
    try:
        opts, args = getopt.getopt(argv,"o:p:c:w:n:",["output=","pars=","choice=","weight=","weight-cal="])
    except getopt.GetoptError:
        print (usage_text)
        sys.exit(2)
            
    for opt, arg in opts:
        if opt == '-h': #HELP!
            print (usage_text)
            sys.exit()

        elif opt in ("-p", "--pars"): # List of model parameters for V_CS
            beta = arg
        elif opt in ("-w", "--weight"): # weights the FFCS_USER-data
            weight = arg
        elif opt in ("-n", "--weight-cal"): # recalibrates the weight
            weight_cal = arg
        elif opt in ("-o", "--output"):
            output_dir = arg
            output = arg + ".py"
        elif opt in ("-c", "--choice"):
            choice = arg
            
    print ("Output file: ", output)
    print ('parameters are ', beta)
    print ('choice var is ', choice)
    print ('Weight is ', weight)
    print ('Weight calibration is ', weight_cal)
    
    py = """from biogeme import *
from headers import *
from loglikelihood import *
from statistics import *

# Arguments:
#   - 1  Name for report; Typically, the same as the variable.
#   - 2  Starting value.
#   - 3  Lower bound.
#   - 4  Upper bound.
#   - 5  0: estimate the parameter, 1: keep it fixed.

ASC = Beta('ASC',0,-100,100,0)
"""
    
    V1 = "ASC"

    for par in beta:
        s = "B_"+str(par) #name of beta par
        b = "Beta("+"'"+s+"'"+",0,-100,100,0)" #definition of beta par
        
        py += s+" = "+b+"\n" #append B_par to list of parameters
        V1 += " + "+s+" * "+str(par) #prepare utility function
        #print(V1)
    
    py += """
V0 = 0
V1 = """+V1+"""

V = {0: V0, 1: V1}

# Availability
AVAIL = 1

av = {0: 1, 1: AVAIL}

# Model
prob = bioLogit(V,av,"""+choice+""")
logP = log(prob)

# Weight
weightM = """+str(weight_cal)+" * (1.0 * ("+choice+" == 0) + "+str(weight)+" * ("+choice+""" == 1))

# Defines an itertor on the data
rowIterator('obsIter') 

# Define the likelihood function for the estimation
BIOGEME_OBJECT.WEIGHT = weightM
BIOGEME_OBJECT.ESTIMATE = Sum(logP,'obsIter')

# Statistics
nullLoglikelihood(av,'obsIter')
choiceSet = [0,1]
cteLoglikelihood(choiceSet,"""+choice+"""   ,'obsIter')
availabilityStatistics(av,'obsIter')

BIOGEME_OBJECT.PARAMETERS['optimizationAlgorithm'] = 'CFSQP'
BIOGEME_OBJECT.PARAMETERS['numberOfThreads'] = '2'"""

    

    # make dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    fname = os.path.join(output_dir,output)    
    
    with open(fname, "w") as text_file:
        print(py, file=text_file)

if __name__ == "__main__":
   main(sys.argv[1:])