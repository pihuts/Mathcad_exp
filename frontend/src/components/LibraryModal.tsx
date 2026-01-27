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
import { useLibrary } from '../hooks/useLibrary';
import type { InputConfig } from '../services/api';

interface LibraryModalProps {
  opened: boolean;
  onClose: () => void;
  filePath: string;
  currentInputs: Record<string, any[]>; // Current alias configs from App state
  exportPdf: boolean;
  exportMcdx: boolean;
  outputDir?: string;
  onLoadConfig?: (config: { inputs: InputConfig[]; exportPdf: boolean; exportMcdx: boolean }) => void;
}

export const LibraryModal = ({
  opened,
  onClose,
  filePath,
  currentInputs,
  exportPdf,
  exportMcdx,
  outputDir,
  onLoadConfig,
}: LibraryModalProps) => {
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
  } = useLibrary(filePath);

  // Reset save state when modal opens
  useEffect(() => {
    if (opened) {
      setSaveName('');
      setSaveSuccess(false);
      refetchConfigs();
    }
  }, [opened, refetchConfigs]);

  const handleSave = () => {
    if (!saveName.trim()) return;

    // Convert currentInputs to InputConfig[]
    const inputConfigs: InputConfig[] = Object.entries(currentInputs).flatMap(([alias, configs]) => {
      const firstConfig = configs[0];
      if (!firstConfig) return [];

      // Handle both InputConfig objects and plain values
      if (typeof firstConfig === 'object' && 'value' in firstConfig) {
        return [{ alias, value: firstConfig.value, units: firstConfig.units }];
      }
      return [{ alias, value: firstConfig }];
    });

    const configRequest = {
      name: saveName,
      file_path: filePath,
      inputs: inputConfigs,
      export_pdf: exportPdf,
      export_mcdx: exportMcdx,
      output_dir: outputDir,
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
        if (onLoadConfig) {
          onLoadConfig({
            inputs: config.inputs,
            exportPdf: config.export_pdf,
            exportMcdx: config.export_mcdx,
          });
          onClose();
        }
      },
    });
  };

  return (
    <Modal opened={opened} onClose={onClose} title="Library" size="md">
      <Stack>
        <Group grow>
          <Button
            variant={activeTab === 'load' ? 'filled' : 'light'}
            onClick={() => setActiveTab('load')}
          >
            Load Config
          </Button>
          <Button
            variant={activeTab === 'save' ? 'filled' : 'light'}
            onClick={() => setActiveTab('save')}
          >
            Save Config
          </Button>
        </Group>

        {activeTab === 'load' && (
          <Stack>
            {isLoadingConfigs && <Loader />}
            {listError && (
              <Alert color="red">Error loading configs: {(listError as Error).message}</Alert>
            )}
            {!isLoadingConfigs && configs && configs.length === 0 && (
              <Text c="dimmed">No saved configurations found for this file.</Text>
            )}
            {configs && configs.length > 0 && (
              <Table>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Name</Table.Th>
                    <Table.Th>Created</Table.Th>
                    <Table.Th>Action</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {configs.map((config) => (
                    <Table.Tr key={config.path}>
                      <Table.Td>{config.name}</Table.Td>
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
              <Alert color="red">Error loading config: {(loadError as Error).message}</Alert>
            )}
          </Stack>
        )}

        {activeTab === 'save' && (
          <Stack>
            <TextInput
              label="Configuration Name"
              placeholder="e.g., Bolt Diameters, Load Case 1"
              value={saveName}
              onChange={(e) => setSaveName(e.currentTarget.value)}
            />
            <Group>
              <Button onClick={handleSave} loading={isSaving} leftSection={<IconDeviceFloppy size={16} />}>
                Save Configuration
              </Button>
              {saveSuccess && (
                <Badge color="green">Saved successfully!</Badge>
              )}
            </Group>
            {saveError && (
              <Alert color="red">Error saving config: {(saveError as Error).message}</Alert>
            )}
            <Text size="xs" c="dimmed">
              This will save the current input configuration to a library template for reuse.
            </Text>
          </Stack>
        )}
      </Stack>
    </Modal>
  );
};
