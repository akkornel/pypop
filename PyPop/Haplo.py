#!/usr/bin/env python

# This file is part of PyPop

# Copyright (C) 2003-2005. The Regents of the University of California (Regents)
# All Rights Reserved.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

# IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT,
# INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING
# LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS
# DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED OF THE POSSIBILITY
# OF SUCH DAMAGE.

# REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE. THE SOFTWARE AND ACCOMPANYING
# DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED "AS
# IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT,
# UPDATES, ENHANCEMENTS, OR MODIFICATIONS.


"""Module for estimating haplotypes.

"""
import sys, string, os, re, cStringIO
import numpy

from Arlequin import ArlequinBatch
from Utils import getStreamType, appendTo2dList, GENOTYPE_SEPARATOR, GENOTYPE_TERMINATOR
from DataTypes import checkIfSequenceData, getLocusPairs

class Haplo:
    """*Abstract* base class for haplotype parsing/output.

    Currently a stub class (unimplemented).
    """
    pass

class HaploArlequin(Haplo):
    """Haplotype estimation implemented via Arlequin
    
    Outputs Arlequin format data files and runtime info, also runs and
    parses the resulting Arlequin data so it can be made available
    programatically to rest of Python framework.

    Delegates all calls Arlequin to an internally instantiated
    ArlequinBatch Python object called 'batch'.  """
    
    def __init__(self,
                 arpFilename,
                 idCol,
                 prefixCols,
                 suffixCols,
                 windowSize,
                 mapOrder = None,
                 untypedAllele = '0',
                 arlequinPrefix = "arl_run",
                 debug=0):

        """Constructor for HaploArlequin object.

        Expects:

        - arpFilename: Arlequin filename (must have '.arp' file
          extension)
        
        - idCol: column in input file that contains the individual id.
        
        - prefixCols: number of columns to ignore before allele data
          starts
        
        - suffixCols: number of columns to ignore after allele data
          stops
        
        - windowSize: size of sliding window

        - mapOrder: list order of columns if different to column order in file
          (defaults to order in file)

        - untypedAllele:  (defaults to '0')
        
        - arlequinPrefix: prefix for all Arlequin run-time files
        (defaults to 'arl_run').

        - debug: (defaults to 0)
        
        """

        self.arpFilename = arpFilename
        self.arsFilename = 'arl_run.ars'
        self.idCol = idCol
        self.prefixCols = prefixCols
        self.suffixCols = suffixCols
        self.windowSize = windowSize
        self.arlequinPrefix = arlequinPrefix
        self.mapOrder = mapOrder
        self.untypedAllele = untypedAllele
        self.debug = debug
        
        # arsFilename is default because we generate it
        self.batch = ArlequinBatch(arpFilename = self.arpFilename,
                              arsFilename = self.arsFilename,
                              idCol = self.idCol,
                              prefixCols = self.prefixCols,
                              suffixCols = self.suffixCols,
                              windowSize = self.windowSize,
                              mapOrder = self.mapOrder,
                              debug = self.debug)

    def outputArlequin(self, data):
        """Outputs the specified .arp sample file.
        """
        self.batch.outputArlequin(data)

    def _outputArlRunArs(self, arsFilename):
        """Outputs the run-time Arlequin setting file.

        """
        file = open(arsFilename, 'w')
        file.write("""[Setting for Calculations]
TaskNumber=8
DeletionWeight=1.0
TransitionWeight=1.0
TranversionWeight=1.0
UseOriginalHaplotypicInformation=0
EliminateRedondHaplodefs=1
AllowedLevelOfMissingData=0.0
GameticPhaseIsKnown=0
HardyWeinbergTestType=0
MakeHWExactTest=0
MarkovChainStepsHW=100000
MarkovChainDememorisationStepsHW=1000
PrecisionOnPValueHW=0.0
SignificanceLevelHW=2
TypeOfTestHW=0
LinkageDisequilibriumTestType=0
MakeExactTestLD=0
MarkovChainStepsLD=100000
MarkovChainDememorisationStepsLD=1000
PrecisionOnPValueLD=0.01
SignificanceLevelLD=0.05
PrintFlagHistogramLD=0
InitialCondEMLD=10
ComputeDvalues=0
ComputeStandardDiversityIndices=0
DistanceMethod=0
GammaAValue=0.0
ComputeTheta=0
MismatchDistanceMethod=0
MismatchGammaAValue=0.0
PrintPopDistMat=0
InitialConditionsEM=50
MaximumNumOfIterationsEM=5000
RecessiveAllelesEM=0
CompactHaplotypeDataBaseEM=0
NumBootstrapReplicatesEM=0
NumInitCondBootstrapEM=10
ComputeAllSubHaplotypesEM=0
ComputeAllHaplotypesEM=1
ComputeAllAllelesEM=0
EpsilonValue=1.0e-7
FrequencyThreshold=1.0e-5
ComputeConventionalFST=0
IncludeIndividualLevel=0
ComputeDistanceMatrixAMOVA=0
DistanceMethodAMOVA=0
GammaAValueAMOVA=0.0
PrintDistanceMatrix=0
TestSignificancePairewiseFST=0
NumPermutationsFST=100
ComputePairwiseFST=0
TestSignificanceAMOVA=0
NumPermutationsAMOVA=1000
NumPermutPopDiff=10000
NumDememoPopDiff=1000
PrecProbPopDiff=0.0
PrintHistoPopDiff=1
SignLevelPopDiff=0.05
EwensWattersonHomozygosityTest=0
NumIterationsNeutralityTests=1000
NumSimulFuTest=1000
NumPermMantel=1000
NumBootExpDem=100
LocByLocAMOVA=0
PrintFstVals=0
PrintConcestryCoeff=0
PrintSlatkinsDist=0
PrintMissIntermatchs=0
UnequalPopSizeDiv=0
PrintMinSpannNetworkPop=0
PrintMinSpannNetworkGlob=0
KeepNullDistrib=0""")
        file.close()

    def runArlequin(self):
        """Run the Arlequin haplotyping program.

        Generates the expected '.txt' set-up files for Arlequin, then
        forks a copy of 'arlecore.exe', which must be on 'PATH' to
        actually generate the haplotype estimates from the generated
        '.arp' file.
        """
        # generate the `standard' run file
        self.batch._outputArlRunTxt(self.arlequinPrefix + ".txt", self.arpFilename)
        # generate a customized settings file for haplotype estimation
        self._outputArlRunArs(self.arlequinPrefix + ".ars")
        
        # spawn external Arlequin process
        self.batch.runArlequin()
        
    def genHaplotypes(self):
        """Gets the haplotype estimates back from Arlequin.

        Parses the Arlequin output to retrieve the haplotype estimated
        data.  Returns a list of the sliding `windows' which consists
        of tuples.

        Each tuple consists of a:

        - dictionary entry (the haplotype-frequency) key-value pairs.

        - population name (original '.arp' file prefix)

        - sample count (number of samples for that window)

        - ordered list of loci considered
        """
        outFile = self.batch.arlResPrefix + ".res" + os.sep + self.batch.arlResPrefix + ".htm"
        dataFound = 0
        headerFound = 0

        haplotypes = []
        
        patt1 = re.compile("== Sample :[\t ]*(\S+) pop with (\d+) individuals from loci \[([^]]+)\]")
        patt2 = re.compile("    #   Haplotype     Freq.      s.d.")
        patt3 = re.compile("^\s+\d+\s+UNKNOWN(.*)")
        windowRange = range(1, self.windowSize)
        
        for line in open(outFile, 'r').readlines():
            matchobj = re.search(patt1, line)
            if matchobj:
                headerFound = 1
                popName = matchobj.group(1)
                sampleCount = matchobj.group(2)
                liststr = matchobj.group(3)
                # convert into list of loci
                lociList = map(int, string.split(liststr, ','))
                freqs = {}
                
            if dataFound:
                if line != os.linesep:
                    if self.debug:
                        print string.rstrip(line)
                    matchobj = re.search(patt3, line)
                    if matchobj:
                        cols = string.split(matchobj.group(1))
                        haplotype = cols[2]
                        for i in windowRange:
                            haplotype = haplotype + "_" + cols[2+i]
                        freq = float(cols[0])*float(sampleCount)
                        freqs[haplotype] = freq
                    else:
                        sys.exit("Error: unknown output in arlequin line: %s" % line)
                else:
                    headerFound = 0
                    dataFound = 0
                    haplotypes.append((freqs, popName, sampleCount, lociList))
            if re.match(patt2, line):
                dataFound = 1

        return haplotypes

class Emhaplofreq(Haplo):
    """Haplotype and LD estimation implemented via emhaplofreq.

    This is essentially a wrapper to a Python extension built on top
    of the 'emhaplofreq' command-line program.

    Will refuse to estimate haplotypes longer than that defined by
    'emhaplofreq'.
    
    """
    def __init__(self, locusData,
                 debug=0,
                 untypedAllele='****',
                 stream=None,
                 testMode=False):

        # import the Python-to-C module wrapper
        # lazy importation of module only upon instantiation of class
        # to save startup costs of invoking dynamic library loader
        import _Emhaplofreq

        # assign module to an instance variable so it is available to
        # other methods in class
        self._Emhaplofreq = _Emhaplofreq

        # FIXME: by default assume we are not dealing sequence data
        self.sequenceData = 0
        
        self.matrix = locusData
        self.untypedAllele = untypedAllele
        
        rows, cols = self.matrix.shape
        self.totalNumIndiv = rows
        self.totalLociCount = cols / 2
        
        self.debug = debug

        # initialize flag
        self.maxLociExceeded = 0

        # set "testing" flag to "1" if testMode enabled
        if testMode:
            self.testing = 1
        else:
            self.testing = 0

        # must be passed a stream
        if stream:
            self.stream = stream
        else:
            sys.exit("Emhaplofreq constructor must be passed a stream, output is only available in stream form")
                
        # create an in-memory file instance for the C program to write
        # to; this remains in effect until a call to 'serializeTo()'.
        
        #import cStringIO
        #self.fp = cStringIO.StringIO()

    def serializeStart(self):
        """Serialize start of XML output to XML stream"""
        self.stream.opentag('emhaplofreq')
        self.stream.writeln()

    def serializeEnd(self):
        """Serialize end of XML output to XML stream"""
        self.stream.closetag('emhaplofreq')
        self.stream.writeln()

    def _runEmhaplofreq(self, locusKeys=None,
                        permutationFlag=None,
                        permutationPrintFlag=0,
                        numInitCond=50,
                        numPermutations=1001,
                        numPermuInitCond=5,
                        haploSuppressFlag=None,
                        showHaplo=None,
                        mode=None,
                        testing=0):
        
        """Internal method to call _Emhaplofreq shared library.

        Format of 'locusKeys' is a string as per estHaplotypes():

        - permutationFlag: sets whether permutation test will be
          performed.  No default.

        - permutationPrintFlag: sets whether the result from
          permutation output run will be included in the output XML.
          Default: 0 (disabled).

        - numInitConds: sets number of initial conditions before
          performing the permutation test. Default: 50.

        - numPermutations: sets number of permutations that will be
          performed if 'permutationFlag' *is* set.  Default: 1001.

        - numPermuInitConds: sets number of initial conditions tried
          per-permutation.  Default: 5.

        - haploSuppressFlag: sets whether haplotype information is
          generated in the output.   No default.

        """

        # create an in-memory file instance for the C program to write
        # to; this remains in effect until end of method
        fp = cStringIO.StringIO()

        if (permutationFlag == None) or (haploSuppressFlag == None):
            sys.exit("must pass a permutation or haploSuppressFlag to _runEmhaplofreq!")
	
	# make all locus keys uppercase
	locusKeys = string.upper(locusKeys)

        # if no locus list passed, assume calculation of entire data
        # set
        if locusKeys == None:
            # create key for entire matrix
            locusKeys = ':'.join(self.matrix.colList)

        for group in string.split(locusKeys, ','):
            
            # get the actual number of loci being estimated
            lociCount = len(string.split(group,':'))

            if self.debug:
                print "number of loci for haplotype est:", lociCount

                print lociCount, self._Emhaplofreq.MAX_LOCI

            if lociCount <= self._Emhaplofreq.MAX_LOCI:

                # filter-out all individual untyped at any position
                #subMatrix = appendTo2dList(self.matrix.filterOut(group, self.untypedAllele), ':')
                subMatrix = appendTo2dList(self.matrix.filterOut(group, self.untypedAllele), GENOTYPE_SEPARATOR)

                # calculate the new number of individuals emhaplofreq is
                # being run on
                groupNumIndiv = len(subMatrix)

                if self.debug:
                    print "debug: key for matrix:", group
                    print "debug: subMatrix:", subMatrix
                    print "debug: dump matrix in form for command-line input"
                    for line in range(0, len(subMatrix)):
                        theline = subMatrix[line]
                        print "dummyid",
                        for allele in range(0, len(theline)):
                            print theline[allele], " ",
                        print
                    
                fp.write(os.linesep)

                if self.sequenceData:
                    metaLoci = string.split(string.split(group, ':')[0],'_')[0]
                else:
                    metaLoci = None

                modeAttr = "mode=\"%s\"" % mode
                haploAttr = "showHaplo=\"%s\"" % showHaplo

                if metaLoci:
                    lociAttr = "loci=\"%s\" metaloci=\"%s\"" % (group, metaLoci)
                else:
                    lociAttr = "loci=\"%s\"" % group

                # check maximum length of allele
                maxAlleleLength = 0
                for line in range(0, len(subMatrix)):
                    theline = subMatrix[line]
                    for allelePos in range(0, len(theline)):
                        allele = theline[allelePos]
                        if len(allele) > maxAlleleLength:
                            maxAlleleLength = len(allele)
                        if len(allele) > (self._Emhaplofreq.NAME_LEN)-2:
                            print "WARNING: '%s' (%d) exceeds max allele length (%d) for LD and haplo est in %s" % (allele, len(allele), self._Emhaplofreq.NAME_LEN-2, lociAttr)

                if groupNumIndiv > self._Emhaplofreq.MAX_ROWS:
                    fp.write("<group %s role=\"too-many-lines\" %s %s/>%s" % (modeAttr, lociAttr, haploAttr, os.linesep))
                    continue
                # if nothing left after filtering, simply continue
                elif groupNumIndiv == 0:
                    fp.write("<group %s role=\"no-data\" %s %s/>%s" % (modeAttr, lociAttr, haploAttr, os.linesep))
                    continue
                elif maxAlleleLength > (self._Emhaplofreq.NAME_LEN-2):
                    fp.write("<group %s role=\"max-allele-length-exceeded\" %s %s>%d</group>%s" % (modeAttr, lociAttr, haploAttr, self._Emhaplofreq.NAME_LEN-2, os.linesep))
                    continue
                
                if mode:
                    fp.write("<group %s %s %s>%s" % (modeAttr, lociAttr, haploAttr, os.linesep))
                else:
                    sys.exit("A 'mode' for emhaplofreq must be specified")
                
##                 if permutationFlag and haploSuppressFlag:
##                     fp.write("<group mode=\"LD\" loci=\"%s\">%s" % (group, os.linesep))
##                 elif permutationFlag == 0 and haploSuppressFlag == 0:
##                     fp.write("<group mode=\"haplo\" loci=\"%s\">%s" % (group, os.linesep))
##                 elif permutationFlag and haploSuppressFlag == 0:
##                     fp.write("<group mode=\"haplo-LD\" loci=\"%s\">%s" % (group, os.linesep))
##                 else:
##                     sys.exit("Unknown combination of permutationFlag and haploSuppressFlag")
                fp.write(os.linesep)

                fp.write("<individcount role=\"before-filtering\">%d</individcount>" % self.totalNumIndiv)
                fp.write(os.linesep)
                
                fp.write("<individcount role=\"after-filtering\">%d</individcount>" % groupNumIndiv)
                fp.write(os.linesep)
                
                # pass this submatrix to the SWIG-ed C function
                self._Emhaplofreq.main_proc(fp,
                                            subMatrix,
                                            lociCount,
                                            groupNumIndiv,
                                            permutationFlag,
                                            haploSuppressFlag,
                                            numInitCond,
                                            numPermutations,
                                            numPermuInitCond,
                                            permutationPrintFlag,
                                            testing,
                                            GENOTYPE_SEPARATOR,
                                            GENOTYPE_TERMINATOR)

                fp.write("</group>")

                if self.debug:
                    # in debug mode, print the in-memory file to sys.stdout
                    lines = string.split(fp.getvalue(), os.linesep)
                    for i in lines:
                        print "debug:", i

            else:
                fp.write("Couldn't estimate haplotypes for %s, num loci: %d exceeded max loci: %d" % (group, lociCount, self._Emhaplofreq.MAX_LOCI))
                fp.write(os.linesep)

        # writing to file must be called *after* all output has been
        # generated to cStringIO instance "fp"

        self.stream.write(fp.getvalue())
        fp.close()

        # flush any buffered output to the stream
        self.stream.flush()

    def estHaplotypes(self,
                      locusKeys=None,
                      numInitCond=None):
        """Estimate haplotypes for listed groups in 'locusKeys'.

        Format of 'locusKeys' is a string consisting of:

        - comma (',') separated haplotypes blocks for which to estimate
          haplotypes

        - within each `block', each locus is separated by colons (':')

        e.g. '*DQA1:*DPB1,*DRB1:*DQB1', means to est. haplotypes for
         'DQA1' and 'DPB1' loci followed by est. of haplotypes for
         'DRB1' and 'DQB1' loci.
        """
        self._runEmhaplofreq(locusKeys=locusKeys,
                             numInitCond=numInitCond,
                             permutationFlag=0,
                             haploSuppressFlag=0,
                             showHaplo='yes',
                             mode='haplo',
                             testing=self.testing)
        

    def estLinkageDisequilibrium(self,
                                 locusKeys=None,
                                 permutationPrintFlag=0,
                                 numInitCond=None,
                                 numPermutations=None,
                                 numPermuInitCond=None):
        """Estimate linkage disequilibrium (LD) for listed groups in
        'locusKeys'.

        Format of 'locusKeys' is a string consisting of:

        - comma (',') separated haplotypes blocks for which to estimate
          haplotypes

        - within each `block', each locus is separated by colons (':')

        e.g. '*DQA1:*DPB1,*DRB1:*DQB1', means to est. LD for
         'DQA1' and 'DPB1' loci followed by est. of LD for
         'DRB1' and 'DQB1' loci.
        """
        self._runEmhaplofreq(locusKeys,
                             permutationFlag=1,
                             permutationPrintFlag=permutationPrintFlag,
                             numInitCond=numInitCond,
                             numPermutations=numPermutations,
                             numPermuInitCond=numPermuInitCond,
                             haploSuppressFlag=1,
                             showHaplo='no',
                             mode='LD',
                             testing=self.testing)

    def allPairwise(self,
                    permutationPrintFlag=0,
                    numInitCond=None,
                    numPermutations=None,
                    numPermuInitCond=None,
                    haploSuppressFlag=None,
                    haplosToShow=None,
                    mode=None):
        """Run pairwise statistics.

        Estimate pairwise statistics for a given set of loci.
        Depending on the flags passed, can be used to estimate both LD
        (linkage disequilibrium) and HF (haplotype frequencies), an
        optional permutation test on LD can be run """

        if numPermutations > 0:
            permuMode = 'with-permu'
            permutationFlag = 1
        else:
            permuMode = 'no-permu'
            permutationFlag = 0

        if mode == None:
            mode = 'all-pairwise-ld-' + permuMode

        self.sequenceData = checkIfSequenceData(self.matrix)
        li = getLocusPairs(self.matrix, self.sequenceData)

        if self.debug:
            print li, len(li)

        for pair in li:
            # generate the reversed order in case user
            # specified it in the opposite sense
            sp = string.split(pair,':')
            reversedPair =  sp[1] + ':' + sp[0]

            if (pair in haplosToShow) or (reversedPair in haplosToShow):
                showHaplo = 'yes'
            else:
                showHaplo = 'no'

            self._runEmhaplofreq(pair,
                                 permutationFlag=permutationFlag,
                                 permutationPrintFlag=permutationPrintFlag,
                                 numInitCond=numInitCond,
                                 numPermutations=numPermutations,
                                 numPermuInitCond=numPermuInitCond,
                                 haploSuppressFlag=haploSuppressFlag,
                                 showHaplo=showHaplo,
                                 mode=mode,
                                 testing=self.testing)

            # def allPairwiseLD(self, haplosToShow=None):
            #     """Estimate all pairwise LD and haplotype frequencies.
            
            #     Estimate the LD (linkage disequilibrium)for each pairwise set
            #     of loci.
            #     """
            #     self.allPairwise(permutationFlag=0,
            #                      haploSuppressFlag=0,
            #                      mode='all-pairwise-ld-no-permu')
            
            # def allPairwiseLDWithPermu(self, haplosToShow=None):
            #     """Estimate all pairwise LD.
            
            #     Estimate the LD (linkage disequilibrium)for each pairwise set
            #     of loci.
            #     """
            #     self.allPairwise(permutationFlag=1,
            #                      haploSuppressFlag=0,
            #                      mode='all-pairwise-ld-with-permu')



class Haplostats(Haplo):
    """Haplotype and LD estimation implemented via haplo-stats.

    This is a wrapper to a portion of the 'haplo.stats' R package
    
    """
    def __init__(self, locusData,
                 debug=0,
                 untypedAllele='****',
                 stream=None,
                 testMode=False):

        # import the Python-to-C module wrapper
        # lazy importation of module only upon instantiation of class
        # to save startup costs of invoking dynamic library loader
        import _Haplostats

        # assign module to an instance variable so it is available to
        # other methods in class
        self._Haplostats = _Haplostats

        # FIXME: by default assume we are not dealing sequence data
        self.sequenceData = 0
        
        self.matrix = locusData
        self.untypedAllele = untypedAllele
        
        rows, cols = self.matrix.shape
        self.totalNumIndiv = rows
        self.totalLociCount = cols / 2
        
        self.debug = debug

    def estHaplotypes(self,
                      # locusKeys=None,
                      weight=None,
                      control=None,
                      numInitCond=1):
        """Estimate haplotypes for whole matrix

        FIXME: eventually extend to cover submatrices like Emhaplofreq
        """

        geno = self.matrix
        
        n_loci = geno.colCount
        n_subject = geno.rowCount

        subj_id = range(1, n_subject + 1)
        if n_loci < 2:
            print "Must have at least 2 loci for haplotype estimation!"
            exit(-1)

        # set up weight
        if not weight:
            weight = [1.0]*n_subject
        if len(weight) != n_subject:
            print "Length of weight != number of subjects (nrow of geno)"
            exit(-1)

        # Compute the max number of pairs of haplotypes over all subjects
        # FIXME: hardcode, not yet translated, need to use/modify StringMatrix
        # max_pairs = geno.count.pairs(temp_geno)
        # max_haps = 2*sum(max_pairs)
        max_haps = 18

        # FIXME: do we need this?
        if max_haps > control['max_haps_limit']:
            max_haps = control['max_haps_limit']

        temp_geno = geno.convertToInts()  # simulates setupGeno
        geno_vec = temp_geno.flattenCols()  # gets the columns as integers

        n_alleles = []
        for locus in geno.colList:
            allele_labels = temp_geno.getUniqueAlleles(locus)
            n_alleles.append(len(allele_labels))

        # FIXME: not (yet) using a.freq, so don't calculate
        # also too complicated to translate right now
        # for(i in 1:n_loci){
        #  j <- (i-1)*2 + 1
        #  p <- table(temp.geno[,c(j, (j+1))], exclude=NA)
        #  p <- p/sum(p)
        #  a.freq[[i]] <- list(p=p)
        # }

        loci_insert_order = range(0, n_loci)

        # FIXME: hardcode
        iseed1 = 18717; iseed2= 16090; iseed3=14502

        converge, lnlike, n_u_hap, n_hap_pairs, hap_prob, u_hap, u_hap_code, subj_id, post, hap1_code, hap2_code = \
                  self._haplo_em_fitter(n_loci,
                                        n_subject,
                                        weight,
                                        geno_vec,
                                        n_alleles,
                                        max_haps,
                                        control['max_iter'],
                                        loci_insert_order,
                                        control['min_posterior'],
                                        control['tol'],
                                        control['insert_batch_size'],
                                        control['random_start'],
                                        iseed1,
                                        iseed2,
                                        iseed3,
                                        control['verbose'])

        if numInitCond > 1:
            for i in range(1, numInitCond):
                # seed_array = runif(3)
                seed_array = numpy.random.random(3)

                iseed1 = int(10000 + 20000*seed_array[0])
                iseed2 = int(10000 + 20000*seed_array[1])
                iseed3 = int(10000 + 20000*seed_array[2])

                print iseed1, iseed2, iseed3

                converge_new, lnlike_new, n_u_hap_new, n_hap_pairs_new, hap_prob_new, \
                              u_hap_new, u_hap_code_new, subj_id_new, post_new, hap1_code_new, \
                              hap2_code = \
                              self._haplo_em_fitter(n_loci,
                                                    n_subject,
                                                    weight,
                                                    geno_vec,
                                                    n_alleles,
                                                    max_haps,
                                                    control['max_iter'],
                                                    loci_insert_order,
                                                    control['min_posterior'],
                                                    control['tol'],
                                                    control['insert_batch_size'],
                                                    1,  # set random.start to 1
                                                    iseed1,
                                                    iseed2,
                                                    iseed3,
                                                    control['verbose'])

                if lnlike_new > lnlike:
                    print "found a better lnlikelihood!", lnlike_new
                    # FIXME: need more elegant data structure
                    converge, lnlike, n_u_hap, n_hap_pairs, hap_prob, \
                              u_hap, u_hap_code, subj_id, post, hap1_code, \
                              hap2_code = \
                              converge_new, lnlike_new, n_u_hap_new, n_hap_pairs_new, hap_prob_new, \
                              u_hap_new, u_hap_code_new, subj_id_new, post_new, hap1_code_new, \
                              hap2_code 

        # FIXME: convert back into haplotype data structures here
        # here is the R code for reference

        # u.hap <- matrix(tmp2$u.hap,nrow=tmp2$n.u.hap,byrow=TRUE)
        # # code alleles for haplotpes with original labels
        # # use I() to keep char vectors to factors in making a data.frame
        # haplotype <- data.frame(I(allele.labels[[1]][u.hap[,1]]))
        # for(j in 2:n.loci){
        #     haplotype <- cbind(haplotype, I(allele.labels[[j]][u.hap[,j]]))
        #     }
        # 
        # # haplotype <- data.frame(haplotype)
        # names(haplotype) <- locus.label

        # # convert from 0-offset in C to 1-offset in S, and recode hap codes
        # # to 1,2,..., n_uhap
        # 
        # hap1code  <- tmp2$hap1code  + 1
        # hap2code  <- tmp2$hap2code  + 1
        # uhapcode  <- tmp2$u.hap.code + 1
        # 
        # n1 <- length(uhapcode)
        # n2 <- length(hap1code)
        # 
        # tmp <- as.numeric(factor(c(uhapcode, hap1code, hap2code)))
        # uhapcode <- tmp[1:n1]
        # hap1code <- tmp[(n1+1):(n1+n2)]
        # hap2code <- tmp[(n1+n2+1):(n1+2*n2)]
        # 
        # uhap.df <- data.frame(uhapcode, tmp2$hap.prob, u.hap)
        # 
        # names(uhap.df) <- c("hap.code","hap.prob",locus.label)
        # 
        # indx.subj = tmp2$indx.subj + 1

        return converge, lnlike, n_u_hap, n_hap_pairs, hap_prob, u_hap, u_hap_code, subj_id, post, hap1_code, hap2_code

    def _haplo_em_fitter(self,
                         n_loci,
                         n_subject,
                         weight,
                         geno_vec,
                         n_alleles,
                         max_haps,
                         max_iter,
                         loci_insert_order,
                         min_posterior,
                         tol,
                         insert_batch_size,
                         random_start,
                         iseed1,
                         iseed2,
                         iseed3,
                         verbose):

        _Haplostats = self._Haplostats

        converge = 0
        min_prior = 0.0
        n_unique = 0
        lnlike = 0.0
        n_u_hap = 0
        n_hap_pairs = 0

        tmp1 = _Haplostats.haplo_em_pin_wrap(n_loci, n_subject, weight, n_alleles,
                                             max_haps, max_iter, loci_insert_order,
                                             min_prior, min_posterior, tol, insert_batch_size,
                                             random_start, iseed1, iseed2, iseed3, verbose, geno_vec)

        # values returned from haplo_em_pin
        status1, converge, lnlike, n_u_hap, n_hap_pairs = tmp1

        tmp2 = _Haplostats.haplo_em_ret_info_wrap(\
            # input parameters
            n_u_hap, n_loci, n_hap_pairs,
            # output parameters: declaring array sizes for ret_val
            n_u_hap,          # hap_prob
            n_u_hap * n_loci, # u_hap
            n_u_hap,          # u_hap_code
            n_hap_pairs,        # subj_id
            n_hap_pairs,        # post
            n_hap_pairs,        # hap1_code
            n_hap_pairs,        # hap2_code
            )

        # values returned from haplo_em_ret_info
        status2, hap_prob, u_hap, u_hap_code, subj_id, post, hap1_code, hap2_code = tmp2

        _Haplostats.haplo_free_memory()

        return converge, lnlike, n_u_hap, n_hap_pairs, hap_prob, u_hap, u_hap_code, subj_id, post, hap1_code, hap2_code

        

