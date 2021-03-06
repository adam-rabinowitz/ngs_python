def realignTargetCreator(
        inBam, inVcf, reference, outputList, javaPath = 'java',
        gatkPath = 'GenomeAnalysisTK.jar', threads = 1, memory = None
    ):
    ''' Function to find regions for gatk local relaignment. Function takes 7
    arguments:
    
    1)  inBam - Input BAM file
    2)  inVcf - Imput VCF file listing indels. May be gzipped.
    3)  reference - Fasta file contaning referenc genome sequence.
    4)  outputList - Name of output list file. Should end '.list'.
    5)  javaPath - Path to java.
    6)  gatkPath - Path to GATK jar file.
    7)  threads - Number of threads to use.
    8)  memory - Memory, in GB, to use.
    
    '''
    # Build command
    targetCommand = [javaPath, '-jar', gatkPath, '-T', 'RealignerTargetCreator',
        '-I', inBam, '-R', reference, '-known', inVcf, '-o', outputList, '-nt',
        str(threads)]
    # Add memory
    if memory:
        targetCommand.insert(1, '-Xmx{}g'.format(memory))
    # Join and return command
    targetCommand = ' '.join(targetCommand)
    return(targetCommand)

def realignFromTarget(
        inBam, inVcf, reference, inputList, outBam, javaPath = 'java',
        gatkPath = 'GenomeAnalysisTK.jar', memory = None
    ):
    ''' Function to generate command to peform local realignment using the
    GATK package. Function takes 6 arguments:
    
    1)  inBam - Input BAM file
    2)  inVcf - Imput VCF file listing indels. May be gzipped.
    3)  reference - Fasta file contaning referenc genome sequence.
    4)  inputList - Name of output list file. Should end '.list'.
    5)  javaPath - Path to java.
    6)  gatkPath - Path to GATK jar file.
    
    '''
    # Build command
    realignCommand = [javaPath, '-jar', gatkPath, '-T', 'IndelRealigner', '-I',
        inBam, '-R', reference, '-known', inVcf, '-targetIntervals',
        inputList, '-o', outBam]
    # Add memory
    if memory:
        realignCommand.insert(1, '-Xmx{}g'.format(memory))
    # Join and return command
    realignCommand = ' '.join(realignCommand)
    return(realignCommand)

def gatkRealign(
        inBam, outBam, inVcf, reference, listFile = '', javaPath = 'java',
        gatkPath = 'GenomeAnalysisTK.jar', threads = 1, delete = True,
        memory = None
    ):
    ''' Function combines the functions gatkRealignTargetCreator and
    gatkRealignFromTarget to perform local realignment around indels. Function
    takes 6 arguments:
    
    1)  inBam - Full path to input BAM file.
    2)  outBam - Full path to output BAM file.
    3)  inVcf - Imput VCF file listing indels. May be gzipped.
    4)  reference - Fasta file contaning referenc genome sequence.
    5)  listFile - Full path at which to save target list file.
    5)  javaPath - Path to java.
    7)  gatkPath - Path to GATK jar file.
    8)  delete - Boolean, indicating whether to delete input BAM and target
        list generated by gatkAlignTargetCreator.
    9)  memory - Memory, in GB, to use.
    
    '''
    # Cheack BAM file and create name of output target list file
    if not inBam.endswith('.bam') or not outBam.endswith('.bam'):
        raise IOError("BAM filenames must end '.bam'")
    if listFile:
        delList = False
    else:
        delList = True
        listFile = inBam[:-4] + '_target.list'
    # Create command to generate target files
    targetCommand = realignTargetCreator(
        inBam = inBam, inVcf = inVcf, reference = reference,
        outputList = listFile, javaPath = javaPath, gatkPath = gatkPath,
        threads = threads, memory = memory
    )
    # Create command to perform realignment
    realignCommand = realignFromTarget(
        inBam = inBam, inVcf = inVcf, reference = reference,
        inputList = listFile, outBam = outBam, javaPath = javaPath,
        gatkPath = gatkPath, memory = memory
    )
    # Join command and add deletion if required
    jointCommand = '%s && %s' %(targetCommand, realignCommand)
    if delete and delList:
        jointCommand += ' && rm %s.ba?* %s' %(inBam[:-4], listFile)
    elif delete:
        jointCommand += ' && rm %s.ba?*' %(inBam[:-4])
    elif delList:
        jointCommand += ' && rm %s' %(listFile)
    # Return command
    return(jointCommand)

def baseRecal(
        inBam, inVcf, bsqrTable, reference, javaPath = 'java',
        gatkPath = 'GenomeAnalysisTK.jar', memory = None
    ):
    ''' Function generates a command to generate a base quality score
    recalibration (BSQR) table. Function takes 6 arguments:
    
    1)  inBam - Full path to input BAM file.
    2)  inVcf - Input VCF file listing SNPs. May be gzipped.
    3)  bsqrTable - Full path to output BSQR report.
    4)  reference - Fasta file contaning referenc genome sequence.
    5)  javaPath - Path to java.
    6)  gatkPath - Path to GATK jar file.
    7)  memory - The amount of memory, in GB to use.
    
    '''
    # Create command
    recalCommand = [javaPath, '-jar', gatkPath, '-T BaseRecalibrator -R',
        reference, '-I', inBam, '--knownSites', inVcf, '-o', bsqrTable]
    # Add memory
    if memory:
        recalCommand.insert(1, '-Xmx{}g'.format(memory))
    # Join and return command
    recalCommand = ' '.join(recalCommand)
    return(recalCommand)

def recalApply(
        inBam, outBam, reference, bsqrTable, javaPath = 'java',
        gatkPath = 'GenomeAnalysisTK.jar', delete = True, memory = None
    ):
    ''' Function generates a command to generate a base quality score
    recalibration (BSQR) table. Function takes 6 arguments:
    
    1)  inBam - Full path to input BAM file.
    2)  outBam - Full path to output BAM file.
    3)  bsqrTable - Full path to BSQR report.
    4)  reference - Fasta file contaning referenc genome sequence.
    5)  javaPath - Path to java.
    6)  gatkPath - Path to GATK jar file.
    7)  memory - The amount of memory, in GB, to use.
    
    '''
    # Create command
    recalCommand = [javaPath, '-jar', gatkPath, '-T PrintReads -R',
        reference, '-I', inBam, '-BQSR', bsqrTable, '-o', outBam]
    # Add memory
    if memory:
        recalCommand.insert(1, '-Xmx{}g'.format(memory))
    # Join and return command
    recalCommand = ' '.join(recalCommand)
    return(recalCommand)

def bsqr(
        inBam, outBam, inVcf, reference, bsqrTable = '', javaPath = 'java',
        gatkPath = 'GenomeAnalysisTK.jar', delete = True, memory = None
    ):
    ''' Function combines the functions gatkRealignTargetCreator and
    gatkRealignFromTarget to perform local realignment around indels. Function
    takes 6 arguments:
    
    1)  inBam - Full path to input BAM file.
    2)  outBam - Full path to output BAM file.
    3)  inVcf - Imput VCF file listing SNPs. May be gzipped.
    4)  reference - Fasta file contaning referenc genome sequence.
    5)  bsqrTable - Full path at which to save BSQR report.
    5)  javaPath - Path to java.
    7)  gatkPath - Path to GATK jar file.
    8)  delete - Boolean, indicating whether to delete input BAM.
    9)  memory - Amount of memory, in GB, to use.
    
    '''
    # Cheack BAM file and create name of output target list file
    if not inBam.endswith('.bam') or not outBam.endswith('.bam'):
        raise IOError("BAM filenames must end '.bam'")
    if bsqrTable:
        delTable = False
    else:
        delTable = True
        bsqrTable = inBam[:-4] + '_bsqr.grp'
    # Create command to generate target files
    bsqrTableGenerate = baseRecal(
        inBam=inBam, inVcf=inVcf, bsqrTable=bsqrTable, reference=reference,
        javaPath=javaPath, gatkPath=gatkPath, memory=memory
    )
    # Create command to perform realignment
    bsqrTableApply = recalApply(
        inBam=inBam, reference=reference, bsqrTable=bsqrTable, outBam=outBam,
        javaPath=javaPath, gatkPath=gatkPath, memory=memory
    )
    # Create complete command and return
    jointCommand = '{} && {}'.format(bsqrTableGenerate, bsqrTableApply)
    if delete:
        jointCommand += ' && rm %s.ba?*' %(inBam[:-4])
    return(jointCommand)
