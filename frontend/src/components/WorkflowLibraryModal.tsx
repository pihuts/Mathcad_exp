import {
  Modal,
  Stack,
  Group,
  Button,
  TextInput,
  Text,
  Alert,
  Loader,
  Table,
  Badge,
} from '@mantine/core';
import { IconDeviceFloppy } from '@tabler/icons-react';
import { useState, useEffect } from 'react';
import { useWorkflowLibrary } from '../hooks/useWorkflowLibrary';
import type { WorkflowConfig } from '../services/api';

interface WorkflowLibraryModalProps {
  opened: boolean;
  onClose: () => void;
  currentWorkflow: WorkflowConfig;
  onLoadWorkflow?: (config: WorkflowConfig) => void;
}

export const WorkflowLibraryModal = ({
  opened,
  onClose,
  currentWorkflow,
  onLoadWorkflow,
}: WorkflowLibraryModalProps) => {
  const [activeTab, setActiveTab] = useState<'save' | 'load'>('load');
  const [saveName, setSaveName] = useState('');
  const [saveSuccess, setSaveSuccess] = useState(false);

  const {
    configs,
    isLoadingConfigs,
    listError,
    refetchConfigs,
    saveConfig,
    isSaving,
    saveError,
    loadConfig,
    isLoadingConfig,
    loadError,
  } = useWorkflowLibrary();

  useEffect(() => {
    if (opened) {
      setSaveName('');
      setSaveSuccess(false);
      refetchConfigs();
    }
  }, [opened, refetchConfigs]);

  const handleSave = () => {
    if (!saveName.trim()) return;

    const configRequest = {
      ...currentWorkflow,
      name: saveName,
    };

    saveConfig(configRequest, {
      onSuccess: () => {
        setSaveSuccess(true);
        setTimeout(() => {
          setSaveSuccess(false);
          onClose();
        }, 1500);
      },
    });
  };

  const handleLoad = (configPath: string) => {
    loadConfig(configPath, {
      onSuccess: (config) => {
        if (onLoadWorkflow) {
          onLoadWorkflow(config);
          onClose();
        }
      },
    });
  };

  return (
    <Modal opened={opened} onClose={onClose} title="Workflow Library" size="md">
      <Stack>
        <Group grow>
          <Button
            variant={activeTab === 'load' ? 'filled' : 'light'}
            onClick={() => setActiveTab('load')}
          >
            Load Workflow
          </Button>
          <Button
            variant={activeTab === 'save' ? 'filled' : 'light'}
            onClick={() => setActiveTab('save')}
          >
            Save Workflow
          </Button>
        </Group>

        {activeTab === 'load' && (
          <Stack>
            {isLoadingConfigs && <Loader />}
            {listError && (
              <Alert color="red">Error loading workflows: {(listError as Error).message}</Alert>
            )}
            {!isLoadingConfigs && configs && configs.length === 0 && (
              <Text c="dimmed">No saved workflows found.</Text>
            )}
            {configs && configs.length > 0 && (
              <Table>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Name</Table.Th>
                    <Table.Th>Files</Table.Th>
                    <Table.Th>Created</Table.Th>
                    <Table.Th>Action</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {configs.map((config) => (
                    <Table.Tr key={config.path}>
                      <Table.Td>{config.name}</Table.Td>
                      <Table.Td>{config.files_count}</Table.Td>
                      <Table.Td>{new Date(config.created_at).toLocaleDateString()}</Table.Td>
                      <Table.Td>
                        <Button
                          size="xs"
                          onClick={() => handleLoad(config.path)}
                          loading={isLoadingConfig}
                        >
                          Load
                        </Button>
                      </Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            )}
            {loadError && (
              <Alert color="red">Error loading workflow: {(loadError as Error).message}</Alert>
            )}
          </Stack>
        )}

        {activeTab === 'save' && (
          <Stack>
            <TextInput
              label="Workflow Name"
              placeholder="e.g., Steel Beam Design, Multi-stage Analysis"
              value={saveName}
              onChange={(e) => setSaveName(e.currentTarget.value)}
            />
            <Group>
              <Button onClick={handleSave} loading={isSaving} leftSection={<IconDeviceFloppy size={16} />}>
                Save Workflow
              </Button>
              {saveSuccess && (
                <Badge color="green">Saved successfully!</Badge>
              )}
            </Group>
            {saveError && (
              <Alert color="red">Error saving workflow: {(saveError as Error).message}</Alert>
            )}
            <Text size="xs" c="dimmed">
              This will save the current workflow (files, mappings, export settings) to the library.
            </Text>
          </Stack>
        )}
      </Stack>
    </Modal>
  );
};
