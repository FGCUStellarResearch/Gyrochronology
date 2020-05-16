fid = fopen('Otani_Buzasi_Feb21_target3.csv','w');
ls_fom = ls_snr/4;
wave_fom = wave_snr/4;
acf_fom = acf_snr/4;
flag1 = zeros(1,numel(fname));
test = [pr_ls_period;pr_wave_period;pr_acf_period];
test1 = std(test);
good_period = strings(numel(fname),1);
no_period = strings(numel(fname),1);
mean_period = zeros(numel(fname),1);
upp_err = zeros(numel(fname),1);
low_err = zeros(numel(fname),1);

for ii=1:numel(fname)
%for ii=1:24
        if (ls_fom(ii)>1 & acf_fom(ii)>1 & test1(ii)<1)
            flag1(ii) = 1;
            good_period(ii) = fname{ii};
            mean_period(ii) = (pr_ls_period(ii)+pr_wave_period(ii)+pr_acf_period(ii))/3;
            upp_err(ii) = sqrt(ls_upp_err(ii)^2+wave_upp_err(ii)^2+acf_upp_err(ii)^2)/3;
            low_err(ii) = sqrt(ls_low_err(ii)^2+wave_low_err(ii)^2+acf_low_err(ii)^2)/3;
        end 
        %if (acf_fom(ii)<1 & ls_fom(ii)<1)
        %    flag1(ii) = 2;
        %    no_period(ii) = fname{ii};
        %end 
end

%figure(1)
%plot(pr_ls_period(flag1==1),pr_wave_period(flag1==1),'o')
%figure(2)
%plot(pr_wave_period(flag1==1),pr_acf_period(flag1==1),'o')
%figure(3)
%plot(pr_acf_period(flag1==1),pr_ls_period(flag1==1),'o')


fprintf(fid,'%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n','TIC','LS Period','LS FOM','LS Error -','LS Error +','Wavelet Period','Wave FOM','Wave Error -','Wave Error +','ACF Period','ACF FOM','ACF Error -','ACF Error +','Phot Range (ppt)','Error Phot Range','Detect Flag', 'Mean Period', 'Error +', 'Error -');
for ii=1:numel(fname)
%for ii=1:24
        fprintf(fid,'%s, %6.2f, %6.2f, %6.2f, %6.2f, %6.2f, %6.2f, %6.2f, %6.2f, %6.2f, %6.2f, %6.2f, %6.2f, %6.2f, %6.2f, %1d, %6.2f, %6.2f, %6.2f\n',fname{ii},pr_ls_period(ii), ls_snr(ii)/4,...
            ls_low_err(ii),ls_upp_err(ii),pr_wave_period(ii), wave_snr(ii)/4, wave_low_err(ii), ...
            wave_upp_err(ii),pr_acf_period(ii),acf_snr(ii)/4, acf_low_err(ii),acf_upp_err(ii), ...
            1e3*pr_range(ii),1e3*pr_range_err(ii),flag1(ii),mean_period(ii),upp_err(ii),low_err(ii));
        %fprintf(fid,'%12.6f %12.6f %12.6f\n',1e6*star{ii}.freq(jj), 0.5655/star{ii}.snr(jj), 0.5655/star{ii}.snr(jj))
end
fclose(fid)
