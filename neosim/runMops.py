#!/usr/bin/env python

"""

A simple script to run MOPS. (Work in progress)

Command-line call:
python runMops.py {nightly DIA source directory} {output directory}

Requirements:
MOPS setup (with MOPS_DIR path variable pointing to bin mops_daymops)

Contact moeyensj@uw.edu with questions and / or concerns.

"""

import os
import subprocess
import glob
import argparse
import yaml
import shutil
import multiprocessing

from MopsParameters import MopsParameters
from MopsTracker import MopsTracker

# File suffixes
DIASOURCE_SUFFIX = ".dias"
TRACKLET_SUFFIX = ".tracklets"
TRACKLET_BY_INDEX_SUFFIX = TRACKLET_SUFFIX + ".byIndices"
COLLAPSED_TRACKLET_SUFFIX = TRACKLET_SUFFIX + ".collapsed"
PURIFIED_TRACKLET_SUFFIX = TRACKLET_SUFFIX + ".purified"
FINAL_TRACKLET_SUFFIX = TRACKLET_SUFFIX + ".final"
TRACKLET_BY_ID_SUFFIX = ".byDiaIds"
TRACK_SUFFIX = ".track"
FINAL_TRACK_SUFFIX = TRACK_SUFFIX + ".final"

TRACKLETS_DIR = "tracklets/"
COLLAPSED_TRACKLETS_DIR = "trackletsCollapsed/"
PURIFIED_TRACKLETS_DIR = "trackletsPurified/"
FINAL_TRACKLETS_DIR = "trackletsFinal/"
TRACKLETS_BY_NIGHT_DIR = "trackletsByNight/"
TRACKS_DIR = "tracks/"
FINAL_TRACKS_DIR = "tracksFinal/"

VERBOSE = True

defaults = MopsParameters(verbose=False)


def directoryBuilder(runDir,
                     findTracklets=True,
                     collapseTracklets=True,
                     purifyTracklets=True,
                     removeSubsetTracklets=True,
                     linkTracklets=True,
                     removeSubsetTracks=True,
                     overwrite=False,
                     verbose=VERBOSE):
    """
    Builds the directory structure for MOPS output files. Returns output
    directory keyed dictionary of file paths.

    Possible keys:
        "trackletsDir",
        "collapsedDir",
        "purifiedDir",
        "finalTrackletsDir",
        "trackletsByNightDir",
        "tracksDir",
        "finalTracksDir"

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    runDir: (string), name of the top folder
    findTracklets: (boolean) [True], build findTracklets output directory?
    collapseTracklets: (boolean) [True], build collapseTracklets
        output directory?
    purifyTracklets: (boolean) [True], build purifyTracklets
        output directory?
    removeSubsetTracklets: (boolean) [True], build removeSubsets tracklets
        output directory?
    removeSubsetTracks: (boolean) [True], build removeSubsets tracks
        ouput directory?
    overwrite: (boolean) [True], Use carefully!. If directory structure
        exists delete it.
    ----------------------
    """

    # Check if path exists, if it does only continue if overwrite is true
    if os.path.exists(runDir):
        if overwrite:
            shutil.rmtree(runDir)
            os.mkdir(runDir)
            print "Overwrite triggered: deleting existing directory..."
            print ""
        else:
            raise NameError("Run directory exists! Cannot continue!")
    else:
        os.mkdir(runDir)

    dirsOut = {}

    if findTracklets:
        dirsOut["trackletsDir"] = TRACKLETS_DIR

    if collapseTracklets:
        dirsOut["collapsedDir"] = COLLAPSED_TRACKLETS_DIR

    if purifyTracklets:
        dirsOut["purifiedDir"] = PURIFIED_TRACKLETS_DIR

    if removeSubsetTracklets:
        dirsOut["finalTrackletsDir"] = FINAL_TRACKLETS_DIR

    if linkTracklets:
        dirsOut["trackletsByNightDir"] = TRACKLETS_BY_NIGHT_DIR
        dirsOut["tracksDir"] = TRACKS_DIR

    if removeSubsetTracks:
        dirsOut["finalTracksDir"] = FINAL_TRACKS_DIR

    for d in dirsOut:
        newDir = os.path.join(runDir, dirsOut[d])

        if os.path.exists(newDir):
            print "%s already exists."
        else:
            os.mkdir(newDir)

        dirsOut[d] = newDir

    return dirsOut


def runFindTracklets(diasources, outDir,
                     vmax=defaults.vMax,
                     vmin=defaults.vMin,
                     verbose=VERBOSE):
    """
    Runs findTracklets.

    Generates tracklets given a set of DIA sources.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    diasources: (list of strings), list of nightly diasource files
    outDir: (string), tracklet output directory
    ----------------------
    """
    function = "findTracklets"
    tracklets = []

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    for diasource in diasources:
        trackletsOut = _out(outDir, diasource, TRACKLET_SUFFIX)

        call = [function, "-i", diasource, "-o",
                trackletsOut, "-v", str(vmax), "-m", str(vmin)]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        tracklets.append(trackletsOut)

    if verbose:
        _status(function, False)

    return sorted(tracklets)


def runIdsToIndices(tracklets, diasources, outDir,
                    verbose=VERBOSE):
    """
    Runs idsToIndices.py.

    Rearranges tracklets by index as opposed to id. This format is required
    by collapseTracklets, purifyTracklets and removeSubsets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    tracklets: (list), list of tracklets
    diasources: (list), list of diasources
    outDir: (string), tracklet by index output directory
    ----------------------
    """
    function = "idsToIndices.py"
    byIndex = []

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    for tracklet, diasource in zip(tracklets, diasources):
        byIndexOut = _out(outDir, diasource, TRACKLET_BY_INDEX_SUFFIX)

        script = str(os.getenv("MOPS_DIR")) + "/bin/idsToIndices.py"
        call = ["python", script, tracklet, diasource, byIndexOut]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        byIndex.append(byIndexOut)

    if verbose:
        _status(function, False)

    return sorted(byIndex)


def runCollapseTracklets(trackletsByIndex, diasources, outDir,
                         raTol=defaults.raTol,
                         decTol=defaults.decTol,
                         angTol=defaults.angTol,
                         vTol=defaults.vTol,
                         method=defaults.method,
                         useRMSfilt=defaults.useRMSfilt,
                         rmsMax=defaults.rmsMax,
                         verbose=VERBOSE):
    """
    Runs collapseTracklets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    trackletsByIndex: (list), list of tracklets
    diasources: (list), list of diasources
    outDir: (string), collapsed tracklet output directory
    ----------------------
    """
    function = "collapseTracklets"
    collapsedTracklets = []

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    for tracklet, diasource in zip(trackletsByIndex, diasources):
        collapsedTracklet = _out(outDir, diasource, COLLAPSED_TRACKLET_SUFFIX)

        call = ["collapseTracklets", diasource, tracklet, str(raTol),
                str(decTol), str(angTol), str(vTol), collapsedTracklet,
                "--method", method,
                "--useRMSFilt", str(useRMSfilt),
                "--maxRMS", str(rmsMax)]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        collapsedTracklets.append(collapsedTracklet)

    if verbose:
        _status(function, False)

    return sorted(collapsedTracklets)


def runPurifyTracklets(collapsedTracklets, diasources, outDir,
                       rmsMax=defaults.rmsMax,
                       verbose=VERBOSE):
    """
    Runs purifyTracklets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    collapsedTrackets: (list), list of collapsed tracklets
    diasources: (list), list of diasources
    outDir: (string), purified tracklet output directory
    ----------------------
    """
    function = "purifyTracklets"
    purifiedTracklets = []

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    for tracklet, diasource in zip(collapsedTracklets, diasources):
        purifiedTracklet = _out(outDir, diasource, PURIFIED_TRACKLET_SUFFIX)

        call = ["purifyTracklets",
                "--detsFile", diasource,
                "--pairsFile", tracklet,
                "--maxRMS", str(rmsMax),
                "--outFile", purifiedTracklet]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        purifiedTracklets.append(purifiedTracklet)

    if verbose:
        _status(function, False)

    return sorted(purifiedTracklets)


def runRemoveSubsets(purifiedTracklets, diasources, outDir,
                     rmSubsets=defaults.rmSubsetTracklets,
                     keepOnlyLongest=defaults.keepOnlyLongestTracklets,
                     suffix=FINAL_TRACKLET_SUFFIX,
                     verbose=VERBOSE):
    """
    Runs removeSubsets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    purifiedTracklets: (list), list of purified tracklets
    diasources: (list), list of diasources
    diasourcesDir: (string), directory containing diasources
    outDir: (string), final tracklet output directory
    ----------------------
    """
    function = "removeSubsets"
    finalTracklets = []

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    for tracklet, diasource in zip(purifiedTracklets, diasources):
        finalTracklet = _out(outDir, tracklet, suffix)

        call = ["removeSubsets",
                "--inFile", tracklet,
                "--outFile", finalTracklet,
                "--removeSubsets", str(rmSubsets),
                "--keepOnlyLongest", str(keepOnlyLongest)]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        finalTracklets.append(finalTracklet)

    if verbose:
        _status(function, False)

    return sorted(finalTracklets)


def runIndicesToIds(finalTracklets, diasources, outDir, suffix,
                    verbose=VERBOSE):
    """
    Runs indicesToIds.py.

    Convert back to original tracklet format.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    finalTracklets: (list), list of final (subset removed) tracklets
    diasources: (list), list of diasources
    outDir: (string), tracklet by ID output directory
    ----------------------
    """
    function = "indicesToIds.py"
    byId = []

    outfile = file(outDir + "/indicesToIds.out", "w")
    errfile = file(outDir + "/indicesToIds.err", "w")

    if verbose:
        _status(function, True)

    for tracklet, diasource in zip(finalTracklets, diasources):
        byIdOut = _out(outDir, diasource, suffix + TRACKLET_BY_ID_SUFFIX)

        script = str(os.getenv("MOPS_DIR")) + "/bin/indicesToIds.py"
        call = ["python", script, tracklet, diasource, byIdOut]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        byId.append(byIdOut)

    if verbose:
        _status(function, False)

    return sorted(byId)


def runMakeLinkTrackletsInputByNight(diasourcesDir, trackletsDir, outDir,
                                     diasSuffix=DIASOURCE_SUFFIX,
                                     trackletSuffix=(FINAL_TRACKLET_SUFFIX +
                                                     TRACKLET_BY_ID_SUFFIX),
                                     windowSize=defaults.windowSize,
                                     verbose=VERBOSE):
    """
    Runs makeLinkTrackletsInput_byNight.py.

    Reads tracklet files into dets and ids as required by linkTracklets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    parameters: (MopsParameters object), user or default defined MOPS parameter object
    diasourcesDir: (string), directory containing diasources
    trackletsDir: (string), directory containing final (subset removed) tracklets
    outDir: (string), dets and ids file output directory
    ----------------------
    """
    function = "makeLinkTrackletsInput_byNight.py"

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    script = str(os.getenv("MOPS_DIR")) + "/bin/makeLinkTrackletsInput_byNight.py"
    call = ["python", script,
            "--windowSize", str(windowSize),
            "--diasSuffix", diasSuffix,
            "--trackletSuffix", trackletSuffix,
            diasourcesDir,
            trackletsDir,
            outDir]
    subprocess.call(call, stdout=outfile, stderr=errfile)

    ids = glob.glob(outDir + "*.ids")
    dets = glob.glob(outDir + "*.dets")

    if verbose:
        _status(function, False)

    return sorted(dets), sorted(ids)


def runLinkTracklets(dets, ids, outDir,
                     enableMultiprocessing=True,
                     processes=8,
                     detErrThresh=defaults.detErrThresh,
                     decAccelMax=defaults.decAccelMax,
                     raAccelMax=defaults.raAccelMax,
                     nightMin=defaults.nightMin,
                     detectMin=defaults.detectMin,
                     bufferSize=defaults.bufferSize,
                     latestFirstEnd=defaults.latestFirstEnd,
                     earliestLastEnd=defaults.earliestLastEnd,
                     leafNodeSizeMax=defaults.leafNodeSizeMax,
                     verbose=VERBOSE):
    """
    Runs linkTracklets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    dets: (list), list of dets files
    ids: (list), list of ids files
    outDir: (string), tracks output directory
    ----------------------
    """
    function = "linkTracklets"
    tracks = []

    if verbose:
        _status(function, True)

    if enableMultiprocessing:
        print "Multiprocessing Enabled!"
        print "Using %s CPUs in parallel." % (processes)

        calls = []

        for detIn, idIn in zip(dets, ids):
            trackOut = _out(outDir, detIn, TRACK_SUFFIX)

            call = ["linkTracklets",
                    "-e", str(detErrThresh),
                    "-D", str(decAccelMax),
                    "-R", str(raAccelMax),
                    "-u", str(nightMin),
                    "-s", str(detectMin),
                    "-b", str(bufferSize),
                    "-d", detIn,
                    "-t", idIn,
                    "-o", trackOut]

            if latestFirstEnd is not None:
                call.extend(["-F", str(latestFirstEnd)])
            if earliestLastEnd is not None:
                call.extend(["-L", str(earliestLastEnd)])
            if leafNodeSizeMax is not None:
                call.extend(["-n", str(leafNodeSizeMax)])

            tracks.append(trackOut)

            calls.append(call)

        p = multiprocessing.Pool(processes=processes)
        p.map(_runWindow, calls)

    else:

        for detIn, idIn in zip(dets, ids):
            trackOut = _out(outDir, detIn, TRACK_SUFFIX)
            outfile = file(trackOut + ".out", "w")
            errfile = file(trackOut + ".err", "w")

            call = ["linkTracklets",
                    "-e", str(detErrThresh),
                    "-D", str(decAccelMax),
                    "-R", str(raAccelMax),
                    "-u", str(nightMin),
                    "-s", str(detectMin),
                    "-b", str(bufferSize),
                    "-d", detIn,
                    "-t", idIn,
                    "-o", trackOut]

            if latestFirstEnd is not None:
                call.extend(["-F", str(latestFirstEnd)])
            if earliestLastEnd is not None:
                call.extend(["-L", str(earliestLastEnd)])
            if leafNodeSizeMax is not None:
                call.extend(["-n", str(leafNodeSizeMax)])

            subprocess.call(call, stdout=outfile, stderr=errfile)

            tracks.append(trackOut)

    if verbose:
        _status(function, False)

    return sorted(tracks)


def runArgs():

    default = MopsParameters(verbose=False)

    parser = argparse.ArgumentParser(
        prog="runMops",
        description="Given a set of nightly or obshist DIA sources, will run LSST's Moving Object Pipeline (MOPs)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("diasourcesDir", help="Directory containing nightly diasources (.dias)")
    parser.add_argument("outputDir", help="Output directory to be created for file output (must not exist)")

    # Config file, load parameters from config file if given
    parser.add_argument("-cfg", "--config_file", default=None,
        help="""If given, will read parameter values from file to overwrite default values defined in MopsParameters. 
        Parameter values not-defined in config file will be set to default. See default.cfg for sample config file.""")

    # Verbosity 
    parser.add_argument("-v","--verbose", action="store_false",
        help="Enables/disables print output")

    # findTracklets
    parser.add_argument("-vM", "--velocity_max", default=default.vMax, 
        help="Maximum velocity (used in findTracklets)")
    parser.add_argument("-vm", "--velocity_min", default=default.vMin, 
        help="Minimum velocity (used in findTracklets)")

    # collapseTracklets, purifyTracklets
    parser.add_argument("-rT", "--ra_tolerance", default=default.raTol, 
        help="RA tolerance (used in collapseTracklets)")
    parser.add_argument("-dT", "--dec_tolerance", default=default.decTol, 
        help="Dec tolerance (used in collapseTracklets)")
    parser.add_argument("-aT", "--angular_tolerance", default=default.angTol,
        help="Angular tolerance (used in collapseTracklets)")
    parser.add_argument("-vT", "--velocity_tolerance", default=default.vTol, 
        help="Velocity tolerance (used in collapseTracklets)")
    parser.add_argument("-m","--method", default=default.method,
        help="""Method to collapse tracklets, can be one of: greedy | minimumRMS | bestFit.
        If greedy, then we choose as many compatible tracklets as possible, as returned by the tree search. 
        If minimumRMS, we take the results of the tree search and repeatedly find the tracklet which would 
        have the lowest resulting RMS value if added, then add it. If bestFit, we repeatedly choose the tracklet 
        which is closest to the current approximate line first, rather than re-calculating best-fit line for 
        each possible tracklet. (used in collapseTracklets)""")
    parser.add_argument("-rF","--use_rms_filter", default=default.useRMSfilt,
        help="Enforce a maximum RMS distance for any tracklet which is the product of collapsing (used in collapseTracklets)")
    parser.add_argument("-rM", "--rms_max", default=default.rmsMax,
        help="""Only used if useRMSfilt == true. Describes the function for RMS filtering.  
        Tracklets will not be collapsed unless the resulting tracklet would have RMS <= maxRMSm * average magnitude + maxRMSb 
        (used in collapseTracklets and purifyTracklets""")

    # removeSubsets (tracklets)
    parser.add_argument("-S","--remove_subset_tracklets", default=default.rmSubsetTracklets,
        help="Remove subsets (used in removeSubsets)")
    parser.add_argument("-k","--keep_only_longest_tracklets", default=default.keepOnlyLongestTracklets,
        help="Keep only the longest collinear tracklets in a set (used in removeSubsets)")

    # makeLinkTrackletsInput_byNight
    parser.add_argument("-w", "--window_size", default=default.windowSize,
        help="Number of nights in sliding window (used in makeLinkTrackletsInput_byNight.py")

    # linkTracklets
    parser.add_argument("-e", "--detection_error_threshold", default=default.detErrThresh,
        help="Maximum allowed observational error (used in linkTracklets)")
    parser.add_argument("-D", "--dec_acceleration_max", default=default.decAccelMax,
        help="Maximum sky-plane acceleration in Dec (used in linkTracklets)")
    parser.add_argument("-R", "--ra_acceleration_max", default=default.raAccelMax,
        help="Maximum sky-plane acceleration in RA (used in linkTracklets)")
    parser.add_argument("-u", "--nights_min", default=default.nightMin,
        help="Require tracks to contain detections from at least this many nights (used in linkTracklets)")
    parser.add_argument("-s", "--detections_min", default=default.detectMin,
        help="Require tracks to contain at least this many detections (used in linkTracklets)")
    parser.add_argument("-b", "--output_buffer_size", default=default.bufferSize,
        help="Number of tracks to buffer in memory before flushing output (used in linkTracklets)")
    parser.add_argument("-F", "--latest_first_endpoint", default=default.latestFirstEnd,
        help="If specified, only search for tracks with first endpoint before time specified (used in linkTracklets)")
    parser.add_argument("-L", "--earliest_last_endpoint", default=default.earliestLastEnd,
        help="If specified, only search for tracks with last endpoint after time specified (used in linkTracklets)")
    parser.add_argument("-n", "--leaf_node_size_max", default=default.leafNodeSizeMax,
        help="Set max leaf node size for nodes in KDTree (used in linkTracklets)")

    # removeSubsets (tracks)
    parser.add_argument("-St","--remove_subset_tracks", default=default.rmSubsetTracks,
        help="Remove subsets (used in removeSubsets)")
    parser.add_argument("-kt","--keep_only_longest_tracks", default=default.keepOnlyLongestTracks,
        help="Keep only the longest collinear tracks in a set (used in removeSubsets)")

    args = parser.parse_args()

    return args


def runMops(parameters, tracker,
            findTracklets=True,
            collapseTracklets=True,
            purifyTracklets=True,
            removeSubsetTracklets=True,
            linkTracklets=True,
            removeSubsetTracks=True,
            enableMultiprocessing=True,
            processes=8,
            overwrite=False,
            verbose=VERBOSE):
    """
    Runs Moving Object Pipeline.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    parameters: (MopsParameters object), user or default defined MOPS parameter object
    tracker: (MopsTracker object), object keeps track of output files and directories
    findTracklets: (boolean) [True], run findTracklets?
    collapse: (boolean) [True], run collapseTracklets?
    purify: (boolean) [True], run purifyTracklets?
    removeSubsetTracklets: (boolean) [True], run removeSubsets on tracklets?
    linkTracklets: (boolean) [True], run linkTracklets?
    removeSubsetTracks: (boolean) [True], run removeSubsets on tracks?
    enableMultiprocessing: (boolean) [True], run linkTracklets in parallel?
    processes: (int) [8], when multiprocessing is enabled, use this many processes. 
    ----------------------
    """
    if verbose:
        print "------- Run MOPS -------"
        print "Running LSST's Moving Object Pipeline"
        print ""

    runDir = tracker.runDir
    diasources = tracker.diasources
    diasourcesDir = tracker.diasourcesDir

    # If overwrite, delete progress stored in tracker.
    if overwrite:
        print "Overwrite triggered: clearing tracker..."
        print ""
        tracker = MopsTracker(runDir, verbose=False)
        tracker.getDetections(diasourcesDir)

    # Build directory structure
    dirs = directoryBuilder(
            runDir,
            findTracklets=findTracklets,
            collapseTracklets=collapseTracklets,
            purifyTracklets=purifyTracklets,
            removeSubsetTracklets=removeSubsetTracklets,
            linkTracklets=linkTracklets,
            removeSubsetTracks=removeSubsetTracks,
            overwrite=overwrite,
            verbose=verbose)
    tracker.ranDirectoryBuilder = True

    # Save parameters
    parameters.toYaml(outDir=runDir)
    print ""

    # Run findTracklets
    if findTracklets:
        if tracker.ranFindTracklets is False:
            tracklets = runFindTracklets(
                            diasources, dirs["trackletsDir"],
                            vmax=parameters.vMax,
                            vmin=parameters.vMin,
                            verbose=verbose)
            tracker.ranFindTracklets = True
            tracker.tracklets = tracklets
            tracker.trackletsDir = dirs["trackletsDir"]
            inputTrackletsDir = dirs["trackletsDir"]
            inputTrackletSuffix = TRACKLET_SUFFIX
            tracker.toYaml(outDir=runDir)
        else:
            print "findTracklets has already completed, moving on..."

        print ""

    if collapseTracklets:
        if tracker.ranIdsToIndices is False:
            # Run idsToIndices
            trackletsByIndex = runIdsToIndices(
                                tracklets, diasources, dirs["trackletsDir"],
                                verbose=verbose)
            tracker.ranIdsToIndices = True
            tracker.trackletsByIndex = trackletsByIndex
            tracker.trackletsByIndexDir = dirs["trackletsDir"]
            tracker.toYaml(outDir=runDir)
        else:
            print "idsToIndices has already completed, moving on..."

        print ""

        # Run collapseTracklets
        if tracker.ranCollapseTracklets is False:
            collapsedTracklets = runCollapseTracklets(
                                    trackletsByIndex, diasources,
                                    dirs["collapsedDir"],
                                    raTol=parameters.raTol,
                                    decTol=parameters.decTol,
                                    angTol=parameters.angTol,
                                    vTol=parameters.vTol,
                                    method=parameters.method,
                                    useRMSfilt=parameters.useRMSfilt,
                                    rmsMax=parameters.rmsMax,
                                    verbose=verbose)
            collapsedTrackletsById = runIndicesToIds(
                                        collapsedTracklets, diasources,
                                        dirs["collapsedDir"],
                                        COLLAPSED_TRACKLET_SUFFIX,
                                        verbose=verbose)
            tracker.ranCollapseTracklets = True
            tracker.collapsedTracklets = collapsedTracklets
            tracker.collapsedTrackletsDir = dirs["collapsedDir"]
            tracker.collapsedTrackletsById = collapsedTrackletsById
            tracker.collapsedTrackletsByIdDir = dirs["collapsedDir"]
            inputTrackletsDir = dirs["collapsedDir"]
            inputTrackletSuffix = COLLAPSED_TRACKLET_SUFFIX + TRACKLET_BY_ID_SUFFIX
            tracker.toYaml(outDir=runDir)
        else:
            print "collapseTracklets has already completed, moving on..."

        print ""

    if purifyTracklets:
        # Run purifyTracklets
        if tracker.ranPurifyTracklets is False:
            purifiedTracklets = runPurifyTracklets(
                                    collapsedTracklets, diasources,
                                    dirs["purifiedDir"],
                                    rmsMax=parameters.rmsMax,
                                    verbose=verbose)
            purifiedTrackletsById = runIndicesToIds(
                                        purifiedTracklets, diasources,
                                        dirs["purifiedDir"],
                                        PURIFIED_TRACKLET_SUFFIX,
                                        verbose=verbose)
            tracker.ranPurifyTracklets = True
            tracker.purifiedTracklets = purifiedTracklets
            tracker.purifiedTrackletsDir = dirs["purifiedDir"]
            tracker.purifiedTrackletsById = purifiedTrackletsById
            tracker.purifiedTrackletsByIdDir = dirs["purifiedDir"]
            inputTrackletsDir = dirs["purifiedDir"]
            tracker.toYaml(outDir=runDir)
        else:
            print "purifyTracklets has already completed, moving on..."

        print ""

    if removeSubsetTracklets:
        # Run removeSubsets
        if tracker.ranRemoveSubsetTracklets is False:
            finalTracklets = runRemoveSubsets(
                                purifiedTracklets, diasources,
                                dirs["finalTrackletsDir"],
                                rmSubsets=parameters.rmSubsetTracklets,
                                keepOnlyLongest=parameters.keepOnlyLongestTracklets,
                                verbose=verbose)
            tracker.ranRemoveSubsetTracklets = True
            tracker.finalTracklets = finalTracklets
            tracker.finalTrackletsDir = dirs["finalTrackletsDir"]
            tracker.toYaml(outDir=runDir)
        else:
            print "removeSubsets (tracklets) has already completed, moving on..."

        print ""

        # Run indicesToIds
        if tracker.ranIndicesToIds is False:
            finalTrackletsById = runIndicesToIds(
                                    finalTracklets, diasources,
                                    dirs["finalTrackletsDir"],
                                    FINAL_TRACKLET_SUFFIX,
                                    verbose=verbose)
            tracker.ranIndicesToIds = True
            tracker.finalTrackletsById = finalTrackletsById
            tracker.finalTrackletsByIdDir = dirs["finalTrackletsDir"]
            inputTrackletsDir = dirs["finalTrackletsDir"]
            inputTrackletSuffix = FINAL_TRACKLET_SUFFIX + TRACKLET_BY_ID_SUFFIX
            tracker.toYaml(outDir=runDir)
        else:
            print "indicesToIds has already completed, moving on..."
        
        print ""

    if linkTracklets:
        # Run makeLinkTrackletsInputByNight
        if tracker.ranMakeLinkTrackletsInputByNight is False:
            dets, ids = runMakeLinkTrackletsInputByNight(
                            diasourcesDir, inputTrackletsDir,
                            dirs["trackletsByNightDir"],
                            trackletSuffix=inputTrackletSuffix,
                            windowSize=parameters.windowSize,
                            verbose=verbose)
            tracker.ranMakeLinkTrackletsInputByNight = True
            tracker.dets = dets
            tracker.ids = ids
            tracker.trackletsByNightDir = dirs["trackletsByNightDir"]
            tracker.toYaml(outDir=runDir)
        else:
            print "makeLinkTrackletsInput_byNight has already completed, moving on..."

        print ""

        # Run linkTracklets
        if tracker.ranLinkTracklets is False:
            tracks = runLinkTracklets(
                        dets, ids, dirs["tracksDir"],
                        enableMultiprocessing=enableMultiprocessing,
                        processes=processes,
                        detErrThresh=parameters.detErrThresh,
                        decAccelMax=parameters.decAccelMax,
                        raAccelMax=parameters.raAccelMax,
                        nightMin=parameters.nightMin,
                        detectMin=parameters.detectMin,
                        bufferSize=parameters.bufferSize,
                        latestFirstEnd=parameters.latestFirstEnd,
                        earliestLastEnd=parameters.earliestLastEnd,
                        leafNodeSizeMax=parameters.leafNodeSizeMax,
                        verbose=verbose)
            tracker.ranLinkTracklets = True
            tracker.tracks = tracks
            tracker.tracksDir = dirs["tracksDir"]
            tracker.toYaml(outDir=runDir)
        else:
            print "linkTracklets has already completed, moving on..."

        print ""

    if removeSubsetTracks:
        # Run removeSubsets (tracks)
        if tracker.ranRemoveSubsetTracks is False:
            finalTracks = runRemoveSubsets(
                            tracks, diasources, dirs["finalTracksDir"],
                            rmSubsets=parameters.rmSubsetTracks,
                            keepOnlyLongest=parameters.keepOnlyLongestTracks,
                            suffix=FINAL_TRACK_SUFFIX,
                            verbose=verbose)
            tracker.ranRemoveSubsetTracks = True
            tracker.finalTracks = finalTracks
            tracker.finalTracksDir = dirs["finalTracksDir"]
            tracker.toYaml(outDir=runDir)
        else:
            print "removeSubsets (tracks) has already completed, moving on..."

        print ""

    # Print status and save tracker
    tracker.info()
    tracker.toYaml(outDir=runDir)

    return parameters, tracker


def _status(function, current):

    if current:
        print "------- Run MOPS -------"
        print "Running %s..." % (function)
    else:
        print "Completed running %s." % (function)
        print ""
    return


def _log(function, outDir):
    # Split function name to get rid of possible .py
    function = os.path.splitext(function)[0]

    # Create outfile and errfile streams
    outfile = file(os.path.join(outDir, function + ".out"), "w")
    errfile = file(os.path.join(outDir, function + ".err"), "w")

    return outfile, errfile


def _out(outDir, filename, suffix):
    # Retrieve base file name
    base = os.path.basename(filename)
    # Remove all suffixes from filename and add new
    outName = base.split(".")[0] + suffix
    # Create path 
    outFile = os.path.join(outDir, outName)
    return outFile


def _runWindow(call):
    # Unfortunately pool.map() can"t map a function call of multiple arguments
    # so we have to extract the trackOut name from the function call.
    # When python 3.3 is accepted as standard, pool.starmap() will be used instead.
    trackOut = call[18]
    outfile = file(trackOut + ".out", "w")
    errfile = file(trackOut + ".err", "w")
    subprocess.call(call, stdout=outfile, stderr=errfile)
    return

if __name__ == "__main__":

    # Run command line arg parser and retrieve args
    args = runArgs()
    verbose = args.verbose

    # Retrieve output directory and nightly DIA Sources directory
    runDir = os.path.join(os.path.abspath(args.outputDir), "")
    diasourcesDir = os.path.join(os.path.abspath(args.diasourcesDir), "")

    # Initialize MopsParameters and MopsTracker
    if args.config_file == None:
        parameters = MopsParameters(
                        velocity_max=args.velocity_max,
                        velocity_min=args.velocity_min,
                        ra_tolerance=args.ra_tolerance,
                        dec_tolerance=args.dec_tolerance,
                        angular_tolerance=args.angular_tolerance,
                        velocity_tolerance=args.velocity_tolerance,
                        method=args.method,
                        use_rms_filter=args.use_rms_filter,
                        rms_max=args.rms_max,
                        remove_subset_tracklets=args.remove_subset_tracklets,
                        keep_only_longest_tracklets=args.keep_only_longest_tracklets,
                        window_size=args.window_size,
                        detection_error_threshold=args.detection_error_threshold,
                        dec_acceleration_max=args.dec_acceleration_max,
                        ra_acceleration_max=args.ra_acceleration_max,
                        latest_first_endpoint=args.latest_first_endpoint,
                        earliest_last_endpoint=args.earliest_last_endpoint,
                        nights_min=args.nights_min,
                        detections_min=args.detections_min,
                        output_buffer_size=args.output_buffer_size,
                        leaf_node_size_max=args.leaf_node_size_max,
                        remove_subset_tracks=args.remove_subset_tracks,
                        keep_only_longest_tracks=args.keep_only_longest_tracks,
                        verbose=verbose)
    else:
        if verbose:
            print "Config file given. Reading parameters from file..."
            print ""
        cfg = yaml.load(file(args.config_file, "r"))
        parameters = MopsParameters(**cfg)

    # Initialize tracker
    tracker = MopsTracker(runDir, verbose=verbose)
    tracker.getDetections(diasourcesDir)

    # Run MOPs
    parameters, tracker = runMops(parameters, tracker, verbose=verbose)