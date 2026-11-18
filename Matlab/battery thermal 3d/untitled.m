clc;
clear all;
close all;


plate1_geometry = scale(fegeometry("plate1.stl"), 0.001);
plate2_geometry = scale(fegeometry("plate2.stl"), 0.001);
battery_geometry = scale(fegeometry("batt3.stl"), 0.001);

geo23 = union(battery_geometry, plate2_geometry, KeepBoundaries=[false true]);
model_geometry = rotate(union(plate1_geometry, geo23, KeepBoundaries=[true false]), 90, [1 0 0], [0 0 0]);

model = femodel(AnalysisType="thermalTransient", Geometry=model_geometry);

figure();
pdegplot(model, EdgeLabels="off", FaceLabels="on", CellLabels="on");