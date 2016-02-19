import yaml
import unittest
import shutil
import os

import runMops
from MopsTracker import MopsTracker
from MopsParameters import MopsParameters

PARAMETERS = "unittest/controlRun/full/parameters.yaml"
TRACKER = "unittest/controlRun/full/tracker.yaml"
DATA_DIR = "unittest/testData/full/nightly"
TEST_DIR = "unittest/testRun/full/"

VERBOSE = True

class MopsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dataDir = DATA_DIR
        cls.testDir = TEST_DIR

        cls.testTracker = MopsTracker(TEST_DIR)
        cls.testParameters = MopsParameters(verbose=VERBOSE)

        cls.controlParameters = yaml.load(file(PARAMETERS, "r"))
        cls.controlTracker = yaml.load(file(TRACKER, "r"))

        runMops.runMops(cls.testParameters, cls.testTracker, cls.dataDir, cls.testDir, verbose=VERBOSE)

    def test_directoryBuilder(self):
        controlDirs = [self.controlTracker.trackletsDir, self.controlTracker.trackletsByIndexDir,
        self.controlTracker.collapsedTrackletsDir, self.controlTracker.collapsedTrackletsByIdDir,
        self.controlTracker.purifiedTrackletsDir, self.controlTracker.purifiedTrackletsByIdDir, 
        self.controlTracker.finalTrackletsDir, self.controlTracker.finalTrackletsByIdDir,
        self.controlTracker.trackletsByNightDir, self.controlTracker.tracksDir]

        testDirs = [self.testTracker.trackletsDir, self.testTracker.trackletsByIndexDir,
        self.testTracker.collapsedTrackletsDir, self.testTracker.collapsedTrackletsByIdDir,
        self.testTracker.purifiedTrackletsDir, self.testTracker.purifiedTrackletsByIdDir, 
        self.testTracker.finalTrackletsDir, self.testTracker.finalTrackletsByIdDir,
        self.testTracker.trackletsByNightDir, self.testTracker.tracksDir]

        for td, cd in zip(testDirs, controlDirs):
            self.assertEqual(os.path.basename(td), os.path.basename(cd))

    def test_findTracklets(self):
        testTracklets = sorted(self.testTracker.tracklets)
        controlTracklets = sorted(self.controlTracker.tracklets)

        for tt, ct in zip(testTracklets, controlTracklets):

            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_idsToIndices(self):
        testTrackletsByIndex = sorted(self.testTracker.trackletsByIndex)
        controlTrackletsByIndex = sorted(self.controlTracker.trackletsByIndex)

        for tt, ct in zip(testTrackletsByIndex, controlTrackletsByIndex):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_collapseTracklets(self):
        testCollapsedTracklets = sorted(self.testTracker.collapsedTracklets)
        controlCollapsedTracklets = sorted(self.controlTracker.collapsedTracklets)

        for tt, ct in zip(testCollapsedTracklets, controlCollapsedTracklets):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_collapsedTrackletsById(self):
        testCollapsedTrackletsById = sorted(self.testTracker.collapsedTrackletsById)
        controlCollapsedTrackletsById = sorted(self.controlTracker.collapsedTrackletsById)

        for tt, ct in zip(testCollapsedTrackletsById, controlCollapsedTrackletsById):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_purifyTracklets(self):
        testPurifiedTracklets = sorted(self.testTracker.purifiedTracklets)
        controlPurifiedTracklets = sorted(self.controlTracker.purifiedTracklets)

        for tt, ct in zip(testPurifiedTracklets, controlPurifiedTracklets):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_purifiedTrackletsById(self):
        testPurifiedTrackletsById = sorted(self.testTracker.purifiedTrackletsById)
        controlPurifiedTrackletsById = sorted(self.controlTracker.purifiedTrackletsById)

        for tt, ct in zip(testPurifiedTrackletsById, controlPurifiedTrackletsById):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_removeSubsetsTracklets(self):
        testFinalTracklets = sorted(self.testTracker.finalTracklets)
        controlFinalTracklets = sorted(self.controlTracker.finalTracklets)

        for tt, ct in zip(testFinalTracklets, controlFinalTracklets):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_finalTrackletsById(self):
        testFinalTrackletsById = sorted(self.testTracker.finalTrackletsById)
        controlFinalTrackletsById = sorted(self.controlTracker.finalTrackletsById)

        for tt, ct in zip(testFinalTrackletsById, controlFinalTrackletsById):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_makeLinkTrackletsInput_byNight(self):
        testDets = sorted(self.testTracker.dets)
        controlDets = sorted(self.controlTracker.dets)

        for tt, ct in zip(testDets, controlDets):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

        testIds = sorted(self.testTracker.ids)
        controlIds = sorted(self.controlTracker.ids)

        for tt, ct in zip(testIds, controlIds):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_linkTracklets(self):
        testTracks = sorted(self.testTracker.tracks)
        controlTracks = sorted(self.controlTracker.tracks)

        for tt, ct in zip(testTracks, controlTracks):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_removeSubsetsTracks(self):
        testFinalTracks = sorted(self.testTracker.finalTracks)
        controlFinalTracks = sorted(self.controlTracker.finalTracks)

        for tt, ct in zip(testFinalTracks, controlFinalTracks):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

def suite():
    tests = ['test_directoryBuilder', 'test_findTracklets', 'test_idsToIndices', 'test_collapseTracklets', 'test_collapsedTrackletsById', 
        'test_purifyTracklets', 'test_purifiedTrackletsById', 'test_removeSubsetsTracklets', 'test_finalTrackletsById', 'test_makeLinkTrackletsInput_byNight', 'test_linkTracklets', 'test_removeSubsetsTracks']
    return unittest.TestSuite(map(MopsTest, tests))

if __name__=="__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Runs MOPS on test data and compares the output of each MOPS function to a set of control files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-s1', action='store_true', help="Run unittest only with source 1.")
    group.add_argument('-s2', action='store_true', help="Run unittest only with source 2.")
    group.add_argument('-s3', action='store_true', help="Run unittest only with source 3.")

    args = parser.parse_args()

    if args.s1:
        PARAMETERS = "unittest/controlRun/source1/parameters.yaml"
        TRACKER = "unittest/controlRun/source1/tracker.yaml"
        DATA_DIR = "unittest/testData/source1/nightly"
        TEST_DIR = "unittest/testRun/source1/"
    elif args.s2: 
        PARAMETERS = "unittest/controlRun/source2/parameters.yaml"
        TRACKER = "unittest/controlRun/source2/tracker.yaml"
        DATA_DIR = "unittest/testData/source2/nightly"
        TEST_DIR = "unittest/testRun/source2/"
    elif args.s3:
        PARAMETERS = "unittest/controlRun/source3/parameters.yaml"
        TRACKER = "unittest/controlRun/source3/tracker.yaml"
        DATA_DIR = "unittest/testData/source3/nightly"
        TEST_DIR = "unittest/testRun/source3/" 

    runner = unittest.TextTestRunner()
    results = runner.run(suite())

    if results.wasSuccessful():
        print "All tests PASSED. Deleting MOPs output."
        shutil.rmtree(TEST_DIR)
    else:
        print "FAILURES detected. Keeping MOPs output."
        pass