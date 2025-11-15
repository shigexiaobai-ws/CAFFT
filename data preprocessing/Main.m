fileFolder=fullfile('E:\teddy\venv\RawData');
dirOutput=dir(fullfile(fileFolder,'*.csv'));
fileNames={dirOutput.name}';
FileN=char(fileNames);
numFiles = size(FileN,1); % 获取文件总数
fprintf('总共需要处理 %d 个 CSV 文件。\n', numFiles); % 输出文件总数

for i=1:numFiles
    L=size(FileN(i,:),2);
    fileName = FileN(i,1:L-4); % 获取文件名
    fprintf('正在处理第 %d 个文件: %s.csv\n', i, fileName); % 输出正在处理的文件名
    DeleteData(fileName,0.041,180,3600,2,400);
    fprintf('文件 %s.csv 处理完成。\n', fileName); % 输出文件处理完成信息
end

fprintf('所有 CSV 文件处理完成。\n'); % 输出所有文件处理完成信息