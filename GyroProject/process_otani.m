clear all
import matlab.io.*


%fgnames = dir('../*target4_ts.out');
fgnames = dir('/media/derek/TOSHIBA EXT/K2_data/WideBinaries/ToProcess/outputs/ts/*target4_ts.out');
for ii=1:numel(fgnames)
    temp = fgnames(ii).name;
    fname{ii} = temp;
end
fname = unique(fname);

%function [mean_per, error] = Phot_range(Prot,time,flux)

acf_upp_err = zeros(1,12);
acf_low_err = zeros(1,12);

for ii=1:numel(fname)
%for ii=1:5
    

    %filename = strcat('../',cell2mat(fname(ii)));
    filename = strcat('/media/derek/TOSHIBA EXT/K2_data/WideBinaries/ToProcess/outputs/ts/',cell2mat(fname(ii)));
    delimiter = ',';
    formatSpec = '%f%f%f%f%f%f%[^\n\r]';
    fileID = fopen(filename,'r');
    dataArray = textscan(fileID, formatSpec, 'Delimiter', delimiter, 'TextType', 'string', 'EmptyValue', NaN,  'ReturnOnError', false);
    fclose(fileID);
    time = dataArray{:, 1};
    flux = dataArray{:, 3};
    flux = flux/median(flux);

    clearvars delimiter formatSpec fileID dataArray ans;


time = time-min(time);

%figure(1)
%plot(time,flux)
%title(fname{ii})
%pause

%end

%stop

%for ii=748:numel(prxfiles)
%for ii=611:900
    ii
    mdata = flux;
%ff_ls_period = ones(1,100);
%ff_wave_period = ones(1,100);
%ff_acf_period = ones(1,100);
%ff_hht_period = ones(1,100);

%for ii=1:100
    



ttime = [min(time):mode(diff(time)):max(time)];
fflux = interp1(time,mdata,ttime,'pchip');

k2project_time{ii} = ttime;
k2project_flux{ii} = fflux;


%%%%%%%%%%%%%%%%%%%%%%%%
starno1 = strsplit(fname{ii},'_');
starno2 = starno1(2);
starno = cell2mat(starno2);


[pr_ls_period(ii),pr_wave_period(ii),pr_acf_period(ii),pr_hht_period(ii),ls_upp_err(ii),ls_low_err(ii), ...
    acf_upp_err(ii),acf_low_err(ii),wave_upp_err(ii),wave_low_err(ii),hht_upp_err(ii),hht_low_err(ii),ls_snr(ii),acf_snr(ii),wave_snr(ii)] = calc_periods(ttime,fflux,starno,'K2SP');
%disp('returned')
%pr_mean(ii) = mean(fflux)ls_snr,acf_snr,wave_snr
%pr_range(ii) = (prctile(detrend(fflux),95)-prctile(detrend(fflux),5))/pr_mean(ii)

for icount=1:1000
    testi = randi(numel(fflux),1,numel(fflux));
    frange(icount) = prctile(detrend(fflux(testi)),95)-prctile(detrend(fflux(testi)),5);
    frange2(icount) = prctile(detrend(fflux(testi)),75)-prctile(detrend(fflux(testi)),25);
end
pr_range(ii) = mean(frange);
pr_range_err(ii) = std(frange);
pr_range2(ii) = mean(frange2);
pr_range2_err(ii) = std(frange2);

%Calculate Sph using sliding scale, 5xProt
%Do a loop for each non-experimental period measurement, starting with LS
if pr_ls_period(ii)<0
    ls_sph(ii) = std(fflux);
elseif 5*pr_ls_period(ii) > (max(ttime)-min(ttime))
    ls_sph(ii) = std(fflux);
else
    shift = pr_ls_period(ii)/8;
    num_shift = floor((max(ttime)-min(ttime)-pr_ls_period(ii))/shift);
    min_time = min(ttime);
    max_time = min(ttime)+pr_ls_period(ii);
    for icount = 1:num_shift
        ls_sph_sec(icount) = std(fflux(ttime>min_time & ttime<max_time));
        min_time = min_time+shift;
        max_time = max_time+shift;
    end
    ls_sph(ii) = mean(ls_sph_sec);
end

if pr_wave_period(ii)<0
    wave_sph(ii) = std(fflux);
elseif 5*pr_wave_period(ii) > (max(ttime)-min(ttime))
    wave_sph(ii) = std(fflux);
else
    shift = pr_wave_period(ii)/8;
    num_shift = floor((max(ttime)-min(ttime)-pr_wave_period(ii))/shift);
    min_time = min(ttime);
    max_time = min(ttime)+pr_wave_period(ii);
    for icount = 1:num_shift
        wave_sph_sec(icount) = std(fflux(ttime>min_time & ttime<max_time));
        min_time = min_time+shift;
        max_time = max_time+shift;
    end
    wave_sph(ii) = mean(wave_sph_sec);
end

if pr_acf_period(ii)<0
    acf_sph(ii) = std(fflux);
elseif 5*pr_acf_period(ii) > (max(ttime)-min(ttime));
    acf_sph(ii) = std(fflux);
else
    shift = pr_acf_period(ii)/8;
    num_shift = floor((max(ttime)-min(ttime)-pr_acf_period(ii))/shift);
    min_time = min(ttime);
    max_time = min(ttime)+pr_acf_period(ii);
    for icount = 1:num_shift
        acf_sph_sec(icount) = std(fflux(ttime>min_time & ttime<max_time));
        min_time = min_time+shift;
        max_time = max_time+shift;
    end
    acf_sph(ii) = mean(acf_sph_sec);
end

%this is where to put the boostrap analysis for pr_range, etc.

%%%%%%%%%%%%%%%%%%%%%%%%

%stop

[mean_S(ii), S_error(ii)] = Phot_range(pr_wave_period(ii),ttime,fflux)
%append data to file...

%close all
%save '3Jan_outputB.mat'

%plot(time,mdata,'.')
%plot(time,mdata/mean(mdata),'.')
end
%dlmwrite('pipeout_ktwo201087784-c101_target1_ts.txt',[time mdata],'precision','%.6f','delimiter','\t');

fclose('all');
