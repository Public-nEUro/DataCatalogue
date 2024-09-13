function findjsonldataset(folder)

% silly routine to find "type": "dataset" allowing to manually edit stuff

allfolders = dir(folder);
for f= 3:size(allfolders,1)
    sub = dir(fullfile(allfolders(f).folder,allfolders(f).name));
    for s=3:size(sub,1)
        out = jsondecode(fileread(fullfile(sub(s).folder,sub(s).name)));
        if strcmpi(out.type,"dataset")
            warning('check file %s',fullfile(sub(s).folder,sub(s).name))
        end
    end
end



