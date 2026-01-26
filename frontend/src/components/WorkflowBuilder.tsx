import {
  Stack, Paper, Text, Button, Group, Badge, ActionIcon,
} from '@mantine/core';
import { IconTrash, IconPlus, IconSettings, IconFile } from '@tabler/icons-react';
import {
  DragDropContext,
  Draggable,
  Droppable,
  type DropResult,
} from '@hello-pangea/dnd';
import { browseFile, type WorkflowFile, type FileMapping } from '../services/api';

interface WorkflowBuilderProps {
  files: WorkflowFile[];
  mappings: FileMapping[];
  onFilesChange: (files: WorkflowFile[]) => void;
  onMappingsChange: (mappings: FileMapping[]) => void;
  onOpenMappingModal: (file: WorkflowFile) => void;
  onConfigureInputs: (file: WorkflowFile) => void;
}

export const WorkflowBuilder = ({
  files,
  mappings,
  onFilesChange,
  onMappingsChange,
  onOpenMappingModal,
  onConfigureInputs,
}: WorkflowBuilderProps) => {
  const handleDragEnd = (result: DropResult) => {
    if (!result.destination) {
      return;
    }

    const { source, destination } = result;

    // If dropped in the same position, do nothing
    if (source.droppableId === destination.droppableId &&
      source.index === destination.index) {
      return;
    }

    // Reorder files array
    const newFiles = [...files];
    const [removed] = newFiles.splice(source.index, 1);
    newFiles.splice(destination.index, 0, removed);

    // Update positions
    const updatedFiles = newFiles.map((f, idx) => ({ ...f, position: idx }));
    onFilesChange(updatedFiles);
  };

  const handleAddFile = () => {
    // Placeholder - will be implemented with file picker
    const newFile: WorkflowFile = {
      file_path: '',
      inputs: [],
      position: files.length,
    };
    onFilesChange([...files, newFile]);
  };

  const handleRemoveFile = (filePath: string) => {
    const newFiles = files.filter((f) => f.file_path !== filePath);
    // Update positions
    const updatedFiles = newFiles.map((f, idx) => ({ ...f, position: idx }));
    onFilesChange(updatedFiles);

    // Remove mappings involving this file
    const newMappings = mappings.filter(
      (m) => m.source_file !== filePath && m.target_file !== filePath
    );
    onMappingsChange(newMappings);
  };

  const handleUpdateFilePath = (index: number, newPath: string) => {
    const newFiles = [...files];
    newFiles[index] = { ...newFiles[index], file_path: newPath };
    onFilesChange(newFiles);
  };

  const getMappingsForFile = (filePath: string) => {
    return mappings.filter((m) => m.target_file === filePath);
  };

  return (
    <Stack gap="md">
      <Group justify="space-between">
        <Text fw={500}>Workflow Files (drag to reorder)</Text>
        <Button size="xs" leftSection={<IconPlus size={14} />} onClick={handleAddFile}>
          Add File
        </Button>
      </Group>

      <DragDropContext onDragEnd={handleDragEnd}>
        <Droppable droppableId="workflow-files">
          {(provided, snapshot) => (
            <Stack
              {...provided.droppableProps}
              ref={provided.innerRef}
              gap="xs"
              style={{ minHeight: snapshot.isDraggingOver ? 200 : 'auto' }}
            >
              {files.map((file, index) => (
                <Draggable
                  key={file.file_path || `new-${index}`}
                  draggableId={file.file_path || `new-${index}`}
                  index={index}
                >
                  {(provided, snapshot) => (
                    <Paper
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      p="md"
                      withBorder
                      style={{
                        ...provided.draggableProps.style,
                        cursor: 'grab',
                        opacity: snapshot.isDragging ? 0.5 : 1,
                      }}
                    >
                      <Group justify="space-between">
                        <Group gap="xs" style={{ flex: 1, minWidth: 0 }}>
                          <Badge size="xs" color="blue">
                            {index + 1}
                          </Badge>
                          <Button
                            size="xs"
                            variant="light"
                            leftSection={<IconFile size={14} />}
                            onClick={async () => {
                              const result = await browseFile();
                              if (!result.cancelled && result.file_path) {
                                handleUpdateFilePath(index, result.file_path);
                              }
                            }}
                          >
                            Browse
                          </Button>
                          {file.file_path ? (
                            <Text size="xs" c="dimmed" truncate style={{ flex: 1 }} title={file.file_path}>
                              {file.file_path.split('\\').pop()}
                            </Text>
                          ) : (
                            <Text size="xs" c="dimmed" style={{ flex: 1 }}>No file selected</Text>
                          )}
                        </Group>

                        <Group gap="xs">
                          {getMappingsForFile(file.file_path).length > 0 && (
                            <Badge size="xs" color="green" variant="dot">
                              {getMappingsForFile(file.file_path).length} mapping{getMappingsForFile(file.file_path).length > 1 ? 's' : ''}
                            </Badge>
                          )}
                          <ActionIcon
                            size="xs"
                            variant="light"
                            color="blue"
                            onClick={() => onConfigureInputs(file)}
                            disabled={!file.file_path}
                          >
                            <IconSettings size={16} />
                          </ActionIcon>
                          <ActionIcon
                            size="xs"
                            variant="light"
                            color="green"
                            onClick={() => onOpenMappingModal(file)}
                            disabled={!file.file_path}
                          >
                            <IconPlus size={16} />
                          </ActionIcon>
                          <ActionIcon
                            size="xs"
                            variant="light"
                            color="red"
                            onClick={() => handleRemoveFile(file.file_path)}
                          >
                            <IconTrash size={16} />
                          </ActionIcon>
                        </Group>
                      </Group>
                    </Paper>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </Stack>
          )}
        </Droppable>
      </DragDropContext>
    </Stack>
  );
};
