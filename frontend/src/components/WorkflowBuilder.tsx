import { useState } from 'react';
import { DndContext, DragEndEvent, DragOverlay, closestCenter } from '@hello-pangea/dnd';
import {
  Stack, Paper, Text, Button, Group, Badge, ActionIcon, TextInput,
} from '@mantine/core';
import { IconGripVertical, IconTrash, IconPlus, IconSettings } from '@tabler/icons-react';
import { WorkflowFile, FileMapping, MetaData } from '../services/api';

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
  const [activeId, setActiveId] = useState<string | null>(null);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      const oldIndex = files.findIndex((f) => f.file_path === active.id);
      const newIndex = files.findIndex((f) => f.file_path === over.id);

      const newFiles = [...files];
      const [removed] = newFiles.splice(oldIndex, 1);
      newFiles.splice(newIndex, 0, removed);

      // Update positions
      const updatedFiles = newFiles.map((f, idx) => ({ ...f, position: idx }));
      onFilesChange(updatedFiles);
    }
    setActiveId(null);
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

      <DndContext
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <Stack gap="xs">
          {files.map((file, index) => (
            <Paper
              key={file.file_path || `new-${index}`}
              p="md"
              withBorder
              style={{ cursor: 'grab' }}
            >
              <Group justify="space-between">
                <Group gap="xs">
                  <ActionIcon
                    variant="subtle"
                    style={{ cursor: 'grab' }}
                    onPointerDown={(e) => e.preventDefault()}
                  >
                    <IconGripVertical size={18} />
                  </ActionIcon>
                  <Badge size="xs" color="blue">
                    {index + 1}
                  </Badge>
                  <TextInput
                    size="xs"
                    placeholder="C:\\path\\to\\file.mcdx"
                    value={file.file_path}
                    onChange={(e) => handleUpdateFilePath(index, e.currentTarget.value)}
                    style={{ flex: 1 }}
                  />
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
          ))}
        </Stack>

        <DragOverlay>
          {activeId ? (
            <Paper p="md" withBorder shadow="sm">
              <Text>{activeId}</Text>
            </Paper>
          ) : null}
        </DragOverlay>
      </DndContext>
    </Stack>
  );
};
