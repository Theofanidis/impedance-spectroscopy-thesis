% Check actual poles
pole(linsys)

% Check system properties
linsys

% Get the transfer function
tf(linsys)

% Evaluate response at selected frequencies
w = [0.001 0.01 0.1 1 10 100 10000];

for k = 1:length(w)
    H = freqresp(linsys,w(k));
    fprintf('%g rad/s : %g dB\n', ...
        w(k),20*log10(abs(H)));
end