import sys
import os
import numpy as np
import pandas as pd
from numbers import Number
import sqlalchemy as sqla
from sqlalchemy import *
import re
from collections import defaultdict
import base64
import logging
import datetime
import zipcode
sys.path.append('C:\\Users\\BFEF Conference Room\\bfef\\hyperqual\\hyperqual')
from hqutilities.utils import *
from hqutilities.utils import bfefsetup
from hqutilities.utils.bfefsetup import *

from hqutilities.utils import bfefdb
from hqutilities.utils import solarpvdb
from hqutilities.utils import lmsdb
from hqutilities.utils.lmsdb import *



#Geo Eligibility Assumed: NY, CA, TX

#
#
#
# h = LmsDb("BFEF")
# s = h.Session()

def readInputs(fdir="BluePacePrequalIntake.xlsx", sheetName="Parameters"):
    return pd.read_excel(fdir, sheetname=sheetName, index_col=0, header=None).to_dict()[1]



def involLienChk(involLienAmt, involLienReq=1000):
    if involLienAmt < involLienReq:
        return True
    else:
        return False

def lienToPropValueChk(propDebt, propValue,ltvReq=0.8, closingFees=0.1):
    if propDebt < (propValue * ltvReq):
        return True
    else:
        return False
def cLienToPropValueChk(paceAmt, propDebt, propValue,cLtvReq=0.9, closingFees=0.1):
    if (paceAmt + propDebt) < (propValue * cLtvReq):
        return propValue * cLtvReq
    else:
        ans = float(propValue * cLtvReq) - propDebt
        if ans > 0:
            return ans
        else:
            return 0
def maxFinancingOfPropValue(propValue, maxFinancingReq=0.2, closingFees=0.1):
    return float(propValue * maxFinancingReq)*float(1- closingFees)

def maxAnnAssessment(annTaxes,propValue, maxFinancingReq=0.05, closingFees=0.1):
    return float(float((float(maxFinancingReq) - (float(annTaxes)/float(propValue))))*float(propValue)) *float(1- closingFees)

def maxFinancingOfAnnPay(annTaxes,propValue, term=20, rate=0.06, maxFinancingReq=0.05, closingFees=0.1):
    maxAnn = maxAnnAssessment(annTaxes, propValue, maxFinancingReq)
    return np.pv(rate, term, maxAnn)* ((-1)*(1-float(closingFees)))
def projectMinChk(projCost, projMin=20000):
    if projCost < projMin:
        return False
    else:
        return True
def getMaxFinancing(propDebt,annTaxes, propValue, term=20, rate=0.06, maxFinancingReq=0.05, cLtvReq=0.9, closingFees=0.1):
    maxList = [maxFinancingOfAnnPay(annTaxes, propValue, term, rate, maxFinancingReq, closingFees),
               maxFinancingOfPropValue(propValue, maxFinancingReq, closingFees)]
    #ltvChk = lienToPropValueChk(propDebt, propValue, ltvReq=0.8, closingFees=0.1)
    minMax = min(maxList)
    cLtvChk = cLienToPropValueChk(minMax, propDebt, propValue,cLtvReq, closingFees)
    return min(minMax, cLtvChk)
print getMaxFinancing(800000.05,13000.03, 1100000.03, term=20, rate=0.06, maxFinancingReq=0.05, cLtvReq=0.9, closingFees=0.1,)

def paceEligibility(zip, projectCost, currMrtgFlag, CurrPropTaxFlag, propDebt, propValue,annTaxes, involLienAmt, involLienReq=1000,ltvReq=0.8, closingFees=0.1, elgStates=['CA','NY', 'TX'],term=20, rate=0.06, maxFinancingReq=0.2, cLtvReq=0.9):
    if not involLienChk(involLienAmt, involLienReq):
        return False
    if not lienToPropValueChk(propDebt, propValue,ltvReq, closingFees):
        return False
    if not currMrtgFlag:
        return False
    if not CurrPropTaxFlag:
        return False
    if not projectMinChk:
        return False
    if zipcode.isequal(str(zip)).state not in elgStates:
        return False
    return getMaxFinancing(propDebt,annTaxes, propValue, term, rate, maxFinancingReq, cLtvReq, closingFees)



print paceEligibility(92101, 500000, 1, 1, 750000, 1500000,15000, 0, involLienReq=1000,ltvReq=0.8, closingFees=0.1, elgStates=['CA','NY', 'TX'],term=20, rate=0.06, maxFinancingReq=0.2, cLtvReq=0.9)
            # print maxFinancingOfPropValue(500000, maxFinancingReq=0.2, closingFees=0.1)
#
# print maxFinancingOfAnnPay(15000,500000, term=20, rate=0.06, maxFinancingReq=0.05, closingFees=0.1)

#print maxFinancingOfAnnPay(15000,800000, term=20, rate=0.06, maxFinancingReq=0.05, closingFees=0.1)
#print maxAnnAssessment(2000,2000000, maxFinancingReq=0.05)
#print readInputs(fdir="BluePacePrequalIntake.xlsx", sheetName="Parameters")
# print cLienToPropValueChk(300000, 800000, 1100000,cLtvReq=0.9, closingFees=0.1)
# if cLienToPropValueChk(300000, 800000, 1100000,cLtvReq=0.9, closingFees=0.1) is True:
#     print "YES"