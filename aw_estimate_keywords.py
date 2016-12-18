# aw_estimate_keywords | aw_estimate_keywords prints keywords with estimate data
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


###
###
### This Python script reads a list of lines from a command line argument
### file and for every 2500 lines in the file queries the AdWords API
### to determine if the keyword on the line has daily impression data.
### Keywords that have daily impression data are printed to console.
### 
### The script checks that keywords are less than 80 characters and
### greater than 4 characters. The script checks that lines do not 
### contain more than 9 spaces so as to have no keywords with more
### than 10 words.
###
### It is assumed that pre-processing of input file includes no duplicate
### entries. Per query duplicates checking is performed as well.
###      


from googleads import adwords
from math import ceil
from itertools import permutations
from time import sleep
import pprint
import sys
import io

# returns a list of important keywords depending on impressionsPerDay
# only returns keywords that have impressionsPerDay > 0
def get_important_keywords ( inkeywords, inrsltslst ):

  outlst = []

  for keyword, rslt in zip ( inkeywords, inrsltslst ):

    #if ( rslt['max']['impressionsPerDay'] != 0 ):
    #  outlst.append ( keyword )

    if ( rslt['max']['impressionsPerDay'] != 0 or 
         'averagePosition' in rslt['max'] ):
      outlst.append ( keyword )

  return outlst 

  
# returns a list of KeyWordEstimate results, formats get query to python list
def results_as_list ( estimates ):
  outlst = []

  templst = estimates['campaignEstimates'][0]['adGroupEstimates'][0]

  for i in templst['keywordEstimates']:
    outlst.append ( i )

  return outlst

# returns xsi-type compatible keywordEstimateRequests
def requestforkeyword ( keyword ):

  rval = { 
           'keyword':
              {
                'xsi_type': 'Keyword',
                'text': keyword.strip(),
                'matchType': 'EXACT'
              }
         }
  
  return rval


# returns xsi-type compatible adGroupEstimateRequests
def requestforadgroup ( keywordlst ):

  kwrequestlst = []

  for i in keywordlst:
    # keywords can't be longer than 80 characters 
    # and can't include more than 10 words, check for this
    # also check if keyword is greater than 4 characters
    if ( len ( i ) < 4 or len ( i ) > 80 or i.count(' ') > 9 ):
      pass
    else:
      
      newkw = requestforkeyword ( i )
      
      # check for duplicate element
      if newkw not in kwrequestlst:
        kwrequestlst.append ( requestforkeyword ( i ) )

  rval = {
           'keywordEstimateRequests': kwrequestlst,
           'maxCpc': { 'xsi_type': 'Money', 'microAmount': '2000000' },
         }

  return [rval]

# returns xsi-type compatible campaignEstimateRequests
def requestforcampaign ( keywordlst ):

  rval = {
           'adGroupEstimateRequests': requestforadgroup ( keywordlst ),
           'criteria': 
           [
             { 'xsi_type': 'Location', 'id': '2840' },
             { 'xsi_type': 'Language', 'id': '1000' },
           ],
         }

  return [rval]

# returns selector, creates final selector for get query
def requestSelector ( keywordlst ):
 
  selector = { 
               'campaignEstimateRequests': requestforcampaign ( keywordlst ),
             }

  return selector 

# query the AdWords API for the given keyword list
def queryandprint ( service, keywordlst ):
  # create a selector from list of keywords
  selector = requestSelector ( keywordlst )

  # query AdWordsAPI
  estimates = service.get ( selector )

  sleep ( 5 )

  # structure the results
  rslts = results_as_list ( estimates )

  # filter returned query for important keywords
  importantkeywords = get_important_keywords ( keywordlst, rslts )

  # output keywords
  for keyword in importantkeywords:
    if keyword.find('[') != -1 and keyword.find(']') != -1:
      print ( '%s' % keyword.strip() )
    else:
      print ( '[%s]' % keyword.strip() )


def main ( client ):
  
  if len ( sys.argv ) < 2:
    print ( 'Usage: python aw_estimate_keywords.py [filename]' )
    return

  service = client.GetService ( 'TrafficEstimatorService', version='v201609' )

  file = io.open ( sys.argv[1], 'r' )

  keywordlst = []

  for line in file:

 
    keywordlst.append ( line )

    # every 2500 lines create a selector and call AdWordsAPI for selector
    if len ( keywordlst ) >= 2500:

      # reached max number of keywords per query, query and print
      queryandprint ( service, keywordlst )

      # reset list for next iteration
      keywordlst = []

  # reached the end of the file, query and print
  queryandprint ( service, keywordlst )

  # unique criteria for keyword that doesn't have google data
  # impressionsPerDay = 0.0
  # hasattr 'averagePosition' = False
  # hasattr 'clickThroughRate' = False
  #   

if __name__ == '__main__':

  client = adwords.AdWordsClient.LoadFromStorage()

  main ( client )
