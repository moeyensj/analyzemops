import os
import numpy as np
import pandas as pd
import sqlite3


DETECTION_COLUMNS = {"diaId": "det_id", 
                     "visitId": "field_id", 
                     "objectId": "object_name", 
                     "ra": "ra_deg", 
                     "dec": "dec_deg", 
                     "mjd": "epoch_mjd", 
                     "mag": "mag", 
                     "snr": "mag_sigma"}

__all__ = ["readTracklet", "readTrack", "readIds",
           "readDetectionsIntoDataframe", "readDetectionsIntoDatabase",
           "readTrackletsIntoDatabase", "readTracksIntoDatabase",
           "readNight", "readWindow", "convertDetections",
           "buildTrackletDatabase", "buildTrackDatabase", "attachDatabases"]

def readTracklet(tracklet):
    return np.fromstring(tracklet, sep=" ", dtype=int) 

def readTrack(track):
    return np.fromstring(track, sep=" ", dtype=int)

def readIds(ids):
    return np.fromstring(track, sep=" ", dtype=int)

def readDetectionsIntoDataframe(detsFile, header=None):
    return pd.read_csv(detsFile, header=header, names=["diaId", "visitId", "objectId", "ra", "dec", "mjd", "mag", "snr"], index_col="diaId", delim_whitespace=True)

def readDetectionsIntoDatabase(detsFile, cursor, table="DiaSources", header=None):
    dets_df = readDetectionsIntoDataframe(detsFile, header=header)
    dets_df.to_sql(table, cursor, if_exists="append")
    return 

def readTrackletsIntoDatabase(trackletFile, con, trackIdOffset=0, chunksize=100000):
    
    for i, chunk in enumerate(pd.read_csv(trackFile, header=None, names=["diaId"], chunksize=chunksize)):        
        # Create an array of integer trackletIds
        trackIds = np.arange(trackIdOffset + (chunksize * i) + 1, len(chunk) + trackIdOffset + (chunksize * i) + 1, dtype=int)
        # Read in the trackletFile where every row is a string of diaIds delimited by whitespace
        # Split the string of diaIds into separate columns and then stack the columns so that every tracklet has 
        # a row for every diaId
        chunk_df = pd.DataFrame(pd.DataFrame(chunk["diaId"].str.split(" ").tolist(), index=trackIds).stack(), columns=["diaId"])
        chunk_df.reset_index(1, drop=True, inplace=True)
        chunk_df["trackletId"] = chunk_df.index
        chunk_df = chunk_df[["trackletId", "diaId"]]
        # Not all tracks have the same number of detections, empty detections needs to be dropped
        chunk_df["diaId"].replace("", np.nan, inplace=True)
        chunk_df.dropna(inplace=True)
        
        # Save the resulting dataframe to a sql database
        chunk_df.to_sql("TrackletMembers", con, if_exists="append", index=False)
    return

def readTracksIntoDatabase(trackFile, con, trackIdOffset=0, chunksize=100000):
    
    for i, chunk in enumerate(pd.read_csv(trackFile, header=None, names=["diaId"], chunksize=chunksize)):        
        # Create an array of integer trackIds
        trackIds = np.arange(trackIdOffset + (chunksize * i) + 1, len(chunk) + trackIdOffset + (chunksize * i) + 1, dtype=int)
        # Read in the trackfile where every row is a string of diaIds delimited by whitespace
        # Split the string of diaIds into separate columns and then stack the columns so that every track has 
        # a row for every diaId
        chunk_df = pd.DataFrame(pd.DataFrame(chunk["diaId"].str.split(" ").tolist(), index=trackIds).stack(), columns=["diaId"])
        chunk_df.reset_index(1, drop=True, inplace=True)
        chunk_df["trackId"] = chunk_df.index
        chunk_df = chunk_df[["trackId", "diaId"]]
        # Not all tracks have the same number of detections, empty detections needs to be dropped
        chunk_df["diaId"].replace("", np.nan, inplace=True)
        chunk_df.dropna(inplace=True)
        
        # Save the resulting dataframe to a sql database
        chunk_df.to_sql("TrackMembers", con, if_exists="append", index=False)
    return

def readNight(detFile):
    return int(os.path.basename(detFile).split(".")[0])

def readWindow(trackFile):
    window = os.path.basename(trackFile).split(".")[0].split("_")
    return int(window[1]), int(window[3])

def convertDetections(inFile, outFile, mappingFile, columnDict=DETECTION_COLUMNS, convertObjectIds=True, chunksize=10000):
    
    object_ids = {"NS": -1, "FD": -2}
    object_num = 0
    
    for chunk in pd.read_csv(inFile, sep=" ", chunksize=chunksize):
        chunk = chunk[[columnDict["diaId"], columnDict["visitId"], columnDict["objectId"], 
                       columnDict["ra"], columnDict["dec"], columnDict["mjd"], 
                       columnDict["mag"], columnDict["snr"]]]
        
        if convertObjectIds:
            for object_id in chunk[columnDict["objectId"]].values:
                if object_id not in object_ids.keys():
                    object_num += 1
                    object_ids[object_id] = object_num
            chunk[columnDict["objectId"]].replace(to_replace=object_ids, inplace=True)
        
        chunk.to_csv(outFile, sep=" ", mode="append", header=False, index=False)
    
    mapping = pd.DataFrame.from_dict(data=object_ids, orient='index')
    mapping.to_csv(mappingFile, sep=" ", header=False)
    return

def buildTrackletDatabase(database, outDir):

    database = os.path.join(os.path.abspath(outDir), "", database)
    con = sqlite3.connect(database)

    print "Creating DiaSources table..."
    con.execute("""
        CREATE TABLE DiaSources (
            diaId INTEGER PRIMARY KEY,
            visitId INTEGER,
            objectId INTEGER,
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
            objectId INTEGER PRIMARY KEY,
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
        AND findableAsTrack = 1
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
            diaId INTEGER
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
