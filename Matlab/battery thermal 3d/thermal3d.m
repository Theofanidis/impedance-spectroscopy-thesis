clc;
clear all;
close all;

Ambient = 303;
Time = 15*60;
FEM_Timestep = 5;
SIM_Timestep = 5;


function Q = thandle1(location,state)
    Area = 0.18*0.07;
    Q = -2.73375 .* state.u ./ Area;
end

function T = thandle2(location, state)
    T0 = 30 + 273.15;
    Tmin = -5 + 273.15;
    tau = 350;
    t = state.time;
    T_scalar = Tmin + (T0 - Tmin) * exp(-t / tau);
    T = T_scalar * ones(size(location.x));
end

% Model Design and Properties
plate1_geometry = scale(fegeometry("plate1.stl"), 0.001);
plate2_geometry = scale(fegeometry("plate2.stl"), 0.001);
battery_geometry = scale(fegeometry("batt3.stl"), 0.001);
geo23 = union(battery_geometry, plate2_geometry, KeepBoundaries=[false true]);
geo123 = union(plate1_geometry, geo23, KeepBoundaries=[true false]);
model_geometry = rotate(geo123, 90, [1 0 0], [0 0 0]);
model = femodel(AnalysisType="thermalTransient", Geometry=model_geometry);
pdegplot(model, CellLabels="on", FaceLabels="on");

model.MaterialProperties(1) = materialProperties(...
                                    ThermalConductivity= 205, ...
                                    MassDensity= 2700, ...
                                    SpecificHeat= 900 ...
                                 );
model.MaterialProperties(3) = materialProperties(...
                                    ThermalConductivity= 0.83, ...
                                    MassDensity= 0.68/(0.180*0.027*0.070), ...
                                    SpecificHeat= 1023 ...
                                 );
model.MaterialProperties(2) = materialProperties(...
                                    ThermalConductivity= 205, ...
                                    MassDensity= 2700, ...
                                    SpecificHeat= 900 ...
                                 );

model.CellIC = cellIC(Temperature=Ambient);

% Boundary Condition
model.FaceBC(51) = faceBC(Temperature=273);
model.FaceBC(108) = faceBC(Temperature=273);
%model.FaceLoad(51) = faceLoad(AmbientTemperature=273, ConvectionCoefficient=2.733/(0.18*0.07));
%model.FaceLoad(108) = faceLoad(AmbientTemperature=273, ConvectionCoefficient=2.733/(0.18*0.07));
%model.FaceLoad(51) = faceLoad(Heat=@thandle1);
%model.FaceLoad(108) = faceLoad(Heat=@thandle1);

% Exposed Faces Convection with Ambient
%model.FaceLoad(117) = faceLoad(AmbientTemperature=Ambient, ConvectionCoefficient=);
%model.FaceLoad(109) = faceLoad(AmbientTemperature=Ambient, ConvectionCoefficient=);
%model.FaceLoad(114) = faceLoad(AmbientTemperature=Ambient, ConvectionCoefficient=);
%model.FaceLoad(112) = faceLoad(AmbientTemperature=Ambient, ConvectionCoefficient=);


% Compute Transient
model = generateMesh(model);
results = solve(model, [0 : FEM_Timestep : Time]);
Qd1 = evaluateHeatRate(results, Face=51);
Qd2 = evaluateHeatRate(results, Face=108);
T1 = mean(results.Temperature(findNodes(results.Mesh, "region", "Face", 51), :), 1);
T2 = mean(results.Temperature(findNodes(results.Mesh, "region", "Face", 108), :), 1);
T_center = mean(results.Temperature(findNodes(results.Mesh, "nearest", mean(results.Mesh.Nodes, 2)), :), 1);

% Create 3D Cartesian Grid from FE mesh
x = results.Mesh.Nodes(1, :);
y = results.Mesh.Nodes(2, :);
z = results.Mesh.Nodes(3, :);
xq = linspace(min(x), max(x), 60);
yq = linspace(min(y), max(y), 60);
zq = linspace(min(z), max(z), 60);
[Xq, Yq, Zq] = meshgrid(xq, yq, zq);


fig1 = figure("Name", "3D Animation", "WindowStyle", "normal", "WindowState", "maximized");
fig2 = figure("Name", "Border Heat Flux");

figure(fig2);
subplot(2, 1, 1);
title("Border Heat Flux");
xlabel('t (sec)');
ylabel('qdd (W/m^2)');
hold on;
plot(results.SolutionTimes, Qd1);
plot(results.SolutionTimes, Qd2);
legend("Qd1", "Qd2");
subplot(2, 1, 2);
title("Temperature");
xlabel('t (sec)');
ylabel('T (K)');
hold on;
plot(results.SolutionTimes, T1);
plot(results.SolutionTimes, T2);
plot(results.SolutionTimes, T_center);
legend("T1 (Border)", "T2 (Border)", "Center");

exportgraphics(fig2, 'graphs.png', 'Resolution', 300);
save("workspace.mat");

v = VideoWriter('simulation.mp4', 'MPEG-4');
v.FrameRate = 1/SIM_Timestep;
open(v);

for i = [1 : SIM_Timestep/FEM_Timestep : length(results.SolutionTimes)]
    T = results.Temperature(:, i);

    % Convert data to Cartesian Grid
    %F = scatteredInterpolant(transpose(x), transpose(y), transpose(z), T(:), 'linear', 'none');
    %Tq = F(Xq,Yq,Zq);
    Tq = reshape(interpolateTemperature(results, Xq, Yq, Zq, i), size(Xq));

    figure(fig1);
    sgtitle(sprintf("Iter %d/%d - Time: %.2f s (%.2f min). Center: %.2f K (%.2f C)", i, length(results.SolutionTimes), results.SolutionTimes(i), results.SolutionTimes(i)/60, Tq(30, 30, 30), Tq(30, 30, 30)-273));
    % Slice
    subplot(1, 2, 1);
    cla;
    slice(Xq, Yq, Zq, Tq, (min(x) + max(x))/2, (min(y) + max(y))/2, (min(z) + max(z))/2);
    colormap(turbo);
    clim([273 320]);
    xlabel('X');
    ylabel('Y');
    zlabel('Z');
    rotate3d on;
    hold on;
    % Total
    subplot(1, 2, 2);
    cla;
    pdeplot3D(results.Mesh, ColorMapData=T);
    colormap(turbo);
    clim([273 320]);
    xlabel('X');
    ylabel('Y');
    zlabel('Z');
    rotate3d on;
    axis tight;
    axis equal;
    hold on;
    writeVideo(v, getframe(fig1));
end

close(v);
