clear; 
clc;

model = 'therm';
assignin('base','tol',0.01);

Iin_array   = [1.5 3 4.5 6];
Tcold_array = [-30:2:50];


Vss  = zeros(length(Tcold_array), length(Iin_array));
DTss = zeros(length(Tcold_array), length(Iin_array));
Qcss = zeros(length(Tcold_array), length(Iin_array));

load_system(model)

for i = 1 : length(Iin_array)
    Iin = Iin_array(i);
    assignin('base','Iin',Iin);

    for j = 1:length(Tcold_array)
        Tcold = Tcold_array(j);
        fprintf("Sim: I %d Tc %d \n", Iin, Tcold);

        assignin('base','Tcold',Tcold);
        simOut = sim(model, 'ReturnWorkspaceOutputs','on');

        V  = simOut.get('V');
        DT = simOut.get('DT');
        Qc = simOut.get('Qc');

        Vss(j,i)  = V(end);
        DTss(j,i) = DT(end);
        Qcss(j,i) = Qc(end);

    end
end


figure

subplot(2,1,1)
hold on
grid on
for i = 1:length(Iin_array)
    plot(DTss(:,i), Vss(:,i), '-o')
end
xlabel('\DeltaT (C)')
ylabel('Voltage (V)')
title('Voltage vs \DeltaT')
legend(string(Iin_array) + " A")

subplot(2,1,2)
hold on
grid on
for i = 1:length(Iin_array)
    plot(DTss(:,i), Qcss(:,i), '-o')
end
xlabel('\DeltaT (C)')
ylabel('Q_c (W)')
title('Cooling Power vs \DeltaT')
legend(string(Iin_array) + " A")