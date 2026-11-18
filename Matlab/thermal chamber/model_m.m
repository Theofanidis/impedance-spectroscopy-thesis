
function [Qdout1, Qdout2] = fcn(Tin1, Tin2, t)

    persistent model model_geometry
    persistent results_prev
    persistent initialized
    persistent t_prev
	persistent Q1_prev Q2_prev

    Ambient = 303;

    % Initialize
    if isempty(initialized)
		Q1_prev = 0;
		Q2_prev = 0;

        model_geometry = scale(fegeometry("batt.stl"), 0.001);

        model = femodel( ...
            AnalysisType="thermalTransient", ...
            Geometry=model_geometry);

        model.MaterialProperties = materialProperties( ...
            ThermalConductivity=205, ...
            MassDensity=2700, ...
            SpecificHeat=900);

        model.CellIC = cellIC(Temperature=Ambient);

        model.FaceLoad(5) = faceLoad(Heat=0);
        model.FaceLoad(3) = faceLoad(Heat=0);
        model.FaceLoad(6) = faceLoad(Heat=0);
        model.FaceLoad(1) = faceLoad(Heat=0);

        model = generateMesh(model);

        results_prev = [];
        t_prev = t;
        initialized = true;

        Qdout1 = 0;
        Qdout2 = 0;
        return
    end

    % Calculate elapsed Simulink time
    Timestep = t - t_prev;

    % Ignore repeated or backward time evaluations
    if Timestep <= 0
		Qdout1 = Q1_prev;
		Qdout2 = Q2_prev;
		return
	end

    % Number of FEM substeps
    nSteps = 4;

    % FEM time vector
    tlist = linspace(0, Timestep, nSteps+1);

    % Apply boundary temperatures
    model.FaceBC(2) = faceBC(Temperature=Tin1);
    model.FaceBC(4) = faceBC(Temperature=Tin2);

    % Carry forward the previous final FEM temperature
    if ~isempty(results_prev)
        model.CellIC = cellIC(Temperature=results_prev);
    end

    % Solve FEM
    results = solve(model, tlist);

    % Calculate heat rates
    Q1 = evaluateHeatRate(results, Face=2);
    Q2 = evaluateHeatRate(results, Face=4);

    Qdout1 = -Q1(end);
    Qdout2 = -Q2(end);
	
	Q1_prev = Qdout1;
	Q2_prev = Qdout2;

    % Save only the final FEM time point
    results_prev = filterByIndex(results, numel(results.SolutionTimes));

    % Update previous Simulink time
    t_prev = t;

    fprintf(['t = %.6f | timestep = %.6f | FEM steps = %d | ', ...
             'Tin1 = %.3f | Tin2 = %.3f | ', ...
             'Q1 = %.6f | Q2 = %.6f\n'], ...
             t, Timestep, nSteps, Tin1, Tin2, ...
             Qdout1, Qdout2);

end


% function [Qdout1, Qdout2] = fcn(Tin1, Tin2, t)

    % persistent model model_geometry
    % persistent results_prev
    % persistent initialized
	% persistent t_prev

    % Ambient = 303;
	

	% if isempty(t_prev)
		% Timestep = 0.001;
	% else
		% Timestep = t - t_prev;
	% end
	
	% t_prev = t;
	% dt = Timestep / 4;
	
    % % Initialize FEM model once
    % if isempty(initialized)

        % model_geometry = scale(fegeometry("batt.stl"), 0.001);
		% model = femodel(AnalysisType="thermalTransient", Geometry=model_geometry);

        % model.MaterialProperties = materialProperties(ThermalConductivity=205, MassDensity=2700, SpecificHeat=900);

        % model.CellIC = cellIC(Temperature=Ambient);

        % model.FaceLoad(5) = faceLoad(Heat=0);
        % model.FaceLoad(3) = faceLoad(Heat=0);
        % model.FaceLoad(6) = faceLoad(Heat=0);
        % model.FaceLoad(1) = faceLoad(Heat=0);

        % model = generateMesh(model);

        % results_prev = [];
        % initialized = true;
    % end

    % % Apply boundary temperatures
    % model.FaceBC(2) = faceBC(Temperature=Tin1);
    % model.FaceBC(4) = faceBC(Temperature=Tin2);

    % % Set initial condition from previous FEM solution
    % if ~isempty(results_prev)
        % model.CellIC = cellIC(Temperature=results_prev);
    % end

    % % Solve transient FEM
    % results = solve(model, [0 : dt : Timestep]);

    % % Calculate heat rates
    % Q1 = evaluateHeatRate(results, Face=2);
    % Q2 = evaluateHeatRate(results, Face=4);

    % Qdout1 = -Q1(end);
    % Qdout2 = -Q2(end);

    % % Store previous solution
    % results_prev = results;
	
	% fprintf('t = %.3f | Tin1 = %.3f | Tin2 = %.3f | Q1 = %.6f | Q2 = %.6f\n', ...
    % t, Tin1, Tin2, Qdout1, Qdout2);
	
% end


% function [Qdout1, Qdout2] = fcn(Tin1, Tin2, t)

    % persistent model model_geometry
    % persistent results_prev
    % persistent initialized

    % Ambient = 303;
    % Timestep = 0.01*10;
	% dt = 0.0025*10;

    % % Initialize FEM model once
    % if isempty(initialized)

        % model_geometry = scale(fegeometry("batt.stl"), 0.001);
		% model = femodel(AnalysisType="thermalTransient", Geometry=model_geometry);

        % model.MaterialProperties = materialProperties(ThermalConductivity=205, MassDensity=2700, SpecificHeat=900);

        % model.CellIC = cellIC(Temperature=Ambient);

        % model.FaceLoad(5) = faceLoad(Heat=0);
        % model.FaceLoad(3) = faceLoad(Heat=0);
        % model.FaceLoad(6) = faceLoad(Heat=0);
        % model.FaceLoad(1) = faceLoad(Heat=0);

        % model = generateMesh(model);

        % results_prev = [];
        % initialized = true;
    % end

    % % Apply boundary temperatures
    % model.FaceBC(2) = faceBC(Temperature=Tin1);
    % model.FaceBC(4) = faceBC(Temperature=Tin2);

    % % Set initial condition from previous FEM solution
    % if ~isempty(results_prev)
        % model.CellIC = cellIC(Temperature=results_prev);
    % end

    % % Solve transient FEM
    % results = solve(model, [0 : dt : Timestep]);

    % % Calculate heat rates
    % Q1 = evaluateHeatRate(results, Face=2);
    % Q2 = evaluateHeatRate(results, Face=4);

    % Qdout1 = -Q1(end);
    % Qdout2 = -Q2(end);

    % % Store previous solution
    % results_prev = results;
	
	% fprintf('t = %.3f | Tin1 = %.3f | Tin2 = %.3f | Q1 = %.6f | Q2 = %.6f\n', ...
    % t, Tin1, Tin2, Qdout1, Qdout2);
	
% end

