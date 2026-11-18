
clc;
clear;
close all;

%% 1. Load Simulink model
mdl = 'rom';

load_system(mdl);

%% 2. Check root-level input and output blocks
inports = find_system(mdl, ...
    'SearchDepth', 1, ...
    'BlockType', 'Inport');

outports = find_system(mdl, ...
    'SearchDepth', 1, ...
    'BlockType', 'Outport');

disp('Root-level inputs:');
disp(inports);

disp('Root-level outputs:');
disp(outports);

if ~any(strcmp(inports, [mdl '/T']))
    error('Could not find root-level Inport rom/T.');
end

if ~any(strcmp(outports, [mdl '/Qd']))
    error('Could not find root-level Outport rom/Qd.');
end

%% 3. Calculate operating point at T = 303 K
% This calculates a steady-state operating point.
% It does NOT use 2500 seconds as a temperature.

opspec = operspec(mdl);

% Set the first model input (T) to 303 K
opspec.Inputs(1).u = 303;
opspec.Inputs(1).Known = true;

% Find operating point
op = findop(mdl, opspec);

disp('Operating point calculated.');

%% 4. Define linearization input point
% Input perturbation at the output of root-level Inport T

io(1) = linio([mdl '/T'], 1, 'input');

%% 5. Find the signal connected to Qd
% Get the input port handle of the Qd Outport block

qdh = get_param([mdl '/Qd'], 'PortHandles');

if isempty(qdh.Inport)
    error('Qd has no input port.');
end

% Get the line connected to Qd
lineHandle = get_param(qdh.Inport(1), 'Line');

if isempty(lineHandle) || lineHandle == -1
    error('The Qd Outport is not connected to a signal.');
end

% Identify the source block and source port of that signal
srcBlockHandle = get_param(lineHandle, 'SrcBlockHandle');
srcPortHandle = get_param(lineHandle, 'SrcPortHandle');

if isempty(srcBlockHandle) || srcBlockHandle == -1
    error('Could not identify the source block feeding Qd.');
end

srcBlock = getfullname(srcBlockHandle);

% Find the corresponding output port number
srcPH = get_param(srcBlock, 'PortHandles');

outPort = find(srcPH.Outport == srcPortHandle, 1);

if isempty(outPort)
    error('Could not identify the output port feeding Qd.');
end

disp('Signal feeding Qd originates from:');
disp(srcBlock);

disp('Source output port number:');
disp(outPort);

%% 6. Define linearization output point
% Output measurement at the signal feeding Qd

io(2) = linio(srcBlock, outPort, 'output');

disp('Linearization I/O points:');
disp(io);

%% 7. Linearize the model
% Argument order for your MATLAB version:
% linearize(model, operating_point, I/O_points)

linsys = linearize(mdl, op, io);

disp('Continuous-time linearized model:');
linsys

%% 8. Discretize at 30 Hz
Ts = 1/30;

sysd = c2d(linsys, Ts, 'zoh');

disp('Discrete-time linearized model:');
sysd

%% 9. Plot frequency responses

figure;
bodemag(linsys);
grid on;
title('Continuous-time ROM linearization at 303 K');

figure;
bodemag(sysd);
grid on;
title('Discrete-time ROM linearization at 303 K');

%% 10. Save linearized models
save('rom_linearized.mat', 'linsys', 'sysd', 'op', 'Ts');

disp('Linearization completed.');
disp('Results saved in rom_linearized.mat.');
