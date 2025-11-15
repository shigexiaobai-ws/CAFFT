% 将路径文件整合成一份CSV文件

% 设置根目录
rootFolder = 'E:\teddy\test\combine';

% 获取根目录下所有文件夹
dirOutput = dir(rootFolder);
dirOutput = dirOutput([dirOutput.isdir]); % 仅保留文件夹
dirOutput = dirOutput(~ismember({dirOutput.name}, {'.', '..'})); % 移除 '.' 和 '..' 文件夹

% 循环遍历每个文件夹
for k = 1:length(dirOutput)
    Name = dirOutput(k).name; % 获取文件夹名称
    fprintf('正在处理文件夹: %s\n', Name);

    % 路径文件绝对路径
    fileFolder=fullfile(rootFolder, Name);
    dirOutputCSV=dir(fullfile(fileFolder,'*.csv'));
    fileNames={dirOutputCSV.name}';
    FileN=char(fileNames);

    % 输出位置绝对路径
    Folder='E:\teddy\test\Data\AA00001';
    index=2;
    R={'vehicleplatenumber'	'device_num' 'direction_angle' 'lng' 'lat' 'acc_state'  'right_turn_signals' 'left_turn_signals' 'hand_brake' 'foot_brake' 'location_time' 'gps_speed' 'mileage'};

    for i=1:size(FileN,1)
        fileName = strtrim(FileN(i,:)); % 移除文件名末尾的空格
        L=size(FileN(i,:),2);
        Table= readtable([fileFolder '\' fileName]);
        E=table2cell(Table);
        for j=1:size(E,1)
            R(index,:)=E(j,:);
            index=index+1;
        end
    end

    cell2csv([Folder '\' Name,'.csv'],R);
    fprintf('文件夹 %s 处理完成，已保存到 %s\%s.csv\n', Name, Folder, Name);
end

fprintf('所有文件夹处理完成。\n');