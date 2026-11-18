clear; 
clc;

model = 'therm20';
assignin('base','tol',0.01);

Vin_array = [-20:2:20];
DT_array = [0:20:100];



Iss  = zeros(length(DT_array), length(Vin_array));
DTss = zeros(length(DT_array), length(Vin_array));
Qcss = zeros(length(DT_array), length(Vin_array));

load_system(model)

% For 1st graph

for i = 1 : length(DT_array)
    DT = DT_array(i);
    assignin('base','DT',DT);

    for j = 1:length(Vin_array)
        Vin = Vin_array(j);
        
        fprintf("Sim: V %d DT %d \n", Vin, DT);

        assignin('base','Vin',Vin);
        simOut = sim(model, 'ReturnWorkspaceOutputs','on');

        I  = simOut.get('I');
        Qc = simOut.get('Qc');

        Iss(j,i)  = I(end);
        Qcss(j,i) = Qc(end);

    end
end




figure

subplot(1,1,1)
hold on
grid on
for i = 1:length(DT_array)
    plot(Iss(:,i), Vin_array(:), '-o')
end
xlabel('Voltage (V)')
ylabel('Current (A)')
title('V-I')
legend(string(DT_array) + " oC")



