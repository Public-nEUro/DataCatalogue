function listjl2filetype(datasetjl,listjl,source_name,agent_name)

% reads the list.jsonl (generated from from get_files.py)
% for each item, make a file jsonl for the data catalogue 
% and appends it to the dataset descriptor dataset.jsonl
%
% datasetjl name of the dataset.jsonl
% listjl name of the file_list.jsonl
% source_name and agent_name are used to reference the source element
%      e.g. source_name = 'OpenNeuro_PET'; agent_name = 'Cyril Pernet';
%
% usage: listjl2filetype('mydataset_info.jsonl','mygenerated_file_list.jsonl', 'OpenNeuro_PET','Cyril Pernet')

% 1 - get datasetjl
if ~exist(datasetjl,'file')
    error('dataset.json file %g not found',datasetjl)
end
dataset_info = jsondecode(fileread(datasetjl));
if ~isfield(dataset_info,'metadata_sources')
    dataset_info.metadata_sources.sources.source_name    = source_name;
    dataset_info.metadata_sources.sources.source_version = dataset_info.dataset_version;
    dataset_info.metadata_sources.sources.agent_name     = agent_name;
end
if exist([erase(dataset_info.name," ") '.jsonl'],"file")
    delete([erase(dataset_info.name," ") '.jsonl']);
end
local_jsonwrite([erase(dataset_info.name," ") '.jsonl'],dataset_info);

% 2 - get listjl
files_info = importdata(listjl);

% edit items and append
% silly trick to be on the next line
% local_jsonwrite([erase(dataset_info.name," ") '.jsonl'],'');
% now write over
N = size(files_info,1);
for f=1:N
    fprintf('processing file info %g/%g\n',f,N);
    item.type             = "file";
    item.dataset_id       = dataset_info.dataset_id;
    item.dataset_version  = dataset_info.dataset_version;
    item.path             = cell2mat(extractBetween(files_info{f},'"path": "','",'));
    %item.path(strfind(item.path,'\\'))=[];
    %item.path(strfind(item.path,'//'))=[];
    item.contentbytesize  = str2double(cell2mat(extractBetween(files_info{f},'"contentbytesize":','}')));
    item.metadata_sources.sources.source_name    = source_name;
    item.metadata_sources.sources.source_version = dataset_info.dataset_version;
    item.metadata_sources.sources.agent_name     = agent_name;
    local_jsonwrite([erase(dataset_info.name," ") '.jsonl'],item);
end

% fix known issues
% metadata_sources are  missing square brackets
lines = readlines([erase(dataset_info.name," ") '.jsonl']);
for l=1:size(lines,1)
    if lines(l,:) == ""
        lines(l,:) = [];
    else
        part1 = char(extractBefore(lines(l,:),'"metadata_sources":{"sources":'));
        part2 = char(['"metadata_sources":{"sources":' '[']); % add the square bracket;
        part3 = char(extractAfter(lines(l,:),'"metadata_sources":{"sources":'));
        part3 = [part3(1:end-3) '}]}}']; % rebuild ending adding square bracket
        lines(l,:) = [part1 part2 part3];
    end
end
delete([erase(dataset_info.name," ") '.jsonl']);
fid = fopen([erase(dataset_info.name," ") '.jsonl'], 'wt');
fprintf(fid, '%s\n', lines);
fclose(fid);

function S = local_jsonwrite(varargin)

% Serialize a JSON (JavaScript Object Notation) structure
% local version - fix double // strip down unwanted stuff
% adapted from
%    Guillaume Flandin
%    $Id: spm_jsonwrite.m 8031 2020-12-10 13:37:00Z guillaume $

%-Input parameters
%--------------------------------------------------------------------------
filename = varargin{1};
json     = varargin{2};
opts = struct(...
    'indent','',...
    'prettyprint',false,...
    'replacementstyle','underscore',...
    'convertinfandnan',true);
optregistry(opts);

%-JSON serialization
%--------------------------------------------------------------------------
fmt('init',sprintf(opts.indent));
S = jsonwrite_var(json,~isempty(opts.indent));

%-Output
%--------------------------------------------------------------------------
if ~exist(filename,'file')
    fid = fopen(filename,'w');
    if fid == -1
        error('Unable to open file "%s" for writing.',filename);
    end
    fprintf(fid,'%s',S);
else
    fid = fopen(filename,'at');
    if fid == -1
        error('Unable to open file "%s" for writing.',filename);
    end
    fprintf(fid,'%s',S);
    fprintf(fid,'\n') ;
end
fclose(fid);


%==========================================================================
function S = jsonwrite_var(json,tab)
if nargin < 2, tab = ''; end
if isstruct(json) || isa(json,'containers.Map')
    S = jsonwrite_struct(json,tab);
elseif iscell(json)
    S = jsonwrite_cell(json,tab);
elseif ischar(json)
    if size(json,1) <= 1
        S = jsonwrite_char(json);
    else
        S = jsonwrite_cell(cellstr(json),tab);
    end
elseif isnumeric(json) || islogical(json)
    S = jsonwrite_numeric(json);
elseif isa(json,'string')
    if numel(json) == 1
        if ismissing(json)
            S = 'null';
        else
            S = jsonwrite_char(char(json));
        end
    else
        json = arrayfun(@(x)x,json,'UniformOutput',false);
        json(cellfun(@(x) ismissing(x),json)) = {'null'};
        idx = find(size(json)~=1);
        if numel(idx) == 1 % vector
            S = jsonwrite_cell(json,tab);
        else % array
            S = jsonwrite_cell(num2cell(json,setdiff(1:ndims(json),idx(1))),tab);
        end
    end
elseif isa(json,'datetime') || isa(json,'categorical')
    S = jsonwrite_var(string(json));
elseif isa(json,'table')
    S = struct;
    s = size(json);
    vn = json.Properties.VariableNames;
    for i=1:s(1)
        for j=1:s(2)
            if iscell(json{i,j})
                S(i).(vn{j}) = json{i,j}{1};
            else
                S(i).(vn{j}) = json{i,j};
            end
        end
    end
    S = jsonwrite_struct(S,tab);
else
    if numel(json) ~= 1
        json = arrayfun(@(x)x,json,'UniformOutput',false);
        S = jsonwrite_cell(json,tab);
    else
        p = properties(json);
        if isempty(p), p = fieldnames(json); end % for pre-classdef
        s = struct;
        for i=1:numel(p)
            s.(p{i}) = json.(p{i});
        end
        S = jsonwrite_struct(s,tab);
        %error('Class "%s" is not supported.',class(json));
    end
end

%==========================================================================
function S = jsonwrite_struct(json,tab)
if numel(json) == 1
    if isstruct(json), fn = fieldnames(json); else fn = keys(json); end
    S = ['{' fmt('\n',tab)];
    for i=1:numel(fn)
        key = fn{i};
        if strcmp(optregistry('replacementStyle'),'hex')
            key = regexprep(key,...
                '^x0x([0-9a-fA-F]{2})', '${native2unicode(hex2dec($1))}');
            key = regexprep(key,...
                '0x([0-9a-fA-F]{2})', '${native2unicode(hex2dec($1))}');
        end
        if isstruct(json), val = json.(fn{i}); else val = json(fn{i}); end
        S = [S fmt(tab) jsonwrite_char(key) ':' fmt(' ',tab) ...
            jsonwrite_var(val,tab+1)];
        if i ~= numel(fn), S = [S ',']; end
        S = [S fmt('\n',tab)];
    end
    S = [S fmt(tab-1) '}'];
else
    S = jsonwrite_cell(arrayfun(@(x) {x},json),tab);
end

%==========================================================================
function S = jsonwrite_cell(json,tab)
if numel(json) == 0 ...
        || (numel(json) == 1 && iscellstr(json)) ...
        || all(all(cellfun(@isnumeric,json))) ...
        || all(all(cellfun(@islogical,json)))
    tab = '';
end
S = ['[' fmt('\n',tab)];
for i=1:numel(json)
    S = [S fmt(tab) jsonwrite_var(json{i},tab+1)];
    if i ~= numel(json), S = [S ',']; end
    S = [S fmt('\n',tab)];
end
S = [S fmt(tab-1) ']'];

%==========================================================================
function S = jsonwrite_char(json)
% any-Unicode-character-except-"-or-\-or-control-character
% \" \\ \/ \b \f \n \r \t \u four-hex-digits
%json = strrep(json,'\','\\');
json = strrep(json,'"','\"');
%json = strrep(json,'/','\/');
json = strrep(json,'\','/');  % added to ensure forward slash 
json = strrep(json,'\\','/'); % added to ensure forward slash 
json = strrep(json,'//','/'); % added to ensure forward slash 
json = strrep(json,sprintf('\b'),'\b');
json = strrep(json,sprintf('\f'),'\f');
json = strrep(json,sprintf('\n'),'\n');
json = strrep(json,sprintf('\r'),'\r');
json = strrep(json,sprintf('\t'),'\t');
S = ['"' json '"'];

%==========================================================================
function S = jsonwrite_numeric(json)
if any(imag(json(:)))
    error('Complex numbers not supported.');
end
if numel(json) == 0
    S = jsonwrite_cell({});
    return;
elseif numel(json) > 1
    idx = find(size(json)~=1);
    if numel(idx) == 1 % vector
        if any(islogical(json)) || any(~isfinite(json))
            S = jsonwrite_cell(num2cell(json),'');
        else
            S = ['[' sprintf('%23.16g,',json) ']']; % eq to num2str(json,16)
            S(end-1) = ''; % remove last ","
            S(S==' ') = [];
        end
    else % array
        S = jsonwrite_cell(num2cell(json,setdiff(1:ndims(json),idx(1))),'');
    end
    return;
end
if islogical(json)
    if json, S = 'true'; else S = 'false'; end
elseif ~isfinite(json)
    if optregistry('convertinfandnan')
        S = 'null';
    else
        if isnan(json)
            S = 'NaN';
        elseif json > 0
            S = 'Infinity';
        else
            S = '-Infinity';
        end
    end
else
    S = num2str(json,16);
end

%==========================================================================
function b = fmt(varargin)
persistent tab;
if nargin == 2 && isequal(varargin{1},'init')
    tab = varargin{2};
end
b = '';
if nargin == 1
    if varargin{1} > 0, b = repmat(tab,1,varargin{1}); end
elseif nargin == 2
    if ~isempty(tab) && ~isempty(varargin{2}), b = sprintf(varargin{1}); end
end

%==========================================================================
function val = optregistry(opts)
persistent options
if isstruct(opts)
    options = opts;
else
    val = options.(lower(opts));
end



