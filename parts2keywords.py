# Copyright (C) 2016 Brandon C Tardio btardio@gmail.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


#
# This script parses multiple files and creates in-order keyword combinations
# from the files given. The script processes one unique symbols per file,
# <skip>. If it encounters <skip>, that file will be skipped for the combination.
#

import sys
import shutil
import os
import itertools
import collections
from itertools import permutations


# recursive print all possible combinations of a list
def rprintb ( previous, lst, dct ):
 
  # create combinations of the first item in the list 
  for item in itertools.combinations ( lst[0], 1 ):
    
    outstr = ''
    
    # append the item in the list to previous list
    # ie: create a list ready for converting to str and printing
    previous.append ( item )
    
    # prepare a printable string
    for a in previous:
      if a[0] != '<skip>':
        outstr += '%s ' % a[0]
    dct [ outstr ] = ''
    
    # if the length of the list is greater than 1, recur
    if len ( lst ) > 1:
      dct.update ( rprintb ( previous, lst[1:], dct ) )
    
    # pop the last element of the list in preparation
    # for the next combination
    previous.pop() 
    

  return dct
def processparts ( lst ):

  # list a item 0


  dct = {}


  dct.update ( rprintb ( [('',),], lst, dct ) )

  for key, value in dct.iteritems():
    print ( key.strip() )     


# creates a list of lines read from the file
def listfromfile ( filename ):

  outlst = []

  # open the file
  f = open ( filename, 'r' )

  # read lines from the file and append to outlst
  for line in f:
    if line.strip() != '':
      outlst.append( line.strip() )

  # return the lst
  return outlst


# __main__ program entry point
if __name__ == '__main__':

  # print usage
  if ( len ( sys.argv ) <= 1 or sys.argv[1] == '' ):
    print ( 'Usage: ./python parts2keywords.py [filename1] [filename2] ...' )

  outfileslst = []

  # delete the old processing directory
  try:
    shutil.rmtree( './_parts2keywords_process' )
  except BaseException as e:
    print ( e )

  # make a new processing directory
  try:
    os.mkdir ( './_parts2keywords_process' )
  except BaseException as e:
    print ( e )

  lstsoflsts = []

  # for each file name passed as argument
  for arg in sys.argv:

    # skip the program name
    if arg == sys.argv[0]: pass
    else:
      # create a list from the file
      lst = listfromfile ( arg )
      #lstsoflsts.append ( list ( enumerate ( lst ) ) )

      lstsoflsts.append ( lst )

      #outlst = combine ( outlst, lst )

  processparts ( lstsoflsts )

  # convert the lst to a string for processing
  #lsttostr ( outlst )
