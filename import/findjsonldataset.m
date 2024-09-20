function dataset_file = findjsonldataset(folder)

% silly routine to find "type": "dataset" allowing to manually edit stuff

dataset_file = 'not found';
allfolders = dir(folder);
for f= 3:size(allfolders,1)
    sub = dir(fullfile(allfolders(f).folder,allfolders(f).name));
    for s=3:size(sub,1)
        out = jsondecode(fileread(fullfile(sub(s).folder,sub(s).name)));
        if strcmpi(out.type,"dataset")
            dataset_file = fullfile(sub(s).folder,sub(s).name);
            warning('dataset file %s',dataset_file)
        end
    end
end



