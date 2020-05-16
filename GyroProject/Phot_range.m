function [mean_per, error] = Phot_range(Prot,time,flux)
%%hard code for testing start
%filename = '/home/chaise/Documents/MATLAB/KeplerAmplitude/tess2018206045859-s0001-0000000441120034-0120-s_lc.fits';
%dirname = '/home/chaise/Documents/MATLAB/KeplerAmplitude/hannah_files/'; 

%data = fitsread('tess2018206045859-s0001-0000000441120034-0120-s_lc.fits', 'binarytable');
%time = data{1,1};
%flux = data{1,8};

flux = flux(~isnan(flux));
flux = flux / median(flux);
time = time(~isnan(flux));
%Prot = 11.329;
%%hard code for testing end

%Ti is over all start and Tf is the last point that can be used
Ti = time(1);
Tf = time(end)-Prot;
%veriables for reverse 
Te = time(end);
To = time(1)+Prot;
[afv, T] = min(abs(time - To));
window = zeros(1,T);
i = 1000; %number of windows
std_sum = zeros(1,i);

for n = 1:i
    x = rand;
        if x > .5
            start_time = Ti + (Tf-Ti)*rand(1);
            end_time = start_time + Prot;
            [~, index_st] = min(abs(time - start_time));
            [~, index_end] = min(abs(time - end_time));
                
        else
            end_time = Te + (To-Te)*rand(1);
            start_time = end_time - Prot;
            [~, index_st] = min(abs(time - start_time));
            [~, index_end] = min(abs(time - end_time));
            %fill window with array from start times to end times
        end
        
        %fill the window with array from start time to end time
        window_index = 1;
        for j = index_st:index_end
            window(window_index) = flux(j);
            window_index = window_index + 1;
        end
        
        %standard dev calc
        std_sum(n) = std(window);
        
end    
mean_per = mean(std_sum);
error = std(std_sum);
%end
