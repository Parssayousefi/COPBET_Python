function tbl = CreateTBL(csvFolderPath)
    files = dir(fullfile(csvFolderPath, '*.csv'));
    numFiles = length(files);
    if numFiles == 0
        error('No CSV files found.');
    end

    % Initialize variables to hold data and metadata
    dataCells = cell(numFiles, 1);
    datasets = cell(numFiles, 1);
    subjects = cell(numFiles, 1);
    tasks = cell(numFiles, 1);
    sessions = cell(numFiles, 1);
    atlases = cell(numFiles, 1);

    for i = 1:numFiles
        filename = files(i).name;
        filepath = fullfile(csvFolderPath, filename);
        
        % Extract metadata from filename
        tokens = regexp(filename, 'dat-(.*?)_sub-(.*?)_task-(.*?)_ses-(.*?)_atlas-(.*?)\.csv', 'tokens');
        tokens = tokens{1};
        
        datasets{i} = tokens{1};
        subjects{i} = tokens{2};
        tasks{i} = tokens{3};
        sessions{i} = tokens{4};
        atlases{i} = tokens{5};
        
        % Load the time series data from CSV
        dataCells{i} = readmatrix(filepath);
    end

    % Create a table with the extracted data and metadata
    tbl = table(dataCells, datasets, subjects, tasks, sessions, atlases, ...
                'VariableNames', {'data', 'dataset', 'subject', 'task', 'session', 'atlas'});
end

