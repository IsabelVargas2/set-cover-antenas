clear all
close all
clc
% ===== PROYECTO SET COVER (estructura del profe: optimvar / optimproblem) =====
% Ejecutar con la carpeta del proyecto como carpeta actual de MATLAB.
% Requiere Optimization Toolbox.

%DATOS
A = readmatrix(fullfile("datos","set_cover_500x500.csv"));  % fila i = cliente, columna j = antena
if size(A,1) == 501        % por si MATLAB lee el encabezado 0..499 como una fila de datos
    A = A(2:end,:);
end
C = readmatrix(fullfile("datos","costos.csv"));              % costo de cada antena
C = C(:);
m = size(A,1);             % clientes
n = size(A,2);             % antenas
fprintf("Clientes = %d | Antenas = %d\n",m,n);

%VARIABLES
% Xj = 1 si se instala la antena j, 0 si no  (binaria = entera entre 0 y 1)
Xj = optimvar("Xj",[n,1],"Type","integer","LowerBound",0,"UpperBound",1);

%FO
Z = optimproblem("ObjectiveSense","minimize");
Z.Objective = sum(C.*Xj,"all");

%RESTRICCIONES
% Cada cliente debe quedar cubierto por al menos una antena instalada
R1 = optimconstr(m,1);
for i = 1:m
    R1(i) = A(i,:)*Xj >= 1;
end
Z.Constraints.r1 = R1;

%SOLUCION
Opc = optimoptions("intlinprog","Display","iter","MaxTime",600,"RelativeGapTolerance",0);
[Sol,FO,Exitflag,Output] = solve(Z,"Options",Opc);

%RESULTADOS
Antenas = find(round(Sol.Xj) == 1);
fprintf("\nCosto minimo encontrado = %.0f\n",FO);
fprintf("Numero de antenas = %d\n",numel(Antenas));
fprintf("Antenas elegidas: %s\n",mat2str(Antenas'));
fprintf("Todos los clientes cubiertos: %d\n",all(A*round(Sol.Xj) >= 1));
disp(Output.message)
% show(Z)   % con 500 restricciones imprime muchisimo; descomentar solo si se necesita
