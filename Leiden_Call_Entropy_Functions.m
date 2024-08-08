
clear
addpath(genpath(pwd))


%% Metastate series complexity (<1 minute on example data)
tbl_metastate = CopBET_metastate_series_complexity(tbl,'keepdata',true,'parallel',true);


%% Dynamic conditional correlation (DCC) entropy (Several hours pr scan)
% This one doesn't work with the shortened scans. Please download the full
% dataset. 
%clearvars entropy
%atlas = 'Shen268';
% This one takes several days to run. Second argument is whether to actually run the script or to use saved previous outputs 
tbl_DCC = CopBET_DCC_entropy(tbl,true,'keepdata',true,'parallel',true);
% outputs a vector of entropy values pr scan, each value corresponds to one
% atlas edge/roi-to-roi connection (i.e., 268*267/2 unique values)

% unwrap roi-to-roi DCC edges to network-to-network
Shen268 = niftiread('Atlases/Shen268_2mm.nii');

Shen268labels = readtable('Atlases/shen_268_parcellation_networklabels_1.csv');

atlasnames = {'Medial_frontal','Frontoparietal','Deafult_mode','Subcortical_cerebellum',...
    'Motor','Visual1','Visual2','Visual_association'};

for network1 = 1:8
    for network2 = 1:8
        network_idx1 = find(Shen268labels.Network==network1);
        network_idx2 = find(Shen268labels.Network==network2);
        entropy = nan(height(tbl),1);
        for ses = 1:height(tbl)
            tmp = tbl.entropy{ses}(network_idx1,network_idx2);
            tmp = tmp(tmp~=0);
            entropy(ses) = mean(tmp);
        end
        CopBETtbl.(['DCC_entropy_',atlasnames{network1},'_',atlasnames{network2}]) = entropy;
        plot_boxplots_CH2016(entropy,tbl,['DCC entropy: ',atlasnames{network1},'_',atlasnames{network2}])
    end
end

%% Degree distribution entropy (instant)
clearvars entropy

tbl_degreedistribution = CopBET_degree_distribution_entropy(tbl,'keepdata',true,'parallel',true);
% outputs a vector of entropy values pr scan, each value corresponds to one
% integer "mean degree" at which the degree distribution entropy is evaluated

for degree = 1:100
    for ses = 1:height(tbl)
        entropy(ses,degree) = tbl.entropy{ses}(degree);
    end
    CopBETtbl.(['Degree_distribution_entropy_degree',num2str(degree)]) = entropy(:,degree);
end

% plot entropy for an example mean degree
degree_to_plot = 27;
plot_boxplots_CH2016(entropy(:,degree_to_plot),tbl,['Degree distribution entropy, degree ',num2str(degree_to_plot)])

%% Viol 2019 script (instant)
tbl_pathlength = CopBET_geodesic_entropy(tbl,'keepdata',true,'parallel',true);
% outputs a vector of entropy values pr scan, each value corresponds to one
% integer "mean degree" at which the degree distribution entropy is evaluated

for degree = 1:100
    for ses = 1:height(tbl)
        entropy(ses,degree) = tbl.entropy{ses}(degree);
    end
    CopBETtbl.(['Geodesic_entropy_degree',num2str(degree)]) = entropy(:,degree);
end

%% Sample entropy (several hours pr scan)
clearvars entropy

% This one requires an atlas to be specified. Here we use Yeo-17
atlas = niftiread('Atlases/Yeo17_liberal_2mm.nii');
[tbl,data,opts] = CopBET_CarhartHarris_2016_data([],'denoised_volumes','example');

tbl = CopBET_sample_entropy(tbl,atlas,true,'keepdata',true,'parallel',true);

% outputs a matrix of entropy values pr scan, each matrix contains values
% corresponding to a specific multi-scale sample entropy scale (1 to 5)
% along the rows, and a ROI in the (Yeo17) atlas along the columns. 

for scale = 1:5
    for session = 1:height(tbl)
        for ROI = 1:17
            entropy(session,scale,ROI) = tbl.entropy{session}(scale,ROI);
        end
    end
    for ROI = 1:17
        CopBETtbl.(['Sample_entropy_scale',num2str(scale),'_ROI',num2str(ROI)]) = entropy(:,scale,ROI);
    end
end
scale_to_plot = 2;
ROI_to_plot = 7;
plot_boxplots_CH2016(entropy(:,scale_to_plot,ROI_to_plot),tbl,['Sample entropy, scale: ',num2str(scale_to_plot),', ROI: ',num2str(ROI_to_plot)])


%% Varley script, temporal LZ78 (<5 minutes on example data)
tbl_LZtemporal = CopBET_time_series_complexity(tbl,'LZ78temporal',true,true);


%% Varley script, spatial LZ78 (<5 minutes on example data)
tbl_LZspatial = CopBET_time_series_complexity(tbl,'LZ78spatial',true,true);

%% BoxPlot Code
% Extract relevant columns from the loaded table 'tbl'
tasks = tbl.Task;
entropy_values = tbl.entropy;

% Get unique tasks
unique_tasks = unique(tasks);

% Prepare data for boxplot
boxplot_data = [];
group_labels = [];

for i = 1:length(unique_tasks)
    task_indices = strcmp(tasks, unique_tasks{i});
    boxplot_data = [boxplot_data; entropy_values(task_indices)];
    group_labels = [group_labels; repmat(unique_tasks(i), sum(task_indices), 1)];
end

% Create boxplot
figure;
boxplot(boxplot_data, group_labels);
xlabel('Task');
ylabel('Entropy');
title('Boxplot of Entropy Values by Task');

% Adjust x-tick labels if necessary
set(gca, 'XTickLabel', unique_tasks);
