#!/usr/bin/env python

"""Test driving wrapper.
"""

usageMessage = """Usage: tdw.py INPUTFILE
Process and run population genetics statistics on an INPUTFILE.
Expects to find a file called 'config.ini' in the current directory.

  INPUTFILE   input text file"""

import sys, os

from ParseFile import ParseGenotypeFile
from HardyWeinberg import HardyWeinberg, HardyWeinbergGuoThompson
from Homozygosity import Homozygosity
from ConfigParser import ConfigParser, NoOptionError

if len(sys.argv) != 2:
  sys.exit(usageMessage)

fileName = sys.argv[1]

config = ConfigParser()

if os.path.isfile("config.ini"):
  config.read("config.ini")
else:
  sys.exit("Could not find config.ini" + os.linesep + usageMessage)
				
if len(config.sections()) == 0:
	sys.exit("No output defined!  Exiting...")

# Parse "General" section

try:
	debug = config.getboolean("General", "debug")
except NoOptionError:
	debug=0
except ValueError:
	sys.exit("require a 0 or 1 as debug flag")

if debug:
  for section in config.sections():
    print section
    for option in config.options(section):
      print " ", option, "=", config.get(section, option)


# Parse "ParseFile" section
try:
	alleleDesignator = config.get("ParseFile", "alleleDesignator")
except NoOptionError:
	alleleDesignator = '*'

try:
	untypedAllele = config.get("ParseFile", "alleleDesignator")
except NoOptionError:
	untypedAllele = '****'



input = ParseGenotypeFile(fileName, 
			  alleleDesignator=alleleDesignator, 
			  untypedAllele=untypedAllele,
			  debug=debug)


popData = input.getPopData()
for summary in popData.keys():
 	print "%20s: %s" % (summary, popData[summary])

loci = input.getLocusList()
loci.sort()
for locus in loci:
  print "\nLocus:", locus
  print "======\n"
  
  
  # Parse "HardyWeinberg" section
  
  if config.has_section("HardyWeinberg") and \
     len(config.options("HardyWeinberg")) > 0:
    
    try:
      lumpBelow =  config.getint("HardyWeinberg", "lumpBelow")
    except NoOptionError:
      lumpBelow=5
    except ValueError:
      sys.exit("require integer value")

    hwObject = HardyWeinberg(input.getLocusDataAt(locus), 
                             input.getAlleleCountAt(locus), 
                             lumpBelow=lumpBelow,
                             debug=debug)

      
    try:
      if config.getboolean("HardyWeinberg", "outputChisq"):
        hwObject.getChisq()
    except NoOptionError:
      pass
    except ValueError:
      sys.exit("require a 0 or 1 as a flag")

    # guo & thompson implementation
    hwObject = HardyWeinbergGuoThompson(input.getLocusDataAt(locus), 
                                        input.getAlleleCountAt(locus), 
                                        lumpBelow=5,
                                        debug=debug)

    # FIXME: for testing purposes, set stream to be stdout
    hwObject.dumpTable(locus, sys.stdout)

  # Parse "Homozygosity" section
	
  if config.has_section("Homozygosity") and \
     len(config.options("Homozygosity")) > 0:
          
    try:
      rootPath=config.get("Homozygosity", "rootPath")
    except NoOptionError:
      sys.exit("If homozygosity statistics are run, path to the simulated data sets must be provided")


    hzObject = Homozygosity(input.getAlleleCountAt(locus),
                                    rootPath=rootPath,
                                    debug=debug)
            
    try:
      if config.getboolean("Homozygosity", "outputObservedHomozygosity"):
        print "Fo = ", hzObject.getObservedHomozygosity()
    except NoOptionError:
      pass
    except ValueError:
      sys.exit("require a 0 or 1 as a flag")
          
    if hzObject.canGenerateExpectedStats():
      try:
        if config.getboolean("Homozygosity", "outputCount"):
          print "count = ", hzObject.getCount()
      except NoOptionError:
        pass
      except ValueError:
        sys.exit("require a 0 or 1 as a flag")
                  
      try:
        if config.getboolean("Homozygosity", "outputMean"):
          print "mean of Fe = ", hzObject.getMean()
      except NoOptionError:
        pass
      except ValueError:
        sys.exit("require a 0 or 1 as a flag")
                                                
      try:
        if config.getboolean("Homozygosity", "outputVar"):
          print "var of Fe = ", hzObject.getVar()
      except NoOptionError:
        pass
      except ValueError:
        sys.exit("require a 0 or 1 as a flag")

      try:
        if config.getboolean("Homozygosity", "outputSem"):
          print "sem of Fe = ", hzObject.getSem()
      except NoOptionError:
        pass
      except ValueError:
        sys.exit("require a 0 or 1 as a flag")

      try:
        if config.getboolean("Homozygosity", "outputPValueRange"):
          print "%f < pval < %f" % hzObject.getPValueRange()
      except NoOptionError:
        pass
      except ValueError:
        sys.exit("require a 0 or 1 as a flag")

    else:
      print "Can't generate expected stats"

