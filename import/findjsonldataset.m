function dataset_file = findjsonldataset(folder)

% silly routine to find "type": "dataset" allowing to manually edit stuff
% hack: ifthe folder is 'metadata' is assumes one want to list everyting
% and return instead a structure (just json_write it to keep a record)
% Cyril Pernet Sep 2024

[~,foldername] = fileparts(folder);
if strcmp(foldername,'metadata')
    dataset_file = struct;
    datasetname  = dir(folder); % 1st level
    for ds = 3:size(datasetname,1)
        if datasetname(ds).isdir && strncmp(datasetname(ds).name,'PN',2)
            version = dir(fullfile(datasetname(ds).folder,datasetname(ds).name)); % 2nd level
            for v = 3:size(version)
                if version(v).isdir
                    field = [datasetname(ds).name '_' version(v).name];
                    field = strrep(field,' ',''); % no space
                    field = strrep(field,'-',''); % no minus
                    field = strrep(field,':',''); % no :
                    dataset_file.(field) = fetchset(fullfile(version(v).folder,version(v).name));
                end
            end
        end
    end
else
    dataset_file = fetchset(folder);
end

function dataset_file = fetchset(folder)
% simply search for dataset in durrent flat dir structure
dataset_file = 'not found';
allfolders = dir(folder);
for f= 3:size(allfolders,1)
    sub = dir(fullfile(allfolders(f).folder,allfolders(f).name));
    for s=3:size(sub,1)
        out = jsondecode(fileread(fullfile(sub(s).folder,sub(s).name)));
        if strcmpi(out.type,"dataset")
            dataset_file = fullfile(sub(s).folder,sub(s).name);
            fprintf('dataset file found %s\n',dataset_file)
        end
    end
end


