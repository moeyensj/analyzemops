import os
import sqlite3

def buildTrackletDatabase(database, outDir):

    database = os.path.join(os.path.abspath(outDir), "", database)
    con = sqlite3.connect(database)

    print "Creating DiaSources table..."
    con.execute("""
        CREATE TABLE DiaSources (
            diaId INTEGER PRIMARY KEY,
            visitId INTEGER,
            ssmId INTEGER,
            ra REAL,
            dec REAL,
            mjd REAL,
            mag REAL,
            snr REAL
        );
        """)

    print "Creating AllObjects table..."
    con.execute("""
        CREATE TABLE AllObjects (
            ssmId INTEGER PRIMARY KEY,
            numDetections INTEGER,
            findableAsTracklet BOOL,
            findableAsTrack BOOL,
            numFalseTracklets INTEGER,
            numTrueTracklets INTEGER,
            numFalseCollapsedTracklets INTEGER,
            numTrueCollapsedTracklets INTEGER,
            numFalsePurifiedTracklets INTEGER,
            numTruePurifiedTracklets INTEGER,
            numFalseFinalTracklets INTEGER,
            numTrueFinalTracklets INTEGER,
            numFalseTracks INTEGER,
            numTrueTracks INTEGER,
            numFalseFinalTracks INTEGER,
            numTrueFinalTracks INTEGER
        );
        """)

    print "Creating FoundObjects view..."
    con.execute("""
        CREATE VIEW FoundObjects AS
        SELECT * FROM AllObjects
        WHERE numTrueTracks > 0
        """)

    print "Creating MissedObjects view..."
    con.execute("""
        CREATE VIEW MissedObjects AS
        SELECT * FROM AllObjects
        WHERE numTrueTracks = 0
        """)

    print "Creating AllTracklets table..."
    con.execute("""
        CREATE TABLE AllTracklets (
            trackletId INTEGER PRIMARY KEY,
            linkedObjectId INTEGER,
            numLinkedObjects INTEGER,
            numMembers INTEGER,
            velocity REAL,
            rms REAL,
            night REAL,
            createdBy INTEGER,
            deletedBy INTEGER
        );
        """)

    print "Creating TrackletMembers table..."
    con.execute("""
        CREATE TABLE TrackletMembers (
            trackletId INTEGER,
            diaid INTEGER
        );
        """)

    print "Creating Tracklets view..."
    con.execute("""
        CREATE VIEW Tracklets AS
        SELECT * FROM AllTracklets
        WHERE createdBy = 1
        """)

    print "Creating CollapsedTracklets view..."
    con.execute("""
        CREATE VIEW CollapsedTracklets AS
        SELECT * FROM AllTracklets
        WHERE deletedBy = 2
        OR createdBy = 2
        """)

    print "Creating PurifiedTracklets view..."
    con.execute("""
        CREATE VIEW PurifiedTracklets AS
        SELECT * FROM AllTracklets
        WHERE deletedBy = 3
        OR createdBy = 3
        """)

    print "Creating FinalTracklets view..."
    con.execute("""
        CREATE VIEW FinalTracklets AS
        SELECT * FROM AllTracklets
        WHERE deletedBy = 4
        OR createdBy = 4
        """)

    print ""

    return con, database

def buildTrackDatabase(database, outDir):

    database = os.path.join(os.path.abspath(outDir), "", database)
    con = sqlite3.connect(database)

    print "Creating AllTracks table..."
    con.execute("""
        CREATE TABLE AllTracks (
            trackId INTEGER PRIMARY KEY,
            linkedObjectId INTEGER,
            numLinkedObjects INTEGER,
            numMembers INTEGER,
            rms REAL,
            windowStart REAL,
            startTime REAL,
            endTime REAL,
            subsetOf INTEGER, 
            createdBy INTEGER,
            deletedBy INTEGER
        );
        """)

    print "Creating TrackMembers table..."
    con.execute("""
        CREATE TABLE TrackMembers (
            trackId INTEGER,
            diaId INTEGER
        );
        """)

    print "Creating Tracks view..."
    con.execute("""
        CREATE VIEW Tracks AS
        SELECT * FROM AllTracks
        WHERE createdBy = 5
        """)

    print "Creating FinalTracks view..."
    con.execute("""
        CREATE VIEW FinalTracks AS
        SELECT * FROM AllTracks
        WHERE deletedBy = 6
        OR createdBy = 6
        """)

    print ""

    return con, database

def attachDatabases(con, databases):
    attached_names = []

    if len(databases) > 10:
        print "Warning: Cannot attach more than 10 databases..."
        print "Proceeding with the first 10 databases..."
        databases = databases[0:10]
        
    for i, window in enumerate(databases):
        attached_names.append("db%s" % i)
        print "Attaching %s to con as db%s..." % (window, i)
        con.execute("""ATTACH DATABASE '%s' AS db%s;""" % (window, i))
    return attached_names