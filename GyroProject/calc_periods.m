function [ls_period,wave_period,acf_period,hht_period,ls_upp_err,ls_low_err,acf_upp_err, ...
    acf_low_err,wave_upp_err,wave_low_err,hht_upp_err,hht_low_err,ls_snr,acf_snr,wave_snr] = calc_periods(ttime,fflux,star_no,pipeline)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here

figure(199)
plot(ttime,fflux/median(fflux(~isnan(fflux))),'.k','markersize',2)
xlabel('Time (d)','Interpreter','latex')
ylabel('Relative Flux','Interpreter','latex')
%title(strcat(num2str(star_no),{' '},pipeline),'Interpreter','latex')

title(star_no,'Interpreter','latex')
%saveas(gcf,strcat('LC/',star_no,'_',pipeline,'.fig'))
saveas(gcf,strcat('LC/',star_no,'_',pipeline,'.png'))

%label and save plots with star No & type of pipeline (need to add that to
%pass)
%label and save plot outputs from each fit
% return values for amplitude, noise + P for LS

%1. Lomb-Scargle calculation
[P,f,alpha] = lomb(detrend(fflux(:)),ttime);
min_freq = 1./(ttime(end)-ttime(1));
%min_freq =0.1;
%[aa bb] = max(P);
[aa bb] = findpeaks(P); %find all the peaks
%find all the peaks above min_freq
%find max peak above min_freq
[x1 x2] = find(f(bb)>min_freq); %x1 are locations within b that correspond to peaks
[~, j2] = max(aa(x1)); %j2 is location in aa/bb array
bb = (bb(x1(j2))); %not working properly :(
fmax = f(bb); %Using fmax later for HHT


%alpha(bb)
if (alpha(bb) < 1e-4)
    ls_period = 1./f(bb);
else
    ls_period = -99;
end

%X0 = dft(ttime,detrend(fflux(:))/mean(fflux),f(bb));
%ls_amp = 2*abs(X0)/numel(ttime);


figure(99)
plot(f,P)
text(f(bb),0.95*max(P),strcat('\leftarrow',num2str(ls_period)))
if f(bb) < 5
    xlim([0 max(2,5*f(bb))])
end
%title(strcat(num2str(star_no),{' '},pipeline),'Interpreter','latex')
title(star_no,'Interpreter','latex')
xlabel('Frequency ($\rm c~d^{-1}$)','Interpreter','latex')
ylabel('P','Interpreter','latex')
%saveas(gcf,strcat('LS/',num2str(star_no),'_',pipeline,'_','ls','.fig'))
saveas(gcf,strcat('LS/',num2str(star_no),'_',pipeline,'_','ls','.png'))

%Create a randomized flux string
frand = randperm(length(fflux));

%ls_noise = median(P);
%get noise from 0 to twice max freq (or max freq if smaller); remember to
%sqare root!

%ls_snr = max(P)/ls_noise;

%Error estimation
%Start with estimating noise level in LS
ls_noise = std(diff(P));
%now set limits for interpolating pchip
f_int_low = 0.5*f(bb);
f_int_hi = 2*f(bb);
f_int_step = (f_int_hi-f_int_low)/100;
f_int = [f_int_low:f_int_step:f_int_hi];
%now do interpolation
p = pchip(f,P,f_int);
%OK, next need to find first p value which is more than ls_noise below
%P(bb)
[a1 b1] = max(p);
if (b1 == numel(p))
    b1 = numel(p)-1;
end
f_max = b1+find(p(b1:end)<P(bb)-ls_noise,1)
f_min = find(p(1:b1)<P(bb)-ls_noise,1,'last')
if isempty(f_min)
    f_min = 1;
end
if isempty(f_max)
    f_max = numel(p)-1;
end

min_period = 1/f_int(f_max);
max_period = 1/f_int(f_min);
upp_err = max_period -(1/f(bb));
low_err = (1/f(bb))-min_period;
ls_upp_err = max(1/max(ttime),upp_err);
ls_low_err = max(1/max(ttime),low_err);

ls_snr = sqrt(P(bb)/median(P(f>1 & f<2)));

if (isempty(ls_snr))
    ls_snr = 0;
end




%first, only those war
%then use dft to get peak amplitude! No....just fit a sin curve with known
%frequency...


%%can use peaks and width to find FWHM error...
%%need to fix this so it only searches space of less than time length of
%%segment...and/or checks vs alpha
%%also fix so that NaNs aren't used! go back and remove from the input  TS

%2 Autocorrelation calculation
ta = acf(detrend(fflux(:))/mean(fflux),length(fflux)-1);

[pks,locs,w,p] = findpeaks(smooth(ta,31),'MinPeakDistance',100);
%maybe limit to smoothing at 31 (or gaussian smooth?) and 
%stop the 100 issue because it loses the long-period peaks that are real!
min_loc = ceil((ls_period/2)/mode(diff(ttime)));
pks(locs<min_loc) = [];
w(locs<min_loc) = [];
p(locs<min_loc) = [];
locs(locs<min_loc) = [];

%Set up minimum ACF period to avoid being snared by really high-frequency
%stuff...

[aa bb] = max(pks); %locs(bb) will be the point of max, where bb is in units of lags
%bb = bb+numel(pks(locs<721));
%go to lag length equal to length of ttime

acf_period = locs(bb)*mode(diff(ttime))
if(isempty(bb))
    acf_period = max(ttime)-min(ttime);
end

if (ta(bb)<0)
    acf_period = -99;
end

figure(101)
plot(ta)
%title(strcat(num2str(star_no),{' '},pipeline),'Interpreter','latex')
title(star_no,'Interpreter','latex')
xlabel('Delay','Interpreter','latex')
ylabel('Amplitude','Interpreter','latex')

if ta(bb)>0
    text(locs(bb),0.95*pks(bb),strcat('\leftarrow',num2str(acf_period)))
end
%saveas(gcf,strcat('ACF/',num2str(star_no),'_',pipeline,'_','acf','.fig'))
saveas(gcf,strcat('ACF/',num2str(star_no),'_',pipeline,'_','acf','.png'))
%calculate ACF "noise"
acf_peak = abs(ta(locs(bb)));
acf_noise = median(abs(ta));

acf_noise = std(diff(ta));
acf_snr = acf_peak/acf_noise;
if (isempty(acf_snr))
    acf_snr = 0;
end

%Error estimation
%Start with estimating noise level
ls_noise = std(diff(ta));
%now set limits for interpolating pchip
p_int_low = 0.5*acf_period;
p_int_hi = 1.5*acf_period;
p_int_hi = min(p_int_hi,max(ttime));
p_int_step = (p_int_hi-p_int_low)/100;
p_int = [p_int_low:p_int_step:p_int_hi];
p_vals = mode(diff(ttime))*[1:length(ta)];
%now do interpolation
pol = pchip(p_vals,smooth(ta,451),p_int);
%OK, next need to find first p value which is more than ls_noise below
%P(bb)
[a1 b1] = max(pol);
if b1 == numel(pol)
    b1 = numel(pol)-1;
end

ploc = b1+find(pol(b1:end)<ta(locs(bb))-ls_noise,1);
if ploc>numel(pol)
    ploc = numel(pol)
end

p_max = p_int(ploc);

%p_max = p_int(b1+find(pol(b1:end)<ta(locs(bb))-ls_noise,1));
if isempty(p_max)
    p_max = p_int_hi;
end
p_min = p_int(find(pol(1:b1)<ta(locs(bb))-ls_noise,1,'last'));
if isempty(p_min)
    p_min = p_int_low;
end

upp_err = p_max - acf_period;
low_err = acf_period - p_min;
acf_upp_err = max(1/max(ttime),upp_err);
acf_low_err = max(1/max(ttime),low_err);
%aa
%acf_period
%ta2 = acf(diff(detrend(fflux(:)))/mean(fflux),2500);
%figure(200)
%plot(ta2)
%mean(abs(ta2))
%std(ta2)


%need to work on getting amplitude
%max must be positive or there is no period! in that case maybe -99 or NaN?
%also need to handle the case where vector is empty....maybe use full
%length of TS as period?
%w gives uncertainty

%3. Wavelet calculation
[wave,period,scale,coi,dj,paramout,k] = contwt(detrend(fflux)/mean(fflux),mode(diff(ttime)));
awave = abs(wave);
for ii=1:numel(period) %1001
swave(ii) = sum(awave(ii,:));
end


[pks,locs,w,p] = findpeaks(swave);
if isempty(pks)
    [pks,locs] = max(swave);
end
%pks(locs<100) = [];
%w(locs<100) = [];
%p(locs<100) = [];
%locs(locs<100) = [];
%[aa bb] = max(pks);%locs(bb) will be the point of max, and period(locs(bb)) will be period there
[aa bb] = max(pks(period(locs)<0.75*max(period))); %ensure period is less than half max window
wave_period = period(locs(bb));
%wave_amp = abs(swave(locs(bb)))/(numel(swave)*numel(ttime));
wave_amp = abs(swave(locs(bb)));

%calculate background level
wave_noise = median(swave);
wave_snr = wave_amp/wave_noise;

%%wave amplitude not right yet... FIX

figure(1001)
imagesc(awave/max(awave(:)))
%tempt = [ttime(1):ceil((max(ttime)-min(ttime))/6):max(ttime)];
%pert = [period(1):ceil((max(period)-min(period))/6):max(period)];
colorbar
%set(gca, 'XTick',tempt,'XTickLabel',ttime(tempt))
%set(gca, 'XTick',tempt,'XTickLabel',ttime(tempt)-min(ttime))
%set(gca, 'YTick',[0:ceil(numel(period)/10):numel(period)])
%set(gca, 'XTick',[min(ttime):ttime(end)-min(ttime)],'XTickLabel',[min(ttime):max(ttime)-min(ttime)])
%set(gca, 'YTick',[1:ceil(numel(period)/6):numel(period)],'YTickLabel',round(pert))
set(gca, 'YTick',(1:100:length(period)),'YTickLabel',round(period(1:100:length(period)),3))
%set(gca, 'XTick',[1:numel(tempt)],'XTickLabel',tempt)
%set(gca, 'XTick',[1:ceil(numel(ttime)/6):numel(ttime)], 'XTickLabel',round(tempt))
set(gca, 'XTick',(1:3000:length(ttime)), 'XTickLabel',round(ttime(1:3000:length(ttime))))
%xtickformat('%.0f')
xlabel('Time (d)')
ylabel('Period (d)')
%title(strcat(num2str(star_no),{' '},pipeline),'Interpreter','latex')
title(star_no,'Interpreter','latex')
colormap jet

%saveas(gcf,strcat('Wave/',num2str(star_no),'_',pipeline,'_','wav','.fig'))
saveas(gcf,strcat('Wave/',num2str(star_no),'_',pipeline,'_','wav','.png'))


%%%%%
figure(1010)
plot(period,swave/max(swave))
xlabel('Period (d)')
ylabel('Relative Amplitude (d)')
%title(strcat(num2str(star_no),{' '},pipeline),'Interpreter','latex')
title(star_no,'Interpreter','latex')
%saveas(gcf,strcat('Wave/',num2str(star_no),'_',pipeline,'_','wav_amp','.fig'))
saveas(gcf,strcat('Wave/',num2str(star_no),'_',pipeline,'_','wav_amp','.png'))

%%%%%

%Start with estimating noise level
ls_noise = std(diff(swave));
%make sure we are taking max at the right place!
wave_snr=max(swave)/median(swave);

%now set limits for interpolating pchip
p_int_low = 0.5*wave_period;
p_int_hi = 1.5*wave_period;
p_int_hi = min(p_int_hi,max(ttime));
p_int_step = (p_int_hi-p_int_low)/100;
p_int = [p_int_low:p_int_step:p_int_hi];
%now do interpolation
pol = pchip(period,swave,p_int);
%OK, next need to find first p value which is more than ls_noise below
%P(bb)
[a1 b1] = max(pol)
if b1 == numel(pol)
    b1 = numel(pol)-1;
end
p_max = p_int(b1+find(pol(b1:end)<swave(locs(bb))-ls_noise,1));
p_min = p_int(find(pol(1:b1)<swave(locs(bb))-ls_noise,1,'last'));

if isempty(p_min)
    p_min = 0;
end


upp_err = p_max - wave_period;
low_err = wave_period - p_min;
wave_upp_err = max(1/max(ttime),upp_err);
wave_low_err = max(1/max(ttime),low_err);

%%maybe try a linear transformation and then go back to the nearest
%%integers? IDK how to do this so it looks ok...

%end
%dlmwrite('ktwo201087784-c102_llc.txt',[time mdata],'precision','%.6f','delimiter','\t');

%4. HHT calculation
%allmode2 = eemd(fflux,0.1,100);
%allmode2 = eemd(fflux,0.1,20);
allmode2 = eemd(fflux,0,1);
[fm,am] = fa(allmode2,mode(diff(ttime)));
fm = abs(fm);

%use results from LS for HHT fm
fm_mean = mean(fm,1);
%[afv, fmode] = min(abs(fm_mean - fmax)) %fmode is the mean fm that is closest to fmax
imf_mean = mean(am,1);
[c1 d1] = max(imf_mean(2:end-1));
fmode = 1+d1;



%first trial to make hisrogram %%=(lines that were commented out before)
%%find IMF to use by means(am(:,n))
%imf_mean  = mean(am,1);
%[temp, max_imf] = max(imf_mean(5:end-1));
%%[temp max_imf] = findpeaks(max(imf_mean(1:end-1));
%max_imf = max_imf+5;

figure(11)
%set(figure(11),'visible','off');
h = histogram(fm(:,fmode),1000,'visible','on','normalization','probability','DisplayStyle','stairs');
%h = histogram(fm(:,max_imf),100,'visible','on','normalization','probability','DisplayStyle','stairs');
%h = histcounts(fm(:,max_imf),100);
[pks, locs] = findpeaks(h.Values);

[peak_val mpk] = max(pks);
peak_pos = mean(h.BinEdges(locs(mpk):locs(mpk)+1));
peak_pos2 = mean(fm(:,fmode));
hht_period = 1./peak_pos2;

hht_amp = (imf_mean(fmode))/mean(fflux);
%hht_amp = imf_mean(max_imf)/mean(fflux);


%Start with estimating noise level
ls_noise = std(diff(h.Values));


%now set limits for interpolating pchip
f_int_low = 0.5*peak_pos;
f_int_low = max(f_int_low,min(h.BinEdges(1:end-1)));
f_int_hi = 1.5*peak_pos;
f_int_hi = min(f_int_hi,max(h.BinEdges(1:end-1)));
f_int_step = (f_int_hi-f_int_low)/100;
f_int = [f_int_low:f_int_step:f_int_hi];
%now do interpolation

%figure(2000)
%numel(h.BinEdges)
%numel(h.Values)
bin_width = (h.BinEdges(2)-h.BinEdges(1))/2;
%plot(h.BinEdges(1:end-1)+bin_width,h.Values)


pol = pchip(h.BinEdges(1:end-1)+bin_width,h.Values,f_int);
%hold on
%plot(f_int,pol)
%hold off

%OK, next need to find first p value which is more than ls_noise below
%P(bb)
[a1 b1] = max(pol);
if b1 == numel(pol)
    b1 = b1-1;
end
f_max = f_int(b1+find(pol(b1:end)<peak_val-ls_noise,1));
if isempty(f_max)
    f_max = f_int_hi;
end
f_min = f_int(find(pol(1:b1)<peak_val-ls_noise,1,'last'));
if isempty(f_min)
    f_min = f_int_low;
end

min_period = 1/f_max;
max_period = 1/f_min;
upp_err = max_period -hht_period;
low_err = hht_period-min_period;
hht_upp_err = max(1/max(ttime),upp_err);
hht_low_err = max(1/max(ttime),low_err);


%%%4. HHT calculation
%%allmode2 = eemd(fflux,0.1,100);
%allmode2 = eemd(fflux,0.1,20);
%[fm,am] = fa(allmode2,mode(diff(ttime)));
%
%%find IMF to use by means(am(:,n))
%imf_mean  = mean(am,1);
%[temp max_imf] = max(imf_mean(5:end-1));
%%[temp max_imf] = findpeaks(max(imf_mean(1:end-1));
%max_imf = max_imf+4;
%figure(11)
%h = histogram(fm(:,max_imf),100,'visible','on','normalization','probability','DisplayStyle','stairs');
%%h = histcounts(fm(:,max_imf),100);
%[pks locs w p] = findpeaks(h.Values);
%
%[temp mpk] = max(pks);
%peak_pos = mean(h.BinEdges(locs(mpk):locs(mpk)+1));
%hht_period = 1./peak_pos;
%hht_amp = imf_mean(max_imf)/mean(fflux);
%
%xlabel('Frequency ($\rm c~d^{-1}$)','Interpreter','latex')
%ylabel('Relative Occurrence','Interpreter','latex')
%title(strcat(num2str(star_no),{' '},pipeline),'Interpreter','latex')
%
%%text(fm(locs(mpk),max_imf),0.95*peak_pos,strcat('\leftarrow',num2str(hht_period)))
%text(peak_pos,0.95*max(pks),strcat('\leftarrow',num2str(hht_period)))
%saveas(gcf,strcat('HHT/',num2str(star_no),'_',pipeline,'_','hht','.fig'))
%saveas(gcf,strcat('HHT/',num2str(star_no),'_',pipeline,'_','hht','.png'))

%%calculate HHT "noise"
%hht_noise = std(diff(allmode2(:,max_imf)))/mean(fflux);
%hht_noise = median(abs(am(:,max_imf)))/mean(fflux);
%hht_snr = hht_amp/hht_noise;


end

