
###it is not done yet###
import arcpy
arcpy.CheckOutExtension("Network")
arcpy.env.overwriteOutput = True

workspace = arcpy.env.workspace
# ambil parameter
dataCovid = arcpy.GetParameterAsText(0)
dataJalan = arcpy.GetParameterAsText(1)
Buffer = arcpy.GetParameterAsText(2)
hasil = arcpy.GetParameterAsText(3)

mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]
pCovid = arcpy.MakeFeatureLayer_management(
    dataCovid, "covid")
pCovidL = pCovid.getOutput(0)
arcpy.mapping.AddLayer(df, pCovidL)
# Input Network Dataset
serviceArea = arcpy.na.MakeServiceAreaLayer(
    dataJalan, "Service Area", "Length", "TRAVEL_FROM", Buffer)
SALayer = serviceArea.getOutput(0)

# Misahin
subLayer = arcpy.na.GetNAClassNames(SALayer)
facilitiesLayer = subLayer["Facilities"]
mrbLayer = subLayer["SAPolygons"]

# Mapping Covid
covidCandidateFields = arcpy.ListFields(pCovid)
covidFieldMappings = arcpy.na.NAClassFieldMappings(
    SALayer, facilitiesLayer, False, covidCandidateFields)
covidFieldMappings["Name"].mappedFieldName = "status"
arcpy.na.AddLocations(SALayer, facilitiesLayer, pCovidL,
                      covidFieldMappings, "500 Meters")

# Buat Multi Ring Buffer
arcpy.na.Solve(SALayer, "SKIP", "CONTINUE")

mrbL = arcpy.mapping.ListLayers(SALayer)[5]
arcpy.mapping.AddLayer(df, mrbL)
# Add Field Named Value to Multi Ring Buffer (MRB)
arcpy.AddFieldToAnalysisLayer_na(SALayer, mrbLayer, "value", "SHORT")
# Field Calculate

###it is not done yet###
expression = "reclass(!ToBreak!)"
codeBlock = """def reclass(a):
    if a == 5000:
        return 1
    elif a == 4000:
        return 2
    elif a == 3000:
        return 3
    elif a == 2000:
        return 4
    elif a == 1000:
        return 5"""
arcpy.CalculateField_management(
    mrbLayer, "value", expression, "PYTHON", codeBlock)
# Spaghetti
forSpaghetti = arcpy.CreateFeatureclass_management(
    workspace, "kosong", "POINT")
spaghetti = arcpy.FeatureToPolygon_management(
    mrbLayer, hasil, "", "NO_ATTRIBUTES", forSpaghetti)
# Meatball
meatball = arcpy.FeatureToPoint_management(spaghetti, "meatball", "INSIDE")
# Meatballs
meatballs = arcpy.Intersect_analysis(
    [meatball, mrbLayer], "meatballs", "ALL", "", "POINT")
# Catch the meatball
meatballsHandler = arcpy.Statistics_analysis(
    meatballs, "forJoin", [["value", "SUM"]], "ORIG_FID")
# Join
arcpy.JoinField_management(spaghetti, "FID",
                           meatballsHandler, "ORIG_FID", "SUM_value")
