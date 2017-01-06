import os
import yaml

__all__ = ["Tracker"]


class Tracker(object):

    def __init__(self, runDir, verbose=True):

        self._diasources = None
        self._tracklets = None
        self._trackletsByIndex = None
        self._collapsedTracklets = None
        self._collapsedTrackletsById = None
        self._purifiedTracklets = None
        self._purifiedTrackletsById = None
        self._finalTracklets = None
        self._finalTrackletsById = None
        self._dets = None
        self._ids = None
        self._tracks = None
        self._finalTracks = None
        self._runDir = runDir
        self._resultsDir = None

        self._diasourcesDir = None
        self._trackletsDir = None
        self._trackletsByIndexDir = None
        self._collapsedTrackletsDir = None
        self._collapsedTrackletsByIdDir = None
        self._purifiedTrackletsDir = None
        self._purifiedTrackletsByIdDir = None
        self._finalTrackletsDir = None
        self._finalTrackletsByIdDir = None
        self._trackletsByNightDir = None
        self._tracksDir = None
        self._finalTracksDir = None

        self._ranDirectoryBuilder = False
        self._ranFindTracklets = False
        self._ranIdsToIndices = False
        self._ranCollapseTracklets = False
        self._ranPurifyTracklets = False
        self._ranRemoveSubsetTracklets = False
        self._ranIndicesToIds = False
        self._ranMakeLinkTrackletsInputByNight = False
        self._ranLinkTracklets = False
        self._ranRemoveSubsetTracks = False

        self._mainDatabase = None
        self._windowDatabases = None
        self._trackletResults = None
        self._trackResults = None

        if verbose:
            self.info()

    @property
    def diasources(self):
        return self._diasources

    @diasources.setter
    def diasources(self, value):
        self._diasources = value

    @property
    def tracklets(self):
        return self._tracklets

    @tracklets.setter
    def tracklets(self, value):
        self._tracklets = value

    @property
    def trackletsByIndex(self):
        return self._trackletsByIndex

    @trackletsByIndex.setter
    def trackletsByIndex(self, value):
        self._trackletsByIndex = value

    @property
    def collapsedTracklets(self):
        return self._collapsedTracklets

    @collapsedTracklets.setter
    def collapsedTracklets(self, value):
        self._collapsedTracklets = value

    @property
    def collapsedTrackletsById(self):
        return self._collapsedTrackletsById

    @collapsedTrackletsById.setter
    def collapsedTrackletsById(self, value):
        self._collapsedTrackletsById = value

    @property
    def purifiedTracklets(self):
        return self._purifiedTracklets

    @purifiedTracklets.setter
    def purifiedTracklets(self, value):
        self._purifiedTracklets = value

    @property
    def purifiedTrackletsById(self):
        return self._purifiedTrackletsById

    @purifiedTrackletsById.setter
    def purifiedTrackletsById(self, value):
        self._purifiedTrackletsById = value

    @property
    def finalTracklets(self):
        return self._finalTracklets

    @finalTracklets.setter
    def finalTracklets(self, value):
        self._finalTracklets = value

    @property
    def finalTrackletsById(self):
        return self._finalTrackletsById

    @finalTrackletsById.setter
    def finalTrackletsById(self, value):
        self._finalTrackletsById = value

    @property
    def dets(self):
        return self._dets

    @dets.setter
    def dets(self, value):
        self._dets = value

    @property
    def ids(self):
        return self._ids

    @ids.setter
    def ids(self, value):
        self._ids = value

    @property
    def tracks(self):
        return self._tracks

    @tracks.setter
    def tracks(self, value):
        self._tracks = value

    @property
    def finalTracks(self):
        return self._finalTracks

    @finalTracks.setter
    def finalTracks(self, value):
        self._finalTracks = value

    @property
    def runDir(self):
        return self._runDir

    @runDir.setter
    def runDir(self, value):
        self._runDir = value

    @property
    def diasourcesDir(self):
        return self._diasourcesDir

    @diasourcesDir.setter
    def diasourcesDir(self, value):
        self._diasourcesDir = value

    @property
    def trackletsDir(self):
        return self._trackletsDir

    @trackletsDir.setter
    def trackletsDir(self, value):
        self._trackletsDir = value

    @property
    def trackletsByIndexDir(self):
        return self._trackletsByIndexDir

    @trackletsByIndexDir.setter
    def trackletsByIndexDir(self, value):
        self._trackletsByIndexDir = value

    @property
    def collapsedTrackletsDir(self):
        return self._collapsedTrackletsDir

    @collapsedTrackletsDir.setter
    def collapsedTrackletsDir(self, value):
        self._collapsedTrackletsDir = value

    @property
    def collapsedTrackletsByIdDir(self):
        return self._collapsedTrackletsByIdDir

    @collapsedTrackletsByIdDir.setter
    def collapsedTrackletsByIdDir(self, value):
        self._collapsedTrackletsByIdDir = value

    @property
    def purifiedTrackletsDir(self):
        return self._purifiedTrackletsDir

    @purifiedTrackletsDir.setter
    def purifiedTrackletsDir(self, value):
        self._purifiedTrackletsDir = value

    @property
    def purifiedTrackletsByIdDir(self):
        return self._purifiedTrackletsByIdDir

    @purifiedTrackletsByIdDir.setter
    def purifiedTrackletsByIdDir(self, value):
        self._purifiedTrackletsByIdDir = value

    @property
    def finalTrackletsDir(self):
        return self._finalTrackletsDir

    @finalTrackletsDir.setter
    def finalTrackletsDir(self, value):
        self._finalTrackletsDir = value

    @property
    def finalTrackletsByIdDir(self):
        return self._finalTrackletsByIdDir

    @finalTrackletsByIdDir.setter
    def finalTrackletsByIdDir(self, value):
        self._finalTrackletsByIdDir = value

    @property
    def trackletsByNightDir(self):
        return self._trackletsByNightDir

    @trackletsByNightDir.setter
    def trackletsByNightDir(self, value):
        self._trackletsByNightDir = value

    @property
    def tracksDir(self):
        return self._tracksDir

    @tracksDir.setter
    def tracksDir(self, value):
        self._tracksDir = value

    @property
    def finalTracksDir(self):
        return self._finalTracksDir

    @finalTracksDir.setter
    def finalTracksDir(self, value):
        self._finalTracksDir = value

    @property
    def resultsDir(self):
        return self._resultsDir

    @resultsDir.setter
    def resultsDir(self, value):
        self._resultsDir = value

    @property
    def ranDirectoryBuilder(self):
        return self._ranDirectoryBuilder

    @ranDirectoryBuilder.setter
    def ranDirectoryBuilder(self, value):
        self._ranDirectoryBuilder = value

    @property
    def ranFindTracklets(self):
        return self._ranFindTracklets

    @ranFindTracklets.setter
    def ranFindTracklets(self, value):
        self._ranFindTracklets = value

    @property
    def ranIdsToIndices(self):
        return self._ranIdsToIndices

    @ranIdsToIndices.setter
    def ranIdsToIndices(self, value):
        self._ranIdsToIndices = value

    @property
    def ranCollapseTracklets(self):
        return self._ranCollapseTracklets

    @ranCollapseTracklets.setter
    def ranCollapseTracklets(self, value):
        self._ranCollapseTracklets = value

    @property
    def ranPurifyTracklets(self):
        return self._ranPurifyTracklets

    @ranPurifyTracklets.setter
    def ranPurifyTracklets(self, value):
        self._ranPurifyTracklets = value

    @property
    def ranRemoveSubsetTracklets(self):
        return self._ranRemoveSubsetTracklets

    @ranRemoveSubsetTracklets.setter
    def ranRemoveSubsetTracklets(self, value):
        self._ranRemoveSubsetTracklets = value

    @property
    def ranIdsToIndices(self):
        return self._ranIdsToIndices

    @ranIdsToIndices.setter
    def ranIdsToIndices(self, value):
        self._ranIdsToIndices = value

    @property
    def ranIndicesToIds(self):
        return self._ranIndicesToIds

    @ranIndicesToIds.setter
    def ranIndicesToIds(self, value):
        self._ranIndicesToIds = value

    @property
    def ranMakeLinkTrackletsInputByNight(self):
        return self._ranMakeLinkTrackletsInputByNight

    @ranMakeLinkTrackletsInputByNight.setter
    def ranMakeLinkTrackletsInputByNight(self, value):
        self._ranMakeLinkTrackletsInputByNight = value

    @property
    def ranLinkTracklets(self):
        return self._ranLinkTracklets

    @ranLinkTracklets.setter
    def ranLinkTracklets(self, value):
        self._ranLinkTracklets = value

    @property
    def ranRemoveSubsetTracks(self):
        return self._ranRemoveSubsetTracks

    @ranRemoveSubsetTracks.setter
    def ranRemoveSubsetTracks(self, value):
        self._ranRemoveSubsetTracks = value

    @property
    def mainDatabase(self):
        return self._mainDatabase

    @mainDatabase.setter
    def mainDatabase(self, value):
        self._mainDatabase = value

    @property
    def windowDatabases(self):
        return self._windowDatabases

    @windowDatabases.setter
    def windowDatabases(self, value):
        self._windowDatabases = value

    @property
    def trackletResults(self):
        return self._trackletResults

    @trackletResults.setter
    def trackletResults(self, value):
        self._trackletResults = value

    @property
    def trackResults(self):
        return self._trackResults

    @trackResults.setter
    def trackResults(self, value):
        self._trackResults = value

    def getDetections(self, diasourcesDir):
        diasourceList = sorted(os.listdir(diasourcesDir))
        diasources = []

        for diasource in diasourceList:
            diasources.append(os.path.join(diasourcesDir, diasource))

        self._diasources = diasources
        self._diasourcesDir = diasourcesDir

        print("Found {} detection files in {}.").format(len(diasourceList), diasourcesDir)
        print()

    def info(self):
        print("------- MOPS Tracker --------")
        print("Current run status:")
        print()
        print("\tfindTracklets:                     {}").format(self._ranFindTracklets)
        print("\tidsToIndices.py:                   {}").format(self._ranIdsToIndices)
        print("\tcollapseTracklets:                 {}").format(self._ranCollapseTracklets)
        print("\tpurifyTracklets:                   {}").format(self._ranPurifyTracklets)
        print("\tremoveSubsets (tracklets):         {}").format(self._ranRemoveSubsetTracklets)
        print("\tindicesToIds.py:                   {}").format(self._ranIndicesToIds)
        print("\tmakeLinkTrackletsInputByNight.py:  {}").format(self._ranMakeLinkTrackletsInputByNight)
        print("\tlinkTracklets:                     {}").format(self._ranLinkTracklets)
        print("\tremoveSubsets (tracks):            {}").format(self._ranRemoveSubsetTracks)
        print()

        return

    def toYaml(self, outDir=None):
        if outDir is None:
            outname = "tracker.yaml"
        else:
            outname = os.path.join(outDir, "tracker.yaml")

        print("Saving tracker to {}").format(outname)

        stream = file(outname, "w")
        yaml.dump(self, stream)
        stream.close()

        return

    @classmethod
    def fromYaml(cls, yamlFile):
        print("Loading tracker from {}").format(yamlFile)

        cls = yaml.load(file(yamlFile, "r"))

        return cls
